import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI
from models import EmailMetadata  # Importamos nuestra estructura blindada

# Cargar variables
load_dotenv()

# Instanciar cliente
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)


def process_email_with_llm(
    subject: str, body: str, sender: str
) -> EmailMetadata | None:
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    system_prompt = """
    Eres un Asistente de IA experto en clasificación de correos.
    Analiza el correo y extrae la información siguiendo ESTRICTAMENTE el esquema JSON.
    La 'clasificacion' debe contener una categoría y una subcategoría que tengan sentido lógico con el contenido.
    Si ninguna subcategoría específica encaja, utiliza 'Otros'.
    """

    try:
        response = client.beta.chat.completions.parse(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {
                    "role": "user",
                    "content": f"Remitente: {sender}\nAsunto: {subject}\nCuerpo: {body}",
                },
            ],
            response_format=EmailMetadata,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logging.error(f"[ERROR] Azure OpenAI falló: {e}")
        return None


if __name__ == "__main__":
    # Prueba de estrés: Vamos a simular un billete de tren para ver si respeta la jerarquía
    result = process_email_with_llm(
        subject="Tus billetes de Renfe (Madrid-Córdoba)",
        body="Adjuntamos el localizador de tu viaje para el viernes.",
        sender="ventas@renfe.es",
    )

    if result:
        print(result.model_dump_json(indent=2))
