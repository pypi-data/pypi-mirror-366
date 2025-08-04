import platform
import os
import tempfile
import time
import hashlib

# --- 新增依赖 ---
# 这个模块需要 'requests' 库来处理 URL。
# 请通过 'pip install requests' 安装。
try:
    import requests
except ImportError:
    requests = None

# --- 【新增】文件下载工具类 ---
class FileDownloader:
    """
    一个用于下载并缓存文件的工具类。
    """
    def __init__(self, cache_dir: str = None, cache_duration: int = 86400):
        """
        初始化下载器。
        
        参数:
            cache_dir (str, optional): 缓存目录的路径。如果为 None，则在系统临时目录下创建 'py_downloader_cache'。
            cache_duration (int, optional): 缓存有效期（秒）。默认为 86400 (24小时)。设置为 0 可禁用缓存。
        """
        if cache_dir is None:
            self.cache_dir = os.path.join(tempfile.gettempdir(), 'py_downloader_cache')
        else:
            self.cache_dir = cache_dir
        
        self.cache_duration = cache_duration
        
        # 确保缓存目录存在
        if self.cache_duration > 0:
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, url: str) -> str:
        """根据 URL 生成唯一的缓存文件路径。"""
        # 使用 URL 的 SHA256 哈希值作为文件名，避免文件名冲突和非法字符
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, url_hash)

    def download(self, url: str, timeout: int = 20) -> bytes:
        """
        下载文件，如果存在有效缓存则从缓存中读取。
        
        参数:
            url (str): 要下载的文件的 URL。
            timeout (int, optional): 请求超时时间（秒）。
            
        返回:
            bytes: 文件的二进制内容。
            
        抛出:
            requests.RequestException: 如果下载失败。
            ValueError: 如果 requests 库未安装。
        """
        if requests is None:
            raise ValueError("处理 URL 需要安装 'requests' 库。请运行 'pip install requests'。")

        cache_path = self._get_cache_path(url)

        # 检查缓存是否可用且有效
        if self.cache_duration > 0 and os.path.exists(cache_path):
            file_mod_time = os.path.getmtime(cache_path)
            if (time.time() - file_mod_time) < self.cache_duration:
                print(f"   [Cache] 从缓存加载: {url[:70]}...")
                with open(cache_path, 'rb') as f:
                    return f.read()

        # 如果无缓存或缓存已过期，则下载
        print(f"   [Download] 正在下载: {url[:70]}...")
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # 为错误状态码抛出异常
            content = response.content

            # 如果启用了缓存，则保存文件
            if self.cache_duration > 0:
                with open(cache_path, 'wb') as f:
                    f.write(content)
            
            return content
        except requests.RequestException as e:
            # 将下载错误包装后重新抛出
            raise requests.RequestException(f"下载失败: {e}") from e

    def clear_cache(self):
        """清空缓存目录中的所有文件。"""
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"无法删除缓存文件 {file_path}: {e}")
            print(f"缓存已清空: {self.cache_dir}")

