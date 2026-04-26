"""
Configuración básica - Paso 11
"""
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Intentar leer la API key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Verificar si existe
    if not OPENAI_API_KEY:
        print("❌ ERROR: No se encontró OPENAI_API_KEY en el archivo .env")
        print("Por favor, verifica que el archivo .env contenga tu API key")
    else:
        print(f"✅ API key cargada correctamente (primeros 10 caracteres: {OPENAI_API_KEY[:10]}...)")

# Probar la configuración
if __name__ == "__main__":
    print("=== Probando configuración ===")
    Config()
    print("✅ Prueba completada")