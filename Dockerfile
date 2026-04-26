FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer puerto (Render usa 10000)
EXPOSE 10000

# Comando para ejecutar la app
CMD ["gunicorn", "app:app"]