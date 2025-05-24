# Usa una imagen de Python 3.12
FROM python:3.12-slim

# Variables de entorno para Flask
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crear directorio de la app
WORKDIR /app

# Copiar los archivos de tu app
COPY . .

# Crear carpeta 'uploads'
RUN mkdir -p uploads

# Crear carpeta 'logs'
RUN mkdir -p logs

# Instalar dependencias
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expone el puerto Flask/Gunicorn
EXPOSE 5000

# Comando de arranque con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
