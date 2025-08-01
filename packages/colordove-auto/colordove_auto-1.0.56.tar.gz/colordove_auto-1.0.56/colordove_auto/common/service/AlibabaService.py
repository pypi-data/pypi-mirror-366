import json
import time
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from env import config
from common.library.Request import Request
from common.Common import Common
from common.library.Chrome import Chrome
from common.request.common.ShopRequest import ShopRequest
from common.service.EmailService import EmailService

request = Request()
common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
emailService = EmailService()

class AlibabaService():
    def __init__(self):
        super().__init__()
        self.host = config['api']

    def login(self, driver, data):
        '''
        @Desc    : 登录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        storage_data = data.get("storage_data")

        # 如果 storage_data 存在，注入缓存
        if storage_data:
            print("🌐 使用缓存尝试自动登录")
            self.inject_storage(driver, storage_data)

        # 跳转登录
        driver.get("https://trade.1688.com/order/buyer_order_list.htm")

        try:
            # 最多等待10秒，直到URL中包含 login
            WebDriverWait(driver, 10).until(
                EC.url_contains("login")
            )
            print("🔒 页面已跳转到注册页面，可能未登录")
            need_login = True
        except:
            # 未跳转，说明可能已经登录
            print("✅ 页面未跳转，可能已登录")
            need_login = False

        # 根据 need_login 决定是否执行登录逻辑
        if need_login:
            # 执行登录流程
            self.account_login(driver, data)
        else:
            # 已登录
            print("✅ 已登录")

        print("✅ 登录成功")

        return common.back(1, '登录成功')
    
    def account_login(self, driver, data):
        '''
        @Desc    : 账号登录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        account_id = data.get("account_id")
        login_name = data.get("login_name")
        password = data.get("password")
        try:
            wait = WebDriverWait(driver, 3)

            # 输入账号
            username_input = wait.until(EC.presence_of_element_located((By.ID, "fm-login-id")))
            username_input.clear()
            username_input.send_keys(login_name)
            print("✅ 已输入账号")
            time.sleep(1)

            # 输入密码
            password_input = wait.until(EC.presence_of_element_located((By.ID, "fm-login-password")))
            password_input.clear()
            password_input.send_keys(password) 
            print("✅ 已输入密码")
            time.sleep(1)

            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fm-button.fm-submit.password-login")))
            login_button.click()
            print("✅ 已点击登录按钮")

            print("等待30秒")
            time.sleep(30)

            self.save_storage(driver, account_id)

        except Exception as e:
            print(f"❌ 操作失败: {e}")

        return common.back(1, '登录成功')
    
    def inject_storage(self, driver, storage_data):
        '''
        @Desc    : 注入缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        try:
            cookies = storage_data.get("cookies")

            # 注入主域 cookies
            print("注入主域 cookies")
            driver.get("https://www.1688.com")
            for cookie in cookies:
                if ".1688.com" == cookie.get("domain", ""):
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"⚠️ 注入 cookie 失败：{cookie}, 错误：{e}")

        except Exception as e:
            print(f"⚠️ 缓存登录失败: {e}")
        
        print("注入缓存成功")
    
    def save_storage(self, driver, account_id):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取 cookies
        print("获取 cookies")
        driver.get("https://www.1688.com")
        time.sleep(3)
        cookies = driver.get_cookies()

        storage_data = {
            "account_id": account_id,
            "cookies": json.dumps(cookies)
        }

        # 保存店铺缓存
        print("保存店铺缓存")
        res = shopRequest.saveStorage(storage_data)
        if res['status'] != 1:
            return common.back(0, res['msg'])
        
        print("保存缓存成功")