FROM python:3.11-slim

# System dependencies aur ffmpeg install karne ke liye
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Sabse pehle requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki bacha poora code copy karein
COPY . .

# Port expose karein
EXPOSE 8501

# Streamlit run karne ki command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]