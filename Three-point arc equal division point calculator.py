import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

def calc_circle_by_3pts(x1, y1, x2, y2, x3, y3):
    # 通过三点坐标计算圆心和半径
    temp = x2**2 + y2**2
    bc = (x1**2 + y1**2 - temp) / 2.0
    cd = (temp - x3**2 - y3**2) / 2.0
    det = (x1 - x2) * (y2 - y3) - (x2 - x3) * (y1 - y2)
    if abs(det) < 1e-10:
        return None  # 三点共线
    cx = (bc * (y2 - y3) - cd * (y1 - y2)) / det
    cy = ((x1 - x2) * cd - (x2 - x3) * bc) / det
    r = math.hypot(cx - x1, cy - y1)
    return cx, cy, r

def get_angle(cx, cy, px, py):
    return math.atan2(py - cy, px - cx)

def arc_points(cx, cy, r, theta1, theta2, n, direction):
    # direction: 1=逆时针, -1=顺时针
    dtheta = theta2 - theta1
    if direction == 1:
        if dtheta <= 0:
            dtheta += 2 * math.pi
    else:
        if dtheta >= 0:
            dtheta -= 2 * math.pi
    points = []
    for i in range(1, n + 1):
        t = i / (n + 1)
        theta = theta1 + t * dtheta
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    return points

def draw_arc(ax, cx, cy, r, theta1, theta2, direction):
    dtheta = theta2 - theta1
    if direction == 1:
        if dtheta <= 0:
            dtheta += 2 * math.pi
    else:
        if dtheta >= 0:
            dtheta -= 2 * math.pi
    ts = [theta1 + dtheta * t / 100 for t in range(101)]
    xs = [cx + r * math.cos(t) for t in ts]
    ys = [cy + r * math.sin(t) for t in ts]
    ax.plot(xs, ys, 'b-')

class ArcPointPicker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('三点圆弧等分点计算器V1.0')
        self.geometry('800x600')
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        plt.close('all')  # 关闭所有matplotlib图形
        self.quit()
        self.destroy()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        font_big = ('微软雅黑', 12)
        # 输入区（每个点X和Y同一行）
        labels = ['起点', '经过点', '终点']
        self.entries = []
        for i, text in enumerate(labels):
            ttk.Label(frm, text=f'{text}X', font=font_big).grid(row=i, column=0, sticky='e', pady=2)
            ent_x = ttk.Entry(frm, font=font_big, width=8)
            ent_x.grid(row=i, column=1, pady=2)
            self.entries.append(ent_x)
            ttk.Label(frm, text=f'{text}Y', font=font_big).grid(row=i, column=2, sticky='e', pady=2)
            ent_y = ttk.Entry(frm, font=font_big, width=8)
            ent_y.grid(row=i, column=3, pady=2)
            self.entries.append(ent_y)
        # 取点方式选择
        self.mode_var = tk.StringVar(value='count')
        ttk.Label(frm, text='取点方式', font=font_big).grid(row=3, column=0, sticky='e', pady=2)
        ttk.Radiobutton(frm, text='等分数量', variable=self.mode_var, value='count', command=self.update_mode, style='Big.TRadiobutton').grid(row=3, column=1, sticky='w')
        ttk.Radiobutton(frm, text='等分距离(mm)', variable=self.mode_var, value='dist', command=self.update_mode, style='Big.TRadiobutton').grid(row=3, column=2, sticky='w')
        # 数量输入
        self.ent_count = ttk.Entry(frm, font=font_big, width=8)
        self.ent_count.grid(row=4, column=1, pady=2)
        ttk.Label(frm, text='数量', font=font_big).grid(row=4, column=0, sticky='e', pady=2)
        # 距离输入
        self.ent_dist = ttk.Entry(frm, font=font_big, width=8)
        self.ent_dist.grid(row=5, column=1, pady=2)
        ttk.Label(frm, text='每段长度(mm)', font=font_big).grid(row=5, column=0, sticky='e', pady=2)
        # 默认只显示数量输入
        self.ent_dist.grid_remove()
        frm.grid_rowconfigure(6, minsize=10)
        # 按钮
        ttk.Button(frm, text='计算并绘图', command=self.on_calc, style='Big.TButton').grid(row=6, column=0, columnspan=4, pady=10)
        # 结果区
        self.result_box = tk.Text(frm, width=30, height=15, font=font_big)
        self.result_box.grid(row=7, column=0, columnspan=4, pady=10)
        # 画布区
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        # 设置大号按钮样式
        style = ttk.Style()
        style.configure('Big.TButton', font=font_big)
        style.configure('Big.TRadiobutton', font=font_big)

    def update_mode(self):
        if self.mode_var.get() == 'count':
            self.ent_count.grid()
            self.ent_dist.grid_remove()
        else:
            self.ent_count.grid_remove()
            self.ent_dist.grid()

    def on_calc(self):
        try:
            x1 = float(self.entries[0].get())
            y1 = float(self.entries[1].get())
            x2 = float(self.entries[2].get())
            y2 = float(self.entries[3].get())
            x3 = float(self.entries[4].get())
            y3 = float(self.entries[5].get())
            mode = self.mode_var.get()
            if mode == 'count':
                n = int(self.ent_count.get())
                if n < 1:
                    raise ValueError('取点数量必须大于0')
                seg_len = None
            else:
                seg_len = float(self.ent_dist.get())
                if seg_len <= 0:
                    raise ValueError('每段长度必须大于0')
                n = None
        except Exception as e:
            messagebox.showerror('输入错误', str(e))
            return
        res = calc_circle_by_3pts(x1, y1, x2, y2, x3, y3)
        if not res:
            messagebox.showerror('错误', '三点共线，无法构成圆弧')
            return
        cx, cy, r = res
        theta1 = get_angle(cx, cy, x1, y1)
        theta2 = get_angle(cx, cy, x3, y3)
        theta_mid = get_angle(cx, cy, x2, y2)
        # 判断方向：经过点在起点到终点的逆时针还是顺时针方向
        d1 = (theta_mid - theta1) % (2 * math.pi)
        d2 = (theta2 - theta1) % (2 * math.pi)
        direction = 1 if d1 < d2 else -1
        # 计算弧长
        arc_angle = theta2 - theta1
        if direction == 1:
            if arc_angle <= 0:
                arc_angle += 2 * math.pi
        else:
            if arc_angle >= 0:
                arc_angle -= 2 * math.pi
        arc_len = abs(r * arc_angle)
        # 根据取点方式计算等分点
        if mode == 'count':
            pts = arc_points(cx, cy, r, theta1, theta2, n, direction)
        else:
            n = int(arc_len // seg_len)
            if n < 1:
                messagebox.showerror('输入错误', '弧长不足以分出一段')
                return
            pts = arc_points(cx, cy, r, theta1, theta2, n, direction)
        # 显示结果
        self.result_box.delete('1.0', tk.END)
        self.result_box.insert(tk.END, f'圆弧弧长: {arc_len:.4f} mm\n')
        for i, (x, y) in enumerate(pts, 1):
            self.result_box.insert(tk.END, f'点{i}: X={x:.4f}, Y={y:.4f}\n')
        # 绘图
        self.ax.clear()
        self.ax.plot([x1, x2, x3], [y1, y2, y3], 'ro')
        self.ax.plot(cx, cy, 'go')
        self.ax.text(cx, cy, '圆心', color='g', bbox=dict(facecolor='none', edgecolor='none'))
        draw_arc(self.ax, cx, cy, r, theta1, theta2, direction)
        if pts:
            xs, ys = zip(*pts)
            self.ax.plot(xs, ys, 'ms')
            for i, (x, y) in enumerate(pts, 1):
                self.ax.text(x, y, f'{i}', color='m', bbox=dict(facecolor='none', edgecolor='none'))
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == '__main__':
    app = ArcPointPicker()
    app.mainloop() 