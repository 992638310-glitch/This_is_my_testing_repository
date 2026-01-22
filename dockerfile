FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt .
# 安装系统依赖 (OpenCV等库可能需要)
RUN apt-get update && apt-get install -y libgomp1
RUN pip install --no-cache-dir -r requirements.txt
COPY . .