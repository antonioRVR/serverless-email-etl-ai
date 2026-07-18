import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SCOPES define el nivel de acceso. 'modify' nos permite leer y aplicar etiquetas.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """
    Gestiona la autenticación OAuth2 con Google y devuelve el servicio de la API.
    Si es la primera vez, abre el navegador. Las siguientes, usa token.json.
    """
    creds = None
    
    # 1. Intentamos cargar credenciales previas si existen
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 2. Si no hay credenciales válidas, pedimos al usuario que se loguee
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Si el token caducó, lo refrescamos silenciosamente
            creds.refresh(Request())
        else:
            # Si no hay token, iniciamos el flujo de navegador
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # access_type='offline' y prompt='consent' son CRÍTICOS para forzar a Google 
            # a que nos devuelva el Refresh Token que usaremos en la nube.
            creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')
        
        # 3. Guardamos el token para no volver a pedir login
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # 4. Construimos el cliente de la API
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'❌ Error al conectar con la API de Gmail: {error}')
        return None

if __name__ == '__main__':
    # Bloque de prueba (Solo se ejecuta si corremos este script directamente)
    print("Iniciando autenticación...")
    service = get_gmail_service()
    
    if service:
        print("✅ Autenticación exitosa. Buscando los últimos 3 correos...")
        try:
            # Buscamos en el buzón de entrada (INBOX)
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=3).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print('No se encontraron mensajes.')
            else:
                print('\n📩 Asuntos de tus últimos correos:')
                for message in messages:
                    # Recuperamos los detalles de cada mensaje
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    # Extraemos el Asunto de las cabeceras (headers)
                    headers = msg['payload']['headers']
                    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'Sin Asunto')
                    print(f'- {subject}')
        except Exception as e:
            print(f'❌ Error al leer los correos: {e}')