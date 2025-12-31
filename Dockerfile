FROM python:3.11-slim

# 设置维护者信息
LABEL maintainer="video-generator"
LABEL version="3.0.0"
LABEL description="AI Video Replicate - AI 视频生成与复刻工具 (支持 Seedance & Sora2 & Sora2免费)"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Asia/Shanghai

# ========== Seedance 配置 ==========
ENV SEEDANCE_API_BASE_URL=https://seedanceapi.duckcloud.fun
ENV SEEDANCE_AUTH_TOKEN=""

# ========== Sora2 配置 ==========
ENV SORA2_API_BASE_URL=https://api.jxincm.cn
ENV SORA2_API_KEY=""
ENV SORA2_ENABLED=true

# ========== Sora2免费 配置 ==========
ENV SORA2FREE_API_BASE_URL=https://rendersora2api.duckcloud.fun
ENV SORA2FREE_API_KEY=""

# ========== Qwen3-VL 视频分析配置 ==========
ENV QWEN_API_BASE_URL=https://api-inference.modelscope.cn/v1
ENV QWEN_API_KEY=""
ENV QWEN_MODEL_ID=Qwen/Qwen3-VL-8B-Instruct

# ========== Gradio 配置 ==========
ENV GRADIO_PORT=7860

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 httpx (用于异步 HTTP 请求)
RUN pip install --no-cache-dir httpx[http2] -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用文件
COPY app.py .
COPY qwen3vl.py .
COPY .env.example .env
COPY sample/ ./sample/

# 暴露端口
EXPOSE 7860

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# 启动命令
CMD ["python", "app.py"]
