FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . /app
WORKDIR /app

# Run your application with xvfb
CMD xvfb-run --server-args="-screen 0 1024x768x24" python app.py