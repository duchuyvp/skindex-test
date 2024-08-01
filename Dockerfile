FROM python:3.12

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /chat-service
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false

COPY . /chat-service

RUN poetry install --no-interaction

CMD ["python", "chat_service/app.py"]