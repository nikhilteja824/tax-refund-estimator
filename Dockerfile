#Lightweight python base image
FROM python:3.13-slim


WORKDIR /app

#To have basic tools preinstalled on container
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    lsof \
    telnet \
    grep \
    && rm -rf /var/lib/apt/lists/*

#Just to have docker level caching
COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir --root-user-action=ignore \
    && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt


COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
