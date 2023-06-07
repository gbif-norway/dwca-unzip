FROM python:3.9.17-slim-bullseye
RUN apt-get update && apt-get install -y \
    samba-client \
    unzip \
    curl 
RUN pip install minio
WORKDIR /app
COPY listener.py /app
CMD ["python", "/app/listener.py"]
