import os
import subprocess
import time
from datetime import datetime
import sys

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_git_installed():
    """检查Git是否已安装"""
    returncode, stdout, stderr = run_command("git --version")
    return returncode == 0

def is_git_repo():
    """检查当前目录是否为Git仓库"""
    returncode, stdout, stderr = run_command("git rev-parse --is-inside-work-tree")
    return returncode == 0 and stdout.strip() == "true"

def get_git_remote():
    """获取远程仓库URL"""
    returncode, stdout, stderr = run_command("git remote get-url origin")
    if returncode == 0:
        return stdout.strip()
    return None

def auto_git_commit(force_commit=False):
    """自动Git提交脚本"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行自动Git提交...")
    
    # 检查Git是否已安装
    if not check_git_installed():
        print("错误: 未检测到Git安装，请先安装Git并配置环境变量")
        print("\n请按以下步骤操作:")
        print("1. 访问 https://git-scm.com/downloads 下载Git for Windows")
        print("2. 运行安装程序，按照默认设置安装")
        print("3. 重启命令行窗口使环境变量生效")
        print("4. 重新运行此脚本")
        return False
    
    # 进入项目目录
    try:
        project_path = r"c:\Users\du\Desktop\github自动任务"
        os.chdir(project_path)
        print(f"已切换到项目目录: {project_path}")
    except Exception as e:
        print(f"错误: 无法切换到项目目录 - {e}")
        return False
    
    # 检查是否为Git仓库
    if not is_git_repo():
        print("错误: 当前目录不是Git仓库")
        print("\n请按以下步骤初始化Git仓库:")
        print("1. 运行命令: git init")
        print("2. 运行命令: git add .")
        print("3. 运行命令: git commit -m \"Initial commit\"")
        print("4. 运行命令: git remote add origin <你的GitHub仓库URL>")
        print("5. 运行命令: git push -u origin main")
        return False
    
    # 获取远程仓库信息
    remote_url = get_git_remote()
    if remote_url:
        print(f"远程仓库URL: {remote_url}")
    else:
        print("警告: 未配置远程仓库")
    
    # 添加所有变更
    print("\n正在添加文件到暂存区...")
    returncode, stdout, stderr = run_command("git add .")
    if returncode != 0:
        print(f"错误: git add失败 - {stderr}")
        return False
    print("文件添加成功")
    
    # 如果是强制提交，或者检查到有文件变更，则提交
    should_commit = force_commit
    if not force_commit:
        # 检查是否有文件变更
        returncode, stdout, stderr = run_command("git status --porcelain")
        if returncode != 0:
            print(f"错误: 无法执行git status - {stderr}")
            return False
        
        if stdout.strip():
            print("检测到文件变更，开始提交流程...")
            print("变更文件:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
            should_commit = True
        else:
            print("没有文件变更")
            should_commit = False
    
    if should_commit or force_commit:
        # 提交变更
        commit_message = f"Auto update rules at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"\n正在提交变更: {commit_message}")
        returncode, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
        if returncode != 0:
            if "nothing to commit" in stderr:
                print("没有需要提交的变更")
            else:
                print(f"错误: git commit失败 - {stderr}")
                return False
        else:
            print("提交成功")
        
        # 推送到远程仓库
        print("\n正在推送到远程仓库...")
        returncode, stdout, stderr = run_command("git push")
        if returncode != 0:
            print(f"错误: git push失败 - {stderr}")
            print("请检查网络连接和Git凭证配置")
            return False
        print("推送成功!")
    else:
        # 即使没有变更也强制提交
        if force_commit:
            commit_message = f"Auto update rules at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (no changes)"
            print(f"\n强制提交: {commit_message}")
            returncode, stdout, stderr = run_command(f'git commit --allow-empty -m "{commit_message}"')
            if returncode == 0:
                print("强制提交成功")
                # 推送到远程仓库
                print("\n正在推送到远程仓库...")
                returncode, stdout, stderr = run_command("git push")
                if returncode != 0:
                    print(f"错误: git push失败 - {stderr}")
                    print("请检查网络连接和Git凭证配置")
                    return False
                print("推送成功!")
            else:
                print(f"强制提交失败: {stderr}")
                return False
        else:
            print("没有文件变更，跳过提交")
    
    return True

if __name__ == "__main__":
    try:
        # 检查是否传入了强制提交参数
        force_commit = len(sys.argv) > 1 and sys.argv[1] == "--force"
        auto_git_commit(force_commit=force_commit)
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
