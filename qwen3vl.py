#!/usr/bin/env python3
"""
基于 Qwen3-VL 模型的视频内容分析工具
支持读取本地 MP4 视频文件并提取视频内容描述
支持生成 SORA2 文生视频提示词

由于 API 有大小限制，采用提取视频关键帧的方式进行分析
"""

import os
import sys
import base64
import argparse
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
API_BASE_URL = os.getenv('QWEN_API_BASE_URL', 'https://api-inference.modelscope.cn/v1')
API_KEY = os.getenv('QWEN_API_KEY', 'aaa')
MODEL_ID = os.getenv('QWEN_MODEL_ID', 'Qwen/Qwen3-VL-8B-Instruct')

# 帧提取配置
MAX_FRAMES = 8  # 最多提取的帧数
FRAME_QUALITY = 85  # JPEG 质量


# SORA2 视频提示词专家系统提示词 - 基于复刻SORA2视频提示词专家模板
SORA2_SYSTEM_PROMPT = """你是 SORA2 视频复刻提示词专家。你的任务是根据视频关键帧分析，生成符合 Sora2 文生视频标准的高质量提示词。

## Sora2 五大支柱框架
生成提示词时必须包含以下五个核心要素：

1. **主体与角色 (Subject & Character)**: 清晰定义人物/物体的外观、服装、情感状态
2. **动作与运动 (Action & Movement)**: 使用具体动词描述正在发生的事情和交互方式
3. **环境与背景 (Environment & Setting)**: 建立场景的位置、时间和氛围属性
4. **电影构图 (Cinematography)**: 指定摄像机角度、运动和取景方式
5. **美学与风格 (Aesthetics & Style)**: 确定视觉效果（真实感、动画、胶片类型）

## 世界模拟范式
Sora2 是世界模拟器，有效提示应该：
- 提供初始条件和物理法则（重力、光线、反射）
- 明确物体如何相互作用
- 定义环境特性和材质属性
- 隐含或明确引导物理表现

## 提示词结构模板

### 第一部分：Style（风格定义）
- **Visual Texture（视觉纹理）**: 描述画面的质感特征、材质表面、AI/真实拍摄风格
- **Lighting Quality（光照质量）**: 光源类型、方向、强度和氛围（如 golden hour, three-point lighting）
- **Color Palette（色彩调板）**: 主导色调和配色方案，使用具体色彩名称
- **Atmosphere（氛围）**: 整体情绪和感受（如 playful, nostalgic, energetic）

### 第二部分：Cinematography（电影摄影）
- **Camera（摄像机运动）**: 描述摄像机的移动方式（handheld, dolly, pan, tilt, zoom）
- **Lens（镜头特性）**: 镜头类型、焦距和景深效果（50mm, f/2.8, shallow depth of field）
- **Lighting（布光方案）**: 详细说明光照布置（key light, fill light, rim light）
- **Mood（情绪基调）**: 视觉情绪和节奏

### 第三部分：Scene Breakdown（场景分解）
按时间顺序描述每个场景，包含：
- **场景描述**: 1-3句话描述场景整体视觉呈现
- **Actions**: 具体动作列表，使用精确动词
- **Dialogue**: 对话内容或 "None"
- **Background Sound**: 音乐类型和环境音效

## 质量检查清单
- [ ] 包含材质和纹理细节
- [ ] 明确光源方向和性质
- [ ] 使用具体色彩名称（至少3个）
- [ ] 描述摄像机运动方式和角度
- [ ] 每个场景标注时间戳
- [ ] 使用具体动词而非抽象描述
- [ ] 描述物体间的物理交互

## 输出格式

只输出以下内容，不要输出其他分析：

## SORA2 Prompt (English)
```
[完整的英文提示词，采用专业三段式结构：Style - Cinematography - Scene Breakdown]
[包含五大支柱要素，使用具体、专业的描述]
[约200-400词，适合高精度视频复刻]
```

## SORA2 提示词 (中文)
```
[对应的中文提示词，保持专业术语和结构]
```"""

SORA2_USER_PROMPT_TEMPLATE = """这是从一个视频中提取的 {num_frames} 帧关键画面（按时间顺序）。

请作为 SORA2 视频复刻提示词专家，分析这些画面并生成专业的 SORA2 文生视频提示词。

## 分析要求
1. 仔细观察每帧画面的：主体特征、动作变化、场景环境、光影效果、色彩风格
2. 识别摄像机运动轨迹和镜头切换点
3. 推断场景的时间线顺序
4. 注意材质细节、光源方向、色彩搭配

## 生成要求
- 使用五大支柱框架组织提示词
- 采用三段式结构：Style → Cinematography → Scene Breakdown
- 每个场景使用具体时间戳（如 0:00s - 0:05s）
- 动作描述使用精确动词（press, pour, rotate, drift）
- 包含材质、物理效果、感官细节
- 英文提示词约 200-400 词

## 输出格式
中英文各一个完整的 SORA2 提示词"""


def get_video_files(directory: str = None) -> list:
    """
    获取指定目录下的所有 MP4 视频文件

    Args:
        directory: 目录路径，默认为当前项目的 downloads 和 cache 目录

    Returns:
        视频文件路径列表
    """
    video_files = []

    if directory:
        search_dirs = [directory]
    else:
        # 默认搜索目录
        base_dir = Path(__file__).parent
        search_dirs = [
            base_dir / 'downloads',
            base_dir / 'cache',
            base_dir / 'static' / 'videos'
        ]

    for search_dir in search_dirs:
        if Path(search_dir).exists():
            for file in Path(search_dir).glob('*.mp4'):
                video_files.append(str(file))

    return video_files


def get_video_duration(video_path: str) -> float:
    """获取视频时长（秒）"""
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ],
            capture_output=True,
            text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return 0


def extract_frames(video_path: str, num_frames: int = MAX_FRAMES) -> list:
    """
    从视频中提取关键帧

    Args:
        video_path: 视频文件路径
        num_frames: 要提取的帧数

    Returns:
        帧图片路径列表
    """
    duration = get_video_duration(video_path)
    if duration <= 0:
        print("警告: 无法获取视频时长，使用默认间隔")
        duration = 60  # 默认假设60秒

    # 计算时间间隔
    interval = duration / (num_frames + 1)

    frames = []
    temp_dir = tempfile.mkdtemp(prefix='video_frames_')

    print(f"视频时长: {duration:.1f}秒，提取 {num_frames} 帧...")

    for i in range(num_frames):
        timestamp = interval * (i + 1)
        output_path = os.path.join(temp_dir, f'frame_{i:03d}.jpg')

        try:
            subprocess.run(
                [
                    'ffmpeg', '-y',
                    '-ss', str(timestamp),
                    '-i', video_path,
                    '-vframes', '1',
                    '-q:v', str(int((100 - FRAME_QUALITY) / 10) + 1),
                    output_path
                ],
                capture_output=True,
                check=True
            )

            if os.path.exists(output_path):
                frames.append(output_path)
                print(f"  提取帧 {i+1}/{num_frames} @ {timestamp:.1f}s")

        except subprocess.CalledProcessError as e:
            print(f"  帧 {i+1} 提取失败: {e}")

    return frames


def image_to_base64(image_path: str) -> str:
    """将图片转换为 base64 编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')


def analyze_video(video_path: str, prompt: str = None, stream: bool = True,
                   num_frames: int = MAX_FRAMES, sora2_mode: bool = False, keep_frames: bool = False):
    """
    使用 Qwen3-VL 模型分析视频内容

    Args:
        video_path: 视频文件路径
        prompt: 分析提示词
        stream: 是否使用流式输出
        num_frames: 提取的帧数
        sora2_mode: 是否启用 SORA2 提示词生成模式
        keep_frames: 是否保留提取的帧文件 (默认False，分析完即删)

    Returns:
        如果 keep_frames=True，返回 (result, frames) 元组
        否则返回 result 字符串
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    file_size = os.path.getsize(video_path) / (1024 * 1024)
    print(f"正在读取视频文件: {video_path} ({file_size:.1f}MB)")

    # 提取视频帧
    frames = extract_frames(video_path, num_frames)

    if not frames:
        raise RuntimeError("无法提取视频帧，请确保已安装 ffmpeg")

    print(f"成功提取 {len(frames)} 帧")

    # 获取视频时长用于 SORA2 分析
    duration = get_video_duration(video_path)

    # 根据模式选择提示词
    if sora2_mode:
        print("\n🎬 SORA2 提示词生成模式已启用")
        print(f"📊 视频时长: {duration:.1f}秒")

        # 使用 SORA2 专业提示词
        user_prompt = SORA2_USER_PROMPT_TEMPLATE.format(num_frames=len(frames))
        if duration > 0:
            user_prompt += f"\n\n视频实际时长: {duration:.1f}秒，请根据此时长分配各场景时间。"

        messages = [
            {'role': 'system', 'content': SORA2_SYSTEM_PROMPT},
            {'role': 'user', 'content': None}  # 占位，后面会填充
        ]
    elif prompt:
        user_prompt = prompt
        messages = [{'role': 'user', 'content': None}]
    else:
        # 默认提示词
        user_prompt = f"""这是从一个视频中提取的 {len(frames)} 帧关键画面。
请根据这些画面，详细描述这个视频的内容，包括：
1. 视频中出现的人物或物体
2. 发生的事件或动作
3. 场景环境
4. 视频的主题或表达的意思
5. 视频的整体叙事或故事线"""
        messages = [{'role': 'user', 'content': None}]

    # 构建消息内容
    content = [{'type': 'text', 'text': user_prompt}]

    for frame_path in frames:
        frame_base64 = image_to_base64(frame_path)
        content.append({
            'type': 'image_url',
            'image_url': {
                'url': f'data:image/jpeg;base64,{frame_base64}'
            }
        })

    # 更新最后一条消息的内容
    messages[-1]['content'] = content

    # 创建 API 客户端
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    if sora2_mode:
        print("\n🔄 正在分析视频并生成 SORA2 提示词...")
    else:
        print(f"正在分析视频...")
    print("-" * 50)

    # 调用 API
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        stream=stream
    )

    # 处理响应
    result = ""
    if stream:
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                print(chunk_content, end='', flush=True)
                result += chunk_content
        print()  # 换行
    else:
        result = response.choices[0].message.content
        print(result)

    # 清理临时文件
    if not keep_frames:
        for frame_path in frames:
            try:
                os.remove(frame_path)
            except Exception:
                pass

        try:
            os.rmdir(os.path.dirname(frames[0]))
        except Exception:
            pass

    if sora2_mode:
        print("\n" + "=" * 50)
        print("✅ SORA2 提示词生成完成！")
        print("💡 提示: 可直接复制上方 English Version 用于 SORA2")
        print("=" * 50)

    if keep_frames:
        return result, frames
    return result


def list_videos():
    """列出项目中所有可用的视频文件"""
    video_files = get_video_files()

    if not video_files:
        print("未找到任何视频文件")
        return

    print("=" * 60)
    print("项目中的视频文件:")
    print("=" * 60)

    for i, video_file in enumerate(video_files, 1):
        file_size = os.path.getsize(video_file) / (1024 * 1024)
        file_name = os.path.basename(video_file)
        duration = get_video_duration(video_file)
        duration_str = f"{duration:.1f}s" if duration > 0 else "未知"
        print(f"{i}. [{file_size:.1f}MB, {duration_str}] {file_name}")
        print(f"   路径: {video_file}")

    print("=" * 60)
    return video_files


def interactive_mode(sora2_mode: bool = False):
    """交互式模式，让用户选择视频进行分析"""
    video_files = list_videos()

    if not video_files:
        return

    mode_hint = " (SORA2模式)" if sora2_mode else ""
    print(f"\n请输入要分析的视频编号{mode_hint} (输入 q 退出):")

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() == 'q':
                print("退出程序")
                break

            index = int(user_input) - 1
            if 0 <= index < len(video_files):
                video_path = video_files[index]
                print(f"\n选择的视频: {os.path.basename(video_path)}")

                if not sora2_mode:
                    # 询问自定义提示词
                    custom_prompt = input("输入自定义提示词 (直接回车使用默认): ").strip()
                else:
                    custom_prompt = None

                print("\n" + "=" * 60)
                analyze_video(
                    video_path,
                    custom_prompt if custom_prompt else None,
                    sora2_mode=sora2_mode
                )
                print("=" * 60)

                print("\n继续选择其他视频，或输入 q 退出:")
            else:
                print(f"无效的编号，请输入 1-{len(video_files)} 之间的数字")

        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n退出程序")
            break
        except Exception as e:
            print(f"分析出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='基于 Qwen3-VL 模型的视频内容分析工具 (支持 SORA2 提示词生成)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有视频文件
  python qwen3vl.py --list

  # 分析指定视频
  python qwen3vl.py --video downloads/video.mp4

  # 🎬 生成 SORA2 文生视频提示词 (推荐)
  python qwen3vl.py --video video.mp4 --sora2

  # 使用更多帧数生成更精确的 SORA2 提示词
  python qwen3vl.py --video video.mp4 --sora2 --frames 12

  # 使用自定义提示词分析
  python qwen3vl.py --video video.mp4 --prompt "这个视频讲的是什么故事？"

  # 交互式 SORA2 模式
  python qwen3vl.py --interactive --sora2
        """
    )

    parser.add_argument(
        '--video', '-v',
        type=str,
        help='要分析的视频文件路径'
    )

    parser.add_argument(
        '--sora2', '-s',
        action='store_true',
        help='🎬 启用 SORA2 提示词生成模式，分析视频并输出文生视频提示词'
    )

    parser.add_argument(
        '--prompt', '-p',
        type=str,
        default=None,
        help='自定义分析提示词 (与 --sora2 互斥)'
    )

    parser.add_argument(
        '--frames', '-f',
        type=int,
        default=MAX_FRAMES,
        help=f'要提取的视频帧数 (默认: {MAX_FRAMES}，SORA2 模式建议 8-12)'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出项目中所有视频文件'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='交互式模式'
    )

    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='禁用流式输出'
    )

    args = parser.parse_args()

    # 如果没有任何参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "=" * 60)
        print("💡 快速开始: python qwen3vl.py --video 视频路径.mp4 --sora2")
        print("=" * 60)
        list_videos()
        return

    if args.list:
        list_videos()
    elif args.interactive:
        interactive_mode(sora2_mode=args.sora2)
    elif args.video:
        # SORA2 模式下忽略自定义 prompt
        prompt = None if args.sora2 else args.prompt
        analyze_video(
            args.video,
            prompt=prompt,
            stream=not args.no_stream,
            num_frames=args.frames,
            sora2_mode=args.sora2
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()