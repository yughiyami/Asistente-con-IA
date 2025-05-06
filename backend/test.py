#!/usr/bin/env python3
"""
Script de prueba para verificar la integración de servicios OSINT.
Este script prueba la integración básica con los servicios externos
y verifica que la configuración está correcta.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dotenv import load_dotenv
import httpx
import requests
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl, validator, Field

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("osint_api_test")

# Cargar variables de entorno
load_dotenv()

# Modelos de datos
class ServiceResponse(BaseModel):
    service_name: str
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float

class OSINTRequest(BaseModel):
    target: str
    target_type: str = Field(..., description="email, phone, domain, ip, username, address")
    services: List[str] = []
    
    @validator('target_type')
    def validate_target_type(cls, v):
        allowed_types = ['email', 'phone', 'domain', 'ip', 'username', 'address']
        if v not in allowed_types:
            raise ValueError(f'target_type must be one of {allowed_types}')
        return v

# Configuración de servicios
class ServiceConfig:
    def __init__(self):
        self.services = {
            "webscraping_ai": {
                "api_key": os.getenv("WEBSCRAPING_AI_API_KEY", "demo_api_key"),
                "base_url": "https://api.webscraping.ai",
                "enabled": self._parse_bool(os.getenv("ENABLE_WEBSCRAPING_AI", "True")),
                "rate_limit": int(os.getenv("WEBSCRAPING_AI_RATE_LIMIT", "10")),
            },
            "mattermark": {
                "api_key": os.getenv("MATTERMARK_API_KEY", "demo_api_key"),
                "base_url": "https://api.mattermark.com/companies",
                "enabled": self._parse_bool(os.getenv("ENABLE_MATTERMARK", "True")),
                "rate_limit": int(os.getenv("MATTERMARK_RATE_LIMIT", "5")),
            },
            "global_address": {
                "api_key": os.getenv("GLOBAL_ADDRESS_API_KEY", "demo_api_key"),
                "base_url": "https://globaladdress.p.rapidapi.com",
                "enabled": self._parse_bool(os.getenv("ENABLE_GLOBAL_ADDRESS", "True")),
                "rate_limit": int(os.getenv("GLOBAL_ADDRESS_RATE_LIMIT", "5")),
            },
            "veriphone": {
                "api_key": os.getenv("VERIPHONE_API_KEY", "demo_api_key"),
                "base_url": "https://api.veriphone.io/v2",
                "enabled": self._parse_bool(os.getenv("ENABLE_VERIPHONE", "True")),
                "rate_limit": int(os.getenv("VERIPHONE_RATE_LIMIT", "10")),
            },
            "wayback": {
                "base_url": "https://archive.org/wayback/available",
                "enabled": self._parse_bool(os.getenv("ENABLE_WAYBACK", "True")),
                "rate_limit": int(os.getenv("WAYBACK_RATE_LIMIT", "10")),
            },
            "breach_directory": {
                "api_key": os.getenv("BREACH_DIRECTORY_API_KEY", "demo_api_key"),
                "base_url": "https://breachdirectory.p.rapidapi.com",
                "enabled": self._parse_bool(os.getenv("ENABLE_BREACH_DIRECTORY", "True")),
                "rate_limit": int(os.getenv("BREACH_DIRECTORY_RATE_LIMIT", "5")),
            },
            "eva_pingutil": {
                "base_url": "https://eva.pingutil.com",
                "enabled": self._parse_bool(os.getenv("ENABLE_EVA_PINGUTIL", "True")),
                "rate_limit": int(os.getenv("EVA_PINGUTIL_RATE_LIMIT", "5")),
            },
            "zenrows": {
                "api_key": os.getenv("ZENROWS_API_KEY", "demo_api_key"),
                "base_url": "https://api.zenrows.com",
                "enabled": self._parse_bool(os.getenv("ENABLE_ZENROWS", "True")),
                "rate_limit": int(os.getenv("ZENROWS_RATE_LIMIT", "10")),
            },
        }
    
    def _parse_bool(self, value):
        return value.lower() in ('true', '1', 't', 'yes')
    
    def get_config(self, service_name):
        return self.services.get(service_name)

# Servicios OSINT
class OSINTServices:
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def query_service(self, service_name: str, target: str, target_type: str) -> ServiceResponse:
        start_time = datetime.now()
        
        try:
            service_config = self.config.get_config(service_name)
            if not service_config:
                raise ValueError(f"Service {service_name} not configured")
            
            if not service_config["enabled"]:
                return ServiceResponse(
                    service_name=service_name,
                    status="disabled",
                    error="Service is disabled in configuration",
                    execution_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Implementación específica para cada servicio
            if service_name == "webscraping_ai":
                data = await self._query_webscraping_ai(service_config, target, target_type)
            elif service_name == "mattermark":
                data = await self._query_mattermark(service_config, target, target_type)
            elif service_name == "global_address":
                data = await self._query_global_address(service_config, target, target_type)
            elif service_name == "veriphone":
                data = await self._query_veriphone(service_config, target, target_type)
            elif service_name == "wayback":
                data = await self._query_wayback(service_config, target, target_type)
            elif service_name == "breach_directory":
                data = await self._query_breach_directory(service_config, target, target_type)
            elif service_name == "eva_pingutil":
                data = await self._query_eva_pingutil(service_config, target, target_type)
            elif service_name == "zenrows":
                data = await self._query_zenrows(service_config, target, target_type)
            else:
                raise ValueError(f"Service {service_name} implementation not found")
            
            return ServiceResponse(
                service_name=service_name,
                status="success",
                data=data,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        
        except Exception as e:
            logger.error(f"Error in {service_name}: {str(e)}")
            return ServiceResponse(
                service_name=service_name,
                status="error",
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    # Implementaciones mock de cada servicio para prueba
    async def _query_webscraping_ai(self, config, target, target_type):
        # Simular una petición a webscraping.ai
        if target_type == "domain":
            url = f"{config['base_url']}/html?api_key={config['api_key']}&url=https://{target}"
            # En un caso real, aquí haríamos la petición:
            # response = await self.client.get(url)
            # return response.json()
            
            # Para la prueba, devolvemos datos simulados
            return {"status": "success", "simulated": True, "source": "webscraping_ai"}
        raise ValueError(f"Target type {target_type} not supported by webscraping_ai")
    
    async def _query_mattermark(self, config, target, target_type):
        if target_type == "domain":
            # Simular una búsqueda en Mattermark
            return {"status": "success", "simulated": True, "source": "mattermark", "company_info": {"name": "Example Corp", "domain": target}}
        raise ValueError(f"Target type {target_type} not supported by mattermark")

    async def _query_global_address(self, config, target, target_type):
        if target_type == "address":
            # Simular validación de dirección
            return {"status": "success", "simulated": True, "source": "global_address", "valid": True}
        raise ValueError(f"Target type {target_type} not supported by global_address")
    
    async def _query_veriphone(self, config, target, target_type):
        if target_type == "phone":
            # Simular validación de teléfono
            return {
                "status": "success", 
                "simulated": True, 
                "source": "veriphone", 
                "phone_valid": True, 
                "country": "US", 
                "phone_type": "mobile"
            }
        raise ValueError(f"Target type {target_type} not supported by veriphone")
    
    async def _query_wayback(self, config, target, target_type):
        if target_type == "domain":
            # Simular búsqueda en Wayback Machine
            return {
                "status": "success", 
                "simulated": True, 
                "source": "wayback", 
                "archived_snapshots": {
                    "closest": {
                        "available": True,
                        "url": f"https://web.archive.org/web/20220101/{target}",
                        "timestamp": "20220101"
                    }
                }
            }
        raise ValueError(f"Target type {target_type} not supported by wayback")
    
    async def _query_breach_directory(self, config, target, target_type):
        if target_type == "email":
            # Simular búsqueda de brechas
            return {
                "status": "success", 
                "simulated": True, 
                "source": "breach_directory", 
                "found": True, 
                "breaches": ["example_breach_1", "example_breach_2"]
            }
        raise ValueError(f"Target type {target_type} not supported by breach_directory")
    
    async def _query_eva_pingutil(self, config, target, target_type):
        if target_type == "email":
            # Simular validación de email
            return {
                "status": "success", 
                "simulated": True, 
                "source": "eva_pingutil", 
                "valid": True, 
                "disposable": False
            }
        raise ValueError(f"Target type {target_type} not supported by eva_pingutil")
    
    async def _query_zenrows(self, config, target, target_type):
        if target_type == "domain":
            # Simular web scraping
            return {
                "status": "success", 
                "simulated": True, 
                "source": "zenrows", 
                "content": "<html><body><h1>Ejemplo de página</h1></body></html>"
            }
        raise ValueError(f"Target type {target_type} not supported by zenrows")

# Controlador principal
async def process_osint_request(request: OSINTRequest) -> Dict:
    config = ServiceConfig()
    services = OSINTServices(config)
    
    results = {}
    tasks = []
    
    # Si no se especifican servicios, usar todos los habilitados
    if not request.services:
        request.services = [s for s, cfg in config.services.items() if cfg["enabled"]]
    
    # Ejecutar consultas en paralelo
    for service_name in request.services:
        tasks.append(services.query_service(service_name, request.target, request.target_type))
    
    responses = await asyncio.gather(*tasks)
    
    # Ordenar respuestas
    for response in responses:
        results[response.service_name] = {
            "status": response.status,
            "data": response.data,
            "error": response.error,
            "execution_time": response.execution_time,
        }
    
    await services.close()
    
    return {
        "target": request.target,
        "target_type": request.target_type,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

# Función principal para probar el script
async def main():
    logger.info("Iniciando prueba de integración OSINT API")
    
    # Ejemplo 1: Buscar información sobre un dominio
    domain_request = OSINTRequest(
        target="example.com",
        target_type="domain",
        services=["webscraping_ai", "wayback", "zenrows"]
    )
    
    logger.info(f"Procesando solicitud para dominio: {domain_request.target}")
    domain_results = await process_osint_request(domain_request)
    print(json.dumps(domain_results, indent=2, default=str))
    
    # Ejemplo 2: Verificar un email
    email_request = OSINTRequest(
        target="test@example.com",
        target_type="email",
        services=["breach_directory", "eva_pingutil"]
    )
    
    logger.info(f"Procesando solicitud para email: {email_request.target}")
    email_results = await process_osint_request(email_request)
    print(json.dumps(email_results, indent=2, default=str))
    
    # Ejemplo 3: Validar un número de teléfono
    phone_request = OSINTRequest(
        target="+1234567890",
        target_type="phone",
        services=["veriphone"]
    )
    
    logger.info(f"Procesando solicitud para teléfono: {phone_request.target}")
    phone_results = await process_osint_request(phone_request)
    print(json.dumps(phone_results, indent=2, default=str))
    
    logger.info("Prueba de integración OSINT API completada")

if __name__ == "__main__":
    # Ejecutar el script de prueba
    asyncio.run(main())