FROM python:3.12.1-slim-bookworm

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src .

CMD ["python", "bot.py"]
