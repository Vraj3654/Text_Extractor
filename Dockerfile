# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install System Dependencies required for OpenCV and Tesseract-OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download HuggingFace model during build stage to save startup bandwidth
RUN python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
    MODEL_NAME = 'vennify/t5-base-grammar-correction'; \
    AutoTokenizer.from_pretrained(MODEL_NAME); \
    AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)"

# Copy the core app files into the container
COPY . .

# Expose the API port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
