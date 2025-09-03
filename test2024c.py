import pulp
import pandas as pd

# 读取表格数据
file1_path = r'F:\数学建模国赛\2024C\附件1.xlsx'
file2_path = r'F:\数学建模国赛\2024C\附件2.xlsx'

# 加载表格数据
land_df = pd.read_excel(file1_path)
crop_df = pd.read_excel(file2_path)

# 假设数据
# 地块信息
land_data = land_df[["地块名称", "地块类型", "地块面积/亩"]]
land_data.columns = ["地块", "类型", "面积"]

# 作物信息
crop_data = crop_df[["作物名称", "种植面积/亩"]]
crop_data.columns = ["作物", "面积"]

# 假设每种作物的售价和种植成本（这些数据通常应该由题目给定）
crop_data["售价"] = [6, 7, 8, 6]  # 价格示例：小麦、玉米、黄豆、绿豆
crop_data["种植成本"] = [3, 4, 2, 3]  # 假设成本：小麦、玉米、黄豆、绿豆

# 构建线性规划问题
prob = pulp.LpProblem("Optimal_Crop_Selection", pulp.LpMaximize)

# 定义决策变量：每块地种植的每种作物的面积
x = pulp.LpVariable.dicts("Crop_Area", 
                          ((land, crop) for land in land_data["地块"] for crop in crop_data["作物"]), 
                          lowBound=0, cat='Continuous')  # 连续变量表示每块地种植的面积

# 定义目标函数：最大化总利润
total_profit = pulp.lpSum([x[(land, crop)] * (crop_data[crop_data["作物"] == crop]["售价"].values[0] - crop_data[crop_data["作物"] == crop]["种植成本"].values[0])
                          for land in land_data["地块"] for crop in crop_data["作物"]])

prob += total_profit, "Total Profit"

# 约束条件
# 1. 地块面积限制：每块地的种植面积不能超过其实际面积
for land in land_data["地块"]:
    prob += pulp.lpSum([x[(land, crop)] for crop in crop_data["作物"]]) <= land_data[land_data["地块"] == land]["面积"].values[0], f"Land_{land}_Area_Limit"

# 2. 每块地不能种植超过最大销量的作物
# 假设每种作物的最大销量为 200 亩
max_sales = 200
for crop in crop_data["作物"]:
    prob += pulp.lpSum([x[(land, crop)] for land in land_data["地块"]]) <= max_sales, f"Crop_{crop}_Sales_Limit"

# 3. 最小种植面积约束：假设每种作物最小种植面积为 10 亩
min_area = 10
for land in land_data["地块"]:
    for crop in crop_data["作物"]:
        prob += x[(land, crop)] >= min_area, f"Min_Area_{land}_{crop}"

# 4. 滞销情况（超出销售量的部分不能销售）
for land in land_data["地块"]:
    for crop in crop_data["作物"]:
        prob += x[(land, crop)] <= max_sales, f"Excess_Overflow_{land}_{crop}"

# 求解问题
prob.solve()

# 输出结果
print("Optimal Crop Selection for Each Land:")
for land in land_data["地块"]:
    for crop in crop_data["作物"]:
        area_planted = pulp.value(x[(land, crop)])
        if area_planted > 0:
            print(f"Land {land} should plant {area_planted:.2f} acres of {crop}")
            
# 输出总利润
total_profit_value = pulp.value(prob.objective)
print(f"Total Profit: {total_profit_value:.2f} Yuan")
