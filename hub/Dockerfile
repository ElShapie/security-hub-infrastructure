FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home lab
COPY app.py store.py ./
COPY templates ./templates
COPY static ./static
RUN mkdir /app/data && chown lab:lab /app/data
USER lab
EXPOSE 8000
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
