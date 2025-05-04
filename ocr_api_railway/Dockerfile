# Imagen base de Python
FROM python:3.12-slim

# Instala Tesseract y librerías necesarias
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
 && rm -rf /var/lib/apt/lists/*

# Verifica instalación
RUN which tesseract && tesseract --version

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos
COPY . .

# Instala dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto para Railway
EXPOSE 8080

# Comando para ejecutar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
