# Usa una imagen oficial de Python como base
FROM python:3.12

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

RUN pip install --upgrade pip

# Copiar el archivo requirements.txt dentro del contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código dentro del contenedor
COPY . .

# Comando por defecto para ejecutar el script
CMD ["python", "main.py"]
