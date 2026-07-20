from pydantic import BaseModel, Field
from typing import Literal, Union, Optional


# 1. Definimos las subcategorías ESTRICTAS para cada Categoría Principal
class CatBecas(BaseModel):
    categoria_ia: Literal["Becas y trabajos"]
    subcategoria_ia: Literal[
        "Distribucion fisica y Masters",
        "procesos de seleccion",
        "Solicitudes enviadas",
        "Solicitudes rechazadas",
        "UcoFísicos",
        "Otros",
    ]


class CatEducacion(BaseModel):
    categoria_ia: Literal["Educacion"]
    subcategoria_ia: Literal["certificaciones", "Cursos", "Master", "Otros"]


class CatPersonal(BaseModel):
    categoria_ia: Literal["Personal"]
    subcategoria_ia: Literal[
        "Documentos", "tickets y billetes", "Visitas medicas y salud", "Otros"
    ]


class CatServicios(BaseModel):
    categoria_ia: Literal["Servicios y Subscripciones"]
    subcategoria_ia: Literal["Cloud", "newsletter", "Otros"]


class CatIAM(BaseModel):
    categoria_ia: Literal["IAM y Seguridad"]
    subcategoria_ia: Literal[
        "Ninguna"
    ]  # Al no tener flecha desplegable en tu foto, asumimos que no tiene subcategorías


class CatTrabajo(BaseModel):
    categoria_ia: Literal["Trabajo"]
    # Mantengo las que me pasaste en el contexto anterior. Puedes añadir más aquí fácilmente.
    subcategoria_ia: Literal["LTIMindtree", "MyCompany", "NTER", "Otros"]


# 2. Creamos la Unión. La IA DEBE elegir obligatoriamente una de estas combinaciones.
CategoriaUnion = Union[
    CatBecas, CatEducacion, CatPersonal, CatServicios, CatIAM, CatTrabajo
]


# 3. El modelo final que usa el LLM
class EmailMetadata(BaseModel):
    """Esquema de salida forzado para el LLM."""

    remitente: str
    asunto: str
    clasificacion: CategoriaUnion = Field(
        description="Selecciona la categoría principal y una de sus subcategorías válidas correspondientes."
    )
    urgencia_ia: Literal["Alta", "Media", "Baja"]
    accionable: bool
    resumen_corto: str = Field(description="Resumen de 1-2 líneas del correo.")
