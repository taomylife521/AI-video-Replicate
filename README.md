# AI-video-Replicate

AI 视频生成与复刻工具，支持 **Seedance**、**Sora2** 和 **Sora2免费** 三种模型提供者，提供文生视频、图生视频和视频复刻功能。

## 功能特性

- **三模型支持**: Seedance、Sora2、Sora2免费
- **文生视频**: 通过文本提示词生成视频
- **图生视频**: 上传参考图片生成视频 (Seedance/Sora2)
- **视频复刻**: 上传视频自动提取提示词，一键复刻
- **实时进度**: 任务提交后自动轮询，实时显示生成进度
- **样例视频**: 内置样例视频，快速体验

## 模型对比

| 特性 | Seedance | Sora2 | Sora2免费 |
|------|----------|-------|-----------|
| 模型 | seedance-1-5-pro-251215, seedance-1-0-pro-fast | sora-2 | sora2-landscape-10s/15s, sora2-portrait-10s/15s |
| 时长 | 4s, 5s, 8s, 12s | 10s, 15s | 10s, 15s (模型名包含) |
| 比例 | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | portrait, landscape | 横屏/竖屏 (模型名包含) |
| 图生视频 | ✅ 支持 | ✅ 支持 | ❌ 仅文生视频 |
| 免费额度 | 按需付费 | 按需付费 | 每天 10 次 |

## 快速开始

### 方式一: 本地运行

1. **克隆项目**
```bash
git clone <repository-url>
cd replicate_sora2
```

2. **安装依赖**
```bash
pip install -r requirements.txt
pip install httpx[http2]
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

4. **启动应用**
```bash
python app.py
```

5. **访问界面**
打开浏览器访问 `http://localhost:7860`

### 方式二: Docker 部署

1. **构建镜像**
```bash
docker build -t video-generator:latest .
```

2. **运行容器**
```bash
docker run -d \
  --name ai-video-replicate \
  -p 7860:7860 \
  -e SEEDANCE_AUTH_TOKEN=your-seedance-token \
  -e SORA2_API_KEY=your-sora2-key \
  -e SORA2FREE_API_KEY=your-free-key \
  -e QWEN_API_KEY=your-qwen-key \
  ai-video-replicate:latest
```

3. **使用 docker-compose (推荐)**

创建 `.env` 文件:
```bash
SEEDANCE_AUTH_TOKEN=your-seedance-token
SORA2_API_KEY=your-sora2-key
SORA2_ENABLED=true
SORA2FREE_API_KEY=your-free-key
QWEN_API_KEY=your-qwen-key
```

运行:
```bash
docker-compose up -d
```

访问 http://localhost:7860 使用 AI-video-Replicate

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SEEDANCE_API_BASE_URL` | Seedance API 地址 | https://seedanceapi.duckcloud.fun |
| `SEEDANCE_AUTH_TOKEN` | Seedance API Token | - |
| `SORA2_API_BASE_URL` | Sora2 API 地址 | https://api.jxincm.cn |
| `SORA2_API_KEY` | Sora2 API Key | - |
| `SORA2_ENABLED` | 是否启用 Sora2 | true |
| `SORA2FREE_API_BASE_URL` | Sora2免费 API 地址 | https://rendersora2api.duckcloud.fun |
| `SORA2FREE_API_KEY` | Sora2免费 API Key | (和作者联系) |
| `QWEN_API_BASE_URL` | Qwen3-VL API 地址 | https://api-inference.modelscope.cn/v1 |
| `QWEN_API_KEY` | Qwen3-VL API Key | - |
| `QWEN_MODEL_ID` | Qwen 模型 ID | Qwen/Qwen3-VL-8B-Instruct |
| `GRADIO_PORT` | Gradio 服务端口 | 7860 |

## 使用指南

### 文生视频

1. 选择模型提供者 (seedance / sora2 / sora2free)
2. 输入视频描述提示词
3. 选择模型、时长和比例 (根据模型类型自动显示/隐藏)
4. 点击 "生成视频" 按钮
5. 等待视频生成完成

### 图生视频

1. 选择模型提供者 (seedance 或 sora2)
2. 输入视频描述提示词
3. 上传参考图片
4. 选择模型、时长和比例
5. 点击 "生成视频" 按钮

> 注意: Sora2免费 不支持图生视频

### 视频复刻

1. 点击 "加载样例视频" 或上传想要复刻的短视频

   ![image-20251231114952699](https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/image-20251231114952699.png)

2. 点击 "提取视频提示词" 按钮

   ![image-20251231115042796](https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/image-20251231115042796.png)

3. 系统会自动分析视频并生成 SORA2 风格提示词

4. 确认或修改提示词

5. 选择模型参数后生成新视频

   ![image-20251231115128577](https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/image-20251231115128577.png)

​       生成复刻视频

​      ![image-20251231115159671](https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/image-20251231115159671.png)

## 视频复刻提示词专家

本项目集成了专业的视频复刻提示词生成系统，基于 Sora2 五大支柱框架：

1. **主体与角色 (Subject & Character)**: 外观、服装、情感状态
2. **动作与运动 (Action & Movement)**: 具体动词描述
3. **环境与背景 (Environment & Setting)**: 位置、时间和氛围
4. **电影构图 (Cinematography)**: 摄像机角度、运动和取景
5. **美学与风格 (Aesthetics & Style)**: 视觉效果和风格

生成的提示词采用三段式结构：
- **Style**: 视觉纹理、光照质量、色彩调板、氛围
- **Cinematography**: 摄像机运动、镜头特性、布光方案、情绪基调
- **Scene Breakdown**: 场景分解、动作序列、对话、背景音

## 项目结构

```
AI-video-Replicate/
├── app.py                    # Gradio 前端主程序
├── qwen3vl.py                # Qwen3-VL 视频分析模块
├── Dockerfile                # Docker 镜像
├── docker-compose.yml        # Docker Compose 配置
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量配置
├── .env.example              # 环境变量示例
├── sample/                   # 样例视频目录
│   └── video.mp4            # 样例视频文件
├── 复刻SORA2视频提示词专家.md  # 提示词模板文档
└── README.md                 # 项目文档
```

## 常见问题

### Q: 视频生成需要多长时间？
A: 通常需要 1-5 分钟，具体取决于视频时长和服务器负载。Sora2 可能需要更长时间（最多 15 分钟），Sora2免费 通常在 1-2 分钟内完成。

### Q: 支持哪些图片格式？
A: 支持 PNG、JPG、JPEG、GIF、WebP、BMP 格式。

### Q: 如何获取 API Key？
A:
- Seedance: 联系服务提供商获取
- Sora2: 访问  https://api.jxincm.cn/register?aff=SeEB注册获取
- Sora2免费: 默认 API Key 已配置，每天 10 次免费额度
- Qwen3-VL: 访问 https://modelscope.cn 注册获取

### Q: 视频下载失败怎么办？
A: 系统会提供视频 URL，可以手动复制链接下载。Seedance 视频会通过代理下载。

### Q: Sora2 选项是灰色不可用？
A: 检查 `.env` 文件中的 `SORA2_ENABLED` 是否设置为 `true`，或通过环境变量设置。

### Q: Sora2免费 有什么限制？
A: Sora2免费 每天限制使用 10 次，且仅支持文生视频模式。

## 许可证

MIT License
