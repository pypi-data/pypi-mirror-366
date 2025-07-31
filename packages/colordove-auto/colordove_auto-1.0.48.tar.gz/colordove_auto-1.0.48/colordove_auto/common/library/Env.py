import sys
import platform
import subprocess
import os

class Env:
    def __init__(self):
        super().__init__()

        # 判断系统
        if sys.platform.startswith('win'):
            self.install_windows_chrome()
        elif sys.platform.startswith('linux'):
            self.install_linux_chrome()
        else:
            print("非 Windows 和 Linux 系统，跳过安装谷歌浏览器")

    def install_windows_chrome(self):
        '''
        @Desc    : 安装windows谷歌浏览器
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("检查 Chrome ")

        if self.is_chrome_installed():
            print("Chrome 已安装，跳过安装。")
            return

        # 判断系统版本
        system = platform.system()
        release = platform.release()
        version = platform.version()

        if '2012' in release or '6.3' in version:
            installer = "109.exe"
        else:
            installer = "136.exe"

        installer_path = self.resource_path(f"./drive/chrome/exe/{installer}")

        print(f"开始安装 Chrome ({installer}) ")
        subprocess.run([installer_path, '/silent', '/install'], shell=True)
        print("Chrome 安装完成！")

    def install_linux_chrome(self):
        '''
        @Desc    : 安装 Linux 上的 Google Chrome
        @Author  : 钟水洲
        @Time    : 2025/07/30
        '''
        print("检查 Chrome ")

        if self.is_chrome_installed():
            print("Chrome 已安装，跳过安装。")
            return

        self.install_chrome_rpm()

    def install_chrome_deb(self):
        '''
        @Desc    : 从 Google 官方网站安装 Chrome for Debian/Ubuntu
        '''
        print("开始安装 Chrome (Debian/Ubuntu)")

        # 下载 Chrome 安装包
        download_url = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
        download_path = "/tmp/google-chrome-stable_current_amd64.deb"

        # 使用 curl 下载文件
        subprocess.run(["curl", "-L", download_url, "-o", download_path])

        # 安装 Chrome
        subprocess.run(["sudo", "dpkg", "-i", download_path])

        # 修复缺少的依赖
        subprocess.run(["sudo", "apt-get", "install", "-f"])

        print("Chrome 安装完成！")

    def install_chrome_rpm(self):
        '''
        @Desc    : 从 Google 官方网站安装 Chrome for CentOS/Fedora
        '''
        print("开始安装 Chrome (CentOS/Fedora)")

        # 下载 Chrome 安装包
        download_url = "https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm"
        subprocess.run(["wget", "-O", "google-chrome.rpm", download_url], check=True)

        # 导入 Google 公钥
        subprocess.run(["rpm", "--import", "https://dl.google.com/linux/linux_signing_key.pub"], check=True)

        # 安装 Chrome（使用 dnf 处理依赖）
        subprocess.run(["dnf", "install", "-y", "./google-chrome.rpm"], check=True)

        print("Chrome 安装完成！")

    def is_chrome_installed(self):
        '''
        @Desc    : 检查是否安装了 Google Chrome
        @Author  : 钟水洲
        @Time    : 2025/06/02 11:51:55
        '''
        registry_paths = [
            r"SOFTWARE\Google\Chrome\BLBeacon",                       # 一般在 64 位系统中使用
            r"SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon",           # 32 位 Chrome 安装在 64 位系统
        ]

        # Windows 系统检查
        if sys.platform.startswith('win'):
            import winreg
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        version, _ = winreg.QueryValueEx(key, "version")
                        if version:
                            print(f"检测到已安装 Chrome,版本: {version}")
                            return True
                except FileNotFoundError:
                    continue

        # Linux 系统检查
        elif sys.platform.startswith('linux'):
            # 检查是否有 Chrome 的安装文件
            if subprocess.call("which google-chrome-stable", shell=True) == 0:
                print("检测到已安装 Chrome")
                return True

        return False

    def resource_path(self, relative_path):
        '''
        @Desc    : 获取相对路径的绝对路径
        '''
        return os.path.abspath(relative_path)

