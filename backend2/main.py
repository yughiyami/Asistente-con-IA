"""
Punto de entrada principal de la aplicación.
Ejecuta el servidor FastAPI con Uvicorn.
"""

import uvicorn
import sys
from pathlib import Path

# Agregar el directorio actual al path de Python
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings


def main():
    """
    Función principal que inicia el servidor.
    """
    # Configuración de Uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=settings.debug,
        workers=1 if settings.debug else 4
    )


if __name__ == "__main__":
    print(f"🚀 Iniciando {settings.app_name} v{settings.app_version}")
    print(f"📍 Servidor en http://{settings.host}:{settings.port}")
    print(f"📚 Documentación en http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Modo debug: {'Activado' if settings.debug else 'Desactivado'}")
    print("-" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {str(e)}")
        sys.exit(1)