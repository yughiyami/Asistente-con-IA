# Asistente de Aprendizaje para Arquitectura de Computadoras

Este proyecto implementa un asistente educativo especializado para cursos de arquitectura de computadoras, utilizando FastAPI y el modelo de lenguaje GEMINI. El asistente ofrece tres modos de interacción para facilitar el aprendizaje de los estudiantes.

## Características Principales

### 1. Modo Repaso/Chat
- Responde preguntas sobre arquitectura de computadoras utilizando contenido de PDFs y libros del curso
- Proporciona referencias a fuentes académicas
- Incluye imágenes y diagramas relevantes para facilitar la comprensión

### 2. Modo Examen
- Genera exámenes personalizados sobre temas específicos
- Preguntas de opción múltiple con validación automática
- Retroalimentación detallada sobre respuestas correctas e incorrectas

### 3. Modo Juegos
- **Ahorcado**: Adivina términos técnicos con pistas
- **Wordle**: Descubre términos de 5 letras relacionados con arquitectura de computadoras
- **Diagramas Lógicos**: Resuelve problemas de circuitos y lógica digital
- **Ensamblador**: Encuentra y corrige errores en código ensamblador

## Requisitos Técnicos

- Python 3.9+
- FastAPI
- API key para GEMINI (Google AI)
- Dependencias adicionales listadas en `requirements.txt`

## Configuración

1. Clona este repositorio
2. Crea un entorno virtual: `python -m venv venv`
3. Activa el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instala las dependencias: `pip install -r requirements.txt`
5. Copia `.env.example` a `.env` y configura tus variables de entorno
6. Inicia el servidor: `uvicorn app.main:app --reload`

## Estructura del Proyecto

El proyecto sigue una arquitectura modular con separación clara de responsabilidades:

- `app/`: Código principal de la aplicación
  - `api/`: Endpoints de la API REST
  - `models/`: Modelos de datos
  - `schemas/`: Esquemas Pydantic para validación
  - `services/`: Lógica de negocio
  - `repositories/`: Acceso a datos

Consulta `docs/architecture.md` para más detalles sobre la arquitectura.

## API Documentation

Una vez que el servidor esté en funcionamiento, puedes acceder a:

- Documentación interactiva: `http://localhost:8000/docs`
- Especificación OpenAPI: `http://localhost:8000/openapi.json`

## Desarrollo

Para contribuir al proyecto:

1. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
2. Realiza tus cambios y asegúrate de que los tests pasen
3. Envía un Pull Request con una descripción detallada de los cambios

## Tests

Ejecuta los tests con:

```bash
pytest
```

## Licencia

[MIT](LICENSE)