FROM python:3.13-slim AS builder
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN python -m venv /opt/venv
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS runner
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]