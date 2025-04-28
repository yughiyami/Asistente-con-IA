# Arquitectura del Asistente de Aprendizaje para Arquitectura de Computadoras

Este documento describe la arquitectura del sistema, explicando los componentes principales, la estructura del proyecto y las interacciones entre ellos.

## Visión General

El Asistente de Aprendizaje para Arquitectura de Computadoras es una aplicación web que utiliza inteligencia artificial para proporcionar tres modos de interacción educativa:

1. **Modo Repaso/Chat**: Responde preguntas y proporciona información sobre temas de arquitectura de computadoras, basándose en el contenido de PDFs y libros del curso.

2. **Modo Examen**: Genera exámenes personalizados con preguntas de opción múltiple sobre temas específicos y proporciona retroalimentación detallada sobre las respuestas.

3. **Modo Juegos**: Ofrece varios juegos educativos para reforzar conceptos de arquitectura de computadoras:
   - Ahorcado con términos técnicos
   - Wordle con términos de 5 letras
   - Diagramas lógicos para resolver problemas de circuitos
   - Identificación y corrección de errores en código ensamblador

## Diagrama de Arquitectura

```
+---------------------+       +-------------------------+
|                     |       |                         |
|   Cliente Web       |<----->|   API Backend (FastAPI) |
|   (Frontend)        |       |                         |
|                     |       +------------+------------+
+---------------------+                    |
                                          |
                            +-------------v--------------+
                            |                            |
                            |   Servicios de Aplicación  |
                            |                            |
                            +--+----------+----------+---+
                               |          |          |
                 +-------------v--+  +----v-----+  +-v------------+
                 |                |  |          |  |              |
                 |  Servicio Chat |  | Servicio |  | Servicio     |
                 |  (Repaso)      |  | Examen   |  | Juegos       |
                 |                |  |          |  |              |
                 +--------+-------+  +----+-----+  +------+-------+
                          |               |               |
                          v               v               v
              +-----------+---------------+---------------+---------+
              |                                                     |
              |           Servicio LLM (GEMINI)                    |
              |                                                     |
              +-----------------------------------------------------+
```

## Componentes Principales

### 1. API Backend (FastAPI)

El backend está construido con FastAPI, un framework moderno y de alto rendimiento para Python que proporciona:

- Validación automática de datos con Pydantic
- Documentación automática con Swagger UI y ReDoc
- Soporte nativo para operaciones asíncronas
- Alto rendimiento gracias a Starlette y Uvicorn

### 2. Servicios de Aplicación

#### Servicio de Chat/Repaso
- Procesa consultas de los estudiantes
- Recupera información relevante de PDFs del curso
- Genera respuestas educativas utilizando el modelo LLM
- Proporciona referencias a fuentes académicas e imágenes relevantes

#### Servicio de Examen
- Genera exámenes personalizados según tema y dificultad
- Almacena respuestas correctas para validación
- Evalúa respuestas de estudiantes y proporciona retroalimentación

#### Servicio de Juegos
- Gestiona cuatro tipos de juegos educativos
- Procesa interacciones de juego (adivinanzas, respuestas)
- Proporciona retroalimentación educativa sobre términos y conceptos

### 3. Servicios Externos

#### Servicio LLM (GEMINI)
- Integración con la API de Google GEMINI
- Genera texto educativo para todos los modos
- Procesa consultas y genera respuestas estructuradas

#### Servicio de Imágenes (Opcional)
- Busca o genera imágenes relevantes para los temas tratados
- Proporciona URLs para mostrar en las respuestas

### 4. Repositorios de Datos

#### Repositorio de Exámenes
- Almacena exámenes generados y sus respuestas correctas
- Permite recuperar y validar exámenes

#### Biblioteca de PDFs
- Almacena y gestiona los documentos PDF del curso
- Proporciona contenido para responder consultas

## Estructura de Capas

La aplicación sigue una arquitectura de capas:

1. **Capa de Presentación**: Endpoints de API REST que reciben solicitudes y devuelven respuestas.

2. **Capa de Servicios**: Implementa la lógica de negocio para cada modo (chat, examen, juegos).

3. **Capa de Acceso a Datos**: Gestiona el almacenamiento y recuperación de información (PDFs, exámenes, estados de juego).

4. **Capa de Integración**: Conecta con servicios externos como el LLM GEMINI.

## Flujos de Datos Principales

### Flujo del Modo Repaso/Chat

1. El usuario envía una consulta, opcionalmente con referencias a PDFs específicos.
2. El sistema extrae contenido relevante de los PDFs mencionados.
3. El contenido y la consulta se envían al modelo LLM.
4. El LLM genera una respuesta educativa.
5. El sistema enriquece la respuesta con referencias e imágenes relevantes.
6. La respuesta completa se devuelve al usuario.

### Flujo del Modo Examen

1. El usuario solicita un examen sobre un tema específico, con nivel de dificultad.
2. El sistema genera un prompt para el LLM solicitando preguntas de examen.
3. El LLM genera preguntas de opción múltiple y sus respuestas.
4. El sistema almacena las preguntas y respuestas correctas por separado.
5. Las preguntas se envían al usuario sin las respuestas.
6. El usuario responde y envía sus respuestas.
7. El sistema valida las respuestas y proporciona retroalimentación.

### Flujo del Modo Juegos

1. El usuario selecciona un tipo de juego.
2. El sistema genera el contenido del juego utilizando el LLM.
3. El juego se presenta al usuario.
4. El usuario interactúa con el juego (adivinanzas, respuestas).
5. El sistema procesa las interacciones y actualiza el estado del juego.
6. Al finalizar, el sistema proporciona retroalimentación educativa.

## Consideraciones de Escalabilidad

- **Almacenamiento**: En esta implementación se utiliza almacenamiento en memoria, pero el diseño está preparado para migrar a bases de datos persistentes.

- **Servicios Independientes**: La arquitectura modular permite escalar horizontalmente servicios individuales.

- **Asincronía**: El uso de operaciones asíncronas en FastAPI permite manejar múltiples solicitudes concurrentes eficientemente.

- **Configuración Externalizada**: Las variables de entorno permiten configurar el sistema para diferentes entornos.

## Seguridad

- **Validación de Entrada**: Todos los datos de entrada son validados utilizando Pydantic.

- **Manejo de Excepciones**: Sistema centralizado para gestionar errores y excepciones.

- **CORS**: Configuración de seguridad para controlar el acceso desde dominios específicos.

- **Autenticación**: Estructura preparada para implementar autenticación de usuarios (comentado en el código).

## Extensibilidad

La arquitectura está diseñada para ser fácilmente extensible:

- **Nuevos Juegos**: Se pueden agregar nuevos tipos de juegos educativos.

- **Cambio de LLM**: El servicio LLM está abstraído para permitir cambiar el proveedor.

- **Persistencia**: Se puede agregar almacenamiento persistente implementando repositorios alternativos.

- **Autenticación**: El sistema está preparado para implementar autenticación de usuarios.