FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Sleep for 10 seconds to make sure the APIs are fully started before running the script
CMD ["sh", "-c", "sleep 10 && python run_clients.py"]
