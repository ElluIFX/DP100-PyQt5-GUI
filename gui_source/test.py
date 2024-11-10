import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 读取CSV文件
data = pd.read_csv("Li-ion.csv")

# 打印列名以确认
print(data.columns)

# 提取SOC和电压数据
soc = data[data.columns[0]].to_numpy()
voltage = data[data.columns[1]].to_numpy()

new_soc = np.arange(0, 100 + 1e-9, 0.1)
new_voltage = np.interp(new_soc, soc, voltage)

# 绘制图表
plt.figure(figsize=(10, 6))
plt.plot(new_soc, new_voltage, linestyle="-")
plt.plot(soc, voltage, linestyle="", marker="o")
plt.title("SOC vs Cell Voltage")
plt.xlabel("State of Charge (%)")
plt.ylabel("Cell Voltage (V)")
plt.grid(True)
plt.show()
