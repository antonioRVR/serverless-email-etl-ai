import os
import logging
from typing import Literal, Optional
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import AzureOpenAI

# Cargar variables de entorno
load_dotenv()

# Instanciar el cliente de Azure OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

class EmailMetadata(BaseModel):
    """
    Modelo Pydantic que define el esquema de datos y valida estrictamente
    las categorías y subcategorías requeridas.
    """
    email_id: Optional[str] = Field(
        default=None, 
        description="ID único del correo. Puede ser nulo o vacío durante la inferencia."
    )
    remitente: str = Field(description="Dirección de correo o nombre del remitente")
    asunto: str = Field(description="Asunto del correo")
    fecha_recepcion: Optional[str] = Field(
        default=None, 
        description="Fecha de recepción del correo. Puede ser nulo durante la inferencia."
    )
    
    categoria_ia: Literal[
        'Becas y trabajos', 
        'Educacion', 
        'Personal', 
        'Servicios y Subscripciones', 
        'Trabajo'
    ] = Field(description="Categoría principal del correo")
    
    subcategoria_ia: Optional[Literal[
        'Distribucion fisica y Masters', 'procesos de seleccion', 'Solicitudes enviadas', 'Solicitudes rechazadas',
        'certificaciones', 'Cursos', 'Master', 'IAM y Seguridad',
        'Documentos', 'tickets y billetes', 'Visitas medicas y salud',
        'Cloud', 'newsletter',
        'LTIMindtree', 'MyCompany', 'NTER',
        'Otros'
    ]] = Field(description="Subcategoría específica de la categoría. Si ninguna encaja usar nulo o 'Otros'.")
    
    urgencia_ia: Literal['Alta', 'Media', 'Baja'] = Field(description="Nivel de urgencia del correo")
    accionable: bool = Field(description="Verdadero si el correo requiere una acción por parte del usuario")
    resumen_corto: str = Field(description="Un resumen muy breve del contenido del correo")

def process_email_with_llm(subject: str, body: str, sender: str) -> Optional[EmailMetadata]:
    """
    Procesa el contenido de un correo utilizando Azure OpenAI (Structured Outputs).
    
    Args:
        subject (str): Asunto del correo.
        body (str): Cuerpo o contenido del correo.
        sender (str): Remitente del correo.
        
    Returns:
        EmailMetadata: Objeto Pydantic con la metadata parseada, o None si ocurre un error.
    """
    deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    
    system_prompt = """
Eres un Asistente de IA experto en clasificación de correos electrónicos.
Tu objetivo es analizar el correo que se te proporciona (remitente, asunto, cuerpo) y extraer la información
solicitada siguiendo ESTRICTAMENTE el esquema JSON definido.

Reglas de clasificación:
1. 'categoria_ia' debe ser obligatoriamente una de: 'Becas y trabajos', 'Educacion', 'Personal', 'Servicios y Subscripciones', 'Trabajo'.
2. 'subcategoria_ia' debe encajar semánticamente en las opciones disponibles según la categoría elegida.
   Si NINGUNA subcategoría encaja perfectamente, devuelve nulo o 'Otros'.
3. 'urgencia_ia' debe ser 'Alta', 'Media' o 'Baja'.
4. 'accionable' es true si el correo requiere que el usuario haga algo (responder, pagar, asistir, etc.), de lo contrario false.
5. 'resumen_corto' debe tener máximo 2 o 3 oraciones cortas resumiendo el contenido principal del correo.
6. Completa 'remitente' y 'asunto' con los datos proporcionados en el prompt.
    """

    try:
        response = client.beta.chat.completions.parse(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": f"Remitente: {sender}\nAsunto: {subject}\nCuerpo: {body}"}
            ],
            response_format=EmailMetadata,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logging.error(f"[ERROR] Error al procesar el correo con Azure OpenAI: {e}")
        return None

if __name__ == '__main__':
    # Datos de prueba hardcodeados
    test_subject = "Factura AWS"
    test_body = "Cobro de 50$ por dominio"
    test_sender = "billing@aws.com"
    
    print("Procesando correo de prueba...")
    result = process_email_with_llm(
        subject=test_subject, 
        body=test_body, 
        sender=test_sender
    )
    
    if result:
        print("\nResultado exitoso:")
        print(result.model_dump_json(indent=2))
    else:
        print("\nFallo en el procesamiento. Verifica que las variables de entorno de Azure OpenAI estén configuradas y sean correctas.")
