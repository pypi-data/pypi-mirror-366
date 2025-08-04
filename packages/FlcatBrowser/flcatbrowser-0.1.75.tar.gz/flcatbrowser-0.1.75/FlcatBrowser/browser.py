from abc import ABC, abstractmethod
import os
import threading
import time
from DrissionPage import Chromium, ChromiumOptions
import loguru
from wakepy import keep
from .plugin.intercept import Intercept
from .utils.port import find_free_port
from DrissionPage.errors import PageDisconnectedError
from DrissionPage.func_replace import auto_replace
from .enum import NetworkListenMode
import json
from types import SimpleNamespace
class BaseBrowser(ABC):
    """
    Browser类负责业务逻辑与页面操作。
    """

    def __init__(self, browser_id, data_dir= "", proxy_ip = "", addr = "", on_init_finshed_callback=None, network_listen_mode: NetworkListenMode = NetworkListenMode.XHR):
        """
        初始化一个 BaseBrowser 实例
        
        :param browser_id: (str) 该浏览器实例的唯一标识，用于区分不同的浏览器实例。
        :param data_dir:   (str) 指定浏览器用户数据（User Data）与缓存（Cache）等文件的存储路径。
        :param proxy_ip:   (str) 代理 IP，当前仅支持无验证代理。
        :param addr:       (str) 如果需要连接到已在运行的浏览器实例，可传入其远程调试地址；若为空则新建一个浏览器实例。
        """
        self.browser_id = browser_id
        self.data_dir= data_dir
        self.proxy_ip = proxy_ip
        self.addr = addr
        self.network_listen_mode = network_listen_mode
        self.on_init_finshed_callback = on_init_finshed_callback
        from .website import BaseWebsite
        self.website: "BaseWebsite" = None
        self._stop_event = threading.Event()
        self._init_browser()
        self._after_init_browser()
        
    def _create_browser(self, options):
        return Chromium(addr_or_opts=options)

    def _init_browser(self):
        try:
            if self.addr:
                self.dbrowser = Chromium(addr_or_opts=self.addr)
                self.tab = self.dbrowser.latest_tab
                auto_replace(self.tab)
            else:
                options = ChromiumOptions().set_paths(local_port=find_free_port(),
                    user_data_path=os.path.join(self.data_dir ,f"user/{self.browser_id}"),
                    cache_path=os.path.join(self.data_dir ,"cache"))
            
                # 代理ip只支持无验证的代理
                if self.proxy_ip:
                    options.set_proxy(self.proxy_ip)
                self.dbrowser = self._create_browser(options)
                self.tab = self.dbrowser.latest_tab
                auto_replace(self.tab)
            self._init_website()
            if not self.website:
                raise ValueError('请重写_init_website方法并在其中对self.website进行赋值')
            self.tab.set.auto_handle_alert(accept=True)
            # self.tab.set.window.max()
            self.tab.console.start()
            if self.network_listen_mode == NetworkListenMode.XHR:
                self.tab.add_init_js("""
// xhr_fetch_hook.js (Corrected and Robust Version)
(function() {
    // 1. 防止重复注入
    if (window.__custom_hook_installed) {
        return;
    }
    window.__custom_hook_installed = true;

    const LOG_MARKER = '__MY_XHR_FETCH_HOOK__';
    let requestIdCounter = 0;

    /**
     * 将请求/响应数据发送到控制台
     * @param {object} data - 要记录的数据
     */
    function sendToConsole(data) {
        // 使用console.log，因为它是最通用的
        console.log(JSON.stringify({
            __source__: LOG_MARKER,
            payload: data
        }));
    }

    // --- 2. Hook XMLHttpRequest (Robust Method) ---
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        // 在XHR实例上附加一个自定义属性来存储请求信息
        this._hook_info = {
            id: `xhr-${Date.now()}-${requestIdCounter++}`,
            method: method.toUpperCase(),
            url: url,
            type: 'xhr'
        };
        // 调用原始的open方法，保持原有功能
        return originalOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function(body) {
        if (this._hook_info) {
            const hookInfo = this._hook_info;
            // 尝试记录请求体
            try {
                hookInfo.requestBody = body ? String(body) : null;
            } catch (e) {
                hookInfo.requestBody = '[Could not serialize request body]';
            }
            
            // 添加事件监听器以捕获响应
            this.addEventListener('load', () => {
                const responseHeaders = this.getAllResponseHeaders();
                const responseData = {
                    status: this.status,
                    statusText: this.statusText,
                    headers: responseHeaders,
                    body: this.responseText,
                };
                sendToConsole({ ...hookInfo, response: responseData });
            }, { once: true });

            this.addEventListener('error', () => {
                sendToConsole({ ...hookInfo, error: 'XHR Network Error' });
            }, { once: true });
            
            this.addEventListener('timeout', () => {
                sendToConsole({ ...hookInfo, error: 'XHR Request Timed Out' });
            }, { once: true });
        }
        // 调用原始的send方法，发起请求
        return originalSend.apply(this, arguments);
    };

    // --- 3. Hook fetch (Remains the same, it's generally reliable) ---
    const originalFetch = window.fetch;
    window.fetch = function(input, init = {}) {
        const id = `fetch-${Date.now()}-${requestIdCounter++}`;
        const url = (input instanceof Request) ? input.url : String(input);
        const method = ((input instanceof Request) ? input.method : (init.method || 'GET')).toUpperCase();

        return new Promise((resolve, reject) => {
            originalFetch.apply(this, arguments)
                .then(response => {
                    const clonedResponse = response.clone();
                    const headers = {};
                    clonedResponse.headers.forEach((value, key) => { headers[key] = value; });
                    
                    clonedResponse.text().then(body => {
                        sendToConsole({
                            id: id, type: 'fetch', method: method, url: url,
                            response: {
                                ok: clonedResponse.ok, status: clonedResponse.status,
                                statusText: clonedResponse.statusText, headers: headers, body: body
                            }
                        });
                    }).catch(() => { // 处理非文本响应体
                        sendToConsole({
                            id: id, type: 'fetch', method: method, url: url,
                            response: {
                                ok: clonedResponse.ok, status: clonedResponse.status,
                                statusText: clonedResponse.statusText, headers: headers, body: '[Non-text or unreadable body]'
                            }
                        });
                    });
                    
                    // 将原始响应 resolve 出去，确保网站的 Promise 链继续执行
                    resolve(response);
                })
                .catch(error => {
                    sendToConsole({ id: id, type: 'fetch', method: method, url: url, error: error.message });
                    // 将错误 reject 出去，确保网站能捕获到错误
                    reject(error);
                });
        });
    };

    // --- 4. 增加反检测能力 (可选但推荐) ---
    // 很多反爬脚本会检查函数的 .toString() 是否包含 "[native code]"
    try {
        XMLHttpRequest.prototype.open.toString = () => originalOpen.toString();
        XMLHttpRequest.prototype.send.toString = () => originalSend.toString();
        window.fetch.toString = () => originalFetch.toString();
    } catch(e) {
        // 在某些严格的环境下，修改toString可能会失败，但hook本身仍然有效
    }
})();
""")        
            elif self.network_listen_mode == NetworkListenMode.XHR:
                self.tab.listen.start(self.website.listen_paths)
            else:
                raise Exception(f'不支持的网络监听模式{self.network_listen_mode}')
            threading.Thread(target=self._listen_console, daemon=True).start()
            threading.Thread(target=self._listen_path, daemon=True).start()
            threading.Thread(target=self._prevent_system_sleep, daemon=True).start()
            threading.Thread(target=self._browser_is_alive, daemon=True).start()
            self._start_intercept()
            self.website.open_base_url()
            if self.on_init_finshed_callback:
                self.on_init_finshed_callback()
        except Exception as e:
            loguru.logger.exception(f"[BrowserInit] 异常: {e}")
            self.close()
            raise(e)

    def _prevent_system_sleep(self):
        with keep.running():
            while not self._stop_event.is_set():
                time.sleep(1)
    
    def _start_intercept(self):
        Intercept(self.tab, self.dbrowser)

    def _after_init_browser(self):
        """
        在浏览器初始化完成后执行的操作。
        
        默认实现为空，可在子类中重写此方法，以在浏览器初始化完成后执行自定义逻辑，
        如：预加载页面、设置cookie、执行登录操作等。
        """
        pass

    @abstractmethod
    def _init_website(self):
        """
        初始化 Website（站点）对象。

        默认实现为空，请在子类中重写此方法，创建自定义站点（继承BaseWebsite）的初始化工作，并设置self.website
        """
        pass

    def _before_close(self):
        pass

    def _after_close(self):
        pass

    def close(self):
        """关闭浏览器"""
        try:
            self._before_close()
        except Exception as e:
            loguru.logger.exception(e)
        try:
            self._stop_event.set()
            self.dbrowser.quit(force=True)
        except Exception:
            pass
        self._after_close()

    def _browser_is_alive(self):
        while not self._stop_event.is_set():
            time.sleep(1)
            try:
                try:
                    self.tab.url
                except PageDisconnectedError as e:
                    loguru.logger.exception(f"浏览器已断开连接[{self.boss_id}], {e}")
            except Exception as e:
                self.close()
                loguru.logger.warning(f"检测到浏览器已关闭！ID: {self.browser_id}")

    def _listen_path(self):
        """进行请求监听"""
        while not self._stop_event.is_set():
            time.sleep(1e9)
            try:
                for response in self.tab.listen.steps():
                    if self.website.listen_path_callback:
                        self.website.listen_path_callback(response)
            except Exception as e:
                loguru.logger.exception(f"[_listen_path]错误{e}")

    def _listen_console(self):
        """
        通过监听控制台来捕获由JS Hook发出的网络请求日志。
        """
        LOG_MARKER = '__MY_XHR_FETCH_HOOK__'
        loguru.logger.info("Starting console listener for hooked network requests...")
        while not self._stop_event.is_set():
            try:
                # 使用 .steps() 作为生成器，持续监听
                for response in self.tab.console.steps(timeout=1): # 添加超时以允许检查 _stop_event
                    try:
                        data = json.loads(response.text)
                        # 检查是否是我们注入的Hook发出的日志
                        if isinstance(data, dict) and data.get('__source__') == LOG_MARKER:
                            self._handle_hooked_request(data.get('payload', {}))
                            continue
                    except (json.JSONDecodeError, TypeError):
                        # 不是JSON格式的日志，或者内容为空，忽略
                        pass

                    if self.website.listen_console_callback:
                        self.website.listen_console_callback(response)
            except TimeoutError:
                # 正常超时，继续循环检查 stop_event
                continue
            except Exception as e:
                # 捕获其他可能的异常，例如tab关闭等
                loguru.logger.exception(f"[_listen_console] 发生错误: {e}")
                break # 出现严重错误时退出循环

    def _handle_hooked_request(self, payload: dict):
        """
        处理从JS Hook收到的数据，并将其转换成回调函数期望的格式。
        """
        if not payload or not self.website.listen_path_callback:
            return

        # 创建一个模拟的 response 对象，使其与 tab.listen 的响应结构类似
        # 这样就不需要修改 listen_path_callback 的内部逻辑了
        # SimpleNamespace 允许我们用点符号访问字典键
        mock_response = SimpleNamespace()
        mock_response.url = payload.get('url')
        mock_response.method = payload.get('method')
        mock_response.type = payload.get('type') # 'xhr' or 'fetch'
        
        # 模拟请求信息
        request_data = SimpleNamespace()
        request_data.body = payload.get('requestBody')
        mock_response.request = request_data

        # 模拟响应信息
        response_data = SimpleNamespace()
        if 'error' in payload:
            response_data.status = -1 # 用-1表示网络错误
            response_data.body = payload.get('error')
            response_data.headers = {}
        else:
            response_info = payload.get('response', {})
            response_data.status = response_info.get('status')
            try:
                response_data.body = json.loads(response_info.get('body'))
            except Exception:
                pass
            response_data.headers = response_info.get('headers')
        
        mock_response.response = response_data

        # 调用原始的回调函数
        try:
            self.website.listen_path_callback(mock_response)
        except Exception as e:
            loguru.logger.exception(f"[_handle_hooked_request] 执行回调时出错: {e}")