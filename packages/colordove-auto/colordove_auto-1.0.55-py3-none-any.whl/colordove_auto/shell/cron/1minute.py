import subprocess
import psutil

def is_process_running(command_keyword):
    """
    判断某个包含关键字的命令是否正在运行
    """
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline'])
            if command_keyword in cmdline and 'grep' not in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def start_task_if_not_running():
    run_task = "colordove_auto start"
    if not is_process_running("colordove_auto start"):
        print(f"启动任务: {run_task}")
        subprocess.Popen(run_task, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("任务已在运行中，无需重复启动")

if __name__ == "__main__":
    start_task_if_not_running()
