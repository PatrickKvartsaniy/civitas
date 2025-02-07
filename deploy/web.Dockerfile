FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

COPY ../requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip && \
    pip install --root-user-action=ignore --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python", "main.py", "web"]
