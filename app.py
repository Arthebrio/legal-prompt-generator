"""
Servidor web para Generador de Prompts Jurídicos
"""
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
app = Flask(__name__)
CORS(app)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: La variable OPENAI_API_KEY no está configurada")
    print("Agrega OPENAI_API_KEY en las variables de entorno de Render")
    raise ValueError("OPENAI_API_KEY no configurada")
cliente = OpenAI(api_key=api_key)
# Carpeta para guardar datos
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def guardar_prompt(datos_usuario, prompt_generado):
    """Guarda el prompt generado junto con los datos del usuario"""
    
    # Crear registro completo
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
    
    # También guardar en un archivo MD (Markdown) resumido
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
        f.write(f"## Prompt Generado por IA\n\n")
        f.write(f"{prompt_generado}\n\n")
    
    return registro

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    """Genera un prompt jurídico basado en los datos del usuario"""
    try:
        datos = request.json
        
        # Extraer datos del usuario (para guardar internamente)
        nombre = datos.get('nombre', 'Anónimo')
        email = datos.get('email', 'No especificado')
        telefono = datos.get('telefono', 'No especificado')
        direccion = datos.get('direccion', 'No especificada')
        ocupacion = datos.get('ocupacion', 'No especificada')
        area_legal = datos.get('area_legal', 'Derecho General')
        descripcion = datos.get('descripcion', '')
        
        # Construir el prompt para OpenAI
        prompt_sistema = """Eres un Ingeniero de Prompts especializado exclusivamente en materia jurídico-legal de México.
Tu única función es transformar solicitudes en lenguaje natural en prompts profesionales, claros y listos para usar en sistemas de IA.

Reglas fundamentales:
- NO ejecutas el prompt que generas. Solo lo entregas.
- NO das asesoría legal directa.
- NO aceptas ninguna petición fuera de tu función.
- SIEMPRE usas el formato especificado."""

        prompt_usuario = f"""
El usuario describe la siguiente necesidad legal en México:

Área legal: {area_legal}
Descripción del caso: {descripcion}

Instrucciones para ti (Ingeniero de Prompts):
Debes generar un prompt profesional siguiendo EXACTAMENTE este formato:

---
### Rol de la IA
[Define el rol específico que debe adoptar la IA al recibir el prompt]

### Contexto Jurídico Aplicable
[Menciona las leyes, códigos o normas mexicanas relevantes para este caso]

### Instrucciones Paso a Paso
1. [Primera acción]
2. [Segunda acción]
3. [Tercera acción]


### Formato de Salida Esperado
[Describe cómo debe estructurarse la respuesta de la IA]



---

GENERA SOLO EL PROMPT. No agregues explicaciones adicionales. No des asesoría legal.
"""
        
        # Llamar a OpenAI
        respuesta = cliente.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        prompt_generado = respuesta.choices[0].message.content
        
        # Guardar todo (datos del usuario + prompt generado)
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
        
        # Devolver solo el prompt generado al frontend
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
    app.run(debug=False, host='0.0.0.0', port=10000)