"""
项目初始化脚本
"""
import os
import json

def create_default_files():
    """创建默认的配置文件"""
    
    # 创建默认config.json
    if not os.path.exists('config.json'):
        config = {
            "bgpath": "",
            "donecolor": 3,
            "interval": 20,
            "reverse": False,
            "sort": "name",
            "taskcolor": 8,
            "theme": "dark",
            "transparent": True
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("已创建默认 config.json")
    
    # 创建默认theme.json (如果不存在)
    if not os.path.exists('theme.json'):
        theme = {
            "dark": {
                "MainColor": ["#FFF", "#000", "#222", "#BBB", "#444"],
                "rootcanvas": {"bg": "#000", "highlightbackground": "#FFF"},
                "canvas": {"bg": "#222", "highlightbackground": "#FFF"},
                "SetWindow": {"bg": "#222", "highlightbackground": "#FFF"},
                "ReadWindow": {"bg": "#222", "highlightbackground": "#FFF"},
                "TimeChooser": {"bg": "#000", "highlightbackground": "#FFF"},
                "CanvasLabel": {
                    "color_text": ["#BBB", "#FFF", "#FFF"],
                    "color_fill": ["#000", "#000", "#000"],
                    "color_outline": ["#444", "#BBB", "#FFF"]
                },
                "CanvasButton": {
                    "color_text": ["#BBB", "#FFF", "#FFF"],
                    "color_fill": ["#000", "#444", "#777"],
                    "color_outline": ["#444", "#BBB", "#FFF"]
                },
                "CanvasEntry": {
                    "color_text": ["#BBB", "#FFF", "#FFF"],
                    "color_fill": ["#000", "#000", "#000"],
                    "color_outline": ["#444", "#BBB", "#FFF"]
                },
                "CanvasText": {
                    "color_text": ["#BBB", "#FFF", "#FFF"],
                    "color_fill": ["#000", "#000", "#000"],
                    "color_outline": ["#444", "#BBB", "#FFF"]
                },
                "ToolButton": {
                    "color_text": ["#777", "#FFF", "#FFF"]
                }
            },
            "light": {
                "MainColor": ["#000", "#DDD", "#FFF", "#444", "#BBB"],
                "rootcanvas": {"bg": "#DDD", "highlightbackground": "#000"},
                "canvas": {"bg": "#FFF", "highlightbackground": "#000"},
                "SetWindow": {"bg": "#FFF", "highlightbackground": "#000"},
                "ReadWindow": {"bg": "#FFF", "highlightbackground": "#000"},
                "TimeChooser": {"bg": "#DDD", "highlightbackground": "#000"},
                "CanvasLabel": {
                    "color_text": ["#444", "#000", "#000"],
                    "color_fill": ["#DDD", "#DDD", "#DDD"],
                    "color_outline": ["#BBB", "#444", "#000"]
                },
                "CanvasButton": {
                    "color_text": ["#444", "#000", "#000"],
                    "color_fill": ["#DDD", "#BBB", "#888"],
                    "color_outline": ["#BBB", "#444", "#000"]
                },
                "CanvasEntry": {
                    "color_text": ["#444", "#000", "#000"],
                    "color_fill": ["#DDD", "#DDD", "#DDD"],
                    "color_outline": ["#BBB", "#444", "#000"]
                },
                "CanvasText": {
                    "color_text": ["#444", "#000", "#000"],
                    "color_fill": ["#DDD", "#DDD", "#DDD"],
                    "color_outline": ["#BBB", "#444", "#000"]
                },
                "ToolButton": {
                    "color_text": ["#888", "#000", "#000"]
                }
            }
        }
        with open('theme.json', 'w', encoding='utf-8') as f:
            json.dump(theme, f, indent=4, ensure_ascii=False)
        print("已创建默认 theme.json")
    
    # 创建空的tasks.json
    if not os.path.exists('tasks.json'):
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
        print("已创建默认 tasks.json")
    
    # 创建空的图标文件占位符（如果不存在）
    if not os.path.exists('task.ico'):
        print("提示: task.ico 文件不存在，打包时将不包含图标")
        print("您可以添加一个图标文件以获得更好的用户体验")

    print("项目初始化完成！")

if __name__ == "__main__":
    create_default_files()