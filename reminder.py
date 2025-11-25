"""
任务提醒模块
提供任务开始前的提醒功能
"""
import time
import json
import os
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import tkintertools as tkintertools

class ReminderManager:
    """提醒管理器"""
    
    def __init__(self, reminder_file='reminders.json'):
        self.reminder_file = reminder_file
        self.reminders = {}
        self.load_reminders()
        self.running = False
        self.thread = None
    
    def load_reminders(self):
        """加载提醒设置"""
        if os.path.exists(self.reminder_file):
            try:
                with open(self.reminder_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
            except:
                self.reminders = {}
        else:
            self.reminders = {}
    
    def save_reminders(self):
        """保存提醒设置"""
        with open(self.reminder_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, indent=4, ensure_ascii=False)
    
    def start_reminder_check(self):
        """开始提醒检查"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._reminder_check_loop, daemon=True)
            self.thread.start()
    
    def stop_reminder_check(self):
        """停止提醒检查"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _reminder_check_loop(self):
        """提醒检查循环"""
        while self.running:
            try:
                self.check_reminders()
                time.sleep(10)  # 每10秒检查一次
            except Exception as e:
                print(f"提醒检查错误: {e}")
                time.sleep(30)
    
    def check_reminders(self):
        """检查需要触发的提醒"""
        current_time = time.time()
        reminders_to_remove = []
        
        for reminder_id, reminder_data in self.reminders.items():
            if reminder_data.get('triggered', False):
                continue
                
            reminder_time = reminder_data['reminder_time']
            
            if current_time >= reminder_time:
                # 触发提醒
                self.trigger_reminder(reminder_data)
                reminders_to_remove.append(reminder_id)
        
        # 移除已触发的提醒
        for reminder_id in reminders_to_remove:
            del self.reminders[reminder_id]
        
        if reminders_to_remove:
            self.save_reminders()
    
    def trigger_reminder(self, reminder_data):
        """触发提醒"""
        try:
            # 在主线程中显示提醒
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            task_name = reminder_data['task_name']
            task_time = reminder_data['task_time']
            
            # 格式化时间显示
            task_time_str = datetime.fromtimestamp(reminder_data['original_time']).strftime('%Y/%m/%d %H:%M:%S')
            
            message = f"🔔 任务提醒\n\n任务: {task_name}\n开始时间: {task_time_str}\n\n请准备开始任务！"
            
            # 显示消息框
            messagebox.showinfo("任务提醒", message)            
            root.destroy()
        except Exception as e:
            print(f"触发提醒错误: {e}")
    
    def add_reminder(self, task_create_time, task_name, task_time, minutes_before):
        """添加提醒"""
        current_time = time.time()
    
        # 首先检查任务时间是否已经过期（任务开始时间是否在当前时间之前）
        if task_time <= current_time:
            return False, "不能为已过期的任务设置提醒"
    
        # 计算提醒时间（任务开始前 minutes_before 分钟）
        reminder_time = task_time - (minutes_before * 60)
    
        # 检查提醒时间是否已经过期
        if reminder_time <= current_time:
            return False, f"提醒时间设置无效：任务将在 {int((task_time - current_time)/60)} 分钟后开始，无法设置提前 {minutes_before} 分钟提醒"
    
        reminder_id = f"{task_create_time}_{minutes_before}"
    
        self.reminders[reminder_id] = {
            'task_create_time': task_create_time,
            'task_name': task_name,
            'task_time': task_time,
            'original_time': task_time,
            'reminder_time': reminder_time,
            'minutes_before': minutes_before,
            'triggered': False
        }
    
        self.save_reminders()
        return True, f"提醒设置成功：将在任务开始前 {minutes_before} 分钟提醒您"
    
    def remove_reminder(self, task_create_time):
        """移除任务的所有提醒"""
        reminders_to_remove = [
            reminder_id for reminder_id in self.reminders.keys()
            if reminder_id.startswith(task_create_time)
        ]
        
        for reminder_id in reminders_to_remove:
            del self.reminders[reminder_id]
        
        if reminders_to_remove:
            self.save_reminders()
    
    def get_task_reminders(self, task_create_time):
        """获取任务的提醒设置"""
        return [
            reminder_data for reminder_id, reminder_data in self.reminders.items()
            if reminder_id.startswith(task_create_time)
        ]
    
    def has_reminder(self, task_create_time):
        """检查任务是否有提醒"""
        return any(reminder_id.startswith(task_create_time) for reminder_id in self.reminders.keys())

# 全局提醒管理器实例
reminder_manager = ReminderManager()


class ReminderWindow:
    """提醒设置窗口"""
    
    toplevel = None
    canvas = None
    current_task = None
    theme = None  # 添加这一行来存储主题配置
    
    @classmethod
    def init_window(cls, master, theme):
        """初始化窗口"""
        cls.theme = theme  # 保存主题配置
        if cls.toplevel is None:
            cls.toplevel = tkintertools.Toplevel(master, geometry='300x250')
            cls.toplevel.overrideredirect(True)
            cls.toplevel.bind('<B1-Motion>', cls.move)
            cls.toplevel.bind('<Button-1>', cls.move)
            cls.toplevel.title("设置提醒")
            
            cls.canvas = tkintertools.Canvas(
                cls.toplevel, 298, 248,
                bg=theme['ReadWindow']['bg'], 
                highlightbackground=theme['ReadWindow']['highlightbackground'])
            cls.canvas.configure(highlightthickness=1)
            cls.canvas.place(x=0, y=0)
            
            # 标题
            cls.canvas.create_text(
                150, 20, text='—— 设置提醒 ——', 
                font=('楷体', 14), fill=theme['MainColor'][3])
            
            # 提前时间设置
            cls.canvas.create_text(
                50, 60, text='提前提醒(分钟):', 
                font=('楷体', 11), fill=theme['MainColor'][0], anchor='w')
            
            cls.minutes_entry = tkintertools.CanvasEntry(
                cls.canvas, 150, 55, 80, 25, 0, '15',
                font=('楷体', 11),
                color_outline=theme['CanvasEntry']['color_outline'],
                color_fill=theme['CanvasEntry']['color_fill'],
                color_text=theme['CanvasEntry']['color_text'])
            
            # 任务信息显示
            cls.task_info_text = cls.canvas.create_text(
                150, 110, text='', 
                font=('楷体', 10), fill=theme['MainColor'][0], width=250)
            
            # 按钮
            cls.confirm_button = tkintertools.CanvasButton(
                cls.canvas, 70, 180, 80, 30, 5, '确定',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=cls.confirm_reminder)
            
            cls.cancel_button = tkintertools.CanvasButton(
                cls.canvas, 170, 180, 80, 30, 5, '取消',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=cls.close)
            
            # 关闭按钮
            tkintertools.CanvasButton(
                cls.canvas, 275, 5, 20, 20, 0, '×',
                font=('楷体', 15),
                color_fill=('', 'red', theme['MainColor'][4]),
                color_text=theme['ToolButton']['color_text'],
                color_outline=tkintertools.COLOR_NONE,
                command=cls.close)
    
    @classmethod
    def open(cls, master, theme, geometry, task):
        """打开提醒设置窗口"""
        cls.init_window(master, theme)
        cls.current_task = task
        
        # 更新任务信息显示
        task_info = f"任务: {task.data['name']}\n时间: {task.data['date']}"
        cls.canvas.itemconfigure(cls.task_info_text, text=task_info)
        
        # 设置默认提前时间
        cls.minutes_entry.set('15')
        
        # 显示窗口
        cls.toplevel.geometry('300x250+%d+%d' % (geometry[0]+350*tkintertools.S, geometry[1]))
        cls.toplevel.deiconify()
        cls.toplevel.lift()
    
    @classmethod
    def close(cls):
        """关闭提醒设置窗口"""
        cls.toplevel.withdraw()
        cls.current_task = None
    

    @classmethod
    def confirm_reminder(cls):
        """确认设置提醒"""
        try:
            minutes = int(cls.minutes_entry.get().strip())
            if minutes <= 0:
                messagebox.showwarning("提示", "提前时间必须大于0分钟!")
                return
    
            if minutes > 1440:  # 24小时
                messagebox.showwarning("提示", "提前时间不能超过24小时(1440分钟)!")
                return
    
            # 检查任务时间是否已经过去
            task_time = cls.current_task.data['time']
            current_time = time.time()
    
            if task_time <= current_time:
                messagebox.showwarning("提示", "不能为已过期的任务设置提醒！")
                return
    
            # 检查提醒时间是否有效
            reminder_time = task_time - (minutes * 60)
            if reminder_time <= current_time:
                minutes_until_task = int((task_time - current_time) / 60)
                messagebox.showwarning("提示", 
                    f"提醒时间设置无效！\n\n"
                    f"任务将在 {minutes_until_task} 分钟后开始\n"
                    f"无法设置提前 {minutes} 分钟提醒\n\n"
                    f"请设置小于 {minutes_until_task} 分钟的提前时间")
                return
    
            # 添加提醒
            success, message = reminder_manager.add_reminder(
                cls.current_task.data['create'],
                cls.current_task.data['name'],
                task_time,
                minutes
            )
    
            if success:
                messagebox.showinfo("成功", message)
                # 更新任务卡片的提醒按钮状态
                if hasattr(cls.current_task, 'reminder_button'):
                    # 使用类中存储的主题配置，而不是直接使用theme变量
                    cls.current_task.reminder_button.configure(
                        color_fill=('', 'orange', cls.theme['MainColor'][4]))
                    cls.current_task.reminder_button.state()
            else:
                messagebox.showwarning("提示", message)
    
            cls.close()
    
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的数字！")

    
    @classmethod
    def move(cls, event, coords=[0, 0]):
        """窗口拖动"""
        if event.y <= 180:
            if event.type.__str__() == '4':
                coords[0], coords[1] = event.x, event.y
            else:
                x, y = event.x - coords[0], event.y - coords[1]
                lx, ly = map(int, cls.toplevel.geometry().split('+')[-2:])
                cls.toplevel.geometry('300x200+%d+%d' % (lx+x, ly+y))


def open_reminder_setting(task):
    """打开提醒设置"""
    from main import MainWindow, theme  # 延迟导入避免循环导入
    geometry = tuple(int(i) for i in MainWindow.root.geometry().split('+')[-2:])
    ReminderWindow.open(MainWindow.root, theme, geometry, task)


# 启动提醒检查
reminder_manager.start_reminder_check()
