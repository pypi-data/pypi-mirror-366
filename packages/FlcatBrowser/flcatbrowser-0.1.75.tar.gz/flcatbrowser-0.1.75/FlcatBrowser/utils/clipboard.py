import platform
import pyperclip
import struct
import os
import io
import base64
import tempfile
from PIL import Image
from typing import Union, Tuple, List
# 假设 file_downloader.py 在同一目录下
from .file_downloader import FileDownloader
import time
import loguru
import win32console
import win32gui
# --- 新增依赖 ---
# 这个模块需要 'requests' 库来处理 URL。
# 请通过 'pip install requests' 安装。
try:
    import requests
except ImportError:
    requests = None

# --- 全局常量 ---
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
# 【重要】创建全局下载器实例，以便在多次调用中共享缓存
downloader = FileDownloader(cache_duration=10*24*60*60)

# --- Windows 专用模块导入 ---
if platform.system() == 'Windows':
    import win32clipboard
    import win32con

# --- 核心功能函数 ---

def _open_clipboard_with_retry(retries: int = 5, delay: float = 0.1) -> bool:
    """
    尝试打开剪贴板，并在失败时重试。
    
    返回:
        bool: 是否成功打开。
    """
    for i in range(retries):
        try:
            # 1. 获取当前控制台窗口的句柄 (HWND)
            hwnd = win32console.GetConsoleWindow()
            if hwnd == 0:
                # 如果在某些没有控制台的环境下运行（如IDLE），尝试获取活动窗口
                hwnd = win32gui.GetForegroundWindow()
                if hwnd == 0:
                    loguru.logger.warning('无法获取有效的窗口句柄')
                # 不使用窗口句柄剪贴板会被抢占
            win32clipboard.OpenClipboard(hwnd)
            return True # 成功打开，立即返回
        except Exception as e:
            loguru.logger.exception(f'打开剪贴板失败：{e}')
            if i < retries - 1:
                time.sleep(delay) # 等待一会再试
            else:
                # 最后一次尝试仍然失败，则放弃
                pass
    raise Exception('打开剪贴板失败') # 所有尝试都失败了

def save_clipboard() -> dict:
    """保存当前剪贴板内容（Windows支持多格式，其他平台仅保存文本）"""
    system = platform.system()
    saved_data = {'system': system}

    if system == 'Windows':
        saved_data['data'] = {}
        opened = False
        try:
            _open_clipboard_with_retry()
            opened = True
            formats = []
            current_format = 0
            while True:
                current_format = win32clipboard.EnumClipboardFormats(current_format)
                if current_format == 0:
                    break
                formats.append(current_format)
            
            for fmt in formats:
                try:
                    saved_data['data'][fmt] = win32clipboard.GetClipboardData(fmt)
                except Exception:
                    pass
        except Exception as e:
            loguru.logger.exception(e)
            pass
        finally:
            # 【修复】仅在成功打开后才关闭，防止 "线程没有打开的剪贴板" 错误
            if opened:
                win32clipboard.CloseClipboard()
    else:
        try:
            saved_data['text'] = pyperclip.paste()
        except pyperclip.PyperclipException:
            saved_data['text'] = None
    return saved_data

def restore_clipboard(saved_data: dict):
    """恢复剪贴板内容"""
    system = saved_data.get('system', '')
    
    if system == 'Windows' and 'data' in saved_data:
        opened = False
        try:
            _open_clipboard_with_retry()
            opened = True
            win32clipboard.EmptyClipboard()
            for fmt, data in saved_data['data'].items():
                try:
                    win32clipboard.SetClipboardData(fmt, data)
                except Exception:
                    continue
        finally:
            # 【修复】仅在成功打开后才关闭
            if opened:
                win32clipboard.CloseClipboard()
    else:
        if saved_data.get('text'):
            pyperclip.copy(saved_data['text'])

def set_clipboard_text(text: str) -> Tuple[bool, str]:
    """设置剪贴板文本内容（跨平台）"""
    try:
        pyperclip.copy(text)
        # Windows下的二次验证可以简化或移除，pyperclip通常足够可靠
        if platform.system() == "Windows":
            # 简单的验证
            pasted_text = pyperclip.paste()
            if pasted_text != text:
                 # 如果 pyperclip 失败，尝试 win32api 作为备用方案
                raise RuntimeError("pyperclip 写入后验证失败")
        return (True, "")
    except Exception as e:
        error_msg = f"设置剪贴板失败 (pyperclip): {str(e)}"
        if platform.system() == "Windows":
            opened = False
            try:
                _open_clipboard_with_retry()
                opened = True
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
                return (True, "使用 Windows API 备用方案成功")
            except Exception as win_err:
                error_msg += f" | Windows API 备用方案也失败: {str(win_err)}"
            finally:
                if opened:
                    win32clipboard.CloseClipboard()
        return (False, error_msg)

def copy_files_to_clipboard(file_paths: List[str]) -> Tuple[bool, str]:
    """将一个或多个文件路径复制到剪贴板（仅限Windows）。"""
    if platform.system() != "Windows":
        return (False, "文件复制功能仅支持 Windows 系统")

    if not isinstance(file_paths, list) or not file_paths:
        return (False, "参数必须是-一个非空列表")
    abs_paths = [os.path.abspath(p) for p in file_paths]
    files_str = '\0'.join(abs_paths) + '\0\0'
    drop_files_struct = struct.pack('Iiiii', 20, 0, 0, 0, 1)
    data = drop_files_struct + files_str.encode('utf-16-le')
    opened = False
    try:
        _open_clipboard_with_retry()
        opened = True
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_HDROP, data)
        return (True, "")
    except Exception as e:
        return (False, f"复制文件到剪贴板失败: {e}")
    finally:
        # 【修复】仅在成功打开后才关闭
        if opened:
            win32clipboard.CloseClipboard()

def copy_image_to_clipboard_from_binary(image_data: bytes) -> Tuple[bool, str]:
    """从二进制数据复制图片到剪贴板。"""
    if platform.system() != "Windows":
        return (False, "图片复制功能仅支持 Windows 系统")
    
    # 【说明】所有耗时操作都在获取剪贴板锁之前完成，这是正确的做法。
    try:
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        output = io.BytesIO()
        image.save(output, 'BMP')
        bmp_data = output.getvalue()[14:]
        output.close()
    except Exception as e:
        return (False, f"准备图片数据失败 (非剪贴板错误): {e}")

    opened = False
    try:
        _open_clipboard_with_retry()
        opened = True
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)
        return (True, "")
    except Exception as e:
        return (False, f"写入图片到剪贴板失败: {e}")
    finally:
        # 【修复】仅在成功打开后才关闭
        if opened:
            win32clipboard.CloseClipboard()

# 其他函数 set_clipboard_image, copy_image_to_clipboard_from_base64,
# copy_file_to_clipboard_from_binary, copy_file_to_clipboard_from_base64
# 都是调用上述核心函数，所以不需要修改。
def set_clipboard_image(image_path: str) -> Tuple[bool, str]:
    if not os.path.exists(image_path):
        return (False, f"图片文件不存在: {image_path}")
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        return copy_image_to_clipboard_from_binary(image_data)
    except Exception as e:
        return (False, f"从文件路径复制图片失败: {e}")

def copy_image_to_clipboard_from_base64(base64_data: str) -> Tuple[bool, str]:
    try:
        if base64_data.startswith('data:'):
            base64_data = base64_data.split(',', 1)[1]
        
        image_data = base64.b64decode(base64_data)
        return copy_image_to_clipboard_from_binary(image_data)
    except Exception as e:
        return (False, f"从 base64 数据复制图片失败: {e}")

def copy_file_to_clipboard_from_binary(file_data: bytes, filename: str, temp_dir: str = None) -> Tuple[bool, str]:
    if platform.system() != "Windows":
        return (False, "文件复制功能仅支持 Windows 系统")
    
    try:
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        
        temp_path = os.path.join(temp_dir, filename)
        
        with open(temp_path, 'wb') as f:
            f.write(file_data)
        
        success, msg = copy_files_to_clipboard([temp_path])
        if success:
            return (True, f"临时文件已创建并复制: {temp_path}")
        else:
            return (False, f"复制文件到剪贴板失败: {msg}")
    except Exception as e:
        return (False, f"从二进制数据复制文件失败: {str(e)}")

def copy_file_to_clipboard_from_base64(base64_data: str, filename: str, temp_dir: str = None) -> Tuple[bool, str]:
    try:
        file_data = base64.b64decode(base64_data)
        return copy_file_to_clipboard_from_binary(file_data, filename, temp_dir)
    except Exception as e:
        return (False, f"从 base64 数据复制文件失败: {str(e)}")


# --- 类型自动识别与读取 ---

def _process_and_copy_url_list(items: List[dict]) -> Tuple[bool, str]:
    """辅助函数：处理含URL或Base64的字典列表，下载并复制为文件。"""
    # 【说明】此函数现在不接受 downloader 作为参数，而是直接使用全局实例。
    if platform.system() != "Windows":
        return (False, "此功能仅支持 Windows 系统")

    temp_file_paths = []
    temp_dir = tempfile.gettempdir()
    
    try:
        for i, item in enumerate(items):
            if not all(k in item for k in ["type", "url", "filename"]):
                return (False, f"列表中的第 {i+1} 个项目缺少 'type', 'url', 或 'filename' 键。")

            url_str = item['url']
            filename = item['filename']
            file_data = b''

            if url_str.startswith(('http://', 'https://')):
                try:
                    # 【修复】使用全局 downloader 实例以利用缓存
                    file_data = downloader.download(url_str)
                    print(f"   Downloading '{filename}' from URL...") # 添加日志以便观察
                except Exception as e:
                    return (False, f"下载文件 '{filename}' 失败: {e}")
            
            elif url_str.startswith('data:'):
                try:
                    _header, encoded_data = url_str.split(',', 1)
                    file_data = base64.b64decode(encoded_data)
                except (ValueError, TypeError) as e:
                    return (False, f"解码 base64 数据 '{filename}' 失败: {e}")
            
            else:
                return (False, f"不支持的 URL 格式: '{url_str[:50]}...'。")

            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            temp_file_paths.append(temp_path)

        if not temp_file_paths:
            return (True, "列表为空或未成功处理任何文件，无需复制。")

        return copy_files_to_clipboard(temp_file_paths)

    except Exception as e:
        return (False, f"处理文件列表时发生未知错误: {e}")

def copy_auto(content: Union[str, bytes, List], **kwargs) -> Tuple[bool, str]:
    """【修改】自动识别内容类型并复制到剪贴板。"""
    # ... (函数体前半部分不变) ...
    if isinstance(content, str):
        if os.path.exists(content):
            _, ext = os.path.splitext(content.lower())
            if ext in SUPPORTED_IMAGE_EXTENSIONS:
                return set_clipboard_image(content)
            else:
                return copy_files_to_clipboard([content])
        else:
            return set_clipboard_text(content)
    
    elif isinstance(content, bytes):
        try:
            Image.open(io.BytesIO(content))
            is_image = True
        except Exception:
            is_image = False
        
        if is_image:
            return copy_image_to_clipboard_from_binary(content)
        else:
            filename = kwargs.get('filename')
            if filename:
                return copy_file_to_clipboard_from_binary(content, filename)
            else:
                return (False, "无法自动识别字节流类型，请提供 'filename' 参数以作为文件复制。")

    elif isinstance(content, list):
        if not content:
            return (True, "列表为空，无需操作。")
        
        if all(isinstance(item, str) for item in content):
            return copy_files_to_clipboard(content)
        elif all(isinstance(item, dict) for item in content):
            # 【修复】调用内部函数，该函数会使用全局 downloader
            return _process_and_copy_url_list(content)
        else:
            return (False, "列表内容不统一，必须全部为字符串（文件路径）或全部为字典。")
            
    else:
        return (False, f"不支持的内容类型: {type(content)}")


def get_clipboard_content() -> Tuple[Union[str, None], Union[str, list, bytes, None]]:
    """智能检测并获取剪贴板内容（文本、图片或文件）。"""
    if platform.system() != "Windows":
        try:
            text = pyperclip.paste()
            return ('text', text) if text else ('unknown', None)
        except pyperclip.PyperclipException:
            return ('unknown', None)

    opened = False
    try:
        _open_clipboard_with_retry()
        opened = True
        
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            data = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return ('files', list(data))
        
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
            dib_data = win32clipboard.GetClipboardData(win32con.CF_DIB)
            try:
                bmp_header = b'BM' + struct.pack('<I', len(dib_data) + 14) + b'\x00\x00\x00\x00\x36\x00\x00\x00'
                image = Image.open(io.BytesIO(bmp_header + dib_data))
                output = io.BytesIO()
                image.save(output, 'PNG')
                return ('image_binary', output.getvalue())
            except Exception:
                pass
        
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            return ('text', text)
        
        return ('unknown', None)
    
    except Exception:
        return ('unknown', None)
    finally:
        # 【修复】仅在成功打开后才关闭
        if opened:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass


# --- 测试代码 ---
if __name__ == "__main__":
    import time
    
    # 仅在 Windows 上运行完整测试
    if platform.system() != 'Windows':
        print("此测试脚本的完整功能仅在 Windows 上受支持。")
        exit()

    # --- 创建测试文件 ---
    TEST_TEXT = "Hello, Clipboard! This is a test."
    TEST_TXT_FILENAME = "clipboard_test_file.txt"
    TEST_PNG_FILENAME = "clipboard_test_image.png"
    TEST_BIN_FILENAME = "clipboard_test_data.bin"
    TEST_BIN_CONTENT = b'\x01\x02\x03\xDE\xAD\xBE\xEF'
    TEST_IMAGE_BYTES = None

    print("--- Setting up test files ---")
    with open(TEST_TXT_FILENAME, "w", encoding="utf-8") as f:
        f.write(TEST_TEXT)
    print(f"Created: {TEST_TXT_FILENAME}")

    try:
        img = Image.new('RGB', (200, 100), color='red')
        img.save(TEST_PNG_FILENAME)
        print(f"Created: {TEST_PNG_FILENAME}")
        with open(TEST_PNG_FILENAME, 'rb') as f:
            TEST_IMAGE_BYTES = f.read()
    except Exception as e:
        print(f"Could not create test image: {e}")
        TEST_PNG_FILENAME = None

    print("\n--- Starting Clipboard Tests ---")
    
    # 1. 测试复制纯文本
    print("\n1. Testing Text Copy...")
    original_clipboard = save_clipboard()
    success, message = copy_auto(TEST_TEXT)
    print(f"   Success: {success}, Message: {message}")
    if success:
        content_type, content = get_clipboard_content()
        print(f"   Read back type: '{content_type}', Content match: {content == TEST_TEXT}")
    time.sleep(1)
    restore_clipboard(original_clipboard)

    if TEST_PNG_FILENAME:
        # 2. 测试通过路径复制图片
        print("\n2. Testing Image Copy (from path)...")
        original_clipboard = save_clipboard()
        success, message = copy_auto(TEST_PNG_FILENAME)
        print(f"   Success: {success}, Message: {message}")
        if success:
            content_type, content = get_clipboard_content()
            print(f"   Read back type: '{content_type}', Content is bytes: {isinstance(content, bytes)}")
        time.sleep(1)
        restore_clipboard(original_clipboard)
    
    if TEST_IMAGE_BYTES:
        # 3. 测试通过二进制数据复制图片
        print("\n3. Testing Image Copy (from bytes)...")
        original_clipboard = save_clipboard()
        success, message = copy_auto(TEST_IMAGE_BYTES)
        print(f"   Success: {success}, Message: {message}")
        if success:
            content_type, content = get_clipboard_content()
            print(f"   Read back type: '{content_type}', Content is bytes: {isinstance(content, bytes)}")
        time.sleep(1)
        restore_clipboard(original_clipboard)

    # 4. 测试通过路径复制单个文件
    print("\n4. Testing Single File Copy (from path)...")
    original_clipboard = save_clipboard()
    success, message = copy_auto(TEST_TXT_FILENAME)
    print(f"   Success: {success}, Message: {message}")
    if success:
        content_type, content = get_clipboard_content()
        expected_path = os.path.abspath(TEST_TXT_FILENAME)
        print(f"   Read back type: '{content_type}', Content match: {isinstance(content, list) and content[0] == expected_path}")
    time.sleep(1)
    restore_clipboard(original_clipboard)

    # 5. 测试通过二进制数据复制文件（需要提供filename）
    print("\n5. Testing File Copy (from bytes with filename)...")
    original_clipboard = save_clipboard()
    success, message = copy_auto(TEST_BIN_CONTENT, filename=TEST_BIN_FILENAME)
    print(f"   Success: {success}, Message: {message}")
    if success:
        content_type, content = get_clipboard_content()
        temp_file_path = message.split(": ")[-1]
        print(f"   Read back type: '{content_type}', Content match: {isinstance(content, list) and content[0] == temp_file_path}")
    time.sleep(1)
    restore_clipboard(original_clipboard)

    if TEST_PNG_FILENAME:
        # 6. 测试复制多个文件
        print("\n6. Testing Multiple Files Copy (from paths)...")
        original_clipboard = save_clipboard()
        files_to_copy = [TEST_TXT_FILENAME, TEST_PNG_FILENAME]
        success, message = copy_auto(files_to_copy)
        print(f"   Success: {success}, Message: {message}")
        if success:
            content_type, content = get_clipboard_content()
            expected_paths = sorted([os.path.abspath(p) for p in files_to_copy])
            print(f"   Read back type: '{content_type}', Content match: {isinstance(content, list) and sorted(content) == expected_paths}")
        time.sleep(1)
        restore_clipboard(original_clipboard)
    
        # 7. 【修改】测试从URL和Base64混合复制，并验证缓存
        print("\n7. Testing Mixed Copy (from URL/Base64) & Caching...")
        if requests is None:
            print("   Skipping test: 'requests' library not installed.")
        else:
            # 准备下载器和测试数据
            downloader = FileDownloader(cache_duration=300) # 5分钟缓存
            downloader.clear_cache() # 确保开始时缓存是空的

            base64_gif_data = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
            base64_gif_filename = "red_pixel.gif"
            http_image_url = "https://via.placeholder.com/150"
            http_image_filename = "placeholder_150.png"
            
            test_payload = [
                {"type": "images", "url": base64_gif_data, "filename": base64_gif_filename},
                {"type": "file", "url": http_image_url, "filename": http_image_filename},
            ]
            files_to_clean = [base64_gif_filename, http_image_filename]

            # 第一次复制（应该会下载）
            print("\n   --- First attempt (should download from web) ---")
            original_clipboard = save_clipboard()
            # 注意: copy_auto 内部会创建自己的 downloader 实例
            success, message = copy_auto(test_payload)
            print(f"   Success: {success}, Message: {message}")
            restore_clipboard(original_clipboard)
            time.sleep(1)

            # 第二次复制（应该会从缓存加载）
            print("\n   --- Second attempt (should load from cache) ---")
            original_clipboard = save_clipboard()
            # 我们再次调用 copy_auto，它会创建新的 downloader，但会使用相同的缓存目录
            success, message = copy_auto(test_payload)
            print(f"   Success: {success}, Message: {message}")
            restore_clipboard(original_clipboard)

            # 清理此测试创建的临时文件
            temp_dir = tempfile.gettempdir()
            for f_name in files_to_clean:
                path_to_remove = os.path.join(temp_dir, f_name)
                if os.path.exists(path_to_remove):
                    os.remove(path_to_remove)
            
            # 清理下载缓存
            downloader.clear_cache()
    # --- 清理测试文件 ---
    print("\n--- Cleaning up test files ---")
    if os.path.exists(TEST_TXT_FILENAME):
        os.remove(TEST_TXT_FILENAME)
        print(f"Removed: {TEST_TXT_FILENAME}")
    if TEST_PNG_FILENAME and os.path.exists(TEST_PNG_FILENAME):
        os.remove(TEST_PNG_FILENAME)
        print(f"Removed: {TEST_PNG_FILENAME}")
    temp_bin_path = os.path.join(tempfile.gettempdir(), TEST_BIN_FILENAME)
    if os.path.exists(temp_bin_path):
        os.remove(temp_bin_path)
        print(f"Removed temporary file: {temp_bin_path}")