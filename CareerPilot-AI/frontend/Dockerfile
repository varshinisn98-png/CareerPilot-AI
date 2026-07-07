FROM python:3.11-slim

WORKDIR /app

# Install Streamlit and dependencies
RUN pip install --no-cache-dir streamlit==1.35.0 httpx==0.27.0

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
