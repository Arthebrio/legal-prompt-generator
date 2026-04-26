"""
Servidor web para Generador de Prompts Jurídicos
"""
import os
import json
import glob
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import openai

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configurar OpenAI (versión 0.28.1)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: La variable OPENAI_API_KEY no está configurada")
    print("Agrega OPENAI_API_KEY en el archivo .env")
    raise ValueError("OPENAI_API_KEY no configurada")
openai.api_key = api_key

# Carpeta para guardar datos
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def guardar_prompt(datos_usuario, prompt_generado):
    """Guarda el prompt generado junto con los datos del usuario"""
    
    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": {
            "nombre": datos_usuario.get("nombre", ""),
            "direccion": datos_usuario.get("direccion", ""),
            "email": datos_usuario.get("email", ""),
            "telefono": datos_usuario.get("telefono", ""),
            "ocupacion": datos_usuario.get("ocupacion", "")
        },
        "caso": {
            "area_legal": datos_usuario.get("area_legal", ""),
            "descripcion": datos_usuario.get("descripcion", "")
        },
        "prompt_generado": prompt_generado
    }
    
    # Guardar en archivo JSON
    archivo = os.path.join(DATA_FOLDER, f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)
    
    # Guardar en Markdown
    archivo_md = os.path.join(DATA_FOLDER, f"resumen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(archivo_md, "w", encoding="utf-8") as f:
        f.write(f"# Resumen de Consulta Jurídica\n\n")
        f.write(f"**Fecha:** {registro['fecha']}\n\n")
        f.write(f"## Datos del Usuario\n\n")
        f.write(f"- **Nombre:** {datos_usuario.get('nombre', 'No especificado')}\n")
        f.write(f"- **Dirección:** {datos_usuario.get('direccion', 'No especificada')}\n")
        f.write(f"- **Email:** {datos_usuario.get('email', 'No especificado')}\n")
        f.write(f"- **Teléfono:** {datos_usuario.get('telefono', 'No especificado')}\n")
        f.write(f"- **Ocupación:** {datos_usuario.get('ocupacion', 'No especificada')}\n\n")
        f.write(f"## Consulta Legal\n\n")
        f.write(f"**Área:** {datos_usuario.get('area_legal', 'No especificada')}\n\n")
        f.write(f"**Descripción del caso:**\n{datos_usuario.get('descripcion', 'No especificada')}\n\n")
        f.write(f"## Prompt Generado\n\n")
        f.write(f"{prompt_generado}\n\n")
    
    return registro

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/historial')
def historial():
    """Devuelve el historial de consultas guardadas"""
    archivos = []
    for archivo in glob.glob("data/prompt_*.json"):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                archivos.append({
                    "fecha": data.get("fecha", ""),
                    "usuario": data.get("usuario", {}).get("nombre", "Anónimo"),
                    "area_legal": data.get("caso", {}).get("area_legal", ""),
                    "prompt": data.get("prompt_generado", "")
                })
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
    
    archivos.sort(key=lambda x: x["fecha"], reverse=True)
    
    return jsonify({
        "success": True,
        "archivos": archivos
    })

@app.route('/generar', methods=['POST'])
def generar():
    """Genera un prompt jurídico basado en los datos del usuario"""
    try:
        datos = request.json
        
        nombre = datos.get('nombre', 'Anónimo')
        email = datos.get('email', 'No especificado')
        telefono = datos.get('telefono', 'No especificado')
        direccion = datos.get('direccion', 'No especificada')
        ocupacion = datos.get('ocupacion', 'No especificada')
        area_legal = datos.get('area_legal', 'Derecho General')
        descripcion = datos.get('descripcion', '')
        
        prompt_sistema = "Eres un Ingeniero de Prompts especializado en materia jurídico-legal de México."
        
        prompt_usuario = f"""
Área legal: {area_legal}
Descripción del caso: {descripcion}

Genera un prompt profesional con este formato:
### Rol de la IA
### Contexto Jurídico Aplicable  
### Instrucciones Paso a Paso
### Formato de Salida Esperado
"""
        
        # Usar sintaxis de openai 0.28.1
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        prompt_generado = respuesta.choices[0].message.content
        
        datos_usuario = {
            "nombre": nombre,
            "direccion": direccion,
            "email": email,
            "telefono": telefono,
            "ocupacion": ocupacion,
            "area_legal": area_legal,
            "descripcion": descripcion
        }
        
        guardar_prompt(datos_usuario, prompt_generado)
        
        return jsonify({
            "success": True,
            "prompt": prompt_generado
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)