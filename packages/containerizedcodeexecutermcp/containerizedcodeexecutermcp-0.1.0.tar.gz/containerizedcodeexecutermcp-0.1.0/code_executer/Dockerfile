
FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app
COPY . /app

EXPOSE 8888

RUN pip install uv

RUN uv init

RUN uv add sympy

CMD ["uv", "run", "executer.py"]
