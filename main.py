"""
Generador de Prompts Jurídicos - Con menú interactivo
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def generar_prompt():
    print("\n" + "="*50)
    print("📝 NUEVO PROMPT JURÍDICO")
    print("="*50)
    
    area = input("\n📌 Área legal (Civil, Laboral, Penal, Mercantil): ")
    caso = input("📌 Describe el caso: ")
    
    print("\n⏳ Generando prompt...\n")
    
    prompt_usuario = f"""
Área legal: {area}
Caso: {caso}

Genera un prompt profesional para un abogado experto en {area}.
El prompt debe incluir preguntas clave, normativa aplicable y pasos a seguir.
"""
    
    respuesta = cliente.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un abogado experto. Genera prompts claros y útiles."},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.7,
        max_tokens=600
    )
    
    print("\n" + "="*50)
    print("⚖️ PROMPT GENERADO ⚖️")
    print("="*50)
    print(respuesta.choices[0].message.content)
    print("="*50)

def main():
    while True:
        print("\n" + "="*40)
        print("⚖️  GENERADOR DE PROMPTS JURÍDICOS  ⚖️")
        print("="*40)
        print("1. Nuevo prompt")
        print("2. Salir")
        print("-"*40)
        
        opcion = input("Elige (1-2): ")
        
        if opcion == "1":
            generar_prompt()
        elif opcion == "2":
            print("\n👋 Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida")

if __name__ == "__main__":
    main()