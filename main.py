import calendar
import json
import os
import time
from tkinter import Event, filedialog, messagebox
from pomodoro import open_pomodoro
from daily_recorder import daily_recorder
from reminder import reminder_manager, open_reminder_setting
import tkintertools

__version__ = '1.0'
config, theme, S = {}, {}, tkintertools.S


def configure(modify: bool = False, **kw):
    """ 配置设定 """
    global config, theme
    with open('config.json', 'r') as file:
        config = json.load(file)
    if modify:
        config.update(kw)
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)
    else:
        with open('theme.json', 'r') as file:
            theme = json.load(file)[config['theme']]
        if config['transparent']:
            for widget in ('Label', 'Button', 'Entry', 'Text'):
                theme['Canvas' + widget]['color_fill'] = tkintertools.COLOR_NONE


configure()


class MainWindow:
    """ 主界面 """

    root = tkintertools.Tk(geometry='300x500+300+100')
    root.overrideredirect(True)
    root.iconbitmap('task.ico')

    rootcanvas = tkintertools.Canvas(
        root, 298, 498, bg=theme['rootcanvas']['bg'])
    rootcanvas.configure(
        highlightthickness=1, highlightbackground=theme['rootcanvas']['highlightbackground'])
    canvas = tkintertools.Canvas(root, 298, 445, bg=theme['canvas']['bg'])
    rootcanvas.place(x=0, y=0)
    canvas.place(x=1, y=30)
    bg = canvas.create_image(150, 222.5)
    rootcanvas.bind('<B1-Motion>', lambda event: MainWindow.move(event))
    rootcanvas.bind('<Button-1>', lambda event: MainWindow.move(event))
    canvas.bind('<MouseWheel>', lambda event: TaskCard.scroll(event))

    # 修改工具栏按钮顺序和功能
    widgets_tool: list[tkintertools._BaseWidget | int] = [
        # 第一个按钮：主页面按钮（房子图标）
        tkintertools.CanvasButton(
            rootcanvas, 165, 5, 20, 20, 0, '🏠',
            font=('楷体', 12),
            color_fill=('', 'skyblue', theme['MainColor'][4]),
            color_text=theme['ToolButton']['color_text'],
            color_outline=tkintertools.COLOR_NONE,
            command=lambda: switch_to_homepage()),
        # 第二个按钮：番茄钟
        tkintertools.CanvasButton(
            rootcanvas, 187, 5, 20, 20, 0, '⏰',
            font=('楷体', 12),
            color_fill=('', 'orange', theme['MainColor'][4]),
            color_text=theme['ToolButton']['color_text'],
            color_outline=tkintertools.COLOR_NONE,
            command=lambda: open_pomodoro()),
        # 第三个按钮：当日记录报告
        tkintertools.CanvasButton(
            rootcanvas, 209, 5, 20, 20, 0, '📝',
            font=('楷体', 12),
            color_fill=('', 'pink', theme['MainColor'][4]),
            color_text=theme['ToolButton']['color_text'],
            color_outline=tkintertools.COLOR_NONE,
            command=lambda: generate_daily_report()), 
        # 第四个按钮：设置
        tkintertools.CanvasButton(
            rootcanvas, 231, 5, 20, 20, 0, '⚙',
            font=('楷体', 12),
            color_fill=('', 'green', theme['MainColor'][4]),
            color_text=theme['ToolButton']['color_text'],
            color_outline=tkintertools.COLOR_NONE,
            command=lambda: openset()),
        # 第五个按钮：最小化
        tkintertools.CanvasButton(
            rootcanvas, 253, 5, 20, 20, 0, '-',
            font=('楷体', 15),
            color_fill=('', '#777', theme['MainColor'][4]),
            color_text=theme['ToolButton']['color_text'],
            color_outline=tkintertools.COLOR_NONE,
            command=lambda: windowswitch(True)),
        # 第六个按钮：关闭
        tkintertools.CanvasButton(
            rootcanvas, 275, 5, 20, 20, 0, '×',
            font=('楷体', 15),
            color_fill=('', 'red', theme['MainColor'][4]),
            color_text=theme['ToolButton']['color_text'],
            color_outline=tkintertools.COLOR_NONE,
            command=root.quit),

        rootcanvas.create_text(
            5, 14, text='📃', fill=theme['MainColor'][0], anchor='w', font=('楷体', 12)),
        rootcanvas.create_text(
            20, 15, text='学习工具箱', fill=theme['MainColor'][0], anchor='w', font=('楷体', 12)),
        rootcanvas.create_text(
            5, 487, text='任务个数:', anchor='w', fill=theme['MainColor'][0], font=('楷体', 12)),
        rootcanvas.create_text(80, 487, anchor='w', font=('楷体', 12)),
        rootcanvas.create_text(295, 487, anchor='e', font=('楷体', 12))]
    
    # 底部新建任务按钮
    new_task_button = None

    widgets_new: list[tkintertools._BaseWidget] = [
        canvas.create_text(
            -150, 20, text='新建任务', fill=theme['MainColor'][0], font=('楷体', 20)),
        canvas.create_line(-240, 40, -60, 40, fill=theme['MainColor'][0]),
        canvas.create_text(
            -275, 70, text='任务名称', fill=theme['MainColor'][0], anchor='w', font=('楷体', 12)),
        canvas.create_text(
            -275, 100, text='开始时间', fill=theme['MainColor'][0], anchor='w', font=('楷体', 12)),
        canvas.create_text(
            -275, 130, text='重要程度', fill=theme['MainColor'][0], anchor='w', font=('楷体', 12)),
        canvas.create_text(
            -150, 160, text='任务描述', fill=theme['MainColor'][0], font=('楷体', 12)),
        tkintertools.CanvasEntry(  # 任务名称输入框
            canvas, -205, 59, 180, 22, 0, '',
            limit=8, font=('楷体', 14),
            color_outline=theme['CanvasEntry']['color_outline'],
            color_fill=theme['CanvasEntry']['color_fill'],
            color_text=theme['CanvasEntry']['color_text']),
        tkintertools.CanvasButton(  # 时间选择按钮
            canvas, -47, 89, 22, 22, 0, '🕒',
            font=('楷体', 12),
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: timechoose()),
        tkintertools.CanvasLabel(
            canvas, -205, 89, 155, 22,
            font=('楷体', 11),
            color_outline=theme['CanvasLabel']['color_outline'],
            color_fill=theme['CanvasLabel']['color_fill'],
            color_text=theme['CanvasLabel']['color_text']),
        tkintertools.CanvasButton(  # 时间显示标签
            canvas, -205, 120, 20, 20,
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: levelchoose(1)),
        tkintertools.CanvasButton(  # 以下5个是重要程度选择框
            canvas, -180, 120, 20, 20,
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: levelchoose(2)),
        tkintertools.CanvasButton(  
            canvas, -155, 120, 20, 20,
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: levelchoose(3)),
        tkintertools.CanvasButton(  
            canvas, -130, 120, 20, 20,
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: levelchoose(4)),
        tkintertools.CanvasButton( 
            canvas, -105, 120, 20, 20,
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: levelchoose(5)),
        tkintertools.CanvasButton(
            canvas, -55, 120, 60, 25, 0, '📊 帮助',
            font=('楷体', 10),
            color_fill=('', '#2196F3', theme['MainColor'][4]),  # 使用蓝色系
            color_text=('white', 'white', 'white'),
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: show_priority_help()),
        tkintertools.CanvasText(   # 任务描述文本框
            canvas, -275, 180, 250, 210, 0,
            font=('楷体', 12),
            color_outline=theme['CanvasText']['color_outline'],
            color_fill=theme['CanvasText']['color_fill'],
            color_text=theme['CanvasText']['color_text']),
        tkintertools.CanvasButton(  # 创建任务按钮
            canvas, -275, 400, 100, 25, 0, '创建',
            font=('楷体', 12),
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: createtask()),
        tkintertools.CanvasButton(  # 取消按钮
            canvas, -125, 400, 100, 25, 0, '取消',
            font=('楷体', 12),
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: switchtonew())]

    @classmethod
    def move(cls, event: Event, coords: list = [0, 0]):
        """ 拖动窗口 """
        if 0 <= event.x/S <= 160 and 0 <= event.y/S <= 30:
            if event.type.__str__() == '4':
                coords[0], coords[1] = event.x, event.y
            else:
                x, y = event.x - coords[0], event.y - coords[1]
                lx, ly = map(int, cls.root.geometry().split('+')[-2:])
                cls.root.geometry('300x500+%d+%d' % (lx+x, ly+y))

    @classmethod
    def topmost(cls, switch: list = [True]):
        """ 窗口置顶 """
        cls.root.attributes('-topmost', switch[0])
        switch[0] = not switch[0]
        if switch[0]:
            cls.widgets_tool[2].configure(
                color_text=('grey', 'white', 'white'))
        else:
            cls.widgets_tool[2].configure(
                color_text=('springgreen', 'springgreen', 'springgreen'))


class MiniWindow:
    """ 迷你小窗 """

    toplevel = tkintertools.Toplevel(
        MainWindow.root, geometry='30x30+1000+100')
    toplevel.attributes('-transparentcolor', 'white')
    toplevel.attributes('-topmost', True)
    toplevel.overrideredirect(True)
    toplevel.withdraw()
    toplevel.bind('<Double-Button-1>', lambda _: windowswitch(False))
    toplevel.bind('<Button-1>', lambda event: MiniWindow.move(event))
    toplevel.bind('<B1-Motion>', lambda event: MiniWindow.move(event))

    canvas = tkintertools.Canvas(toplevel, 30, 30, bg='white')
    canvas.create_text(15, 15, text='👀', font=('楷体', 20))
    canvas.place(x=0, y=0)

    @classmethod
    def move(cls, event: Event, coords: list = [0, 0]):
        """ 拖动小窗 """
        if event.type.__str__() == '4':
            coords[0], coords[1] = event.x/S, event.y/S
        else:
            x, y = event.x/S - coords[0], event.y/S - coords[1]
            lx, ly = map(int, cls.toplevel.geometry().split('+')[-2:])
            cls.toplevel.geometry('30x30+%d+%d' % (lx+x, ly+y))


class ReadWindow:
    """ 任务详情 """

    def __init__(self, data: dict):
        geometry = tuple(int(i)
                         for i in MainWindow.root.geometry().split('+')[-2:])
        self.toplevel = tkintertools.Toplevel(
            MainWindow.root, geometry='300x400+%d+%d' % (geometry[0]+300*S, geometry[1]))
        self.toplevel.overrideredirect(True)
        self.toplevel.bind('<B1-Motion>', self.move)
        self.toplevel.bind('<Button-1>', self.move)
        self.canvas = tkintertools.Canvas(
            self.toplevel, 298, 398,
            bg=theme['ReadWindow']['bg'], highlightbackground=theme['ReadWindow']['highlightbackground'])
        self.canvas.configure(highlightthickness=1)
        self.canvas.place(x=0, y=0)
        self.image = self.canvas.create_image(150, 200)
        self.canvas.create_text(
            150, 25, text='—— 任务详情 ——', font=('楷体', 15), fill=theme['MainColor'][3])
        tkintertools.CanvasLabel(
            self.canvas, 10, 50, 280, 40, 5, '任务名称:%s' % data['name'],
            justify='left', font=('楷体', 13),
            color_outline=theme['CanvasLabel']['color_outline'],
            color_fill=theme['CanvasLabel']['color_fill'],
            color_text=theme['CanvasLabel']['color_text'])
        tkintertools.CanvasLabel(
            self.canvas, 10, 100, 280, 40, 5, '开始时间:%s' % data['date'],
            justify='left', font=('楷体', 13),
            color_outline=theme['CanvasLabel']['color_outline'],
            color_fill=theme['CanvasLabel']['color_fill'],
            color_text=theme['CanvasLabel']['color_text'])
        tkintertools.CanvasLabel(
            self.canvas, 10, 150, 280, 40, 5, '创建时间:%s' % data['create'],
            justify='left', font=('楷体', 13),
            color_outline=theme['CanvasLabel']['color_outline'],
            color_fill=theme['CanvasLabel']['color_fill'],
            color_text=theme['CanvasLabel']['color_text'])
        tkintertools.CanvasLabel(
            self.canvas, 10, 200, 280, 40, 5, '重要程度:%s' % (
                int(data['level'])*'★'),
            justify='left', font=('楷体', 13),
            color_outline=theme['CanvasLabel']['color_outline'],
            color_fill=theme['CanvasLabel']['color_fill'],
            color_text=theme['CanvasLabel']['color_text'])
        tkintertools.CanvasLabel(
            self.canvas, 10, 250, 280, 100, 5, '%s' % data['description'],
            font=('楷体', 12),
            color_outline=theme['CanvasLabel']['color_outline'],
            color_fill=theme['CanvasLabel']['color_fill'],
            color_text=theme['CanvasLabel']['color_text'])
        tkintertools.CanvasButton(
            self.canvas, 100, 360, 100, 30, 5, '确定',
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=self.toplevel.destroy)
        self.setbg()

    def move(self, event: Event, coords: list = [0, 0]):
        """ 窗口拖动 """
        if event.y <= 350:
            if event.type.__str__() == '4':
                coords[0], coords[1] = event.x, event.y
            else:
                x, y = event.x - coords[0], event.y - coords[1]
                lx, ly = map(int, self.toplevel.geometry().split('+')[-2:])
                self.toplevel.geometry('300x400+%d+%d' % (lx+x, ly+y))

    def setbg(self):
        """ 设置背景 """
        if SetWindow.image and SetWindow.image.file[-3:] == 'gif':
            SetWindow.image.play(self.canvas, self.image, config['interval'])
        elif SetWindow.image:
            self.bg = tkintertools.PhotoImage(config['bgpath'])
            self.canvas.itemconfigure(self.image, image=self.bg)


class SetWindow:
    """ 设置界面 """

    image = None
    toplevel = tkintertools.Toplevel(MainWindow.root, geometry='300x500')
    toplevel.overrideredirect(True)
    toplevel.withdraw()
    toplevel.bind('<Button-1>', lambda event: SetWindow.move(event))
    toplevel.bind('<B1-Motion>', lambda event: SetWindow.move(event))
    canvas = tkintertools.Canvas(
        toplevel, 298, 498, bg=theme['SetWindow']['bg'])
    canvas.configure(highlightthickness=1,
                     highlightbackground=theme['SetWindow']['highlightbackground'])
    canvas.place(x=0, y=0)
    bg = canvas.create_image(150, 250)
    canvas.create_rectangle(0, 0, 300, 30, fill=theme['MainColor'][1], width=0)
    canvas.create_text(
        5, 15, text='⚙设置', anchor='w', font=('楷体', 12), fill=theme['MainColor'][0])
    canvas.create_text(
        150, 470, fill=theme['MainColor'][0], justify='center', font=('楷体', 10),
        text='本工具由Group7\n—— 基于@Xiaokang2022 thinkertools工具 ——\n使用Python的tkinter模块打造(版本号:%s)' % __version__)
    
    # 添加主题切换按钮
    theme_button = tkintertools.CanvasButton(
        canvas, 100, 150, 100, 30, 5, '深色主题' if config['theme'] == 'light' else '浅色主题',
        font=('楷体', 12),
        color_fill=theme['CanvasButton']['color_fill'],
        color_text=theme['CanvasButton']['color_text'],
        color_outline=theme['CanvasButton']['color_outline'],
        command=lambda: SetWindow.toggle_theme())
    
    # 添加跳转链接按钮
    tkintertools.CanvasButton(
        canvas, 100, 200, 100, 30, 5, '访问Github',
        font=('楷体', 12),
        color_fill=theme['CanvasButton']['color_fill'],
        color_text=theme['CanvasButton']['color_text'],
        color_outline=theme['CanvasButton']['color_outline'],
        command=lambda: os.system('start https://github.com/tsuimin888/learningbox'))
    
    # 保留关闭按钮
    tkintertools.CanvasButton(
        canvas, 275, 5, 20, 20, 0, '×',
        font=('楷体', 15),
        color_fill=('', 'red', theme['MainColor'][4]),
        color_text=theme['ToolButton']['color_text'],
        color_outline=tkintertools.COLOR_NONE,
        command=lambda: openset())

    @classmethod
    def move(cls, event: Event, coords: list = [0, 0]):
        """ 拖动窗口 """
        if 0 <= event.x/S <= 260 and 0 <= event.y/S <= 30:
            if event.type.__str__() == '4':
                coords[0], coords[1] = event.x, event.y
            else:
                x, y = event.x - coords[0], event.y - coords[1]
                lx, ly = map(int, cls.toplevel.geometry().split('+')[-2:])
                cls.toplevel.geometry('300x500+%d+%d' % (lx+x, ly+y))

    @classmethod
    def loadbg(cls):
        """ 加载并显示背景 """
        try:
            cls.image = tkintertools.PhotoImage(
                config['bgpath']) if config['bgpath'] else ''
            if cls.image and cls.image.file[-3:] == 'gif':
                [None for _ in cls.image.parse()]
                cls.image.play(MainWindow.canvas, MainWindow.bg,
                               config['interval'])
                cls.image.play(SetWindow.canvas, SetWindow.bg,
                               config['interval'])
            else:
                MainWindow.canvas.itemconfigure(MainWindow.bg, image=cls.image)
                SetWindow.canvas.itemconfigure(SetWindow.bg, image=cls.image)
        except:
            messagebox.showerror('图片错误', '所选背景图片无法显示！')
    
    @classmethod
    def toggle_theme(cls):
        """ 切换主题 """
        # 更新配置文件
        if config['theme'] == 'light':
            configure(True, theme='dark')
            cls.theme_button.configure(text='浅色主题')
        else:
            configure(True, theme='light')
            cls.theme_button.configure(text='深色主题')
        
        # 显示提示信息
        messagebox.showinfo("主题切换", "主题已切换，重启应用以完全生效")

    @classmethod
    def update_theme_button(cls):
        """ 更新主题按钮文本 """
        if config['theme'] == 'light':
            cls.theme_button.configure(text='深色主题')
        else:
            cls.theme_button.configure(text='浅色主题')

class TaskCard:
    """ 任务卡片 """

    taskspool = []
    key = 0
    flag = True
    bar = MainWindow.canvas.create_line(
        295, 5, 295, 5, fill=theme['MainColor'][0])

    def __init__(self, canvas: tkintertools.Canvas, data: dict):
        self.taskspool.append(self)
        self.color = ['green','skyblue', 'orange', 'yellow','red']
        self.canvas = canvas
        self.data = data
        self.interface()
        self.setflag(True)

    def interface(self):
        """ 图形接口 """
        self.y = (len(self.taskspool) + self.key)*55 - 50
        self.widgets: list[tkintertools._BaseWidget] = [
            tkintertools.CanvasLabel(
                self.canvas, 10, self.y, 280, 50,
                color_outline=theme['CanvasLabel']['color_outline'],
                color_fill=theme['CanvasLabel']['color_fill'],
                color_text=theme['CanvasLabel']['color_text']),
            tkintertools.CanvasButton(  # 提醒按钮
                self.canvas, 190, self.y+5, 20, 20, 0, '⏰',
                font=('楷体', 10),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=lambda: open_reminder_setting(self)),
            tkintertools.CanvasButton(  # 详情按钮
                self.canvas, 215, self.y+5, 20, 20, 0, '…',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=lambda: ReadWindow(self.data)),
            tkintertools.CanvasButton(  # 完成按钮
                self.canvas, 240, self.y+5, 20, 20, 0, '✔',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=self.destroy),
            tkintertools.CanvasButton(  # 编辑按钮
                self.canvas, 265, self.y+5, 20, 20, 0, '✏️',
                font=('楷体', 12),
                color_fill=theme['CanvasButton']['color_fill'],
                color_text=theme['CanvasButton']['color_text'],
                color_outline=theme['CanvasButton']['color_outline'],
                command=lambda: switchtoedit(self))]
    
        # 保存提醒按钮引用以便后续更新状态
        self.reminder_button = self.widgets[1]
    
        # 检查是否有提醒设置，如果有则改变按钮颜色
        if reminder_manager.has_reminder(self.data['create']):
            self.reminder_button.configure(
                color_fill=('', 'orange', theme['MainColor'][4]))
            self.reminder_button.state()
    
        self.items = [
            self.canvas.create_text(
                15, self.y+17, text=self.data['name'], font=('楷体', 15), anchor='w', fill=theme['MainColor'][0]),
            self.canvas.create_text(
                15, self.y+38, text=self.data['date'], font=('楷体', 12), anchor='w', fill=theme['MainColor'][0]),
            self.canvas.create_text(287, self.y+38, text=int(self.data['level'])*'★', font=('楷体', 12),
                                anchor='e', fill=self.color[int(self.data['level'])-1])]


    def destroy(self, switch: bool = False):
        """ 删除任务 """
        if not switch and not messagebox.askyesno(
            '完成确认', '是否完成任务：%s?' % self.data['name']):
            return  
        # 移除该任务的所有提醒
        reminder_manager.remove_reminder(self.data['create'])
        # 记录已完成任务
        if not switch:  # 只有在真正完成任务时记录
            daily_recorder.add_completed_task(self.data['name'], 'task') 
        tkintertools.move(MainWindow.canvas, self, 300, 0, 300, 'smooth')
        if switch:
            self.sort(self.taskspool.index(self)+1)
            for widget in self.widgets:
                widget.destroy()
            for item in self.items:
                self.canvas.delete(item)
            self.taskspool.remove(self)
            deletetask(self.data['create'])
            updatestate()
            self.setflag(True)
        else:
            MainWindow.root.after(500, self.destroy, True)
  
    def update(self):
        """ 更新信息 """
        MainWindow.canvas.itemconfigure(self.items[0], text=self.data['name'])
        MainWindow.canvas.itemconfigure(self.items[1], text=self.data['date'])
        MainWindow.canvas.itemconfigure(self.items[2], text=int(
            self.data['level'])*'★', fill=self.color[int(self.data['level'])-1])

    def move(self, x: int, y: int):
        """ 移动任务卡片 """
        self.y += y
        for widget in self.widgets:
            widget.move(x, y)
        for item in self.items:
            self.canvas.move(item, x, y)

    @classmethod
    def sort(cls, key: int = None, flag: bool = False):
        """ 排序 """
        if key != None:
            if len(cls.taskspool) > 8:
                if cls.key == 8-len(cls.taskspool):
                    flag = True
            if flag:
                cls.key += 1
            for ind, task in enumerate(cls.taskspool):
                if ind >= key and not flag:
                    tkintertools.move(MainWindow.canvas, task,
                                      0, -55, 300, 'smooth')
                elif ind < key and flag:
                    tkintertools.move(MainWindow.canvas, task,
                                      0, 55, 300, 'smooth')
        else:
            for ind, task in enumerate(cls.taskspool):
                dy = 5 + (ind + cls.key) * 55 - task.y
                tkintertools.move(MainWindow.canvas, task,
                                  0, dy, 300, 'smooth')

    @classmethod
    def scroll(cls, event: Event):
        """ 滚动 """
        key = 1 if event.delta > 0 else -1
        length = len(cls.taskspool)  
        # 如果任务数量不足9个，不需要滚动
        if length < 9 or not cls.flag:
            return  
        # 检查滚动边界
        new_key = cls.key + key
        if new_key > 0 or new_key < 8 - length:
            return  
        cls.key = new_key 
        # 计算滚动条移动距离
        bar_move_distance = -55 * key * 8 / length 
        # 移动滚动条
        tkintertools.move(MainWindow.canvas, cls.bar, 0, bar_move_distance, 300, 'smooth')
        # 移动所有任务卡片
        for task in cls.taskspool:
            tkintertools.move(MainWindow.canvas, task, 0, 55 * key, 300, 'smooth')

    @classmethod
    def setflag(cls, boolean: bool):
        """ 设置标志 """
        cls.flag = boolean
        coords = MainWindow.canvas.coords(TaskCard.bar)
        if cls.flag and (key := len(TaskCard.taskspool)) > 8:
            length = 435*8/key
            coords[1] = 5 + (435-length)*cls.key/(8-key)
            coords[3] = coords[1] + length
        else:
            coords[3] = coords[1]
        MainWindow.canvas.coords(TaskCard.bar, *coords)


class TimeChooser:
    """ 
    日期时间选择界面
    提供可视化的日期和时间选择功能，支持鼠标滚轮选择
    """
    
    # 画布容器，用于显示时间选择界面
    canvas = tkintertools.Canvas(
        MainWindow.root, 250, 160, bg=theme['TimeChooser']['bg'],
        highlightbackground=theme['TimeChooser']['highlightbackground'])
    
    # 配置画布边框
    canvas.configure(highlightthickness=1)
    
    # 绑定鼠标滚轮事件，用于时间选择
    canvas.bind('<MouseWheel>', lambda event: TimeChooser.move(event))
    
    # 创建时间选择区域的背景装饰
    canvas.create_rectangle(160, 60, 250, 75, fill=theme['MainColor'][4], width=0)
    canvas.create_line(160, 5, 160, 155, fill=theme['MainColor'][0])
    canvas.create_text(205, 65, text=':   :', font=('楷体', 12), 
                      fill=theme['MainColor'][0])
    
    # 日期显示文本（年月）
    date = canvas.create_text(
        80, 15, fill=theme['MainColor'][0], font=('楷体', 12),
        text=time.strftime('%Y-%m', time.localtime()))
    
    # 时间选择器变量 - 存储当前选择的小时、分钟、秒
    hour_value = 0        # 当前选择的小时 (0-23)
    minute_value = 0      # 当前选择的分钟 (0-59)  
    second_value = 0      # 当前选择的秒 (0-59)
    
    # 时间显示文本对象数组 - 每个时间单位显示3个数字（上、中、下）
    hour_texts = []       # 小时显示的3个文本对象
    minute_texts = []     # 分钟显示的3个文本对象  
    second_texts = []     # 秒钟显示的3个文本对象
    
    # 时间列表（用于兼容旧代码，新实现中不再使用）
    timelist = [0, 0, 0]
    
    # 创建遮罩矩形，限制时间选择区域的显示范围
    canvas.create_rectangle(162, 130, 248, 165, fill=theme['TimeChooser']['bg'], width=0)
    canvas.create_rectangle(162, -5, 248, 6, fill=theme['TimeChooser']['bg'], width=0)
    
    # 年月导航按钮
    tkintertools.CanvasButton(
        canvas, 27, 5, 20, 20, 0, '‹',  # 上月按钮
        font=('楷体', 20),
        color_fill=('', theme['MainColor'][4], theme['MainColor'][3]),
        color_outline=tkintertools.COLOR_NONE,
        color_text=theme['ToolButton']['color_text'],
        command=lambda: TimeChooser.modify(0, -1))  # 月份-1
    
    tkintertools.CanvasButton(
        canvas, 113, 5, 20, 20, 0, '›',  # 下月按钮
        font=('楷体', 20),
        color_fill=('', theme['MainColor'][4], theme['MainColor'][3]),
        color_outline=tkintertools.COLOR_NONE,
        color_text=theme['ToolButton']['color_text'],
        command=lambda: TimeChooser.modify(0, 1))  # 月份+1
    
    tkintertools.CanvasButton(
        canvas, 5, 5, 20, 20, 0, '«',  # 上一年按钮
        font=('楷体', 20),
        color_fill=('', theme['MainColor'][4], theme['MainColor'][3]),
        color_outline=tkintertools.COLOR_NONE,
        color_text=theme['ToolButton']['color_text'],
        command=lambda: TimeChooser.modify(-1, 0))  # 年份-1
    
    tkintertools.CanvasButton(
        canvas, 135, 5, 20, 20, 0, '»',  # 下一年按钮
        font=('楷体', 20),
        color_fill=('', theme['MainColor'][4], theme['MainColor'][3]),
        color_outline=tkintertools.COLOR_NONE,
        color_text=theme['ToolButton']['color_text'],
        command=lambda: TimeChooser.modify(1, 0))  # 年份+1
    
    # 确定按钮
    tkintertools.CanvasButton(
        canvas, 165, 135, 80, 20, 0, '确定',
        font=('楷体', 12),
        color_fill=theme['CanvasButton']['color_fill'],
        color_text=theme['CanvasButton']['color_text'],
        color_outline=theme['CanvasButton']['color_outline'],
        command=lambda: TimeChooser.settime())  # 点击后设置时间
    
    # 日期按钮列表
    datelist = []

    @classmethod
    def init_time_display(cls):
        """
        初始化时间显示组件
        为小时、分钟、秒钟分别创建3个文本显示项，形成类似数字滚轮的效果
        """
        # 清除旧的文本项（如果存在）
        for item in cls.hour_texts + cls.minute_texts + cls.second_texts:
            cls.canvas.delete(item)
        cls.hour_texts.clear()
        cls.minute_texts.clear()
        cls.second_texts.clear()
        
        # 小时显示区域 - 创建3个垂直排列的文本项
        # 位置计算：x=175, y从45开始，每个间隔15像素
        for i in range(3):
            text_item = cls.canvas.create_text(
                175, 45 + i * 15,  # 垂直排列3个数字
                fill=theme['MainColor'][0], 
                font=('楷体', 11), 
                anchor='n',  # 文本锚点为顶部
                text='00'    # 初始文本
            )
            cls.hour_texts.append(text_item)
        
        # 分钟显示区域 - 创建3个垂直排列的文本项
        for i in range(3):
            text_item = cls.canvas.create_text(
                205, 45 + i * 15,
                fill=theme['MainColor'][0], 
                font=('楷体', 11), 
                anchor='n',
                text='00'
            )
            cls.minute_texts.append(text_item)
        
        # 秒钟显示区域 - 创建3个垂直排列的文本项
        for i in range(3):
            text_item = cls.canvas.create_text(
                235, 45 + i * 15,
                fill=theme['MainColor'][0], 
                font=('楷体', 11), 
                anchor='n',
                text='00'
            )
            cls.second_texts.append(text_item)
        
        # 更新显示内容
        cls.update_time_display()

    @classmethod
    def update_time_display(cls):
        """
        更新时间显示内容
        每个时间单位显示3个相邻的数字，中间的数字高亮表示当前选中值
        使用取模运算确保数字在有效范围内循环
        """
        # 更新小时显示
        for i in range(3):
            # 计算显示的值：当前值-1, 当前值, 当前值+1，使用取模确保在0-23范围内
            value = (cls.hour_value - 1 + i) % 24
            # 更新文本内容，格式化为2位数
            cls.canvas.itemconfig(cls.hour_texts[i], text=f'{value:02d}')
            
            # 设置颜色：中间的数字高亮显示（当前选中值）
            if i == 1:  # 中间的数字是当前选中的
                cls.canvas.itemconfig(cls.hour_texts[i], fill='springgreen')
            else:
                cls.canvas.itemconfig(cls.hour_texts[i], fill=theme['MainColor'][0])
        
        # 更新分钟显示（逻辑同小时）
        for i in range(3):
            value = (cls.minute_value - 1 + i) % 60
            cls.canvas.itemconfig(cls.minute_texts[i], text=f'{value:02d}')
            if i == 1:
                cls.canvas.itemconfig(cls.minute_texts[i], fill='springgreen')
            else:
                cls.canvas.itemconfig(cls.minute_texts[i], fill=theme['MainColor'][0])
        
        # 更新秒钟显示（逻辑同小时）
        for i in range(3):
            value = (cls.second_value - 1 + i) % 60
            cls.canvas.itemconfig(cls.second_texts[i], text=f'{value:02d}')
            if i == 1:
                cls.canvas.itemconfig(cls.second_texts[i], fill='springgreen')
            else:
                cls.canvas.itemconfig(cls.second_texts[i], fill=theme['MainColor'][0])

    @classmethod
    def updatedate(cls):
        """
        加载并更新日期选择界面
        生成当前月份的日历视图，只能选择今天及之后的日期
        """
        # 清除现有的日期按钮
        for button in cls.datelist:
            button.destroy()
        cls.datelist.clear()
        
        # 解析当前显示的年月
        year, month = map(int, cls.canvas.itemcget(cls.date, 'text').split('-'))
        
        # 获取当前月份的日历数据
        monthdata = calendar.monthcalendar(year, month)
        
        # 获取当前系统日期
        current_time = time.localtime()
        current_year = current_time.tm_year
        current_month = current_time.tm_mon
        current_day = current_time.tm_mday
        
        # 计算当前日期的时间戳（只到天，忽略时分秒）
        current_timestamp = time.mktime((current_year, current_month, current_day, 0, 0, 0, 0, 0, 0))      
        
        # 遍历月份数据，生成日期按钮
        for x, line in enumerate(monthdata):      # x: 周索引
            for y, value in enumerate(line):      # y: 星期索引, value: 日期
                if value:  # 只处理有效的日期（非0）
                    # 计算该日期的时间戳
                    day_timestamp = time.mktime((year, month, value, 0, 0, 0, 0, 0, 0))                  
                    
                    # 检查是否是今天
                    is_today = (year == current_year and month == current_month and value == current_day)       
                    
                    # 只允许选择当前及之后的日期（不能选择过去的日期）
                    if day_timestamp >= current_timestamp:
                        # 如果是今天，用特殊颜色标记
                        if is_today:
                            cls.datelist.append(
                                tkintertools.CanvasButton(
                                    cls.canvas, 5+y*22, 27+x*22, 20, 20, 0, str(value),
                                    font=('楷体', 10),
                                    color_outline=tkintertools.COLOR_NONE,
                                    color_text=('white',)*3,  # 白色文本
                                    color_fill=('springgreen', 'springgreen', 'springgreen'),  # 绿色背景表示今天
                                    command=lambda value=value: cls.setdate(value)))
                        else:
                            # 未来日期，正常显示
                            cls.datelist.append(
                                tkintertools.CanvasButton(
                                    cls.canvas, 5+y*22, 27+x*22, 20, 20, 0, str(value),
                                    font=('楷体', 10),
                                    color_outline=tkintertools.COLOR_NONE,
                                    color_text=(theme['MainColor'][0],)*3,
                                    color_fill=('', theme['MainColor'][4], theme['MainColor'][3]),
                                    command=lambda value=value: cls.setdate(value)))
                    else:
                        # 过去的日期显示为灰色且不可点击
                        if is_today:
                            # 今天即使在过去时间段也要特殊标记（理论上不会出现这种情况）
                            cls.datelist.append(
                                tkintertools.CanvasButton(
                                    cls.canvas, 5+y*22, 27+x*22, 20, 20, 0, str(value),
                                    font=('楷体', 10),
                                    color_outline=tkintertools.COLOR_NONE,
                                    color_text=('white',)*3,
                                    color_fill=('springgreen', 'springgreen', 'springgreen'),
                                    command=lambda value=value: cls.setdate(value)))
                        else:
                            # 普通过去日期，灰色显示，无点击事件
                            cls.datelist.append(
                                tkintertools.CanvasButton(
                                    cls.canvas, 5+y*22, 27+x*22, 20, 20, 0, str(value),
                                    font=('楷体', 10),
                                    color_outline=tkintertools.COLOR_NONE,
                                    color_text=('#888888',)*3,  # 灰色文本
                                    color_fill=('', '#CCCCCC', '#CCCCCC'),  # 灰色背景
                                    command=None))  # 无点击事件，不可选择

        # 初始化时间显示组件
        cls.init_time_display()
        # 从当前显示的时间更新内部值
        cls.update_from_display()

    @classmethod
    def modify(cls, y: int = 0, m: int = 0):
        """
        修改年月显示
        支持切换到任何月份（不限制过去月份）
        
        Args:
            y: 年份变化量（-1: 上一年, 1: 下一年, 0: 不变）
            m: 月份变化量（-1: 上一月, 1: 下一月, 0: 不变）
        """
        # 解析当前显示的年月
        year, month = map(int, cls.canvas.itemcget(cls.date, 'text').split('-'))
        
        # 处理月份边界情况（12月+1=1月，1月-1=12月）
        if month + m == 0:    # 1月-1=12月，年份-1
            year -= 1
            month = 13
        if month + m == 13:   # 12月+1=1月，年份+1
            year += 1
            month = 0
        
        # 计算新的年月（允许切换到任何月份，不限制过去月份）
        new_year = year + y
        new_month = month + m
            
        # 更新日期显示
        cls.canvas.itemconfigure(cls.date, text='%d-%02d' % (new_year, new_month))
        
        # 重新加载日期选择界面
        cls.updatedate()

    @classmethod
    def move(cls, event: Event):
        """
        处理鼠标滚轮事件，用于时间选择
        根据鼠标位置判断操作的是小时、分钟还是秒钟
        
        Args:
            event: 鼠标滚轮事件对象
        """
        # 检查是否在有效区域内
        if event.y/S >= 130 or event.y/S <= 5:
            return
        
        # 判断滚轮方向：向上滚动为1，向下滚动为-1
        key = 1 if event.delta > 0 else -1
        
        # 根据鼠标x坐标判断操作的时间单位
        if 160 < event.x/S < 190:
            # 小时选择区域
            # 使用取模运算确保小时在0-23范围内循环
            cls.hour_value = (cls.hour_value - key) % 24
            cls.update_time_display()
            
        elif 190 < event.x/S < 220:
            # 分钟选择区域
            # 使用取模运算确保分钟在0-59范围内循环
            cls.minute_value = (cls.minute_value - key) % 60
            cls.update_time_display()
            
        elif 220 < event.x/S < 250:
            # 秒钟选择区域  
            # 使用取模运算确保秒钟在0-59范围内循环
            cls.second_value = (cls.second_value - key) % 60
            cls.update_time_display()

    @classmethod
    def setdate(cls, day: int):
        """
        设置选择的日期
        
        Args:
            day: 选择的日期（1-31）
        """
        # 解析当前显示的年月
        year, month = map(int, cls.canvas.itemcget(cls.date, 'text').split('-'))
        
        # 获取当前任务创建界面中显示的时间
        date = MainWindow.widgets_new[8].configure('text')
        
        # 从当前时间中提取时间部分，如果不存在则使用默认时间
        time_part = date[11:] if len(date) > 11 else '00:00:00'
        
        # 构建完整的日期时间字符串
        date = f'{year}/{month:02d}/{day:02d} {time_part}'
        
        # 更新任务创建界面的时间显示
        MainWindow.widgets_new[8].configure(text=date)
        
        # 更新时间选择器的显示以匹配新的日期
        cls.update_from_display()

    @classmethod
    def settime(cls):
        """
        确认时间选择
        将当前选择的时间应用到任务创建界面，并关闭时间选择器
        """
        # 获取任务创建界面中当前的日期部分
        date = MainWindow.widgets_new[8].configure('text')
        
        # 构建时间字符串，格式化为2位数
        time_str = f'{cls.hour_value:02d}:{cls.minute_value:02d}:{cls.second_value:02d}'
        
        # 替换日期字符串中的时间部分
        date = date[:11] + time_str
        
        # 更新任务创建界面的时间显示
        MainWindow.widgets_new[8].configure(text=date)
        
        # 关闭时间选择器
        timechoose()

    @classmethod
    def update_from_display(cls):
        """
        从任务创建界面的时间显示更新内部时间值
        用于初始化或日期改变时同步时间显示
        """
        # 获取任务创建界面中显示的时间
        date = MainWindow.widgets_new[8].configure('text')
        
        # 检查时间部分是否存在
        if len(date) > 11:
            try:
                # 提取时间部分并解析
                time_part = date[11:]
                hours, minutes, seconds = map(int, time_part.split(':'))
                
                # 更新内部时间值
                cls.hour_value = hours
                cls.minute_value = minutes  
                cls.second_value = seconds
                
                # 更新时间显示
                cls.update_time_display()
            except (ValueError, IndexError):
                # 如果时间解析失败，使用默认值（0:00:00）
                cls.hour_value = 0
                cls.minute_value = 0
                cls.second_value = 0
                cls.update_time_display()


def windowswitch(mini: bool):
    """ 窗口切换 """
    if mini:
        MainWindow.root.withdraw()
        MiniWindow.toplevel.deiconify()
    else:
        MainWindow.root.deiconify()
        MiniWindow.toplevel.withdraw()


def redmask(widget: tkintertools._BaseWidget, ind=0):
    """ 红色标记 """
    if ind & 1:
        widget.configure(color_outline=theme['CanvasEntry']['color_outline'])
    else:
        widget.configure(color_outline=('red',)*3)
    widget.state()
    if ind < 5:
        MainWindow.root.after(100, redmask, widget, ind+1)


def checkargument():
    """ 参数检查 """
    if not (name := MainWindow.widgets_new[6].get()):
        redmask(MainWindow.widgets_new[6])
        return
    if not (level := levelchoose()):
        for i in range(7):
            redmask(MainWindow.widgets_new[9+i])
        return
    return name, MainWindow.widgets_new[8].configure('text'), level

def check_task_duplicate(name: str, date: str, exclude_create_time: str = None) -> tuple[bool, str]:
    """
    检查任务是否重复（名称和时间都相同）
    返回: (是否重复, 重复任务的创建时间)
    """
    try:
        # 如果任务名称为空，不算重复
        if not name.strip():
            return False, ""
            
        with open('tasks.json', 'r', encoding='utf-8') as file:
            tasks = json.load(file)
        
        for create_time, task in tasks.items():
            # 如果是编辑任务，跳过自身
            if exclude_create_time and create_time == exclude_create_time:
                continue
                
            # 调试信息：打印比较的任务信息
            print(f"比较: 新任务='{name}' '{date}' vs 现有任务='{task['name']}' '{task['date']}'")
            
            # 检查名称和时间是否都相同
            if task['name'] == name and task['date'] == date:
                print(f"发现重复任务: {name} at {date}")
                return True, create_time
                
        print(f"未发现重复任务: {name}")
        return False, ""
    except Exception as e:
        print(f"检查重复任务时出错: {e}")
        return False, ""

def check_time_conflict(new_date: str, exclude_create_time: str = None) -> tuple[bool, str]:
    """
    检查时间冲突 - 判断开始时间相差≤15分钟
    new_date: 新任务的开始时间
    exclude_create_time: 要排除的任务创建时间（用于编辑任务时排除自身）
    返回: (是否冲突, 冲突任务的创建时间)
    """
    try:
        # 将新任务的时间字符串转换为时间戳
        new_time = time.mktime(time.strptime(new_date, '%Y/%m/%d %H:%M:%S'))
        
        with open('tasks.json', 'r', encoding='utf-8') as file:
            tasks = json.load(file)
        
        for create_time, task in tasks.items():
            # 如果是编辑任务，跳过自身
            if exclude_create_time and create_time == exclude_create_time:
                continue
                
            # 检查时间是否冲突（相差≤15分钟）
            task_time = task['time']
            time_diff = abs(new_time - task_time)
            
            # 调试信息
            print(f"时间检查: 新任务={new_date}({new_time}) vs 现有任务={task['date']}({task_time}), 时间差={time_diff}秒")
            
            if time_diff <= 15 * 60:  # 15分钟 = 900秒
                print(f"发现时间冲突: 时间差{time_diff}秒 ≤ 900秒")
                return True, create_time
                
        print(f"未发现时间冲突: {new_date}")
        return False, ""
    except Exception as e:
        print(f"检查时间冲突时出错: {e}")
        return False, ""


def createtask():
    """ 创建任务 """
    if args := checkargument():
        name, time_, level = args
    else:
        return

    print(f"=== 开始创建任务: {name} at {time_} ===")

    # 检查重复任务（名称和时间都相同）
    is_duplicate, duplicate_create_time = check_task_duplicate(name, time_)
    if is_duplicate:
        duplicate_task = None
        with open('tasks.json', 'r', encoding='utf-8') as file:
            tasks = json.load(file)
            if duplicate_create_time in tasks:
                duplicate_task = tasks[duplicate_create_time]
        
        duplicate_info = ""
        if duplicate_task:
            duplicate_info = f"\n\n重复任务详情:\n名称: {duplicate_task['name']}\n时间: {duplicate_task['date']}\n重要程度: {duplicate_task['level']}"
            
        if not messagebox.askyesno("重复任务", 
            f"已存在完全相同的任务：\n任务名称: {name}\n开始时间: {time_}{duplicate_info}\n\n是否确定要创建重复任务?"):
            return

    # 检查时间冲突（相差15分钟内）
    is_conflict, conflict_create_time = check_time_conflict(time_)
    if is_conflict:
        conflict_task = None
        with open('tasks.json', 'r', encoding='utf-8') as file:
            tasks = json.load(file)
            if conflict_create_time in tasks:
                conflict_task = tasks[conflict_create_time]
        
        conflict_info = ""
        if conflict_task:
            # 计算时间差
            new_time = time.mktime(time.strptime(time_, '%Y/%m/%d %H:%M:%S'))
            conflict_time_diff = abs(new_time - conflict_task['time'])
            conflict_minutes = conflict_time_diff // 60
            conflict_info = f"\n\n冲突任务详情:\n名称: {conflict_task['name']}\n时间: {conflict_task['date']}\n与当前任务相差: {conflict_minutes}分钟"
            
        if not messagebox.askyesno("时间冲突", 
                f"已存在开始时间相近（15分钟内）的任务：{time_}{conflict_info}\n\n是否确定要创建此任务?"):
            return

    create = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
    data = {
        'name': name,
        'date': time_,
        'level': level,
        'create': create,
        'description': MainWindow.widgets_new[-3].get(),
        'time': time.mktime(time.strptime(time_, '%Y/%m/%d %H:%M:%S'))
    }
    with open('tasks.json', 'r', encoding='utf-8') as file:
        dic: dict = json.load(file)
    dic[create] = data
    with open('tasks.json', 'w', encoding='utf-8') as file:
        json.dump(dic, file, indent=4)
    TaskCard(MainWindow.canvas, data).move(300, 0)
    sort_tasks()
    print(f"=== 任务创建成功: {name} ===")
    # 创建成功后返回主页
    switchtonew()


def deletetask(create: str):
    """ 删除任务 """
    with open('tasks.json', 'r', encoding='utf-8') as file:
        dic: dict = json.load(file)
    del dic[create]
    with open('tasks.json', 'w', encoding='utf-8') as file:
        json.dump(dic, file, indent=4)


def edittask(task: TaskCard):
    """ 编辑任务 """
    if args := checkargument():
        name, time_, level = args
    else:
        return

    print(f"=== 开始编辑任务: {name} at {time_} ===")

    # 检查重复任务（排除自身）
    is_duplicate, duplicate_create_time = check_task_duplicate(name, time_, task.data['create'])
    if is_duplicate:
        duplicate_task = None
        with open('tasks.json', 'r', encoding='utf-8') as file:
            tasks = json.load(file)
            if duplicate_create_time in tasks:
                duplicate_task = tasks[duplicate_create_time]
        
        duplicate_info = ""
        if duplicate_task:
            duplicate_info = f"\n\n重复任务详情:\n名称: {duplicate_task['name']}\n时间: {duplicate_task['date']}\n重要程度: {duplicate_task['level']}"
            
        if not messagebox.askyesno("重复任务", 
            f"已存在完全相同的任务：\n任务名称: {name}\n开始时间: {time_}{duplicate_info}\n\n是否确定要修改为重复任务?"):
            return

    # 检查时间冲突（排除自身）
    is_conflict, conflict_create_time = check_time_conflict(time_, task.data['create'])
    if is_conflict:
        conflict_task = None
        with open('tasks.json', 'r', encoding='utf-8') as file:
            tasks = json.load(file)
            if conflict_create_time in tasks:
                conflict_task = tasks[conflict_create_time]
        
        conflict_info = ""
        if conflict_task:
            # 计算时间差
            new_time = time.mktime(time.strptime(time_, '%Y/%m/%d %H:%M:%S'))
            conflict_time_diff = abs(new_time - conflict_task['time'])
            conflict_minutes = conflict_time_diff // 60
            conflict_info = f"\n\n冲突任务详情:\n名称: {conflict_task['name']}\n时间: {conflict_task['date']}\n与当前任务相差: {conflict_minutes}分钟"
            
        if not messagebox.askyesno("时间冲突", 
                f"已存在开始时间相近(15分钟内)的任务：{time_}{conflict_info}\n\n是否确定要修改此任务？"):
            return
    # 如果任务时间改变，移除原有的提醒
    old_time = task.data['time']
    new_time = time.mktime(time.strptime(time_, '%Y/%m/%d %H:%M:%S'))  
    if old_time != new_time:
        reminder_manager.remove_reminder(task.data['create'])
        # 重置提醒按钮状态
        if hasattr(task, 'reminder_button'):
            task.reminder_button.configure(
                color_fill=theme['CanvasButton']['color_fill'])
            task.reminder_button.state()
    data = {
        'name': name,
        'date': time_,
        'level': level,
        'description': MainWindow.widgets_new[-3].get(),
        'time': time.mktime(time.strptime(time_, '%Y/%m/%d %H:%M:%S'))
    }
    with open('tasks.json', 'r', encoding='utf-8') as file:
        dic: dict[str, dict] = json.load(file)
    task.data.update(data)
    task.update()
    dic[task.data['create']].update(data)
    with open('tasks.json', 'w', encoding='utf-8') as file:
        json.dump(dic, file, indent=4)
    sort_tasks()
    print(f"=== 任务编辑成功: {name} ===")
    switchtoedit(None)


def loadtask():
    """ 加载任务 """
    with open('tasks.json', 'r+', encoding='utf-8') as file:
        data = file.read()
    if data:
        tasks = json.loads(data)
        for task in tasks:
            TaskCard(MainWindow.canvas, tasks[task])
    sort_tasks()


def sort_tasks():
    """统一的任务排序函数"""
    TaskCard.taskspool.sort(
        key=lambda task: task.data['time'])
    TaskCard.sort()


def timechoose(switch: list = [True]):
    """ 时间选择 """
    if switch[0]:
        TimeChooser.canvas.place(x=25, y=150)
    else:
        TimeChooser.canvas.place_forget()
    switch[0] = not switch[0]


def levelchoose(key: int = 0, cache: list = [0]):
    """ 等级选择 """
    color = ['green', 'skyblue', 'orange', 'yellow', 'red']
    for ind, button in enumerate(MainWindow.widgets_new[9:14]):
        if ind < key:
            button.configure(color_fill=(color[key-1],)*3)
        else:
            button.configure(color_fill=theme['CanvasButton']['color_fill'])
        button.state()
    cache[0], temp = key, cache[0]
    if not key:
        return temp


def updatestate():
    """ 更新状态栏 """
    num = len(TaskCard.taskspool)
    color = 'springgreen' if not num else 'orange' if num <= config['taskcolor'] else 'red'
    MainWindow.rootcanvas.itemconfigure(
        MainWindow.widgets_tool[-2], text=num, fill=color)
    today = (int(time.time()/86400)+1)*86400
    taskleave = 0
    for task in TaskCard.taskspool:
        if task.data['time'] <= today:
            taskleave += 1
    if taskleave:
        color = 'orange' if taskleave <= config['donecolor'] else 'red'
        MainWindow.rootcanvas.itemconfigure(
            MainWindow.widgets_tool[-1], text='剩余%d个' % taskleave, fill=color)
    else:
        MainWindow.rootcanvas.itemconfigure(
            MainWindow.widgets_tool[-1], text='已完成', fill='springgreen')
    MainWindow.widgets_new[6].set('')
    MainWindow.widgets_new[8].configure(
        text=time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()))
    MainWindow.widgets_new[-3].set('')
    levelchoose()


def openset(switch: list = [True]):
    """ 打开设置界面 """
    if switch[0]:
        SetWindow.toplevel.deiconify()
        SetWindow.update_theme_button()  # 更新主题按钮文本
        geo = [int(i) for i in MainWindow.root.geometry().split('+')[-2:]]
        SetWindow.toplevel.geometry('300x500+%d+%d' % (geo[0]+300*S, geo[1]))
    else:
        SetWindow.toplevel.withdraw()
    switch[0] = not switch[0]

def switch_to_homepage():
    """切换到主页面（任务列表）"""
    # 如果当前在新任务页面，则切换回主页面
    if not TaskCard.flag:
        switchtonew()

# 创建底部新建任务按钮的函数
def create_new_task_button():
    """创建底部新建任务按钮"""
    if MainWindow.new_task_button is None:
        MainWindow.new_task_button = tkintertools.CanvasButton(
            MainWindow.canvas, 100, 410, 100, 30, 5, '+ 新建任务',
            font=('楷体', 12),
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=lambda: switchtonew())
def hide_new_task_button():
    """隐藏底部新建任务按钮"""
    if MainWindow.new_task_button:
        # 使用移动动画将按钮移出屏幕，而不是禁用
        tkintertools.move(MainWindow.canvas, MainWindow.new_task_button, 0, 100, 200, 'smooth')
def show_new_task_button():
    """显示底部新建任务按钮"""
    if MainWindow.new_task_button:
        # 使用移动动画将按钮移回原位
        tkintertools.move(MainWindow.canvas, MainWindow.new_task_button, 0, -100, 200, 'smooth')

def switchtonew(ind=0, switch: list = [1]):
    """ 切换新建界面 """
    widget = TaskCard.taskspool + MainWindow.widgets_new
    if ind == len(widget):
        switch[0] = -switch[0]
        if switch[0] == 1:
            # 切换回主页面
            TaskCard.setflag(True)
            updatestate()
            # 显示底部新建任务按钮
            show_new_task_button()
        else:
            # 切换到新建任务页面
            TaskCard.setflag(False)
            # 隐藏底部新建任务按钮
            hide_new_task_button()
        return
    elif not ind:
        if switch[0] == 1:
            TaskCard.setflag(False)
    
    key = ind if switch[0] == 1 else -ind-1
    tkintertools.move(
        MainWindow.canvas, widget[key], 300*switch[0], 0, 200, 'rebound')
    MainWindow.root.after(30, switchtonew, ind+1)

def switchtoedit(task: TaskCard, ind=0, switch: list = [1]):
    """ 切换编辑界面 """
    widget = TaskCard.taskspool + MainWindow.widgets_new
    if ind == len(widget):
        switch[0] = -switch[0]
        if switch[0] == 1:
            # 切换回主页面
            TaskCard.setflag(True)
            MainWindow.canvas.itemconfigure(
                MainWindow.widgets_new[0], text='新建任务')
            MainWindow.widgets_new[-2].configure(text='创建')
            MainWindow.widgets_new[-1].command = lambda: switchtonew()
            MainWindow.widgets_new[-2].command = lambda: createtask()
            updatestate()
            # 显示底部新建任务按钮
            show_new_task_button()
        return
    elif not ind:
        if switch[0] == 1:
            # 切换到编辑页面
            TaskCard.setflag(False)
            MainWindow.canvas.itemconfigure(
                MainWindow.widgets_new[0], text='编辑任务')
            MainWindow.widgets_new[-2].configure(text='完成')
            MainWindow.widgets_new[-1].command = lambda: switchtoedit(None)
            MainWindow.widgets_new[-2].command = lambda: edittask(task)
            MainWindow.widgets_new[6].set(task.data['name'])
            MainWindow.widgets_new[8].configure(text=task.data['date'])
            MainWindow.widgets_new[-3].set(task.data['description'])
            MainWindow.widgets_new[task.data['level']+8].command()
            # 隐藏底部新建任务按钮
            hide_new_task_button()
    
    key = ind if switch[0] == 1 else -ind-1
    tkintertools.move(
        MainWindow.canvas, widget[key], 300*switch[0], 0, 200, 'rebound')
    MainWindow.root.after(30, switchtoedit, task, ind+1)

def switch_to_homepage():
    """切换到主页面（任务列表）"""
    # 如果当前在新任务页面，则切换回主页面
    if not TaskCard.flag:
        switchtonew()

def generate_daily_report():
    """生成每日报告"""
    try:
        # 更新未完成任务列表
        uncompleted_tasks = [task.data['name'] for task in TaskCard.taskspool]
        daily_recorder.update_uncompleted_tasks(uncompleted_tasks)
        
        # 生成报告
        report_text = daily_recorder.generate_report_text()
        
        # 显示报告
        messagebox.showinfo("每日报告", report_text)
        
    except Exception as e:
        messagebox.showerror("错误", f"生成报告时出错：{str(e)}")


def show_priority_help():
    """显示优先级帮助图片"""
    try:
        # 尝试加载图片
        if os.path.exists('priority_help.jpg'):
            # 使用标准tkinter来显示图片，因为tkintertools对图片支持有限
            import tkinter as tk
            from PIL import Image, ImageTk
            
            # 创建新窗口
            img_window = tk.Toplevel(MainWindow.root)
            img_window.title("四象限时间管理法")
            img_window.geometry("800x600")
            img_window.attributes('-topmost', True)
            
            # 加载图片
            image = Image.open('priority_help.jpg')
            # 调整图片大小以适应窗口
            image = image.resize((780, 550), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # 创建标签显示图片
            label = tk.Label(img_window, image=photo)
            label.image = photo  # 保持引用
            label.pack(padx=10, pady=10)
            
            # 添加关闭按钮
            close_btn = tk.Button(img_window, text="关闭", command=img_window.destroy, 
                                 font=('楷体', 12), bg='#4CAF50', fg='white')
            close_btn.pack(pady=10)
            
        else:
            raise FileNotFoundError("图片文件不存在")
            
    except Exception as e:
        # 图片加载失败，使用文字说明
        print(f"图片加载失败: {e}")
        show_priority_text_help()

def show_priority_text_help():
    """显示优先级文字帮助（图片加载失败时的备选方案）"""
    try:
        # 创建新窗口显示优先级帮助文字
        help_window = tkintertools.Toplevel(
            MainWindow.root, geometry='600x400')
        help_window.title("四象限时间管理法")
        help_window.attributes('-topmost', True)
      
        # 创建画布
        help_canvas = tkintertools.Canvas(
            help_window, 598, 398, 
            bg=theme['ReadWindow']['bg'],
            highlightbackground=theme['ReadWindow']['highlightbackground'])
        help_canvas.configure(highlightthickness=1)
        help_canvas.place(x=0, y=0)
        
        # 添加标题
        help_canvas.create_text(
            300, 20, text='四象限时间管理法', 
            font=('楷体', 16, 'bold'), 
            fill=theme['MainColor'][0])
        
        # 显示图片内容（由于tkintertools的限制，我们用文字和图形来模拟图片内容）
        # 第一象限
        help_canvas.create_rectangle(50, 50, 250, 150, outline='red', width=2)
        help_canvas.create_text(150, 70, text='第一象限', font=('楷体', 12, 'bold'), fill='red')
        help_canvas.create_text(150, 90, text='重要且紧急', font=('楷体', 10), fill='red')
        help_canvas.create_text(150, 110, text='马上做', font=('楷体', 10), fill='red')
        help_canvas.create_text(150, 130, text='危机应对区', font=('楷体', 9), fill='red')
        
        # 第二象限
        help_canvas.create_rectangle(250, 50, 450, 150, outline='orange', width=2)
        help_canvas.create_text(350, 70, text='第二象限', font=('楷体', 12, 'bold'), fill='orange')
        help_canvas.create_text(350, 90, text='重要不紧急', font=('楷体', 10), fill='orange')
        help_canvas.create_text(350, 110, text='重点做', font=('楷体', 10), fill='orange')
        help_canvas.create_text(350, 130, text='战略成长区', font=('楷体', 9), fill='orange')
        
        # 第三象限
        help_canvas.create_rectangle(50, 150, 250, 250, outline='yellow', width=2)
        help_canvas.create_text(150, 170, text='第三象限', font=('楷体', 12, 'bold'), fill='yellow')
        help_canvas.create_text(150, 190, text='紧急不重要', font=('楷体', 10), fill='yellow')
        help_canvas.create_text(150, 210, text='授权做', font=('楷体', 10), fill='yellow')
        help_canvas.create_text(150, 230, text='琐碎忙碌区', font=('楷体', 9), fill='yellow')
        
        # 第四象限
        help_canvas.create_rectangle(250, 150, 450, 250, outline='green', width=2)
        help_canvas.create_text(350, 170, text='第四象限', font=('楷体', 12, 'bold'), fill='green')
        help_canvas.create_text(350, 190, text='不重要不紧急', font=('楷体', 10), fill='green')
        help_canvas.create_text(350, 210, text='减少做', font=('楷体', 10), fill='green')
        help_canvas.create_text(350, 230, text='注意力黑洞区', font=('楷体', 9), fill='green')
        
        # 坐标轴标签
        help_canvas.create_text(25, 100, text='重要', font=('楷体', 12), fill=theme['MainColor'][0], angle=90)
        help_canvas.create_text(475, 100, text='不重要', font=('楷体', 12), fill=theme['MainColor'][0], angle=90)
        help_canvas.create_text(250, 280, text='紧急', font=('楷体', 12), fill=theme['MainColor'][0])
        help_canvas.create_text(250, 30, text='不紧急', font=('楷体', 12), fill=theme['MainColor'][0])
        
        # 说明文字
        help_canvas.create_text(
            300, 320, 
            text='★ 重要程度1-5级对应：1-不重要不紧急，2-紧急不重要，3-重要不紧急，4-重要且紧急，5-非常重要且紧急',
            font=('楷体', 10), 
            fill=theme['MainColor'][0],
            width=550)
        
        # 关闭按钮
        tkintertools.CanvasButton(
            help_canvas, 250, 350, 100, 30, 5, '关闭',
            font=('楷体', 12),
            color_fill=theme['CanvasButton']['color_fill'],
            color_text=theme['CanvasButton']['color_text'],
            color_outline=theme['CanvasButton']['color_outline'],
            command=help_window.destroy)
            
    except Exception as e:
        messagebox.showerror("错误", f"显示帮助时出错：{str(e)}")


if __name__ == '__main__':
    """ 初始加载 """
    loadtask()
    updatestate()
    SetWindow.loadbg()
    TimeChooser.updatedate()  
    # 创建底部新建任务按钮
    create_new_task_button()
    # 确保程序启动时显示主页面（任务列表）
    TaskCard.setflag(True)
    
    try:
        MainWindow.root.mainloop()
    finally:
        # 程序退出时停止提醒检查
        reminder_manager.stop_reminder_check()