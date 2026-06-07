FROM python:3.10-slim

WORKDIR /workspace

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit dashboard
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
