FROM python:3.9
WORKDIR /app
COPY dashboard.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
