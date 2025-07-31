import os
import random
import re
import keyboard
import requests
import time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import wraps
from loguru import logger
from web3 import Web3
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.action_chains import ActionChains
import psutil
from .db_manager import DatabaseManager


class SeleniumBase:
    def __init__(self, ads_id = None,onekey = None,account= None,eclipse_account = None,evm_account = None,solana_account =  None):
        """
        初始化基础类
        """
        self.ads_id = ads_id
        self.open_url = f"http://localhost:50325/api/v1/browser/start?user_id={self.ads_id}"
        self.close_url = f"http://localhost:50325/api/v1/browser/stop?user_id={self.ads_id}"
        self.driver = None
        self.onekey = onekey
        self.account = account
        self.eclipse_account = eclipse_account
        self.evm_account = evm_account
        self.solana_account = solana_account

    @staticmethod
    def retry(max_attempts=3, delay=1):
        """
        重试装饰器
        :param max_attempts: 最大重试次数
        :param delay: 重试间隔时间(秒)
        :return: 装饰器函数
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                last_exception = None

                while attempts < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        last_exception = e
                        if attempts < max_attempts:
                            logger.warning(f"第 {attempts} 次尝试失败: {str(e)[:80]}, {delay} 秒后重试...")
                            time.sleep(delay)
                        else:
                            logger.error(f"已达到最大重试次数 {max_attempts}, 最后一次错误: {str(e)[:80]}")

                raise last_exception

            return wrapper

        return decorator
    def kill_chrome_processes(self):
        """强制终止所有 Chrome 和 Chromedriver 进程，不保留任何特定目录的进程"""
        chrome_process_names = [
            'chrome',  # Linux/macOS 进程名
            'chromedriver',  # Chromedriver 进程
            'Google Chrome',  # Windows 进程名
            'chrome.exe',  # Windows Chrome 进程
            'chromedriver.exe'  # Windows Chromedriver 进程
        ]

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name']
                if process_name in chrome_process_names:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    @retry(max_attempts=3, delay=1)
    def init_driver(self,user_data_dir:str = None,extensions:list = None):
        """
        初始化WebDriver
        :return: WebDriver实例
        """
        page_load_strategy = "normal"
        headless = False
        extension_dirs = []
        for extension in extensions:
            extension_dirs.append(f"{user_data_dir}/Extensions/{extension}")

        if user_data_dir:
            os.environ['WDM_LOCAL'] = '1'
            os.environ['WDM_CACHE_PATH'] = os.path.join(os.getcwd(), 'webdriver_cache')
            CHROME_DRIVER_VERSION = "134.0.6998.118"
            driver_manager = ChromeDriverManager(
                driver_version=CHROME_DRIVER_VERSION,
                chrome_type=ChromeType.GOOGLE
            )
            service = Service(executable_path=driver_manager.install())

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument("--profile-directory=Default")
            if headless:
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--no-sandbox")
            if extension_dirs:
                if isinstance(extension_dirs, str):
                    extension_dirs = [extension_dirs]
                extensions_to_load = ",".join(extension_dirs)
                chrome_options.add_argument(f"--load-extension={extensions_to_load}")
            if page_load_strategy:
                chrome_options.page_load_strategy = page_load_strategy
            
            try:
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                if "session not created: probably user data directory is already in use" in str(e):
                    logger.warning("检测到用户数据目录被占用，正在终止Chrome进程...")
                    self.kill_chrome_processes()
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    raise e

        else:
            resp = requests.get(self.open_url).json()
            if resp["code"] != 0:
                logger.error("请检查ads_id")
                raise Exception("请检查ads_id")
            chrome_driver = resp["data"]["webdriver"]
            service = Service(executable_path=chrome_driver)
            chrome_options = Options()
            if page_load_strategy:
                chrome_options.page_load_strategy = page_load_strategy
            chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver.set_window_size(1920,1080)

        t_delay = 2
        time.sleep(2)
        try:
            self.driver.get('chrome-extension://jnmbobjmhlngoefaiojfljckilhhlhcj/ui-expand-tab.html#/#/')
            try:
                time.sleep(t_delay)
                keyboard.send('caps lock')
                keyboard.send('caps lock')
                keyboard.write("abc1234")
                keyboard.press_and_release('tab')
                keyboard.write("abc1234")
                keyboard.press_and_release('enter')
            except Exception as e:
                logger.error(f"插件弹窗处理失败: {str(e)}")
            try:
                time.sleep(0.5)
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                self.button_click('//span[text() ="设置" or text() ="設置"]',"点击设置")
            except:
                time.sleep(0.5)
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(0.5)
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                with self.ignore_errors():
                    self.button_click('//span[text() = "我明白了"] | //span[text() = "完成"]',"关闭更新提示", wait_time=1, process_time=1)
                time.sleep(0.5)
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                self.button_click('//span[text() ="设置" or text() ="設置"]', "点击设置")

            if self.get_text(
                    '//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div/div/div[4]/div/div[6]/div[1]/div/div[2]/div/span',delay = 0) != "Bridge":
                self.button_click(
                    '//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div/div/div[4]/div/div[6]/div[1]/div/div[2]/div/span',
                    "加载选项")

                self.button_click('//span[text() = "Bridge"]',"选择bridge模式")

                self.wait_get_text(
                    '//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div/div/div[4]/div/div[6]/div[1]/div/div[2]/div/span',
                    "Bridge", info_text="模式切换失败")

        except Exception as e:
            if str(e) == "模式切换失败":
                raise Exception("OneKey : 模式切换失败")
            else:
                pass
        return self.driver

    @contextmanager
    def ignore_errors(self):
        """忽略块内所有异常的上下文管理器"""
        try:
            yield
        except Exception as e:
            if str(e) == "OneKey : gas 过高":
                raise Exception("OneKey : gas 过高")
            elif str(e) == "OneKey : 连接 OneKey 钱包失败":
                raise Exception("OneKey : 连接 OneKey 钱包失败")
            elif str(e) == "OneKey : 链上服务器拥堵":
                raise Exception("OneKey : 链上服务器拥堵")
            pass
    def browser_quit(self):
        with self.ignore_errors():
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.quit()
    def check_wallet_connection(self, xpath, expected_text="0x", wait_time=3):
        """
        检查钱包连接状态
        :param wait_time:
        :param xpath: 钱包按钮的xpath
        :param expected_text: 0x开头的地址
        :return: 是否已连接
        """
        time.sleep(2)
        try:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                wallet_button = WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            except:
                self.driver.switch_to.window(self.driver.window_handles[1])
                wallet_button = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            if expected_text:
                if wallet_button.text.startswith(expected_text):
                    logger.info("钱包已连接")
                    return True
            else:
                logger.info("钱包已连接")
                return True
        except:
            logger.error(f"钱包未连接")
            return False

    def check_onekey_connection(self, xpath, expected_text="回", wait_time=2):
        """
        检查钱包连接状态
        :param wait_time:
        :param xpath: 钱包按钮的xpath
        :param expected_text:
        :return: 是否已连接
        """
        time.sleep(2)
        try:
            wallet_button = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if expected_text in wallet_button.text:
                return False
        except:
            return True


    def get_balance(self, xpath, split_index=0):
        """
        获取余额
        :param xpath: 余额元素的xpath
        :param split_index: 分割后获取的索引
        :return: 余额数值
        """
        try:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                balance = float(
                    re.search(r'\d+\.?\d*',
                              self.get_text(xpath, wait_time=4, error_text="获取初始余额失败").replace(",","")).group()
                )
            except:
                self.driver.switch_to.window(self.driver.window_handles[1])
                balance = float(
                    re.search(r'\d+\.?\d*',
                              self.get_text(xpath, wait_time=4, error_text="获取初始余额失败").replace(",","")).group()
                )
            logger.warning(f"初始钱包余额为 : {balance}")
            return float(balance)
        except Exception as e:
            raise (Exception("获取初始余额失败.."))

    def get_balance_end(self, xpath, split_index=0):
        """
        获取最终获取余额
        :param xpath: 余额元素的xpath
        :param split_index: 分割后获取的索引
        :return: 余额数值
        """
        time.sleep(5)
        try:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                balance_end = float(self.get_text(xpath,wait_time = 2,error_text="获取最终余额失败"))
            except:
                self.driver.switch_to.window(self.driver.window_handles[1])
                balance_end = float(self.get_text(xpath,wait_time = 2,error_text="获取最终余额失败"))
            logger.debug(f"最终钱包余额为 : {balance_end}")
            return float(balance_end)
        except Exception as e:
            raise Exception("获取最终余额失败..")

    def button_click(self, xpath, info_text="点击按钮成功", process_time = 2,use_js=False, wait_time=10, retry=0):
        """
        等待元素变为可点击状态后执行点击操作
        :param process_time:
        :param xpath: 元素的xpath路径
        :param info_text: 成功时的日志信息
        :param use_js: 是否使用JavaScript点击
        :param wait_time: 最大等待时间（秒）
        :param retry: 重试次数
        :raises: Exception 当元素不可点击时
        """
        time.sleep(process_time)
        attempt = 0
        while attempt <= retry:
            try:
                # 先确保元素存在
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

                # 等待元素变为可点击状态
                WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )

                # self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

                if use_js:
                    self.driver.execute_script("arguments[0].click();", element)
                    if info_text:
                        logger.info(f"使用JavaScript点击按钮: {info_text}")
                else:
                    element.click()
                    if info_text:
                        logger.info(info_text)

                return  # 点击成功，退出函数

            except Exception as e:
                # logger.warning(f"[{info_text}]发生意外错误（尝试 {attempt + 1}/{retry + 1})")
                pass

            attempt += 1
            if attempt <= retry:
                time.sleep(2)
        if info_text:logger.error(f"[{info_text}]失败")
        raise Exception(f"[{info_text}]失败")

    def amount_input(self, xpath, value, wait_time=10,error_text = "",delay=2):
        """
        :param delay:
        :param error_text: 描述信息
        :param xpath: 输入框的xpath
        :param value: 要输入的值
        :param wait_time: 等待时间
        """
        time.sleep(delay)
        try:
            input_element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            input_element.click()
            input_element.clear()
            self.driver.execute_script("arguments[0].value = '';", input_element)

            input_element.send_keys(value)
            if value:
                logger.info(f"输入 {value} 成功")
        except Exception as e:
            # logger.error(f"输入失败: {str(e)}")
            if error_text:
                raise Exception(f"{error_text}")
            else:
                raise Exception(f"输入 {value} 失败")

    def get_text(self, xpath, wait_time=10, error_text="获取文本失败", delay=2,attribute_name = None):
        """
        获取元素文本
        :param attribute_name:
        :param delay:
        :param error_text: 错误信息文本
        :param xpath: 输入框的xpath
        :param wait_time: 等待时间
        :return:
        """
        time.sleep(delay)
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text if element.text else (element.get_attribute(attribute_name) if attribute_name else "")
        except:
            raise Exception(error_text)
    def get_value(self, xpath, wait_time=2, error_text="获取价值失败", delay=0):
        time.sleep(delay)
        def _parse(text):
            match = re.search(r"-|\d+\.?\d*", str(text.replace("\n","")).replace(" ", "").replace(",", ""))
            if not match:
                return None
            value = match.group()
            return 0.0 if value == "-" else float(value)
        try:
            current_text = self.get_text(xpath, wait_time=wait_time, error_text="wait_for_text_change_new:获取价格失败", delay=0)
            return _parse(current_text)
        except:
            raise Exception(error_text)
    def get_attribute(self, xpath,attribute_name, wait_time=10, error_text="获取文本失败", delay=2):
        """
        获取元素文本
        :param attribute_name:
        :param delay:
        :param error_text: 错误信息文本
        :param xpath: 输入框的xpath
        :param wait_time: 等待时间
        :return:
        """
        time.sleep(delay)
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.get_attribute(attribute_name)
        except:
            raise Exception(error_text)
    def get_is_selected(self, xpath, wait_time=5, error_text="获取勾选状态失败", delay=2):
        """
        获取复选框勾选状态
        """
        time.sleep(delay)
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.is_selected()
        except:
            raise Exception(error_text)

    def wait_get_text(self, xpath, specify_text, wait_time=20, info_text="等待获取文本失败"):
        """
        等待元素位置变成指定文本
        :param info_text: 描述信息文本
        :param xpath: 输入框的xpath
        :param specify_text: 匹配文本,可谓列表
        :param wait_time: 等待时间
        :return:实际文本
        """
        time.sleep(2)
        try:
            WebDriverWait(self.driver, wait_time).until(
                lambda driver: any(
                    text in driver.find_element(By.XPATH, xpath).text
                    for text in specify_text
                )
            )
            return next(
                text for text in specify_text
                if text in self.driver.find_element(By.XPATH, xpath).text
            )
        except:
            raise Exception(info_text)

    # def wait_for_text_change_new(self, xpath, initial_text, split_index = 0,wait_time=20, info_text="等待文本变化失败"):
    #     """
    #     等待指定元素的文本从初始值发生变化
    #     :param split_index:
    #     :param xpath: 元素的xpath路径
    #     :param initial_text: 初始文本内容
    #     :param wait_time: 最大等待时间(秒)，默认20秒
    #     :param info_text: 超时时的错误提示信息
    #     :return: 变化后的文本内容
    #     :raises: Exception 当超时或元素不存在时抛出异常
    #     """
    #     time.sleep(2)
    #     try:
    #         try:
    #             self.driver.switch_to.window(self.driver.window_handles[0])
    #             WebDriverWait(self.driver, wait_time).until(
    #                 lambda driver: float(re.search(r'\d+\.?\d*',self.get_text(xpath, wait_time=4, error_text="等待变化：获取初始余额失败",delay=0).replace(",","")).group()) != float(initial_text)
    #             )
    #             logger.warning(f"变化之后值为：{re.search(r'\d+\.?\d*',self.get_text(xpath, wait_time=4, error_text="等待变化：获取初始余额失败",delay=0).replace(",","")).group()}")
    #             return re.search(r'\d+\.?\d*',self.get_text(xpath, wait_time=4, error_text="等待变化：获取初始余额失败",delay=0).replace(",","")).group()
    #
    #         except:
    #             self.driver.switch_to.window(self.driver.window_handles[1])
    #             WebDriverWait(self.driver, 5).until(
    #                 lambda driver: float(re.search(r'\d+\.?\d*',self.get_text(xpath, wait_time=4, error_text="等待变化：获取初始余额失败",delay=0).replace(",","")).group()) != float(initial_text)
    #             )
    #             logger.warning(f"变化之后值为：{re.search(r'\d+\.?\d*',self.get_text(xpath, wait_time=4, error_text="等待变化：获取初始余额失败",delay=0).replace(",","")).group()}")
    #             return re.search(r'\d+\.?\d*',self.get_text(xpath, wait_time=4, error_text="等待变化：获取初始余额失败",delay=0).replace(",","")).group()
    #     except Exception as e:
    #         raise Exception(info_text)
    def wait_for_text_change_new(self, xpath, initial_text, split_index=0, wait_time=20, info_text="等待文本变化失败"):
        """
        等待指定元素的文本从初始值发生变化，兼容 '-' 表示 0 的情况
        :param xpath: 元素的xpath路径
        :param initial_text: 初始文本内容（可以是数字或 '-'）
        :param wait_time: 最大等待时间(秒)
        :param info_text: 超时时的错误提示信息
        :return: 变化后的文本内容（字符串）
        :raises: Exception 当超时或元素不存在时抛出异常
        """
        time.sleep(2)

        def _parse(text):
            match = re.search(r"-|\d+\.?\d*", str(text).replace(",", ""))
            if not match:
                return None
            value = match.group()
            return 0.0 if value == "-" else float(value)

        initial_value = _parse(initial_text)
        if initial_value is None:
            raise ValueError(f"初始文本 '{initial_text}' 不是有效的金额格式")

        def _wait_for_change(driver):
            try:
                current_text = self.get_text(xpath, wait_time=2, error_text="wait_for_text_change_new:获取价格失败", delay=0)
                current_value = _parse(current_text)
                if current_value is None:
                    return False
                return current_value != initial_value
            except:
                return False
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
            WebDriverWait(self.driver, wait_time).until(_wait_for_change)
        except:
            try:
                self.driver.switch_to.window(self.driver.window_handles[1])
                WebDriverWait(self.driver, 5).until(_wait_for_change)
            except:
                logger.error("900")
                raise Exception("900")

        final_text = _parse(self.get_text(xpath, wait_time=4, error_text=info_text, delay=0))
        logger.warning(f"变化之后值为：{final_text}")
        return final_text

    def wait_for_text_change(self, xpath, initial_text, wait_time=20, info_text="等待文本变化失败"):
        """
        等待指定元素的文本从初始值发生变化
        :param xpath: 元素的xpath路径
        :param initial_text: 初始文本内容
        :param wait_time: 最大等待时间(秒)，默认20秒
        :param info_text: 超时时的错误提示信息
        :return: 变化后的文本内容
        :raises: Exception 当超时或元素不存在时抛出异常
        """
        time.sleep(2)
        try:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                WebDriverWait(self.driver, wait_time).until(
                    lambda driver: driver.find_element(By.XPATH, xpath).text.rstrip("0").rstrip(".") != initial_text
                )
                logger.warning(f"变化之后值为：{self.driver.find_element(By.XPATH, xpath).text.rstrip("0").rstrip(".")}")
                return self.driver.find_element(By.XPATH, xpath).text.rstrip("0").rstrip(".")

            except:
                self.driver.switch_to.window(self.driver.window_handles[1])
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.find_element(By.XPATH, xpath).text.rstrip("0").rstrip(".") != initial_text
                )
                logger.warning(f"变化之后值为：{self.driver.find_element(By.XPATH, xpath).text.rstrip("0").rstrip(".")}")
                return self.driver.find_element(By.XPATH, xpath).text.rstrip("0").rstrip(".")
        except Exception as e:
            raise Exception(info_text)

    def wait_for_attribute_change(self, xpath, attribute_name, initial_value, wait_time=20, info_text="等待属性变化失败"):
        """
        等待指定元素的某个属性从初始值发生变化
        :param xpath: 元素的xpath路径
        :param attribute_name: 要监视的属性名（如"text"、"value"、"class"等）
        :param initial_value: 属性的初始值
        :param wait_time: 最大等待时间(秒)，默认20秒
        :param info_text: 超时时的错误提示信息
        :return: 变化后的属性值
        :raises: Exception 当超时或元素不存在时抛出异常
        """
        time.sleep(2)
        try:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                WebDriverWait(self.driver, wait_time).until(
                    lambda driver: driver.find_element(By.XPATH, xpath).text != initial_value
                    if attribute_name == "text" else
                    driver.find_element(By.XPATH, xpath).get_attribute(attribute_name) != initial_value
                )
                element = self.driver.find_element(By.XPATH, xpath)
                return element.text if attribute_name == "text" else element.get_attribute(attribute_name)

            except:
                self.driver.switch_to.window(self.driver.window_handles[1])
                WebDriverWait(self.driver, wait_time).until(
                    lambda driver: driver.find_element(By.XPATH, xpath).text != initial_value
                    if attribute_name == "text" else
                    driver.find_element(By.XPATH, xpath).get_attribute(attribute_name) != initial_value
                )
                element = self.driver.find_element(By.XPATH, xpath)
                return element.text if attribute_name == "text" else element.get_attribute(attribute_name)

        except Exception as e:
            raise Exception(info_text)

    def browser_close(self):
        if self.driver:
            self.driver.quit()
            requests.get(self.close_url)
            logger.info("浏览器已关闭")

    def handle_update_popup(self, wait_time=3):
        """
        处理"我明白了"更新弹窗
        :param wait_time: 等待时间
        :return: 是否找到并处理了弹窗
        """
        try:
            specific_button = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="root"]/div/div/span/span/span/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[2]/div/div/button | //span[text()="我明白了"]'))
            )
            self.driver.execute_script("arguments[0].click();", specific_button)
            logger.info("检测更新页面并已点击")
            return True
        except:
            logger.info("未找到更新页面，继续正常流程")
            return False

    def handle_xf_popup(self, wait_time=3):
        """
        处理"我明白了"更新弹窗
        :param wait_time: 等待时间
        :return: 是否找到并处理了弹窗
        """
        try:
            specific_button = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="root"]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[3]/div/button[1]/span | //span[text() = "關閉" or text() = "关闭"]'))
            )
            self.driver.execute_script("arguments[0].click();", specific_button)
            logger.info("检测悬浮球页面并已点击")
            return True
        except:
            logger.info("未找到悬浮球页面，继续正常流程")
            return False

    def handle_auth_popup(self, is_approve=False, wait_time=10,is_walletconnection = True,auth_value = 0):
        """
        处理授权弹窗
        :param auth_value:
        :param is_walletconnection:
        :param is_approve:
        :param wait_time: 等待时间
        """
        if is_approve:
            info = self.get_text('//*[contains(text(),"授权")] | //*[contains(text(),"授權")] | //*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[2]/h1',wait_time = 5)
            if  "授權" not in info  and "授权" not in info and "Order" not in info:
                logger.debug("应为授权，实则发送")
                return True
            try:
                if auth_value:
                    open_approve_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div[2]/div[4]/div/div[2]/div'
                                                    )))
                    logger.info("修改额度按钮已点击")
                    time.sleep(2)
                    self.driver.execute_script("arguments[0].click();", open_approve_button)
                    # set_approve_button = WebDriverWait(self.driver, wait_time).until(
                    #     EC.element_to_be_clickable((By.XPATH,
                    #                                 '//*[@id="root"]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[2]/form/div/fieldset[2]/div[1]/span'
                    #                                 )))
                    # self.driver.execute_script("arguments[0].click();", set_approve_button)
                    logger.debug(f"自定义授权额度为{auth_value}")
                    self.amount_input('/html/body/div[1]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[2]/form/div/fieldset[1]/div[1]/div[2]/span/input',auth_value)
                else:
                    raise Exception()
                time.sleep(2)
                confirm_button = WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                '//*[@id="root"]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[3]/div/button[2]'))
                )
                self.driver.execute_script("arguments[0].click();", confirm_button)
                time.sleep(5)
                logger.success("自定义授权成功")
            except:
                logger.error(f"自定义授权失败，默认额度授权")
                pass
        try:
            if '风' in self.get_text( '//*[contains(text(),"风")]',error_text='不存在交易风险', wait_time=2,delay=0):
                self.button_click('/html/body/div[1]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div',
                    "点击自行承担风险", process_time=0)
        except:
            pass
        if is_walletconnection:
            try:
                gas = self.get_text('/html/body/div[1]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[2]/span[1]',delay = 0,error_text = "gas 获取失败",wait_time = 3).split()[0]
                value = self.get_text('//span/span[contains(text(),"$")]',delay=0,wait_time=2).strip().split("$")[-1]
                logger.debug(f"OneKey : gas费用: {gas}----{value}")
                if float(value) > 0.6:
                    raise Exception("OneKey : gas 过高")
            except Exception as e:
                if "OneKey : gas 过高" in str(e):
                    raise Exception("OneKey : gas 过高")
                pass
        try:
            confirm_button = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH,'//button[@aria-disabled = "false"]/span[text()="授權" or text()="授权" or text()="确认" or text()="確認" or text()="储存" or text()="儲存"]')) )
            confirm_button.click()
            # self.driver.execute_script("arguments[0].click();", confirm_button)
            logger.info("OneKey : 点击[确认、授权、储存]按钮")
            # self.button_click('//button[@aria-disabled = "false"]/span[text()="授權" or text()="授权" or text()="确认" or text()="確認" or text()="储存" or text()="儲存"]',info_text = 'OneKey : 点击[确认、授权、储存]按钮',process_time = 0)
        except:
            if self.get_attribute('//button[@data-testid = "page-footer-confirm"]',"aria-disabled",delay = 0,wait_time = 2,error_text = "获取确认按钮状态失败")  == 'true':
                raise Exception("OneKey : 链上服务器拥堵")
            logger.error(f"OneKey : 无法点击[确认、授权、储存]按钮")
            raise Exception("OneKey : 无法点击[确认、授权、储存]按钮")

    def handle_all_popups(self, index=1, is_approve=False, check_time=30, update_wait_time=2, auth_wait_time=10,is_walletconnection = True,is_address_valid = False,onekey = None,account = None,auth_value=0):
        """
        处理所有常见弹窗（更新提示和授权）
        :param auth_value:
        :param account: 账户编号
        :param onekey: 钱包名称
        :param is_address_valid:
        :param is_walletconnection:
        :param check_time: 窗口检测时间
        :param is_approve: 是否需要无限授权
        :param index: 要切换到的窗口索引
        :param update_wait_time: 更新弹窗等待时间
        :param auth_wait_time: 授权弹窗等待时间
        :return: 窗口句柄列表
        """
        time.sleep(1)

        # 检查窗口数量是否满足要求
        if not self.__check_window_count(min_windows=3, wait_time=check_time):
            logger.error("窗口数量不足，无法处理弹窗")
            raise Exception("OneKey : 未能正常弹出 OneKey 窗口")

        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[index])
        logger.info(f"当前窗口数量: {len(handles)} - {self.driver.title}")
        if "OneKey" not in self.driver.title:
            raise Exception()
        try:
            # if onekey:
            #     self.handle_account(onekey, account)
            # time.sleep(3)
            if self.handle_auth_popup(is_approve, auth_wait_time,is_walletconnection,auth_value):
                return
        except Exception as e:
            if "OneKey : gas 过高" in str(e):
                raise Exception("OneKey : gas 过高")
            # 处理更新弹窗
            self.handle_update_popup(update_wait_time)
            # 处理悬浮球弹窗
            self.handle_xf_popup(update_wait_time)
            # 检测是否锁定onekey
            # if not self.check_onekey_connection(
            #         '//span[text()="歡迎回来" or text() = "欢迎回来"] | /html/body/div[1]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div[1]/div[2]/div[2]/span[1]',
            #         "回", wait_time=1):
            #     logger.error("OneKey : OneKey 被锁定")
            #     raise Exception("OneKey : OneKey 被锁定")
            # 短暂等待
            # time.sleep(2)

            # 检验钱包和账户
            # if onekey:
            #     self.handle_account(onekey,account)

            # 处理授权弹窗
            if self.handle_auth_popup(is_approve, auth_wait_time,is_walletconnection,auth_value):
                return

        # 检测钱包连接状态
        if is_walletconnection:
            if  self.check_onekey_connection('//span[text() = "在設備上確認" or text() = "在设备上确认"] | /html/body/div[1]/div/div/span/span/span/div/div[4]/div/div/span/span/div/div/div/div/div/div[2]/span',expected_text='在',wait_time=20):
                logger.error("OneKey : 连接 OneKey 钱包失败")
                raise Exception("OneKey : 连接 OneKey 钱包失败")


        # 等待交易确认
        self.__check_window_count(mode=0, min_windows=3, wait_time=30)


        # 切回主窗口
        self.driver.switch_to.window(handles[0])

        return handles

    def handle_onekey(self,index = 2,is_approve=False, check_time=30, update_wait_time=3, auth_wait_time=10,is_walletconnection = True,is_address_valid = False,onekey = None,account = None,auth_value = 0):
        """
        处理所有常见弹窗（更新提示和授权）-----------正常交互及授权
        :param auth_value:
        :param account: 账户编号
        :param onekey: 钱包名称
        :param is_address_valid: 是否检测有无地址
        :param index:
        :param is_walletconnection:
        :param check_time: 窗口检测时间
        :param is_approve: 是否需要无限授权
        :param update_wait_time: 更新弹窗等待时间
        :param auth_wait_time: 授权弹窗等待时间
        :is_walletconnection: 连接钱包使用False
        :return: 窗口句柄列表
        """
        try:
            self.handle_all_popups(index = index, is_approve = is_approve,check_time = check_time,update_wait_time=update_wait_time, auth_wait_time=auth_wait_time,is_walletconnection = is_walletconnection,is_address_valid = is_address_valid,onekey = onekey,account = account,auth_value=auth_value)
        except Exception as e:
            if str(e) == "OneKey : 未配置 OneKey 硬件钱包":
                raise Exception("OneKey : 未配置 OneKey 硬件钱包")
            elif str(e) == "OneKey : OneKey 被锁定":
                raise Exception("OneKey : OneKey 被锁定")
            elif str(e) == "OneKey : 未能正常弹出 OneKey 窗口":
                raise Exception("OneKey : 未能正常弹出 OneKey 窗口")
            elif str(e) == "OneKey : 连接 OneKey 钱包失败":
                raise Exception("OneKey : 连接 OneKey 钱包失败")
            elif str(e) == "OneKey : OneKey钱包无地址":
                raise Exception("OneKey : OneKey钱包无地址")
            elif str(e) == "OneKey : 确认前钱包-账户与实际不匹配":
                raise Exception("OneKey : 确认前钱包-账户与实际不匹配")
            elif  str(e) == "OneKey : 链上服务器拥堵":
                raise Exception("OneKey : 链上服务器拥堵")
            elif str(e) == "OneKey : gas 过高":
                raise Exception("OneKey : gas 过高")
            else:
                logger.error("发生错误,切换窗口")
                self.handle_all_popups(index =2 if index==1 else 1, is_approve = is_approve,check_time = check_time,update_wait_time=update_wait_time, auth_wait_time=auth_wait_time,is_walletconnection = is_walletconnection,is_address_valid = is_address_valid,onekey = onekey,account = account,auth_value=auth_value)
    def capture_connect_wallet(self,index = 2,onekey = None,account = None,check_time = 30):
        '''
        连接钱包中使用的方法及捕捉错误
        :param index:
        :param account: 账户编号
        :param onekey: 钱包名称
        :return:
        '''
        try:
            self.handle_onekey(index=index,check_time = check_time,is_walletconnection=False,is_address_valid=True,onekey = onekey,account = account)
        except Exception as e:
            if str(e) == "OneKey : 未配置 OneKey 硬件钱包":
                raise Exception("OneKey : 未配置 OneKey 硬件钱包")
            elif str(e) == "OneKey : OneKey 被锁定":
                raise Exception("OneKey : OneKey 被锁定")
            elif str(e) == "OneKey : 未能正常弹出 OneKey 窗口":
                raise Exception("OneKey : 未能正常弹出 OneKey 窗口")
            elif str(e) == "OneKey : 连接 OneKey 钱包失败":
                raise Exception("OneKey : 连接 OneKey 钱包失败")
            elif str(e) == "OneKey : OneKey钱包无地址":
                raise Exception("OneKey : OneKey钱包无地址")
            elif str(e) == "OneKey : 确认前钱包-账户与实际不匹配":
                raise Exception("OneKey : 确认前钱包-账户与实际不匹配")
            elif  str(e) == "OneKey : 链上服务器拥堵":
                raise Exception("OneKey : 链上服务器拥堵")
            pass
    def scroll_to_center(self, xpath):
        """
        将页面滚动到指定元素的正中央
        :param xpath: 元素的xpath定位
        :return: 目标元素对象
        """
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))

            # 专用居中滚动脚本
            script = """
                var element = arguments[0];
                var viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
                var elementRect = element.getBoundingClientRect();
                var elementAbsoluteTop = window.pageYOffset + elementRect.top;
                var centerPosition = elementAbsoluteTop - (viewportHeight / 2) + (elementRect.height / 2);
                window.scrollTo({
                    top: centerPosition,
                    behavior: 'smooth'  // 添加平滑滚动效果
                });
            """
            self.driver.execute_script(script, element)
            time.sleep(0.5)  # 适当缩短等待时间
            logger.info(f"已将元素滚动到视窗中央")
            return element

        except Exception as e:
            logger.error(f"元素居中滚动失败 - 错误: {str(e)}")
            raise

    def __check_window_count(self, mode=1, min_windows=2, wait_time=30, check_interval=1):
        """
        检查窗口数量是否满足最小要求
        :param mode: 1:大于等于触发  0： 小于触发
        :param min_windows: 最小窗口数量要求（默认为2）
        :param wait_time: 最大等待时间（秒）
        :param check_interval: 检查间隔（秒）
        :return: 如果窗口数量满足要求返回True，否则返回False
        """
        start_time = time.time()
        if mode:
            while time.time() - start_time < wait_time:
                handles = self.driver.window_handles
                current_count = len(handles)

                if current_count >= min_windows:
                    logger.info(f"检测打开窗口数量满足要求: 当前{current_count}个，要求大于等于{min_windows}个")
                    return True

                time.sleep(check_interval)
        else:
            while time.time() - start_time < wait_time:
                handles = self.driver.window_handles
                current_count = len(handles)

                if current_count < min_windows:
                    logger.info(f"检测关闭窗口数量满足要求: 当前{current_count}个，要求小于{min_windows}个")
                    return True

        logger.warning(f"等待窗口超时")
        return False

    def handle_account(self, onekey, account):
        if "Base" not in self.get_text('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div[1]/span',error_text = "获取测试网失败"):
            logger.warning("切换网络")
            self.button_click('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div[1]/span','',process_time=0)
            self.amount_input('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[1]/div/span/input',"Base",wait_time=0)
            self.button_click('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div[2]/div',"选择Base测试网",process_time=0)


        # info = '-'.join([self.get_text('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div[3]/div[2]/div/div[1]/span',
        #                               wait_time = 5,error_text = "获取 onekey 名称失败",delay = 0),
        #                 self.get_text('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div[3]/div[2]/div/div[2]/span',
        #                               wait_time = 5,error_text = "获取 账户编号 名称失败",delay = 0)])
        # if not (self.onekey in info and "#"+self.account in info):
        #     logger.warning(f"{self.onekey}-#{self.account} 与 {info} 不匹配，切换账号")
        self.button_click('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div[3]',"呼出钱包列表")
        self.button_click(f'//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div/span[text() = "{self.onekey}"]',f"选择{self.onekey}钱包",process_time=0)
        self.button_click(f'//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div/div/div/div/span[text() = "Account #{self.account}"]',f"选择Account #{self.account}账户",process_time=1)
        time.sleep(1)
    def move_to_element(self, xpath, timeout=10):
        """
        将鼠标移动到指定元素
        :param xpath:
        :param timeout: 等待超时时间
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH,  xpath))
            )
            ActionChains(self.driver).move_to_element(element).perform()
        except Exception as e:
            raise Exception("移动鼠标位置失败")




    def handle_auth_popup_backpack(self, is_approve=False,auth_value = 0):
        """
        处理授权弹窗
        :param auth_value:
        :param is_approve:
        """
        if is_approve:
            info = self.get_text('//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[2]/h1',wait_time = 5)
            if  "授權" not in info  and "授权" not in info and "Order" not in info:
                logger.debug("应为授权，实则发送")
                return True
            try:
                try:
                    if '风' in self.get_text('/html/body/div[1]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/label',error_text='不存在交易风险',wait_time=2):
                        self.button_click('/html/body/div[1]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div',"点击自行承担风险",process_time = 0)
                except:
                    pass
                if auth_value:
                    open_approve_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//*[@id="root"]/div/div/div/span/span/span/div/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div[2]/div[4]/div/div[2]/div'
                                                    )))
                    logger.info("修改额度按钮已点击")
                    time.sleep(2)
                    self.driver.execute_script("arguments[0].click();", open_approve_button)
                    # set_approve_button = WebDriverWait(self.driver, wait_time).until(
                    #     EC.element_to_be_clickable((By.XPATH,
                    #                                 '//*[@id="root"]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[2]/form/div/fieldset[2]/div[1]/span'
                    #                                 )))
                    # self.driver.execute_script("arguments[0].click();", set_approve_button)
                    logger.debug(f"自定义授权额度为{auth_value}")
                    self.amount_input('/html/body/div[1]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[2]/form/div/fieldset[1]/div[1]/div[2]/span/input',auth_value)
                else:
                    raise Exception()
                time.sleep(2)
                confirm_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                '//*[@id="root"]/div/div/div/span/span/span/div/div[6]/div/div[2]/div[3]/div/button[2]'))
                )
                self.driver.execute_script("arguments[0].click();", confirm_button)
                time.sleep(5)
                logger.success("自定义授权成功")
            except:
                logger.error(f"自定义授权失败，默认额度授权")
                pass
        with self.ignore_errors():
            self.button_click('//*[contains(text(),"anyway")]',"忽略过程",wait_time=2,process_time=0)
        try:
            self.button_click('//span[text() = "确认"]',"BackPack : 点击[确认、授权、储存]按钮")
        except:
            logger.error(f"OneKey : 无法点击[确认、授权、储存]按钮")
            raise Exception("OneKey : 无法点击[确认、授权、储存]按钮")


    def handle_account_backpack(self,account):
        logger.debug(f"选择账户{account}")
        try:
            self.button_click('//span[contains(text(),"Wallet")]',"",wait_time = 3)
            self.button_click(f'//span[contains(text(),"{account[0:5]}")]',"",process_time=0)
        except:
            pass

    def handle_all_popups_backpack(self, index=1, is_approve=False,auth_value=0):
        """
        处理所有常见弹窗（更新提示和授权）
        :param auth_value:
        :param is_approve: 是否需要无限授权
        :param index: 要切换到的窗口索引
        :return: 窗口句柄列表
        """
        time.sleep(2)


        # 检查窗口数量是否满足要求
        if not self.__check_window_count(min_windows=3, wait_time=13):
            logger.error("窗口数量不足，无法处理弹窗")
            raise Exception("BackPack : 未能正常弹出 BackPack 窗口")

        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[index])
        logger.info(f"当前窗口数量: {len(handles)} - {self.driver.title}")
        if "Backpack" not in self.driver.title:
            raise Exception()

        # 解锁backpack
        try:
            self.amount_input('//input[@placeholder = "Password"]', "1111aaaa", error_text="无需解锁", wait_time=3)
            self.button_click('//span[text() = "解锁"]', "点击解锁", wait_time=3)
        except Exception as e:
            logger.debug(e)
            pass

        if self.eclipse_account:
            self.handle_account_backpack(self.eclipse_account)
        # time.sleep(3)
        if self.handle_auth_popup_backpack(is_approve, auth_value):
            return

        with self.ignore_errors():
            self.button_click('//span[text() = "Done"]',info_text= "点击 Done",wait_time=1)

        # 等待交易确认
        self.__check_window_count(mode=0, min_windows=3, wait_time=30)

        # 切回主窗口
        self.driver.switch_to.window(handles[0])

        return handles

    def handle_backpack(self,index = 2,is_approve=False,auth_value = 0):
        """
        处理所有常见弹窗（更新提示和授权）-----------正常交互及授权
        :param is_approve:
        :param auth_value:
        :param index:
        """
        try:
            self.handle_all_popups_backpack(index = index, is_approve = is_approve,auth_value=auth_value)
        except Exception as e:
            if str(e) == 'BackPack : 未能正常弹出 BackPack 窗口':
                raise Exception("BackPack : 未能正常弹出 BackPack 窗口")
            logger.error("发生错误,切换窗口")
            self.handle_all_popups_backpack(index =2 if index==1 else 1, is_approve = is_approve,auth_value=auth_value)

    def refresh_the_page(self,delay = 0,sleep = 2):
        time.sleep(delay)
        logger.info("刷新页面")
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.refresh()
        time.sleep(sleep)

    def comparison_of_balance(self,init_balance,final_balance,token):
        if token == "ETH":
            if abs(float(init_balance) - float(final_balance)) > 0.0003:
                return True
            else:
                logger.warning(f"ETH 余额变化小于0.0003,疑似只扣除gas费,交易可能失败.")
        else:
            if float(init_balance) != float(final_balance):
                return True
        return False

    def press_escape(self, delay=0.5):
        """
        等待后发送ESC键
        :param delay: 等待时间(秒)，默认0.5秒
        """
        time.sleep(delay)
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

def get_chain_balance(account, address,time):
    global rpc
    chain_map = {
        "BASE": ["https://base.llamarpc.com", "https://base-pokt.nodies.app", "https://base-rpc.publicnode.com"],
        "ArbitrumOne": ["https://arbitrum.drpc.org", "https://arb-pokt.nodies.app", "https://arbitrum.therpc.io"],
        "Optimism": ["https://optimism-rpc.publicnode.com", "https://op-pokt.nodies.app",
                     "https://optimism.drpc.org"]}
    balances = {"BASE": 0, "ArbitrumOne": 0, "Optimism": 0}
    chains = list(chain_map.keys())
    for chain in chains:
        for i in range(3):
            try:
                rpc = chain_map[chain][i]
                w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 10}))
                balances[chain] = w3.from_wei(w3.eth.get_balance(address), "ether")
                logger.debug(f"{chain}余额: {balances[chain]} ETH")
                break
            except Exception as e:
                logger.warning(f"{chain} RPC:{rpc} 连接失败: {str(e)}")
        else:
            logger.error(f"{chain} 所有RPC均失败")
            balances[chain] = 0

    with DatabaseManager() as db:
        db.executemany_with_retry(
            """INSERT INTO balance 
              (chain, account_name, account_address, token_name, token_address, balance, is_deleted) 
              VALUES (%s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE 
              balance=VALUES(balance), update_time=NOW()""",
            [(f"{chain}_{time}", account, address, "ETH", "", balances[chain], False)
             for chain in balances]
        )
        logger.success(f"{account=} 余额快照成功")
@contextmanager
def ignore_errors():
    """忽略块内所有异常的上下文管理器"""
    try:
        yield
    except Exception as e:
        if str(e) == "OneKey : 连接 OneKey 钱包失败":
            raise Exception("OneKey : 连接 OneKey 钱包失败")
        elif str(e) == "OneKey : 链上服务器拥堵":
            raise Exception("OneKey : 链上服务器拥堵")
        elif str(e) == "OneKey : gas 过高":
            raise Exception("OneKey : gas 过高")

