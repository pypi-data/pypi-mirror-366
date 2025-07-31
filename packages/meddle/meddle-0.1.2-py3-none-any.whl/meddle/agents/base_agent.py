import logging
import random
from typing import Callable, cast

import humanize

from ..backend import FunctionSpec, query
from ..interpreter import ExecutionResult
from ..journal import Journal, Node
from ..utils import data_preview
from ..utils.config import Config
from ..utils.metric import MetricValue, WorstMetricValue
from ..utils.response import extract_code, extract_text_up_to_code, wrap_code

logger = logging.getLogger("meddle")
ExecCallbackType = Callable[[str, bool], ExecutionResult]

review_func_spec = FunctionSpec(
    name="submit_review",
    json_schema={
        "type": "object",
        "properties": {
            "is_bug": {
                "type": "boolean",
                "description": "true if the output log shows that the execution failed or has some bug, otherwise false.",
            },
            "summary": {
                "type": "string",
                "description": "if there is a bug, propose a fix. Otherwise, write a short summary (2-3 sentences) describing the empirical findings.",
            },
            "metric": {
                "type": "number",
                "description": "If the code ran successfully, report the value of the validation metric. Otherwise, leave it null.",
            },
            "lower_is_better": {
                "type": "boolean",
                "description": "true if the metric should be minimized (i.e. a lower metric value is better, such as with MSE), false if the metric should be maximized (i.e. a higher metric value is better, such as with accuracy).",
            },
        },
        "required": ["is_bug", "summary", "metric", "lower_is_better"],
    },
    description="Submit a review evaluating the output of the training script.",
)

class BaseAgent:
    def __init__(
        self,
        task_desc: str,
        cfg: Config,
        journal: Journal,
    ):
        super().__init__()
        self.task_desc = task_desc
        self.cfg = cfg
        self.acfg = cfg.agent
        self.journal = journal
        self.data_preview: str | None = None
        self.profile = "You are a helpful assistance. "

    def has_empty_journal(self) -> bool:
        """Check if the journal is empty."""
        return not self.journal.nodes or len(self.journal.nodes) <= 0

    def update_with_external_journal(self, external_journal: Journal):
        if not isinstance(external_journal, Journal):
            raise ValueError("external_journal must be an instance of Journal")
        for n in external_journal.nodes:
            self.journal.append(n)
    
    def search_policy(self) -> Node | None:
        """Select a node to work on (or None to draft a new node)."""
        search_cfg = self.acfg.search

        # initial drafting (stop drafting if we have enough draft nodes)
        if len(self.journal.draft_nodes) < search_cfg.num_drafts:
            logger.debug("[search policy] drafting new node (not enough drafts)")
            return None

        # debugging (set default prob to 1.0 to forcely debug)
        if random.random() < search_cfg.debug_prob:
            # nodes that are buggy + leaf nodes + debug depth < max debug depth
            debuggable_nodes = [
                n
                for n in self.journal.buggy_nodes
                if (n.is_leaf and n.debug_depth <= search_cfg.max_debug_depth)
            ]
            if debuggable_nodes:
                logger.debug("[search policy] debugging")
                return random.choice(debuggable_nodes)
            logger.debug("[search policy] not debugging by chance")

        # back to drafting if no nodes to improve
        good_nodes = self.journal.good_nodes
        if not good_nodes:
            logger.debug("[search policy] drafting new node (no good nodes)")
            return None

        # greedy
        greedy_node = self.journal.get_best_node()
        logger.debug("[search policy] greedy node selected")
        return greedy_node

    @property
    def _prompt_environment(self):
        is_medical_code_lib_enabled = self.acfg.force_monai_with_prompt or self.acfg.enable_monai_knowledge_base
        pkgs = [
            "numpy",
            "pandas",
            "scikit-learn",
            "statsmodels",
            "xgboost",
            "lightGBM",
            "torch",
            "torchvision",
            "torch-geometric",
            "bayesian-optimization",
            "timm",
            "optuna",
        ]
        if is_medical_code_lib_enabled:
            pkgs += ["monai","lifelines"]
            
        random.shuffle(pkgs)
        pkg_str = ", ".join([f"`{p}`" for p in pkgs])
        
        if is_medical_code_lib_enabled:
            env_prompt = {
                "Installed Packages": f"Your solution can use any relevant deep learning packages such as: {pkg_str}. Feel free to use any other packages too (all packages are already installed!). For neural networks training on medical images, we suggest using MONAI rather than PyTorch/TensorFlow."
            }
        else:
            env_prompt = {
                "Installed Packages": f"Your solution can use any relevant deep learning packages such as: {pkg_str}. Feel free to use any other packages too (all packages are already installed!)."
            }
        return env_prompt

    @property
    def _prompt_impl_guideline(self):
        impl_guideline = [
            "The code should **implement the proposed solution** and **print the value of the evaluation metric computed on a hold-out validation set**.",
            "The code should be a single-file python program that is self-contained and can be executed as-is.",
            "No parts of the code should be skipped, don't terminate the before finishing the script.",
            "Your response should only contain a single code block.",
            f"Be aware of the running time of the code, it should complete within {humanize.naturaldelta(self.cfg.exec.timeout)}.",
            'All the provided input data is stored in "./input" directory.',
            '**If there is test data provided for this task, please save the test predictions in a `submission.csv` file in the "./working" directory as described in the task description** This is extremely important since this file is used for grading/evaluation. DO NOT FORGET THE submission.csv file!',
            'You can also use the "./working" directory to store any temporary files that your code needs to create.',
        ]
        if self.acfg.force_monai_with_prompt:
            impl_guideline.append(
                "You are recommended to use MONAI instead of PyTorch to implement these parts:"
                "1. **Data Pipeline**:"
                "- Use monai.data.ImageDataset for medical imaging data"
                "- Always wrap with MONAI transforms instead of PyTorch transforms, for example:"
                "     * Spatial transforms: EnsureChannelFirstd, Resized, RandRotate90d, RandZoomd, RandFlipd"
                "     * Intensity transforms: ScaleIntensityd, NormalizeIntensityd"    
                "     * Remember to use appropriate spatial_size with Resized when the image sizes are different"
                "2. **Network Design** (if your task is 3D):"
                "- Select from monai.networks.nets (DenseNet121/UNet for classification/segmentation)"
            )
        if self.acfg.expose_prediction:
            impl_guideline.append(
                "The implementation should include a predict() function, "
                "allowing users to seamlessly reuse the code to make predictions on new data. "
                "The prediction function should be well-documented, especially the function signature."
            )

        if self.acfg.k_fold_validation > 1:
            impl_guideline.append(
                f"The evaluation should be based on {self.acfg.k_fold_validation}-fold cross-validation but only if that's an appropriate evaluation for the task at hand."
            )

        return {"Implementation guideline": impl_guideline}

    @property
    def _prompt_resp_fmt(self):
        return {
            "Response format": (
                "Your response should be a brief outline/sketch of your proposed solution in natural language (3-5 sentences), "
                "followed by a single markdown code block (wrapped in ```) which implements this solution and prints out the evaluation metric. "
                "There should be no additional headings or text in your response. Just natural language text followed by a newline and then the markdown code block. "
            )
        }

    def plan_and_code_query(self, prompt, retries=3) -> tuple[str, str]:
        """Generate a natural language plan + code in the same LLM call and split them apart."""
        completion_text = None
        for _ in range(retries):
            completion_text = query(
                system_message=prompt,
                user_message=None,
                model=self.acfg.code.model,
                temperature=self.acfg.code.temp,
            )

            code = extract_code(completion_text)
            nl_text = extract_text_up_to_code(completion_text)

            if code and nl_text:
                # merge all code blocks into a single string
                return nl_text, code

            print("Plan + code extraction failed, retrying...")
        print("Final plan + code extraction attempt failed, giving up...")
        return "", completion_text  # type: ignore

    def update_data_preview(self):
        self.data_preview = data_preview.generate(self.cfg.workspace_dir)

    def parse_exec_result(self, node: Node, exec_result: ExecutionResult):
        ''' core function for feedback for this Agent'''
        logger.debug(f"Agent is parsing execution results for node {node.id}")

        node.absorb_exec_result(exec_result)

        prompt = {
            "Introduction": (
                self.profile + 
                "You have written code to solve this task and now need to evaluate the output of the code execution. "
                "You should determine if there were any bugs as well as report the empirical findings."
            ),
            "Task description": self.task_desc,
            "Implementation": wrap_code(node.code),
            "Execution output": wrap_code(node.term_out, lang=""),
        }

        response = cast(
            dict,
            query(
                system_message=prompt,
                user_message=None,
                func_spec=review_func_spec,
                model=self.acfg.feedback.model,
                temperature=self.acfg.feedback.temp,
            ),
        )

        # if the metric isn't a float then fill the metric with the worst metric
        if not isinstance(response["metric"], float):
            response["metric"] = None

        node.analysis = response["summary"]
        node.is_buggy = (
            response["is_bug"]
            or node.exc_type is not None
            or response["metric"] is None
        )

        if node.is_buggy:
            node.metric = WorstMetricValue()
        else:
            node.metric = MetricValue(
                response["metric"], maximize=not response["lower_is_better"]
            )

    def step(self, exec_callback: ExecCallbackType):
        ''' core logic of the actions of this Agent '''
        raise NotImplementedError

