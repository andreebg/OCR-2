# Usa una imagen base ligera de Python 3.12
FROM python:3.12-slim

# Instala Tesseract OCR y sus dependencias necesarias
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Verificación explícita para asegurarse de que Tesseract se instaló correctamente
RUN which tesseract && tesseract --version

# Establece el directorio de trabajo
WORKDIR /app

# Copia el código de la aplicación al contenedor
COPY . .

# Instala pip y las dependencias necesarias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto 8080 (requerido por Railway)
EXPOSE 8080

# Comando para lanzar la API con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
