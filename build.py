"""
应用打包脚本
"""
import os
import sys
import subprocess
import shutil

def check_required_files():
    """检查必需的文件是否存在"""
    required_files = ['main.py', 'config.json', 'theme.json', 'tasks.json']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    # 检查图标文件
    if not os.path.exists('task.ico'):
        print("警告: task.ico 文件不存在，将使用默认图标")
    
    if missing_files:
        print(f"缺少以下必需文件: {missing_files}")
        return False
    return True

def install_requirements():
    """安装打包依赖"""
    print("正在安装打包依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("依赖安装成功！")
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False
    return True

def build_executable():
    """构建可执行文件"""
    print("正在构建可执行文件...")
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=学习工具箱",
    ]
    
    # 只有当图标文件存在时才添加图标参数
    if os.path.exists('task.ico'):
        cmd.extend(["--icon=task.ico"])
    
    # 添加数据文件
    if os.path.exists('config.json'):
        cmd.extend(["--add-data=config.json;."])
    if os.path.exists('theme.json'):
        cmd.extend(["--add-data=theme.json;."])
    if os.path.exists('tasks.json'):
        cmd.extend(["--add-data=tasks.json;."])   
    if os.path.exists('task.ico'):
        cmd.extend(["--add-data=priority_help.jpg;."])
    if os.path.exists('reminder.py'):
        cmd.extend(["--add-data=reminder.py;."])
    
    cmd.append("main.py")
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("打包成功！")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    except FileNotFoundError:
        print("错误: 找不到 pyinstaller 命令，请确保已安装 pyinstaller")
        return False
    
    return True

def create_installer():
    """创建安装程序（可选）"""
    print("正在创建安装程序...")
    
    # 如果有Inno Setup，可以创建安装程序
    iss_content = """
[Setup]
AppName=学习工具箱
AppVersion=1.0
DefaultDirName={pf}\\学习工具箱
DefaultGroupName=学习工具箱
UninstallDisplayIcon={app}\\学习工具箱.exe
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\学习工具箱.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion; Check: not IsUpgrade
Source: "theme.json"; DestDir: "{app}"; Flags: ignoreversion; Check: not IsUpgrade

[Icons]
Name: "{group}\\学习工具箱"; Filename: "{app}\\学习工具箱.exe"
Name: "{group}\\卸载学习工具箱"; Filename: "{uninstallexe}"
Name: "{commondesktop}\\学习工具箱"; Filename: "{app}\\学习工具箱.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Code]
var
  IsUpgrade: Boolean;

function InitializeSetup(): Boolean;
begin
  IsUpgrade := FileExists(ExpandConstant('{app}\\学习工具箱.exe'));
  Result := True;
end;
"""
    
    with open("setup.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    print("已生成Inno Setup安装脚本 setup.iss")

def main():
    """主函数"""
    print("开始打包学习工具箱应用...")
    
    # 检查必需的文件
    if not check_required_files():
        print("请确保所有必需的文件都存在后再进行打包")
        return
    
    # 安装依赖
    if not install_requirements():
        print("依赖安装失败，无法继续打包")
        return
    
    # 构建可执行文件
    if build_executable():
        print("可执行文件已生成到 dist/ 目录")
        
        # 创建安装程序脚本
        create_installer()
        
        print("打包完成！")
        print("运行文件位置: dist/学习工具箱.exe")
    else:
        print("打包失败！")

if __name__ == "__main__":
    main()