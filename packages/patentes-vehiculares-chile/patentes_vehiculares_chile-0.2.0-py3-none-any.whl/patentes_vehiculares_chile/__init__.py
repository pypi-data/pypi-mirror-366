"""
Patentes Vehiculares Chile

Una librería Python para validar y trabajar con patentes vehiculares chilenas.
"""

__version__ = "0.2.0"
__author__ = "Jorge Gallardo"
__email__ = "jorgito899@gmail.com"

from .validador import (
    validar_patente, 
    es_formato_valido, 
    detectar_tipo_patente, 
    limpiar_patente,
    calcular_dv,
    validar_rut
)
from .tipos import TipoPatente, FormatoPatente, FormatoRut

from .generador import (
    generar_patente_vehiculo_antiguo,
    generar_patente_vehiculo_nuevo,
    generar_patente_motocicleta_antigua,
    generar_patente_motocicleta_nueva,
    generar_rut
)

__all__ = [
    "validar_patente",
    "es_formato_valido",
    "detectar_tipo_patente",
    "limpiar_patente", 
    "TipoPatente",
    "FormatoPatente",
    "calcular_dv",
    "validar_rut"
]