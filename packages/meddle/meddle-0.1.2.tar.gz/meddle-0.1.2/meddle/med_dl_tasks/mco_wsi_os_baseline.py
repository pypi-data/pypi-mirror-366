import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
import matplotlib.pyplot as plt

# 加载数据
data = pd.read_csv("./mco_wsi_gigapath/train_meta.csv")

# === Event 1: 总生存分析 ===
# 时间变量：OS_Months
# 事件变量：Death_Event (0=存活/删失, 1=任何原因死亡)

time_col = 'OS_Months'
event_col = 'Death_Event'

print(f"总生存分析:")
print(f"总患者数: {len(data)}")
print(f"死亡事件: {data[event_col].sum()}")
print(f"删失: {len(data) - data[event_col].sum()}")
print(f"中位生存期: {data[time_col].median()}月")

# Kaplan-Meier生存曲线
kmf = KaplanMeierFitter()
kmf.fit(data[time_col], data[event_col])
kmf.plot_survival_function()
plt.title('Overall Survival')
# plt.show()
plt.savefig('overall_survival.png')

# 按分期分组的生存曲线
for stage in data['Overall_Stage'].unique():
    stage_data = data[data['Overall_Stage'] == stage]
    kmf.fit(stage_data[time_col], stage_data[event_col], label=f'Stage {stage}')
    kmf.plot_survival_function()
plt.title('Overall Survival by Stage')
# plt.show()
plt.savefig('overall_survival_by_stage.png')