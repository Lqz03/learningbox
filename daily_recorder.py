"""
每日任务记录模块
记录已完成和未完成的任务
"""
import json
import os
import time
from datetime import datetime

class DailyRecorder:
    """每日任务记录器"""
    
    def __init__(self, record_file='daily_records.json'):
        self.record_file = record_file
        self.load_records()
    
    def load_records(self):
        """加载记录文件"""
        if os.path.exists(self.record_file):
            try:
                with open(self.record_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except:
                self.records = {}
        else:
            self.records = {}
    
    def save_records(self):
        """保存记录到文件"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)
    
    def get_today_key(self):
        """获取今天的日期键"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def add_completed_task(self, task_name, task_type='task'):
        """
        添加已完成任务
        task_type: 'task'表示任务清单上确认完成的任务
        'pomodoro'表示已完成的番茄时钟专注任务
        """
        today = self.get_today_key()
        
        if today not in self.records:
            self.records[today] = {
                'completed': [],
                'uncompleted': []
            }
        
        # 避免重复记录
        completed_tasks = [task['name'] for task in self.records[today]['completed']]
        if task_name not in completed_tasks:
            self.records[today]['completed'].append({
                'name': task_name,
                'type': task_type,
                'time': datetime.now().strftime('%H:%M:%S')
            })
            self.save_records()
    
    def update_uncompleted_tasks(self, task_names):
        """更新未完成任务列表"""
        today = self.get_today_key()
        
        if today not in self.records:
            self.records[today] = {
                'completed': [],
                'uncompleted': []
            }
        
        # 清空并重新设置未完成任务
        self.records[today]['uncompleted'] = []
        for task_name in task_names:
            self.records[today]['uncompleted'].append({
                'name': task_name,
                'time': datetime.now().strftime('%H:%M:%S')
            })
        
        self.save_records()
    
    def get_today_report(self):
        """获取今日报告"""
        today = self.get_today_key()
        
        if today not in self.records:
            return {
                'completed': [],
                'uncompleted': []
            }
        
        return self.records[today]
    
    def generate_report_text(self):
        """生成报告文本"""
        report = self.get_today_report()
        today = datetime.now().strftime('%Y年%m月%d日')
        
        text = f"📊 每日任务报告 - {today}\n\n"
        
        text += "✅ 已完成的任务：\n"
        if report['completed']:
            for task in report['completed']:
                type_icon = '🍅' if task['type'] == 'pomodoro' else '✓'
                text += f"   {type_icon} {task['name']}\n"
        else:
            text += "   今日暂无已完成的任务\n"
        
        text += "\n⏳ 未完成的任务：\n"
        if report['uncompleted']:
            for task in report['uncompleted']:
                text += f"   • {task['name']}\n"
        else:
            text += "   恭喜！所有任务都已完成！\n"
        
        text += "\n————————————————\n"
        text += "波浪式前进，螺旋式上升。道路是曲折的，前途是光明的。✨"
        
        return text

# 全局记录器实例
daily_recorder = DailyRecorder()