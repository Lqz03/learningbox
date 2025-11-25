"""
番茄时钟模块
提供专注工作和休息的计时功能
"""
import time
import tkintertools as tkintertools
from tkinter import messagebox
from daily_recorder import daily_recorder

class PomodoroWindow:
    """ 番茄时钟界面 """
    
    toplevel = None
    canvas = None
    timer_text = None
    status_text = None
    start_button = None
    reset_button = None
    
    # 番茄时钟状态
    is_running = False
    is_break = False
    work_time = 25 * 60  # 默认25分钟工作时间
    break_time = 5 * 60   # 默认5分钟休息时间
    time_left = work_time
    timer_id = None
    current_task = ""  # 当前专注任务
    
    @classmethod
    def init_window(cls, master, theme):
        """ 初始化窗口 """
        if cls.toplevel is None:
            cls.toplevel = tkintertools.Toplevel(
                master, geometry='350x500')
            cls.toplevel.overrideredirect(True)
            cls.toplevel.bind('<B1-Motion>', cls.move)
            cls.toplevel.bind('<Button-1>', cls.move)
            
            cls.canvas = tkintertools.Canvas(
                cls.toplevel, 348, 498,
                bg=theme['ReadWindow']['bg'], 
                highlightbackground=theme['ReadWindow']['highlightbackground'])
            cls.canvas.configure(highlightthickness=1)
            cls.canvas.place(x=0, y=0)            
            # 标题
            cls.canvas.create_text(
                175, 30, text='—— 番茄时钟 ——', font=('楷体', 16), fill=theme['MainColor'][3])
            
            # 任务输入区域
            cls.canvas.create_text(
                175, 70, text='专注任务', font=('楷体', 12), fill=theme['MainColor'][0])
            cls.task_entry = tkintertools.CanvasEntry(
                cls.canvas, 75, 85, 200, 25, 0, '',
                font=('楷体', 11),
                color_outline=theme['CanvasEntry']['color_outline'],
                color_fill=theme['CanvasEntry']['color_fill'],
                color_text=theme['CanvasEntry']['color_text'])
            
            # 时间设置区域
            cls.canvas.create_text(
                175, 130, text='时间设置', font=('楷体', 12), fill=theme['MainColor'][0])
            
            # 专注时间设置
            cls.canvas.create_text(
                100, 155, text='专注时长(分钟):', font=('楷体', 10), fill=theme['MainColor'][0], anchor='w')
            cls.work_time_entry = tkintertools.CanvasEntry(
                cls.canvas, 200, 150, 50, 25, 0, '25',
                font=('楷体', 11),
                color_outline=theme['CanvasEntry']['color_outline'],
                color_fill=theme['CanvasEntry']['color_fill'],
                color_text=theme['CanvasEntry']['color_text'])
            
            # 休息时间设置
            cls.canvas.create_text(
                100, 185, text='休息时长(分钟):', font=('楷体', 10), fill=theme['MainColor'][0], anchor='w')
            cls.break_time_entry = tkintertools.CanvasEntry(
                cls.canvas, 200, 180, 50, 25, 0, '5',
                font=('楷体', 11),
                color_outline=theme['CanvasEntry']['color_outline'],
                color_fill=theme['CanvasEntry']['color_fill'],
                color_text=theme['CanvasEntry']['color_text'])
            
            # 时间显示
            cls.timer_text = cls.canvas.create_text(
                175, 240, text='25:00', font=('楷体', 35), fill=theme['MainColor'][0])
            
            # 状态显示
            cls.status_text = cls.canvas.create_text(
                175, 290, text='准备开始', font=('楷体', 14), fill=theme['MainColor'][0])
            
            # 当前任务显示
            cls.task_text = cls.canvas.create_text(
                175, 320, text='', font=('楷体', 11), fill=theme['MainColor'][0], width=300)
            
            # 控制按钮
            cls.start_button = tkintertools.CanvasButton(
                cls.canvas, 75, 350, 80, 35, 5, '开始',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=cls.toggle_timer)
            
            cls.reset_button = tkintertools.CanvasButton(
                cls.canvas, 195, 350, 80, 35, 5, '重置',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=cls.reset_timer)
            
            # 关闭按钮
            tkintertools.CanvasButton(
                cls.canvas, 320, 10, 20, 20, 0, '×',
                font=('楷体', 15),
                color_fill=('', 'red', theme['MainColor'][4]),
                color_text=theme['ToolButton']['color_text'],
                color_outline=tkintertools.COLOR_NONE,
                command=cls.close)
            
            cls.canvas.create_text(
                125, 400, text='使用方法：', 
                font=('楷体', 10), fill=theme['MainColor'][0], anchor='nw')
            
            cls.canvas.create_text(
                125, 420, text='1. 输入专注任务', 
                font=('楷体', 9), fill=theme['MainColor'][0], anchor='nw')
            
            cls.canvas.create_text(
                125, 440, text='2. 设置专注和休息时间', 
                font=('楷体', 9), fill=theme['MainColor'][0], anchor='nw')
            
            cls.canvas.create_text(
                125, 460, text='3. 点击开始按钮', 
                font=('楷体', 9), fill=theme['MainColor'][0], anchor='nw')
    
    @classmethod
    def open(cls, master, theme, geometry):
        """ 打开番茄时钟 """
        cls.init_window(master, theme)
        cls.toplevel.geometry('350x500+%d+%d' % (geometry[0]+350*tkintertools.S, geometry[1]))
        cls.toplevel.deiconify()
        cls.toplevel.lift()
        cls.update_display()
    
    @classmethod
    def close(cls):
        """ 关闭番茄时钟 """
        if cls.timer_id:
            cls.toplevel.master.after_cancel(cls.timer_id)
            cls.timer_id = None
        cls.toplevel.withdraw()
    
    @classmethod
    def toggle_timer(cls):
        """ 开始/暂停计时器 """
        if not cls.is_running:
            # 检查任务是否输入
            cls.current_task = cls.task_entry.get().strip()
            if not cls.current_task:
                messagebox.showwarning("提示", "请输入专注任务！")
                return
            
            # 获取用户设置的时间
            try:
                work_str = cls.work_time_entry.get().strip()
                break_str = cls.break_time_entry.get().strip()
                
                # 检查是否为空
                if not work_str or not break_str:
                    messagebox.showwarning("提示", "请输入专注时间和休息时间！")
                    return
                
                # 转换为整数
                work_minutes = int(work_str)
                break_minutes = int(break_str)
                
                # 验证时间范围
                if work_minutes <= 0 or work_minutes > 180:
                    messagebox.showwarning("提示", "专注时间在1-180分钟之间比较合适!")
                    return
                
                if break_minutes <= 0 or break_minutes > 60:
                    messagebox.showwarning("提示", "休息时间在1-60分钟之间比较合适!")
                    return
                
                cls.work_time = work_minutes * 60
                cls.break_time = break_minutes * 60
                cls.time_left = cls.work_time
                
            except ValueError:
                # 如果转换失败，提示用户输入有效的数字
                messagebox.showwarning("提示", "请输入有效的时间数字！")
                return
        
        cls.is_running = not cls.is_running
        cls.start_button.configure(text='暂停' if cls.is_running else '继续')
        
        if cls.is_running:
            cls.canvas.itemconfigure(cls.status_text, text='专注时间' if not cls.is_break else '休息时间')
            cls.canvas.itemconfigure(cls.task_text, text=f'任务: {cls.current_task}')
            cls.countdown()
        else:
            cls.canvas.itemconfigure(cls.status_text, text='已暂停')
    
    @classmethod
    def reset_timer(cls):
        """ 重置计时器 """
        if cls.timer_id:
            cls.toplevel.master.after_cancel(cls.timer_id)
            cls.timer_id = None
        
        cls.is_running = False
        cls.is_break = False
        cls.time_left = cls.work_time
        cls.current_task = ""
        cls.start_button.configure(text='开始')
        cls.canvas.itemconfigure(cls.status_text, text='准备开始')
        cls.canvas.itemconfigure(cls.task_text, text='')
        cls.update_display()
    
    @classmethod
    def countdown(cls):
        """ 倒计时 """
        if not cls.is_running:
            return
    
        if cls.time_left > 0:
            cls.time_left -= 1
            cls.update_display()
            # 递归调用实现持续计时
            cls.timer_id = cls.toplevel.master.after(1000, cls.countdown)
        else:
            # 时间到，切换状态
            cls.is_break = not cls.is_break
            cls.time_left = cls.break_time if cls.is_break else cls.work_time  
            # 专注时间结束时自动记录到每日报告
            if not cls.is_break:  # 专注时间结束
                daily_recorder.add_completed_task(cls.current_task, 'pomodoro')  
            # 显示提示信息
            if cls.is_break:
                message = f"'{cls.current_task}' 专注时间结束！\n\
                    开始{cls.break_time//60}分钟休息"
            else:
                message = f"休息时间结束！\n开始新一轮'{cls.current_task}'专注"  
            messagebox.showinfo("番茄时钟", message)     
            # 更新状态显示
            cls.canvas.itemconfigure(cls.status_text, 
                                   text='休息时间' if cls.is_break else '专注时间')
            # 继续倒计时
            cls.update_display()
            cls.timer_id = cls.toplevel.master.after(1000, cls.countdown)
    
    @classmethod
    def update_display(cls):
        """ 更新显示 """
        minutes = cls.time_left // 60
        seconds = cls.time_left % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        cls.canvas.itemconfigure(cls.timer_text, text=time_str)
    
    @classmethod
    def move(cls, event, coords=[0, 0]):
        """ 窗口拖动 """
        if event.y <= 350:
            if event.type.__str__() == '4':
                coords[0], coords[1] = event.x, event.y
            else:
                x, y = event.x - coords[0], event.y - coords[1]
                lx, ly = map(int, cls.toplevel.geometry().split('+')[-2:])
                cls.toplevel.geometry('350x500+%d+%d' % (lx+x, ly+y))


def open_pomodoro():
    """ 打开番茄时钟 """
    from main import MainWindow, theme  # 导入主窗口和主题配置
    geometry = tuple(int(i) for i in MainWindow.root.geometry().split('+')[-2:])
    PomodoroWindow.open(MainWindow.root, theme, geometry)
