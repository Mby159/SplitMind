# SplitMind Dockerfile
# 用于构建和运行 SplitMind 隐私保护多智能体任务编排系统

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml README.md ./
COPY splitmind/ ./splitmind/

# 安装 Python 依赖
RUN pip install --no-cache-dir -e ".[all]"

# 暴露 Web 服务端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 默认命令：启动 Web 服务
CMD ["uvicorn", "splitmind.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
