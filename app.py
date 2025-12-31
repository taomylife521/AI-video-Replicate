"""
视频生成 Gradio 前端界面 (远程API版)
支持 Seedance 和 Sora2 两种模型提供者
支持文生视频和图生视频两种模式

调用远程 API 服务，无需本地启动 API 服务器
"""

import os
import re
import time
import tempfile
import httpx
import ssl
import base64
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
from qwen3vl import analyze_video

load_dotenv()

# ========== Seedance API 配置 ==========
SEEDANCE_API_BASE_URL = os.getenv("SEEDANCE_API_BASE_URL", "https://seedanceapi.duckcloud.fun")
SEEDANCE_AUTH_TOKEN = os.getenv("SEEDANCE_AUTH_TOKEN", "sk-doubao-video-2025")

# ========== Sora2 API 配置 ==========
SORA2_API_BASE_URL = os.getenv("SORA2_API_BASE_URL", "https://api.jxincm.cn")
SORA2_API_KEY = os.getenv("SORA2_API_KEY", "")
SORA2_ENABLED = os.getenv("SORA2_ENABLED", "true").lower() == "true"

# ========== Sora2免费 API 配置 ==========
SORA2FREE_API_BASE_URL = os.getenv("SORA2FREE_API_BASE_URL", "https://rendersora2api.duckcloud.fun")
SORA2FREE_API_KEY = os.getenv("SORA2FREE_API_KEY", "")

# 兼容旧配置
if not SEEDANCE_AUTH_TOKEN:
    SEEDANCE_AUTH_TOKEN = os.getenv("AUTH_TOKEN", "sk-doubao-video-2025")
if not SEEDANCE_API_BASE_URL:
    SEEDANCE_API_BASE_URL = os.getenv("API_BASE_URL", "https://seedanceapi.duckcloud.fun")


def get_seedance_auth_headers() -> dict:
    """获取 Seedance 包含鉴权信息的请求头"""
    headers = {}
    if SEEDANCE_AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {SEEDANCE_AUTH_TOKEN}"
    return headers


def get_sora2_auth_headers() -> dict:
    """获取 Sora2 包含鉴权信息的请求头"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if SORA2_API_KEY:
        headers["Authorization"] = f"Bearer {SORA2_API_KEY}"
    return headers


def _get_content_type(suffix: str) -> str:
    """获取文件MIME类型"""
    content_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp"
    }
    return content_types.get(suffix.lower(), "application/octet-stream")


def request_with_retry(method, url, max_retries=3, timeout=60.0, **kwargs):
    """带重试机制的请求函数，专门处理 SSL、协议错误和重定向"""
    last_error = None
    
    # 尝试多种配置组合
    configs = [
        {"http2": False, "verify": True},  # 标准配置
        {"http2": False, "verify": False}, # 禁用验证 (应对证书问题)
    ]
    
    # 规范化 URL，确保没有重复的斜杠
    if "://" in url:
        parts = url.split("://", 1)
        url = f"{parts[0]}://{parts[1].replace('//', '/')}"

    for config in configs:
        for attempt in range(max_retries):
            try:
                with httpx.Client(
                    timeout=timeout,
                    http2=config["http2"],
                    verify=config["verify"],
                    follow_redirects=True
                ) as client:
                    response = client.request(method, url, **kwargs)
                    
                    # 检查重定向 (httpx follow_redirects=True 会自动处理，但 POST 可能变 GET)
                    # 如果返回 302 且我们想要 POST，我们需要确认是否变成了 GET
                    if response.status_code == 302 and method == "POST":
                        print(f"[API] POST 请求被重定向 (302)，请检查 API 地址是否正确: {url}")
                    
                    # 如果响应状态码不是 2xx，记录更多信息
                    if response.status_code >= 400:
                        print(f"[API] 请求失败: HTTP {response.status_code} - {response.text[:200]}")
                        response.raise_for_status()
                        
                    return response.json()
            except (httpx.HTTPError, ssl.SSLError, Exception) as e:
                last_error = e
                # 如果是 SSL 错误且当前验证为 True，则跳出重试循环，尝试下一个配置
                if isinstance(e, (ssl.SSLError, httpx.ConnectError)) and config["verify"]:
                    print(f"[API] SSL/连接错误，将尝试备选配置: {str(e)}")
                    break
                
                # 处理 302 特殊情况：如果 response 存在且是 302
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 302:
                    print(f"[API] 捕获到 302 重定向错误: {e.response.headers.get('Location')}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"[API] 请求失败 ({type(e).__name__}: {str(e)})，正在进行第 {attempt + 2} 次重试 (等待 {wait_time}s)...")
                    time.sleep(wait_time)
                else:
                    print(f"[API] 第 {attempt + 1} 次尝试失败，已达到最大重试次数")
                    
    # 如果所有尝试都失败了
    raise last_error


# ========== 模型提供者选项 ==========
PROVIDER_OPTIONS = ["seedance", "sora2", "sora2free"]

# ========== Seedance 模型选项 ==========
SEEDANCE_MODEL_OPTIONS = [
    ("seedance-1-5-pro-251215 (最新)", "seedance-1-5-pro-251215"),
    ("seedance-1-0-pro-fast (快速)", "seedance-1-0-pro-fast"),
]

# Seedance 时长选项
SEEDANCE_DURATION_OPTIONS = [4, 5, 8, 12]

# Seedance 比例选项
SEEDANCE_RATIO_OPTIONS = [
    ("21:9 (超宽银幕)", "21:9"),
    ("16:9 (横屏·默认)", "16:9"),
    ("4:3 (经典比例)", "4:3"),
    ("1:1 (正方形)", "1:1"),
    ("3:4 (竖屏偏方)", "3:4"),
    ("9:16 (竖屏·抖音/Shorts)", "9:16"),
]

# ========== Sora2 模型选项 ==========
SORA2_MODEL_OPTIONS = [
    ("sora-2", "sora-2"),
]

# Sora2 时长选项
SORA2_DURATION_OPTIONS = [10, 15]

# Sora2 比例选项 (orientation)
SORA2_RATIO_OPTIONS = [
    ("portrait (竖屏)", "portrait"),
    ("landscape (横屏)", "landscape"),
]

# ========== Sora2免费 模型选项 ==========
SORA2FREE_MODEL_OPTIONS = [
    ("sora2-landscape-10s (横屏10秒)", "sora2-landscape-10s"),
    ("sora2-landscape-15s (横屏15秒)", "sora2-landscape-15s"),
    ("sora2-portrait-10s (竖屏10秒)", "sora2-portrait-10s"),
    ("sora2-portrait-15s (竖屏15秒)", "sora2-portrait-15s"),
]


def upload_image(file_path: str) -> dict:
    """
    上传图片到 Seedance 远程API服务
    """
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "message": f"图片文件不存在: {file_path}"}

    try:
        with open(path, "rb") as f:
            files = {"file": (path.name, f, _get_content_type(path.suffix))}
            return request_with_retry(
                "POST",
                f"{SEEDANCE_API_BASE_URL}/api/upload/",
                files=files,
                headers=get_seedance_auth_headers(),
                timeout=60.0
            )
    except Exception as e:
        return {"success": False, "message": f"上传失败: {str(e)}"}


def create_seedance_video(prompt: str, model: str, duration: int, ratio: str, image_url: str = None) -> dict:
    """
    创建 Seedance 视频任务
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "ratio": ratio
    }
    if image_url:
        payload["image"] = image_url

    try:
        return request_with_retry(
            "POST",
            f"{SEEDANCE_API_BASE_URL}/api/video/create/",
            json=payload,
            headers=get_seedance_auth_headers(),
            timeout=120.0
        )
    except Exception as e:
        return {"success": False, "message": f"创建视频失败: {str(e)}"}


def get_seedance_videos() -> list:
    """
    获取 Seedance 视频列表
    """
    try:
        result = request_with_retry(
            "GET",
            f"{SEEDANCE_API_BASE_URL}/api/videos/",
            headers=get_seedance_auth_headers(),
            timeout=30.0
        )
        if result.get("success"):
            return result.get("data", [])
        return []
    except Exception as e:
        print(f"[API] 获取视频列表失败: {e}")
        return []


def find_seedance_video_by_task_id(task_id: str) -> dict:
    """
    根据task_id从 Seedance 视频列表中查找视频
    参考 client.py 中的 find_video_by_task_id 方法
    """
    videos = get_seedance_videos()
    if not videos:
        return None

    # 提取核心task_id（去掉 ::model 后缀）
    core_task_id = task_id.split("::")[0] if "::" in task_id else task_id

    for video in videos:
        vid_task_id = video.get("taskId") or video.get("task_id") or ""
        vid_id = str(video.get("id", ""))

        # 精确匹配
        if task_id == vid_task_id or task_id == vid_id:
            return video

        # 核心ID匹配
        if core_task_id == vid_task_id or core_task_id == vid_id:
            return video

        # 部分匹配
        if vid_task_id and core_task_id in vid_task_id:
            return video
        if core_task_id and vid_task_id and vid_task_id in core_task_id:
            return video

    return None


# ========== Sora2 API 函数 ==========

def upload_image_to_url(file_path: str) -> str:
    """
    将本地图片转换为 base64 data URL 或上传到图床
    Sora2 需要图片 URL，这里使用 base64 data URL
    """
    path = Path(file_path)
    if not path.exists():
        return None

    try:
        with open(path, "rb") as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            content_type = _get_content_type(path.suffix)
            return f"data:{content_type};base64,{base64_data}"
    except Exception as e:
        print(f"[Sora2] 图片转换失败: {e}")
        return None


def create_sora2_video(prompt: str, model: str, duration: int, orientation: str, image_urls: list = None) -> dict:
    """
    创建 Sora2 视频任务

    Args:
        prompt: 视频描述提示词
        model: 模型名称 (sora-2)
        duration: 视频时长 (10 或 15 秒)
        orientation: 屏幕方向 (portrait 或 landscape)
        image_urls: 图片URL列表 (图生视频模式)

    Returns:
        API 响应字典
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "orientation": orientation,
        "size": "large",
        "watermark": False,
        "private": True,
        "images": image_urls if image_urls else []
    }

    try:
        print(f"[Sora2] 发送请求: {SORA2_API_BASE_URL}/v1/video/create")
        print(f"[Sora2] 参数: model={model}, duration={duration}, orientation={orientation}")

        result = request_with_retry(
            "POST",
            f"{SORA2_API_BASE_URL}/v1/video/create",
            json=payload,
            headers=get_sora2_auth_headers(),
            timeout=120.0
        )

        # Sora2 返回格式转换为统一格式
        if result.get("id"):
            return {
                "success": True,
                "data": {
                    "task": {
                        "task_id": result.get("id")
                    },
                    "status": result.get("status"),
                    "model": result.get("model")
                }
            }
        return {"success": False, "message": "创建任务失败，未获取到任务ID"}

    except Exception as e:
        return {"success": False, "message": f"创建Sora2视频失败: {str(e)}"}


def query_sora2_video(task_id: str) -> dict:
    """
    查询 Sora2 视频任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态字典
    """
    try:
        result = request_with_retry(
            "GET",
            f"{SORA2_API_BASE_URL}/v1/video/query?id={task_id}",
            headers=get_sora2_auth_headers(),
            timeout=30.0
        )
        return result
    except Exception as e:
        print(f"[Sora2] 查询任务失败: {e}")
        return None


# ========== Sora2免费 API 函数 ==========

def get_sora2free_auth_headers() -> dict:
    """获取 Sora2免费 包含鉴权信息的请求头"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SORA2FREE_API_KEY}"
    }
    return headers


def create_sora2free_video(prompt: str, model: str) -> dict:
    """
    创建 Sora2免费 视频任务 (SSE 流式响应)

    Args:
        prompt: 视频描述提示词
        model: 模型名称

    Returns:
        包含视频URL的字典
    """
    if not SORA2FREE_API_KEY:
        return {"success": False, "message": "Sora2免费 API Key 未配置"}

    try:
        import re

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": True
        }

        url = f"{SORA2FREE_API_BASE_URL}/v1/chat/completions"

        print(f"[Sora2免费] 发送请求: {url}")
        print(f"[Sora2免费] 模型: {model}")

        # 发送 SSE 请求
        with httpx.Client(timeout=300.0) as client:
            with client.stream(
                "POST",
                url,
                json=payload,
                headers=get_sora2free_auth_headers()
            ) as response:
                if response.status_code != 200:
                    error_text = response.text[:500] if response.text else "无响应内容"
                    return {"success": False, "message": f"请求失败: HTTP {response.status_code}\n{error_text}"}

                # 解析 SSE 流，提取视频URL
                video_url = None
                full_content = ""

                for line in response.iter_lines():
                    if line:
                        # SSE 格式: data: {...}
                        line = line.decode('utf-8') if isinstance(line, bytes) else line
                        if line.startswith('data: '):
                            data = line[6:]  # 去掉 'data: '
                            if data == '[DONE]':
                                break
                            try:
                                import json as json_module
                                chunk = json_module.loads(data)
                                delta = chunk.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_content += content
                                    # 从 HTML 格式提取视频URL
                                    # 格式: ```html\n<video src='https://xxx.mp4' controls></video>\n```
                                    video_match = re.search(r"src='(https?://[^']+\.mp4)'", content)
                                    if video_match:
                                        video_url = video_match.group(1)
                                        print(f"[Sora2免费] ✅ 提取到视频URL: {video_url}")
                            except json_module.JSONDecodeError:
                                continue

                if video_url:
                    return {"success": True, "video_url": video_url, "raw_content": full_content}
                else:
                    return {"success": False, "message": "未在响应中提取到视频URL", "raw_content": full_content}

    except httpx.TimeoutException:
        return {"success": False, "message": "请求超时"}
    except Exception as e:
        return {"success": False, "message": f"请求失败: {str(e)}"}


def generate_sora2free_video(prompt: str, model: str):
    """生成 Sora2免费 视频"""
    if not prompt or not prompt.strip():
        return None, "❌ 请输入视频描述提示词"

    if not SORA2FREE_API_KEY:
        return None, "❌ Sora2免费 API Key 未配置"

    try:
        print(f"[Sora2免费] 🎬 正在提交文生视频任务...")

        create_result = create_sora2free_video(prompt, model)

        if not create_result.get("success"):
            return None, f"❌ {create_result.get('message', '未知错误')}"

        video_url = create_result.get("video_url")
        if video_url:
            print(f"[Sora2免费] 📎 视频URL: {video_url}")
            # 下载视频到本地
            local_path = download_video_to_local(video_url, use_seedance_proxy=False)
            if local_path:
                return local_path, f"✅ Sora2免费视频生成成功!\n📎 视频URL: {video_url}\n💡 已下载到本地"
            else:
                return None, f"⚠️ 视频生成成功但下载失败\n📎 视频URL: {video_url}\n请复制链接手动下载"
        else:
            return None, f"⚠️ 未获取到视频URL"

    except Exception as e:
        return None, f"❌ 发生错误: {str(e)}"


def download_video_to_local(video_url: str, use_seedance_proxy: bool = True) -> str:
    """
    下载视频到本地临时文件
    参考 client.py 中的 download_video 方法

    优先使用代理下载，解决国内网络无法直接访问外网视频URL的问题

    Args:
        video_url: 视频URL
        use_seedance_proxy: 是否使用 Seedance 代理 (仅对 Seedance 视频有效)
    """
    if not video_url:
        return None

    try:
        print(f"[Gradio] 📥 正在下载视频到本地...")

        # 检查是否需要使用代理（外网视频域名）
        proxy_domains = [
            "ark-content-generation",
            "tos-ap-southeast",
            "volces.com"
        ]
        use_proxy = use_seedance_proxy and any(domain in video_url for domain in proxy_domains)

        if use_proxy:
            # 使用代理URL下载
            download_url = f"{SEEDANCE_API_BASE_URL}/proxy/{video_url}"
            print(f"[Gradio] 🔄 使用代理下载: {SEEDANCE_API_BASE_URL}/proxy/...")
        else:
            download_url = video_url

        # 使用较长的超时时间，视频文件可能较大
        try:
            # 同样尝试多种配置
            configs = [
                {"http2": False, "verify": True},
                {"http2": False, "verify": False},
            ]
            
            response = None
            last_err = None
            
            for config in configs:
                try:
                    with httpx.Client(
                        timeout=300.0, 
                        follow_redirects=True,
                        http2=config["http2"],
                        verify=config["verify"]
                    ) as client:
                        response = client.get(download_url)
                        response.raise_for_status()
                        break
                except Exception as e:
                    last_err = e
                    if config["verify"]: continue
                    else: raise e

            if response and response.status_code == 200:
                # 获取文件扩展名
                content_type = response.headers.get("content-type", "")
                if "mp4" in content_type or video_url.endswith(".mp4"):
                    suffix = ".mp4"
                elif "webm" in content_type or video_url.endswith(".webm"):
                    suffix = ".webm"
                else:
                    suffix = ".mp4"  # 默认mp4

                # 创建临时文件
                fd, temp_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(fd, 'wb') as f:
                    f.write(response.content)

                file_size = len(response.content) / (1024 * 1024)  # MB
                print(f"[Gradio] ✅ 视频下载完成: {temp_path} ({file_size:.2f} MB)")
                return temp_path
            else:
                print(f"[Gradio] ❌ 视频下载失败: HTTP {response.status_code}")
                return None

        except httpx.TimeoutException:
            print(f"[Gradio] ❌ 视频下载超时")
            return None
        except Exception as e:
            print(f"[Gradio] ❌ 视频下载失败: {e}")
            return None

    except Exception as e:
        print(f"[Gradio] ❌ 视频下载过程发生异常: {e}")
        return None


def generate_seedance_video(prompt: str, model: str, duration: int, ratio: str, image=None):
    """生成 Seedance 视频 - 包含轮询等待逻辑"""
    if not prompt or not prompt.strip():
        return None, "❌ 请输入视频描述提示词"

    # 确保提示词中的参数与 UI 选择一致，防止提示词自带的参数覆盖 UI 选择
    # 移除可能存在的旧参数 (兼容 -duration=8 或 -ratio=16:9 格式)
    prompt = re.sub(r'\s*-duration=\d+', '', prompt)
    prompt = re.sub(r'\s*-ratio=[\d:]+', '', prompt)
    # 追加当前 UI 选择的参数到提示词末尾
    prompt = f"{prompt.strip()} -duration={duration} -ratio={ratio}"

    max_wait_seconds = 600  # 最大等待10分钟
    poll_interval = 10  # 每10秒轮询一次

    try:
        # 如果有图片，先上传
        image_url = None
        if image is not None:
            print("[Seedance] 📤 正在上传图片...")
            upload_result = upload_image(image)
            if not upload_result.get("success"):
                return None, f"❌ 图片上传失败: {upload_result.get('message', '未知错误')}"
            image_url = upload_result.get("url")
            if not image_url:
                return None, "❌ 上传成功但未获取到图片URL"
            print(f"[Seedance] ✅ 图片上传成功: {image_url}")

        # 创建视频任务
        mode = "图生视频" if image_url else "文生视频"
        print(f"[Seedance] 🎬 正在提交{mode}任务到远程服务器...")

        create_result = create_seedance_video(prompt, model, duration, ratio, image_url)

        if not create_result.get("success"):
            return None, f"❌ 创建任务失败: {create_result.get('message', '未知错误')}"

        # 提取task_id
        task_data = create_result.get("data", {})
        task = task_data.get("task", {})
        task_id = task.get("task_id") or task_data.get("taskId") or task_data.get("task_id") or task_data.get("id")

        if not task_id:
            return None, f"⚠️ 任务已提交({mode})，但无法获取任务ID，请稍后手动查询"

        print(f"[Seedance] ✅ 任务创建成功! 任务ID: {task_id}")

        # 轮询等待视频生成完成
        start_time = time.time()
        elapsed = 0
        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        while elapsed < max_wait_seconds:
            # 查找视频
            video = find_seedance_video_by_task_id(task_id)

            if video:
                status = (video.get("status") or "").lower()
                video_url = video.get("url") or video.get("videoUrl") or video.get("video_url")

                # 检查完成状态
                if status in ["completed", "success", "done", "finished", "succeeded"]:
                    print(f"[Seedance] 🎉 视频生成完成!")
                    if video_url:
                        print(f"[Seedance] 📎 视频远程地址: {video_url}")
                        # 下载视频到本地，避免Gradio直接访问外网URL导致DNS解析失败
                        local_path = download_video_to_local(video_url, use_seedance_proxy=True)
                        if local_path:
                            return local_path, f"✅ 视频生成成功! ({mode})\n⏱️ 耗时: {int(elapsed)}秒\n🔗 远程服务: {SEEDANCE_API_BASE_URL}\n📎 视频URL: {video_url}\n💡 已通过代理下载到本地"
                        else:
                            # 下载失败时返回代理URL供用户手动下载
                            proxy_url = f"{SEEDANCE_API_BASE_URL}/proxy/{video_url}"
                            return None, f"⚠️ 视频生成完成但下载失败\n📎 原始URL: {video_url}\n🔗 代理URL: {proxy_url}\n请复制代理链接手动下载"
                    else:
                        return None, f"⚠️ 视频生成完成但未获取到URL"

                # 检查失败状态
                if status in ["failed", "error", "failure"]:
                    error_msg = video.get("error") or video.get("message") or "未知错误"
                    return None, f"❌ 视频生成失败: {error_msg}"

            # 更新进度
            elapsed = time.time() - start_time
            idx = int(elapsed / poll_interval) % len(progress_chars)
            print(f"[Seedance] {progress_chars[idx]} 视频生成中... 已等待 {int(elapsed)}秒")

            # 等待下次轮询
            time.sleep(poll_interval)

        # 超时
        return None, f"⏰ 等待超时({max_wait_seconds}秒)，任务ID: {task_id}\n请稍后使用任务ID查询结果"

    except httpx.ConnectError:
        return None, f"❌ 无法连接到远程API服务器: {SEEDANCE_API_BASE_URL}\n请检查网络连接和服务器状态"
    except Exception as e:
        return None, f"❌ 发生错误: {str(e)}"


def generate_sora2_video_task(prompt: str, model: str, duration: int, orientation: str, image=None):
    """生成 Sora2 视频 - 包含轮询等待逻辑"""
    if not prompt or not prompt.strip():
        return None, "❌ 请输入视频描述提示词"

    max_wait_seconds = 900  # Sora2 可能需要更长时间，最大等待15分钟
    poll_interval = 15  # 每15秒轮询一次

    try:
        # 如果有图片，转换为URL
        image_urls = []
        if image is not None:
            print("[Sora2] 📤 正在处理图片...")
            image_url = upload_image_to_url(image)
            if not image_url:
                return None, "❌ 图片处理失败"
            image_urls.append(image_url)
            print(f"[Sora2] ✅ 图片处理成功")

        # 创建视频任务
        mode = "图生视频" if image_urls else "文生视频"
        print(f"[Sora2] 🎬 正在提交{mode}任务到远程服务器...")

        create_result = create_sora2_video(prompt, model, duration, orientation, image_urls)

        if not create_result.get("success"):
            return None, f"❌ 创建任务失败: {create_result.get('message', '未知错误')}"

        # 提取task_id
        task_data = create_result.get("data", {})
        task = task_data.get("task", {})
        task_id = task.get("task_id") or task_data.get("taskId") or task_data.get("task_id") or task_data.get("id")

        if not task_id:
            return None, f"⚠️ 任务已提交({mode})，但无法获取任务ID，请稍后手动查询"

        print(f"[Sora2] ✅ 任务创建成功! 任务ID: {task_id}")

        # 轮询等待视频生成完成
        start_time = time.time()
        elapsed = 0
        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        while elapsed < max_wait_seconds:
            # 查询任务状态
            video = query_sora2_video(task_id)

            if video:
                status = (video.get("status") or "").lower()
                video_url = video.get("video_url") or video.get("videoUrl") or video.get("url")
                progress = video.get("progress", 0)

                # 检查完成状态
                if status in ["completed", "success", "done", "finished", "succeeded"]:
                    print(f"[Sora2] 🎉 视频生成完成!")
                    if video_url:
                        print(f"[Sora2] 📎 视频远程地址: {video_url}")
                        # Sora2 视频不需要代理
                        local_path = download_video_to_local(video_url, use_seedance_proxy=False)
                        if local_path:
                            return local_path, f"✅ 视频生成成功! ({mode})\n⏱️ 耗时: {int(elapsed)}秒\n🔗 远程服务: {SORA2_API_BASE_URL}\n📎 视频URL: {video_url}\n💡 已下载到本地"
                        else:
                            return None, f"⚠️ 视频生成完成但下载失败\n📎 视频URL: {video_url}\n请复制链接手动下载"
                    else:
                        return None, f"⚠️ 视频生成完成但未获取到URL"

                # 检查失败状态
                if status in ["failed", "error", "failure"]:
                    error_msg = video.get("error") or video.get("message") or video.get("detail", {}).get("message") or "未知错误"
                    return None, f"❌ 视频生成失败: {error_msg}"

                # 显示进度
                if progress > 0:
                    print(f"[Sora2] 📊 进度: {progress}%")

            # 更新进度
            elapsed = time.time() - start_time
            idx = int(elapsed / poll_interval) % len(progress_chars)
            print(f"[Sora2] {progress_chars[idx]} 视频生成中... 已等待 {int(elapsed)}秒")

            # 等待下次轮询
            time.sleep(poll_interval)

        # 超时
        return None, f"⏰ 等待超时({max_wait_seconds}秒)，任务ID: {task_id}\n请稍后使用任务ID查询结果"

    except httpx.ConnectError:
        return None, f"❌ 无法连接到远程API服务器: {SORA2_API_BASE_URL}\n请检查网络连接和服务器状态"
    except Exception as e:
        return None, f"❌ 发生错误: {str(e)}"


def generate_video(provider: str, prompt: str, model: str, duration: int, ratio: str, image=None):
    """统一的视频生成入口函数"""
    if provider == "sora2":
        return generate_sora2_video_task(prompt, model, duration, ratio, image)
    elif provider == "sora2free":
        # Sora2免费 只支持文生视频，不支持图片
        return generate_sora2free_video(prompt, model)
    else:
        return generate_seedance_video(prompt, model, duration, ratio, image)


# ========== 样例视频配置 ==========
SAMPLE_VIDEO_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "sample", "video.mp4")
)


def load_sample_video():
    """加载样例视频到视频复刻区域"""
    if os.path.exists(SAMPLE_VIDEO_PATH):
        return SAMPLE_VIDEO_PATH
    else:
        return None


def extract_prompt_from_video(video_path):
    """从视频中提取提示词"""
    if not video_path:
        return "❌ 请先上传视频", ""
    try:
        print(f"[Gradio] 🔍 正在分析视频提取提示词: {video_path}")
        result = analyze_video(video_path, sora2_mode=True, stream=False)
        
        # 提取英文提示词用于生成
        en_match = re.search(r'## SORA2 Prompt \(English\)\s*```\s*(.*?)\s*```', result, re.DOTALL)
        en_prompt = en_match.group(1).strip() if en_match else ""
        
        # 如果没提取到英文，尝试提取中文
        if not en_prompt:
            zh_match = re.search(r'## SORA2 提示词 \(中文\)\s*```\s*(.*?)\s*```', result, re.DOTALL)
            en_prompt = zh_match.group(1).strip() if zh_match else ""
            
        return result, en_prompt
    except Exception as e:
        return f"❌ 提示词提取失败: {str(e)}", ""


# 构建Gradio界面
def create_ui():
    with gr.Blocks(
        title="视频生成 - Seedance & Sora2 & Sora2免费"
    ) as demo:

        # 头部
        gr.Markdown(f"""
        # 🎬 AI 视频生成
        **支持 Seedance、Sora2 和 Sora2免费 三种模型提供者**

        🔗 Seedance 服务: `{SEEDANCE_API_BASE_URL}`
        🔗 Sora2 服务: `{SORA2_API_BASE_URL}`
        🔗 Sora2免费 服务: `{SORA2FREE_API_BASE_URL}`
        """)

        # 主布局：左侧输入区域，右侧输出区域
        with gr.Row():
            # 左侧：输入参数区域
            with gr.Column(scale=1):
                # 视频复刻功能区
                with gr.Group():
                    gr.Markdown("### 📹 视频复刻 (上传视频提取提示词)")
                    with gr.Row():
                        source_video = gr.Video(
                            label="上传短视频",
                            sources=["upload"],
                            interactive=True,
                            height=200
                        )
                    # 上传按钮和样例按钮并排
                    with gr.Row():
                        load_sample_btn = gr.Button("📂 加载样例视频", variant="secondary", size="sm")
                        clear_video_btn = gr.Button("🗑️ 清空视频", variant="stop", size="sm")
                    extract_btn = gr.Button("🔍 提取视频提示词", variant="secondary")
                    extraction_result = gr.Textbox(
                        label="提取结果分析",
                        placeholder="提取出的提示词分析将显示在这里...",
                        interactive=False,
                        lines=5
                    )

                # 提示词输入
                gr.Markdown("### ✍️ 视频配置")
                prompt = gr.Textbox(
                    label="提示词 (Prompt)",
                    placeholder="(确认或输入) 描述你想生成的视频内容...",
                    lines=4,
                    max_lines=8
                )
                gr.Markdown("*您可以修改提取出的提示词或直接输入新提示词*")

                # 模型提供者选择
                provider = gr.Radio(
                    label="模型提供者",
                    choices=PROVIDER_OPTIONS,
                    value="seedance",
                    interactive=True
                )

                # Sora2免费 每日免费次数提示
                sora2free_note = gr.Markdown(
                    "📌 **Sora2免费**：每天免费10次，仅支持文生视频",
                    visible=False
                )

                # 模型选择
                model = gr.Dropdown(
                    label="模型 (model)",
                    choices=[m[0] for m in SEEDANCE_MODEL_OPTIONS],
                    value=SEEDANCE_MODEL_OPTIONS[0][0],
                    interactive=True
                )

                # 时长和比例并排
                with gr.Row(visible=True) as duration_ratio_row:
                    # 时长选择
                    with gr.Column(scale=1):
                        duration = gr.Dropdown(
                            label="时长 (duration)",
                            choices=[str(d) for d in SEEDANCE_DURATION_OPTIONS],
                            value="5",
                            interactive=True
                        )
                        # Seedance 快捷按钮组
                        with gr.Row(visible=True) as seedance_duration_btns:
                            btn_4s = gr.Button("4s")
                            btn_5s = gr.Button("5s", variant="primary")
                            btn_8s = gr.Button("8s")
                            btn_12s = gr.Button("12s")
                        # Sora2 快捷按钮组
                        with gr.Row(visible=False) as sora2_duration_btns:
                            btn_10s = gr.Button("10s", variant="primary")
                            btn_15s = gr.Button("15s")

                    # 比例选择
                    with gr.Column(scale=1):
                        ratio = gr.Dropdown(
                            label="比例 (ratio/orientation)",
                            choices=[r[0] for r in SEEDANCE_RATIO_OPTIONS],
                            value=SEEDANCE_RATIO_OPTIONS[1][0],
                            interactive=True
                        )

                # 图片上传(可选) - 显示缩略图
                gr.Markdown("### 视频图片 (Optional)")
                image = gr.Image(
                    label="上传参考图片 (图生视频模式)",
                    type="filepath",
                    sources=["upload"],
                    interactive=True,
                    height=200
                )
                image_note = gr.Markdown("*当前模型最多支持1张参考图*", visible=True)

                # 生成按钮
                gr.Markdown("*提交后请耐心等待，视频生成通常需要1-5分钟*")
                generate_btn = gr.Button("🎬 生成视频", variant="primary")

            # 右侧：输出结果区域
            with gr.Column(scale=1):
                gr.Markdown("### 生成结果")
                video_output = gr.Video(
                    label="生成的视频",
                    interactive=False,
                    height=350
                )
                status_output = gr.Textbox(
                    label="状态信息",
                    interactive=False,
                    lines=6
                )

        # 事件绑定 - 模型提供者切换
        def update_options_for_provider(provider_value):
            """根据提供者更新模型、时长、比例选项"""
            if provider_value == "sora2":
                model_choices = [m[0] for m in SORA2_MODEL_OPTIONS]
                model_value = SORA2_MODEL_OPTIONS[0][0]
                duration_choices = [str(d) for d in SORA2_DURATION_OPTIONS]
                duration_value = "10"
                ratio_choices = [r[0] for r in SORA2_RATIO_OPTIONS]
                ratio_value = SORA2_RATIO_OPTIONS[1][0]  # landscape 默认
                seedance_btns_visible = False
                sora2_btns_visible = True
                image_visible = True
                image_note_visible = True
                duration_ratio_visible = True
                sora2free_note_visible = False
                generate_btn_interactive = SORA2_ENABLED  # 选择 sora2 时根据配置控制按钮
            elif provider_value == "sora2free":
                model_choices = [m[0] for m in SORA2FREE_MODEL_OPTIONS]
                model_value = SORA2FREE_MODEL_OPTIONS[0][0]
                duration_choices = []
                duration_value = None
                ratio_choices = []
                ratio_value = None
                seedance_btns_visible = False
                sora2_btns_visible = False
                image_visible = False  # Sora2免费不支持图生视频
                image_note_visible = False
                duration_ratio_visible = False  # Sora2免费模型名已包含时长和比例
                sora2free_note_visible = True
                generate_btn_interactive = True  # sora2free 始终可用
            else:
                model_choices = [m[0] for m in SEEDANCE_MODEL_OPTIONS]
                model_value = SEEDANCE_MODEL_OPTIONS[0][0]
                duration_choices = [str(d) for d in SEEDANCE_DURATION_OPTIONS]
                duration_value = "5"
                ratio_choices = [r[0] for r in SEEDANCE_RATIO_OPTIONS]
                ratio_value = SEEDANCE_RATIO_OPTIONS[1][0]  # 16:9 默认
                seedance_btns_visible = True
                sora2_btns_visible = False
                image_visible = True
                image_note_visible = True
                duration_ratio_visible = True
                sora2free_note_visible = False
                generate_btn_interactive = True  # seedance 始终可用

            return (
                gr.update(choices=model_choices, value=model_value),
                gr.update(choices=duration_choices, value=duration_value),
                gr.update(choices=ratio_choices, value=ratio_value),
                gr.update(visible=seedance_btns_visible),
                gr.update(visible=sora2_btns_visible),
                gr.update(visible=image_visible),
                gr.update(visible=image_note_visible),
                gr.update(visible=duration_ratio_visible),
                gr.update(visible=sora2free_note_visible),
                gr.update(interactive=generate_btn_interactive)
            )

        provider.change(
            fn=update_options_for_provider,
            inputs=[provider],
            outputs=[model, duration, ratio, seedance_duration_btns, sora2_duration_btns, image, image_note, duration_ratio_row, sora2free_note, generate_btn]
        )

        # 提取提示词
        extract_btn.click(
            fn=extract_prompt_from_video,
            inputs=[source_video],
            outputs=[extraction_result, prompt],
            show_progress=True
        )

        # 加载样例视频
        def handle_load_sample():
            if os.path.exists(SAMPLE_VIDEO_PATH):
                return SAMPLE_VIDEO_PATH, f"✅ 已加载样例视频: {SAMPLE_VIDEO_PATH}"
            else:
                return None, f"❌ 样例视频不存在: {SAMPLE_VIDEO_PATH}"

        load_sample_btn.click(
            fn=handle_load_sample,
            outputs=[source_video, extraction_result],
            show_progress=True
        )

        # 清空视频
        clear_video_btn.click(
            fn=lambda: (None, ""),
            outputs=[source_video, extraction_result]
        )

        # Seedance 时长快捷按钮
        btn_4s.click(fn=lambda: "4", outputs=duration)
        btn_5s.click(fn=lambda: "5", outputs=duration)
        btn_8s.click(fn=lambda: "8", outputs=duration)
        btn_12s.click(fn=lambda: "12", outputs=duration)

        # Sora2 时长快捷按钮
        btn_10s.click(fn=lambda: "10", outputs=duration)
        btn_15s.click(fn=lambda: "15", outputs=duration)

        # 生成视频
        def process_generate(provider_val, prompt_text, model_text, duration_val, ratio_text, image_file):
            if provider_val == "sora2":
                # Sora2: 转换模型名称和比例
                model_value = next((m[1] for m in SORA2_MODEL_OPTIONS if m[0] == model_text), SORA2_MODEL_OPTIONS[0][1])
                ratio_value = next((r[1] for r in SORA2_RATIO_OPTIONS if r[0] == ratio_text), SORA2_RATIO_OPTIONS[0][1])
            elif provider_val == "sora2free":
                # Sora2免费: 转换模型名称
                model_value = next((m[1] for m in SORA2FREE_MODEL_OPTIONS if m[0] == model_text), SORA2FREE_MODEL_OPTIONS[0][1])
                ratio_value = ""
            else:
                # Seedance: 转换模型名称和比例
                model_value = next((m[1] for m in SEEDANCE_MODEL_OPTIONS if m[0] == model_text), SEEDANCE_MODEL_OPTIONS[0][1])
                ratio_value = next((r[1] for r in SEEDANCE_RATIO_OPTIONS if r[0] == ratio_text), SEEDANCE_RATIO_OPTIONS[1][1])

            return generate_video(provider_val, prompt_text, model_value, int(duration_val) if duration_val else 5, ratio_value, image_file)

        generate_btn.click(
            fn=process_generate,
            inputs=[provider, prompt, model, duration, ratio, image],
            outputs=[video_output, status_output],
            show_progress=True
        )

    return demo


if __name__ == "__main__":
    print(f"[Gradio] 🚀 启动 AI 视频生成客户端 (Seedance & Sora2 & Sora2免费)")
    print(f"[Gradio] 🔗 Seedance API: {SEEDANCE_API_BASE_URL}")
    print(f"[Gradio] 🔗 Sora2 API: {SORA2_API_BASE_URL}")
    print(f"[Gradio] 🔗 Sora2免费 API: {SORA2FREE_API_BASE_URL}")
    print(f"[Gradio] 🔑 Seedance 鉴权: {'已配置' if SEEDANCE_AUTH_TOKEN else '未配置'}")
    print(f"[Gradio] 🔑 Sora2 鉴权: {'已配置' if SORA2_API_KEY else '未配置'}, 启用: {SORA2_ENABLED}")
    print(f"[Gradio] 🔑 Sora2免费 鉴权: {'已配置' if SORA2FREE_API_KEY else '未配置'}")

    demo = create_ui()
    port = int(os.getenv("GRADIO_PORT", "7860"))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True
    )
