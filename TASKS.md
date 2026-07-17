# 🗺️ Roadmap de Tareas (ETL Serverless Pipeline)

## 📋 Lista de Tareas

### [T01] Setup Inicial (✅ COMPLETADO)

- **Estado:** Hecho. Entorno virtual (.venv) creado y dependencias instaladas.

### [T02] Ingesta - Autenticación Gmail API

- **Objetivo:** Lograr que el script local se autentique con OAuth2 y descargue el asunto del último correo no leído para validar la conexión.
- **Archivos:** `gmail_auth.py` (nuevo)
- **Instrucciones para IA:** Escribe el flujo de OAuth2 para Gmail. Si `token.json` no existe, usa `credentials.json` para abrir el navegador localmente y autorizar.
- **Criterio de Aceptación:** El script imprime por consola el Asunto de 1 correo no leído.

### [T03] Transformación - Pydantic y OpenAI

- **Objetivo:** Enviar el texto del correo a `gpt-4o-mini` y forzar una salida JSON usando Pydantic V2.
- **Archivos:** `llm_processor.py` (nuevo)
- **Instrucciones para IA:** Define un modelo Pydantic basado en el Esquema de Datos de `AI_CONTEXT.md`. Usa el método `client.beta.chat.completions.parse` de OpenAI para garantizar la estructura.
- **Criterio de Aceptación:** Una función que recibe un string (correo) y devuelve un objeto Python estructurado y validado.

### [T04] Carga - Conexión e Inserción en Azure SQL

- **Objetivo:** Conectar Python a Azure SQL Server de forma segura y escribir un registro.
- **Archivos:** `db_loader.py` (nuevo), `schema.sql` (nuevo)
- **Instrucciones para IA:** Escribe el archivo `.sql` con el DDL de la tabla. Luego, escribe una función en Python usando `pyodbc` que ejecute un `INSERT INTO`. Maneja colisiones de `email_id` (upsert o ignore).
- **Criterio de Aceptación:** El script inserta un JSON de prueba en la base de datos real.

### [T05] Orquestación Principal (La ETL)

- **Objetivo:** Unir T02, T03 y T04 en un flujo continuo (Extract -> Transform -> Load).
- **Archivos:** `main.py`
- **Instrucciones para IA:** Construye la función `main()`. Debe extraer 5 correos, pasarlos por el LLM en un bucle, guardarlos en Azure SQL, y si todo sale bien, marcar el correo en Gmail como leído y etiquetado.
- **Criterio de Aceptación:** Ejecutar `main.py` procesa la bandeja de entrada de principio a fin de forma autónoma.

### [T06] Despliegue Serverless (Azure Functions)

- **Objetivo:** Adaptar el código para que corra en la nube cada 15 minutos.
- **Archivos:** `function_app.py` (nuevo), `host.json`
- **Instrucciones para IA:** Envuelve la lógica de `main.py` en un Timer Trigger de Azure Functions v2.
- **Criterio de Aceptación:** El código es desplegable sin errores de sintaxis en el entorno de Azure.
