import sys
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

#设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置黑体或其他支持中文的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def parse_file(filename):
    data = {'b': defaultdict(int), 'j': defaultdict(int)}
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                category, value = line.strip().split()
                data[category][value] += 1
    return data

def save_stats(data, category):
    filename = f'stats_{category}.txt'
    with open(filename, 'w') as f:
        for value, count in sorted(data[category].items(), key=lambda x: x[1], reverse=True):
            f.write(f"{value}\t{count}\n")
    print(f"类别 {category} 的统计结果已保存到 {filename}")

def count_frequency(data):
    freq = {'b': defaultdict(int), 'j': defaultdict(int)}
    for category in data:
        for count in data[category].values():
            freq[category][count] += 1
    return freq

def plot_interactive(freq):
    plt.figure(figsize=(10, 6))
    
    # 存储线条对象和对应的数据
    lines_data = {}
    
    for category in freq:
        x = sorted(freq[category].keys())
        y = [freq[category][count] for count in x]
        line, = plt.plot(x, y, 'o-', label='条件分支' if category == 'b' else '直接跳转')
        lines_data[line] = (x, y, category)  # 保存线条对应的数据
    
    # 统一的点击事件处理
    def on_click(event):
        if event.inaxes != plt.gca(): return
        
        # 找出被点击的线条
        clicked_line = None
        min_dist = float('inf')
        for line in lines_data:
            x_data, y_data, _ = lines_data[line]
            # 计算鼠标位置到线条上所有点的距离
            for xi, yi in zip(x_data, y_data):
                dist = (event.xdata - xi)**2 + (event.ydata - yi)**2
                if dist < min_dist:
                    min_dist = dist
                    clicked_line = line
                    clicked_point = (xi, yi)
        
        if clicked_line is None: return
        
        # 清除之前的注释
        for annotation in plt.gca().texts:
            annotation.remove()
        
        # 显示新注释
        plt.annotate(f'({clicked_point[0]:.0f}, {clicked_point[1]:.0f})',
                    clicked_point,
                    textcoords="offset points",
                    xytext=(10,10), ha='center',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        plt.draw()
    
    plt.gcf().canvas.mpl_connect('button_press_event', on_click)
    
    plt.xlabel('出现次数')
    plt.ylabel('分支/跳转指令数')
    plt.title('分支/跳转指令的出现次数分布')
    plt.legend()
    plt.grid(True)
    plt.show()

# 主程序
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py input_file.txt")
        sys.exit(1)
    input_file = sys.argv[1]
    data = parse_file(input_file)
    save_stats(data, 'b')
    save_stats(data, 'j')
    freq = count_frequency(data)
    plot_interactive(freq)
