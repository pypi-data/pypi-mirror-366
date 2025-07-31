import os
import re


def replace_text_in_csv(folder_path):
    """
    Recursively searches for CSV files in a folder and replaces a specific text pattern.

    Args:
        folder_path (str): The path to the folder to start searching from.
    """
    # Define the pattern to search for: starts with /mnt/petrelfs/liwei1/Med-MLEBench/medmnist_preprocess/
    # and captures the rest of the path.
    # The pattern `re.escape()` is used to handle potential special characters in the fixed part of the path.
    search_pattern = re.compile(re.escape("/mnt/petrelfs/liwei1/Med-MLEBench/medmnist_preprocess/") + r"(.*)")

    print(f"Starting search in folder: {folder_path}")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                try:
                    # Read the original content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Perform the replacement using the compiled regex pattern
                    # The `re.sub` function replaces matches of the pattern with the string returned by the lambda function.
                    # The lambda function takes the match object and returns the captured group (the part after the prefix).
                    new_content = search_pattern.sub(r'\1', content)

                    # Check if any replacement was made before writing to avoid unnecessary file writes
                    if new_content != content:
                        print("Changes detected, writing back to file.")
                        # Write the modified content back to the file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                    else:
                        print("No changes needed.")

                except FileNotFoundError:
                    print(f"Error: File not found - {file_path}")
                except PermissionError:
                    print(f"Error: Permission denied to access - {file_path}")
                except Exception as e:
                    print(f"An unexpected error occurred while processing {file_path}: {e}")

    print("Processing complete.")

# --- How to use the script ---
# Replace 'your_folder_path_here' with the actual path to your folder.
# Example usage:
# replace_text_in_csv('/path/to/your/folder')

# Uncomment the line below and provide the folder path to run the script
replace_text_in_csv('./')

