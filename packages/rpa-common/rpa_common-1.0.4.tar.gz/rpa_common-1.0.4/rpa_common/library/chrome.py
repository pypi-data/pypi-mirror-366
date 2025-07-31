import os
import json
import shutil
import platform
import time
import stat
import hashlib
import re
import subprocess
import sys
import threading
import tempfile
import textwrap
import os
import zipfile
import base64
import psutil
from pathlib import Path
from mitmproxy.tools.main import mitmdump
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium import webdriver

from rpa_common import common
from rpa_common.exceptions import IpException, ChromeException, FingerprintException
from rpa_common.request.shopRequest import shopRequest

class chrome():
    def __init__(self):
        super().__init__()

    @staticmethod
    def run_mitmproxy(data, listen_port):
        '''
        @Desc    : 运行mitmproxy
        @return  : subprocess.Popen 对象，用于后续关闭
        @Author  : 钟水洲
        @Time    : 2025/07/09 11:19:47
        '''
        env_data = data.get("env_data")

        if "ip" not in env_data:
            raise IpException("缺少 IP信息")
        ip_data = env_data.get("ip")

        if "http" not in ip_data:
            raise IpException("缺少 http代理")
        http_data = ip_data.get("http")

        ip = http_data.get("ip")
        port = http_data.get("port")
        account = http_data.get("account")
        password = http_data.get("password")

        upstream_url = f"http://{ip}:{port}"
        upstream_auth = f"{account}:{password}"

        # 环境参数
        env_str = json.dumps(env_data, ensure_ascii=False)
        base64_str = base64.b64encode(env_str.encode("utf-8")).decode("utf-8")

        root_dir = Path(__file__).resolve().parents[1]
        print("root_dir", root_dir)

        script_path = os.path.join(root_dir, "mitmdump.py")
        print("script_path", script_path)

        # 创建日志文件路径（使用端口号区分不同实例）
        log_dir = root_dir / "log" / "mitm_logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, f"mitmdump_{listen_port}.log")

        try:
            # 打开日志文件（追加模式）
            with open(log_file_path, "ab") as log_file:
                process = subprocess.Popen([
                    "mitmdump",
                    "-s", script_path,
                    "--listen-port", str(listen_port),
                    "--mode", f"upstream:{upstream_url}",
                    "--upstream-auth", upstream_auth,
                    base64_str,
                ], stdout=log_file, stderr=subprocess.STDOUT)  # 合并stdout和stderr到同一文件

                # 等待几秒，看是否异常退出
                time.sleep(3)

                # 检查是否还活着
                if process.poll() is None:
                    print(f"✅ mitmdump 启动成功，进程ID: {process.pid}")
                    print(f"日志文件: {os.path.abspath(log_file_path)}")
                else:
                    # 异常退出，读取日志文件内容
                    print("❌ mitmdump 启动失败，错误日志:")
                    with open(log_file_path, "rb") as f:
                        print(f.read().decode('utf-8', errors='replace'))

                    return None

        except Exception as e:
            print(f"启动 mitmdump 时发生异常: {str(e)}")
            return None

        return process

    @staticmethod
    def start_driver(data, listen_port, user_data_dir):
        '''
        @Desc    : 启动驱动
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        env_data = data.get("env_data")

        options = uc.ChromeOptions()

        # 指定用户目录
        options.add_argument(f"--user-data-dir={str(user_data_dir)}")
        options.add_argument("--profile-directory=Default")

        if chrome.is_chrome_running_with_user_data_dir(user_data_dir):
            raise ChromeException("店铺已打开, 请先关闭或等待关闭")

        # HTTP 代理
        print("HTTP 代理")
        proxy_ip = f"127.0.0.1:{listen_port}"
        proxy_server = f"http://{proxy_ip}"
        print("proxy_server", proxy_server)

        options.add_argument(f'--proxy-server={proxy_server}')
        options.add_argument("--ignore-certificate-errors")  # 忽略 SSL 证书错误

        # 设置指纹信息
        print("设置指纹信息")
        chrome.setInitFingerprint(options, env_data)

        # 禁用权限、设置语言
        chrome.disable(options, env_data)

        # 系统
        system = platform.system()
        print(system)

        # 获取驱动路径
        driver_path = chrome.getDriverPath(system)

        if system == "Linux":
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless=new")  # 使用Chrome的新无头模式

        # 创建插件
        # proxy_dir = chrome.create_proxy_extension("159.138.148.69", 27776)
        # print("proxy_dir", proxy_dir)
        # options.add_argument("--disable-extensions-except=" + str(proxy_dir))

        driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path
        )

        # 设置驱动指纹信息
        chrome.setDriverFingerprint(driver, data)

        return driver

    @staticmethod
    def is_chrome_running_with_user_data_dir(user_data_dir):
        '''
        @Desc    : 是否已经有该用户目录对应的 Chrome 在运行
        @param   : user_data_dir - Chrome 的用户数据目录路径
        @return  : bool
        @Author  : 钟水洲
        @Time    : 2025/07/22 15:23:49
        '''
        print("检测是否已经有该用户目录对应的 Chrome 在运行")

        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if not proc.info['name']:
                    continue
                if 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if any(str(user_data_dir) in arg for arg in cmdline):
                        return True
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess, OSError) as e:
                continue
        return False

    @staticmethod
    def setPlatform(driver):
        '''
        @Desc    : 修改平台信息
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        print("修改平台信息")
        # 注入 JS 修改 platform 信息
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32'
                    });
                    Object.defineProperty(navigator, 'appVersion', {
                        get: () => '5.0 (Windows)'
                    });
                    Object.defineProperty(navigator, 'oscpu', {
                        get: () => 'Windows NT 10.0; Win64; x64'
                    });
                """
            },
        )

    @staticmethod
    def setWebGL(driver):
        '''
        @Desc    : WebGL 伪装注入
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        print("WebGL 伪装注入")
        webgl_defender_script = """
        (() => {
            const getParameter = WebGLRenderingContext.prototype.getParameter;

            function fakeGetParameter(parameter) {
                if (parameter === 37445) return "Google Inc. (Intel)";
                if (parameter === 37446) return "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00009BC8) Direct3D11 vs_5_0 ps_5_0, D3D11)";
                return getParameter.call(this, parameter);
            }

            WebGLRenderingContext.prototype.getParameter = fakeGetParameter;
            WebGL2RenderingContext.prototype.getParameter = fakeGetParameter;
        })();
        """

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": webgl_defender_script
        })

    @staticmethod
    def setFont(driver):
        '''
        @Desc    : 设置字体
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        font_fingerprint_defender = """
        (() => {
        const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
        CanvasRenderingContext2D.prototype.measureText = function(text) {
            const result = originalMeasureText.apply(this, arguments);
            // 举例伪装某个字体文字的宽度
            if (text === "Arial") {
            return new Proxy(result, {
                get(target, prop) {
                if (prop === 'width') return target.width + 3;
                return target[prop];
                }
            });
            }
            return result;
        };
        })();
        """

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": font_fingerprint_defender
        })

    @staticmethod
    def setAudioContext(driver):
        '''
        @Desc    : AudioContext 伪装注入
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        audiocontext_defender_script = """
        (() => {
            const nativeToString = Function.prototype.toString;
            const toStringMap = new WeakMap();

            // Patch Function.prototype.toString 伪装自定义函数为 [native code]
            Function.prototype.toString = function() {
                return toStringMap.get(this) || nativeToString.call(this);
            };

            function fakeNative(func, nativeStr) {
                toStringMap.set(func, `function ${nativeStr}() { [native code] }`);
                return func;
            }

            // --- Patch getChannelData ---
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            const getChannelDataProxy = fakeNative(function(channel) {
                const data = originalGetChannelData.call(this, channel);
                // 添加轻微扰动，防止 hash 值重复
                for (let i = 0; i < data.length; i++) {
                    data[i] += Math.random() * 1e-7;
                }
                return data;
            }, 'getChannelData');

            Object.defineProperty(AudioBuffer.prototype, 'getChannelData', {
                value: getChannelDataProxy,
                configurable: true
            });

            // --- Patch OfflineAudioContext.startRendering ---
            const originalStartRendering = OfflineAudioContext.prototype.startRendering;
            const startRenderingProxy = fakeNative(function() {
                return originalStartRendering.apply(this, arguments).then(buffer => {
                    // 确保每次渲染结果有轻微差异
                    for (let i = 0; i < buffer.numberOfChannels; i++) {
                        const data = buffer.getChannelData(i);
                        for (let j = 0; j < data.length; j++) {
                            data[j] += Math.random() * 1e-7;
                        }
                    }
                    return buffer;
                });
            }, 'startRendering');

            Object.defineProperty(OfflineAudioContext.prototype, 'startRendering', {
                value: startRenderingProxy,
                configurable: true
            });

            // --- Patch DynamicsCompressorNode attributes ---
            const OriginalDCN = window.DynamicsCompressorNode;
            if (OriginalDCN) {
                const proxyDCN = function(context) {
                    const node = new OriginalDCN(context);
                    // 伪造关键属性
                    Object.defineProperties(node, {
                        threshold: { get: () => ({ value: -50 }) },
                        knee: { get: () => ({ value: 40 }) },
                        ratio: { get: () => ({ value: 12 }) },
                        reduction: { get: () => -20 },
                        attack: { get: () => ({ value: 0 }) },
                        release: { get: () => ({ value: 0.25 }) }
                    });
                    return node;
                };
                proxyDCN.prototype = OriginalDCN.prototype;
                window.DynamicsCompressorNode = fakeNative(proxyDCN, 'DynamicsCompressorNode');
            }
        })();
        """

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": audiocontext_defender_script
        })

    @staticmethod
    def hash_to_int(s):
        '''
        @Desc    : 取字符串的MD5,截取前8位转成整数作为种子
        @Author  : 钟水洲
        @Time    : 2025/07/14 15:23:20
        '''
        s = str(s)
        md5 = hashlib.md5(s.encode('utf-8')).hexdigest()
        return int(md5[:8], 16)

    @staticmethod
    def setCanvas(driver, shop_global_id):
        '''
        @Desc    : Canvas 伪装注入，使用店铺ID确定扰动
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        print("Canvas 伪装注入")
        print("shop_global_id", shop_global_id)
        seed = chrome.hash_to_int(shop_global_id)
        print("seed", seed)
        canvas_defender_script = f"""
        (() => {{
            function mulberry32(a) {{
                return function() {{
                    var t = a += 0x6D2B79F5;
                    t = Math.imul(t ^ (t >>> 15), t | 1);
                    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
                    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
                }}
            }}
            const rand = mulberry32({seed});
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type, encoderOptions) {{
                type = 'image/png';
                encoderOptions = 0.12345;
                const ctx = this.getContext('2d');
                if (ctx && ctx.getImageData && ctx.putImageData) {{
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {{
                        // 利用伪随机数生成 0 或 1 做异或扰动
                        imageData.data[i] ^= (rand() > 0.5 ? 1 : 0);
                        imageData.data[i + 1] ^= (rand() > 0.5 ? 1 : 0);
                        imageData.data[i + 2] ^= (rand() > 0.5 ? 1 : 0);
                    }}
                    ctx.putImageData(imageData, 0, 0);
                }}
                return originalToDataURL.call(this, type, encoderOptions);
            }};
            HTMLCanvasElement.prototype.toDataURL.toString = () => 'function toDataURL() {{ [native code] }}';
        }})();
        """

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": canvas_defender_script
        })

    @staticmethod
    def getChromeVersion():
        '''
        获取本机 Chrome 浏览器主版本号
        '''
        system = platform.system()
        try:
            if system == "Windows":
                # Windows 获取 Chrome 版本（通过注册表或默认路径）
                import winreg
                reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
            elif system == "Linux":
                # Linux 通常直接可以获取
                output = subprocess.check_output(["google-chrome", "--version"]).decode()
                version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output).group(1)
            else:
                raise ChromeException(f"暂不支持的系统: {system}")
            print("Chrome Version:", version)
            return version.split('.')[0]  # 只返回主版本号
        except Exception as e:
            raise ChromeException(f"获取 Chrome 版本失败: {str(e)}")

    @staticmethod
    def getDriverPath(system):
        '''
        @Desc    : 获取驱动路径
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        chrome_major = chrome.getChromeVersion()

        # 映射关系（主版本号 -> 驱动版本文件名）
        version_map = {
            '104': '104.exe',
            '109': '109.exe',
            '114': '114.exe',
            '116': '116.exe',
            '120': '120.exe',
            '122': '122.exe',
            '136': '136.exe',
            '137': '137.exe',
            '138': '138.exe',
        }

        driver_filename = version_map.get(chrome_major)
        if not driver_filename:
            raise ChromeException(f"不支持的 Chrome 主版本号: {chrome_major}")

        if system == "Windows":
            driver_path = common.resourcePath(f"./env/chrome/chromedriver/windows/{driver_filename}")
        elif system == "Linux":
            driver_path = common.resourcePath(f"./env/chrome/chromedriver/linux/{chrome_major}/chromedriver")
            os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        else:
            raise ChromeException(f"不支持的操作系统: {system}")

        print("driver_path", driver_path)
        return driver_path

    @staticmethod
    def disable(options, env_data):
        '''
        @Desc    : 禁用权限
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        # 禁用自动化检测
        options.add_argument("--disable-blink-features=AutomationControlled")

        # 禁用 WebRTC 本地 IP 地址暴露
        options.add_argument("--disable-webrtc")  # 注意：这个参数本身并不能完全禁用 WebRTC，更多的是实验性
        options.add_argument("--force-webrtc-ip-handling-policy=default_public_interface_only")
        options.add_argument("--disable-ipv6")  # 有时候结合禁用 IPv6 效果更佳

        # 不支持触屏
        options.add_argument('--disable-touch-events')
        options.add_argument('--touch-events=disabled')

        # 禁用插件
        options.add_argument("--disable-extensions")
        # 禁用组件扩展
        options.add_argument("--disable-component-extensions-with-background-pages")
        # 禁用默认应用
        options.add_argument("--disable-default-apps")
        # 禁用插件自动发现
        options.add_argument("--disable-plugins-discovery")

        # 内存优化核心参数
        options.add_argument("--disable-software-rasterizer")           # 禁用软件光栅化
        options.add_argument("--no-zygote")                             # 禁用zygote进程
        options.add_argument("--disable-threaded-animation")            # 禁用线程动画
        options.add_argument("--disable-threaded-scrolling")            # 禁用线程滚动
        options.add_argument("--disable-accelerated-2d-canvas")         # 禁用2D加速
        options.add_argument("--memory-pressure-off")                   # 关闭内存压力检测

        # 禁用 Do Not Track 功能
        options.add_argument("--disable-features=EnableDoNotTrack")

        # 启用高 DPI 支持模式
        options.add_argument("--high-dpi-support=1")
        # 防止真实设备信息泄露
        options.add_argument("--use-fake-ui-for-media-stream")
        # 模拟设备信息
        options.add_argument("--use-fake-device-for-media-stream")

        # 禁用背景任务 / 预加载
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-first-run")

        # 获取浏览器语言
        lang = env_data.get("lang")
        browser = lang.get("browser")

        # 禁用浏览器的同源策略
        options.add_argument("--disable-web-security")

        # 资源禁用（节省大量内存）
        prefs = {
            "intl.accept_languages": browser,  # 设置浏览器语言
            'profile.managed_default_content_settings.fonts': 2, # 禁止加载字体
            "profile.default_content_setting_values.media_stream_mic": 2,     # 禁用麦克风
            "profile.default_content_setting_values.media_stream_camera": 2,  # 禁用摄像头
            "profile.default_content_setting_values.geolocation": 2,          # 禁用定位
            "profile.default_content_setting_values.notifications": 2,         # 禁用通知
            "profile.default_content_setting_values.bluetooth": 2,  # 阻止访问蓝牙
            # 禁用所有非代理的 UDP 通信（禁止 WebRTC 直连）
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)

    @staticmethod
    def setInitFingerprint(options, env_data):
        '''
        @Desc    : 设置初始指纹信息
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        user_agent = env_data.get("user_agent")

        screen_size = env_data.get("screen_size")
        width = screen_size.get("width")
        height = screen_size.get("height")

        lang = env_data.get("lang")
        browser_interface = lang.get("browser_interface")

        # 设置浏览器界面语言
        options.add_argument(f"--lang={browser_interface}")
        # 设置窗口大小
        options.add_argument(f"--window-size={width},{height}")
        # 设置 user-agent
        options.add_argument(f"--user-agent={user_agent}")
        # 设置 页面缩放比例
        options.add_argument("--force-device-scale-factor=1")

    @staticmethod
    def setMemoryAndCpu(driver):
        '''
        @Desc    : 模拟内存，CPU
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        print("模拟内存，CPU")
        script = """
        (() => {
            const memoryGetter = function() {
                return 16;
            };
            Object.defineProperty(memoryGetter, 'toString', {
                value: () => 'function get deviceMemory() { [native code] }',
                writable: false
            });

            Object.defineProperty(navigator, 'deviceMemory', {
                get: memoryGetter,
                configurable: true,
                enumerable: true
            });

            const coreGetter = function() {
                return 8;
            };
            Object.defineProperty(coreGetter, 'toString', {
                value: () => 'function get hardwareConcurrency() { [native code] }',
                writable: false
            });

            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: coreGetter,
                configurable: true,
                enumerable: true
            });
        })();
        """

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})

    @staticmethod
    def setSpeechVoices(driver):
        '''
        @Desc    : 模拟语音列表
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        script = """
        window.speechSynthesis.getVoices = function() {
            return [{
                name: "Google US English",
                lang: "en-US",
                voiceURI: "Google US English",
                localService: true,
                default: true
            }];
        };
        """
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})

    @staticmethod
    def getFingerprint(driver, shop_data, params):
        '''
        @Desc    : 获取指纹信息
        @Author  : 钟水洲
        @Time    : 2025/06/24 20:16:20
        '''
        print("指纹检测")

        shop_global_id = shop_data['shop_global_id']
        task_id = params['task_id']

        # 访问页面
        driver.get("https://rpa.spocoo.com/v1/index/fingerprintbrowser.html")

        # 等待页面加载完成
        driver.implicitly_wait(10)

        try:
            # Find all rows in the table
            rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl.f12.td-right tr")

            fingerprint_data = {}

            for row in rows:
                # Get the cells in each row
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 2:
                    key = cells[0].text.strip().replace(":", "").replace("[http header]", "").replace("[navigator]", "").strip()
                    value = cells[1].text.strip()
                    fingerprint_data[key] = value

            if not fingerprint_data:
                raise Exception("指纹数据为空")

            data = {
                "shop_global_id": shop_global_id,
                "task_id": task_id,
                "fingerprint": json.dumps(fingerprint_data, ensure_ascii=False),
            }

            print(json.dumps(data, ensure_ascii=False))

            shopRequest.saveFingerprintLog(data)
        except Exception as e:
            raise FingerprintException(f"获取指纹信息时出错: {str(e)}")

    @staticmethod
    def monitorNewTabs(driver, shop_data, known_handles=None, stop_event=None):
        '''
        @Desc    : 监听新标签页
        @Author  : 钟水洲
        @Time    : 2025/07/12 16:48:57
        '''
        if known_handles is None:
            known_handles = set(driver.window_handles)

        while not (stop_event and stop_event.is_set()):
            current_handles = set(driver.window_handles)
            new_tabs = current_handles - known_handles
            if new_tabs:
                for h in new_tabs:
                    try:
                        driver.switch_to.window(h)
                        print("设置指纹信息")
                        chrome.setDriverFingerprint(driver, shop_data)
                    except Exception as e:
                        print(f"切换标签页出错: {e}")
                known_handles.update(new_tabs)
            time.sleep(0.1)

    @staticmethod
    def setDriverFingerprint(driver, shop_data):
        '''
        @Desc    : 设置驱动指纹信息
        @Author  : 钟水洲
        @Time    : 2025/07/12 16:48:57
        '''
        env_data = shop_data.get("env_data")

        # 获取语言
        lang = env_data.get("lang")
        # 设置驱动语言
        chrome.setDriverLang(driver, lang)

        # 屏幕尺寸
        screen_size = env_data.get("screen_size")
        # 设置驱动屏幕尺寸
        chrome.setDriverScreen(driver, screen_size)

        # 设置驱动时间
        chrome.setDriverTime(driver, env_data)

        # 修改平台信息
        chrome.setPlatform(driver)

        # 设置WebGPU
        chrome.setWebGPU(driver)

        # 设置触屏
        chrome.setTouch(driver)

        # 设置电池
        chrome.setBattery(driver)

        # 模拟内存，CPU
        chrome.setMemoryAndCpu(driver)

        # 模拟语音列表
        # chrome.setSpeechVoices(driver)

        # AudioContext 伪装注入
        # chrome.setAudioContext(driver)

        # WebGL 伪装注入
        chrome.setWebGL(driver)

        # 设置字体指纹
        # chrome.setFont(driver)

        # 店铺账号ID
        shop_global_id = shop_data.get("shop_global_id")
        # Canvas 伪装注入
        chrome.setCanvas(driver, shop_global_id)

    @staticmethod
    def setTouch(driver):
        '''
        @Desc    : 设置触屏
        @Author  : 钟水洲
        @Time    : 2025/07/14 14:27:06
        '''
        print("设置触屏")
        driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {
            "enabled": False
        })

    @staticmethod
    def setBattery(driver):
        '''
        @Desc    : 设置电池
        @Author  : 钟水洲
        @Time    : 2025/07/14 14:27:06
        '''
        print("设置电池")
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                navigator.getBattery = async function() {
                    return {
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1.0,
                        onchargingchange: null,
                        onchargingtimechange: null,
                        ondischargingtimechange: null,
                        onlevelchange: null
                    };
                };
                """
            }
        )

    @staticmethod
    def setWebGPU(driver):
        '''
        @Desc    : 设置WebGPU
        @Author  : 钟水洲
        @Time    : 2025/07/14 14:27:06
        '''
        print("设置WebGPU")
        disable_webgpu_script = """
        (() => {
            try {
                // 让 navigator.gpu 返回 undefined,表示不支持 WebGPU
                Object.defineProperty(navigator, 'gpu', {
                    get: () => undefined,
                    configurable: true
                });
            } catch (e) {
                // 兼容性处理,不报错
            }
        })();
        """

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": disable_webgpu_script
        })

    @staticmethod
    def setDriverLang(driver, lang):
        '''
        @Desc    : 设置驱动语言
        @Author  : 钟水洲
        @Time    : 2025/07/14 14:27:06
        '''
        print("设置驱动语言")
        header = lang.get("header")
        browser_interface = lang.get("browser_interface")

        # 设置请求头
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
            'headers': {
                'Accept-Language': header # 请求头语言
            }
        })

        # 浏览器界面语言
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                (function() {{
                    const spoofedLocale = "{browser_interface}";
                    const original = Intl.DateTimeFormat.prototype.resolvedOptions;
                    Intl.DateTimeFormat.prototype.resolvedOptions = function () {{
                        const options = original.call(this);
                        options.locale = spoofedLocale;
                        return options;
                    }};
                    for (const ctor of [Intl.NumberFormat, Intl.Collator, Intl.PluralRules, Intl.RelativeTimeFormat]) {{
                        const original = ctor.prototype.resolvedOptions;
                        ctor.prototype.resolvedOptions = function () {{
                            const options = original.call(this);
                            options.locale = spoofedLocale;
                            return options;
                        }};
                    }}
                }})();
            """
        })

    @staticmethod
    def setDriverScreen(driver, screen_size):
        '''
        @Desc    : 设置驱动屏幕尺寸
        @Author  : 钟水洲
        @Time    : 2025/07/14 14:27:06
        '''
        print("设置驱动屏幕尺寸")
        width = screen_size.get("width")
        height = screen_size.get("height")

        # 模拟分辨率和缩放
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": False,
        })

        # 注入 JS 伪造 screen 和 window 尺寸
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(screen, 'availWidth', {{ get: () => {width} }});
                Object.defineProperty(screen, 'availHeight', {{ get: () => {height} }});
                Object.defineProperty(screen, 'width', {{ get: () => {width} }});
                Object.defineProperty(screen, 'height', {{ get: () => {height} }});

                Object.defineProperty(window, 'innerWidth', {{ get: () => {width} }});
                Object.defineProperty(window, 'innerHeight', {{ get: () => {height} }});
            """
        })

    @staticmethod
    def setDriverTime(driver, env_data):
        '''
        @Desc    : 设置驱动时间
        @Author  : 钟水洲
        @Time    : 2025/07/14 14:27:06
        '''
        print("设置驱动时间")
        # 时区
        timezone = env_data.get("timezone")

        # 获取语言
        lang = env_data.get("lang")
        browser_interface = lang.get("browser_interface")

        # 设置时区
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': timezone})

        # 注入脚本伪装
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
                    return {{
                        timeZone: "{timezone}",
                        locale: "{browser_interface}",
                        calendar: "gregory",
                        numberingSystem: "latn",
                        timeZoneName: "short"
                    }};
                }};
            """
        })

    @staticmethod
    def create_proxy_extension(proxy_host, proxy_port):
        '''
        @Desc    : 创建 SOCKS5 代理插件 (Manifest V3)
        @Author  : 钟水洲
        @Time    : 2025/07/21 17:34:14
        '''
        # 生成 manifest 内容
        manifest_json_content = """{
            "name": "SOCKS5 Proxy Extension",
            "description": "Sets a SOCKS5 proxy",
            "version": "1.0",
            "manifest_version": 3,
            "permissions": [
                "proxy",
                "storage"
            ],
            "host_permissions": [
                "<all_urls>"
            ],
            "background": {
                "service_worker": "background.js"
            },
            "action": {
                "default_title": "SOCKS5 Proxy"
            }
        }"""

        # 直接将 host 和 port 写入 JS，无需 chrome.storage
        background_js_content = f"""
        chrome.runtime.onInstalled.addListener(() => {{
            const config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "socks5",
                        host: "{proxy_host}",
                        port: {proxy_port}
                    }},
                    bypassList: ["<local>"]
                }}
            }};

            chrome.proxy.settings.set({{ value: config, scope: "regular" }}, () => {{
                console.log("SOCKS5 Proxy set to {proxy_host}:{proxy_port}");
            }});
        }});
        """

        base_dir = Path(__file__).resolve().parents[2]
        extension_dir = base_dir / "cache" / "extension" / "socks5"
        extension_dir.mkdir(parents=True, exist_ok=True)

        # 将内容写入目录
        (extension_dir / "manifest.json").write_text(manifest_json_content, encoding='utf-8')
        (extension_dir / "background.js").write_text(background_js_content, encoding='utf-8')

        return str(extension_dir)