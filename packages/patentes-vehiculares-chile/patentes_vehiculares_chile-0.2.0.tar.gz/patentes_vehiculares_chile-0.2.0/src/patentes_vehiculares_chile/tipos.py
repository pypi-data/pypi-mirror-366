"""
Tipos de datos para patentes vehiculares chilenas.
"""

from enum import Enum
from typing import NamedTuple


class TipoPatente(Enum):
    """Tipos de patentes vehiculares en Chile."""
    ANTIGUA = "antigua"  # Formato: AB1234
    NUEVA = "nueva"      # Formato: ABCD12


class FormatoPatente(NamedTuple):
    """Estructura que define el formato de una patente."""
    patron: str
    longitud: int
    descripcion: str

class FormatoRut(NamedTuple):
    """Estructura que define el formato de un RUT chileno."""
    patron: str
    longitud: int
    descripcion: str

# Formatos de patentes chilenas 1845-2007
FORMATO_VEHICULO_ANTIGUO= FormatoPatente(
    # De acuerdo a la normativa chilena, las PPU antiguas deben tener 2 letras y 4 números
    patron=r"^[ABCDEFGHKLNMOPRSTUVWXYZ][ABCDEFGHIJKLNPRSTUVXYZW][1-9][0-9]{3}$",
    longitud=6,
    descripcion="Formato antiguo: 2 letras + 4 números (ej: AB1234)"
)

# Formatos de patentes chilenas 2008-2023
FORMATO_VEHICULO_NUEVO = FormatoPatente(
    # De acuerdo a la normativa chilena, las letras deben ser consonantes y no vocales, además de dejar de lado
    # las letras M, N, Ñ y Q para evitar confusiones y que se generen siglas groseras.
    patron=r"^[BCDFGHJKLPRSTVWXYZ]{4}[1-9][0-9]{1}$",
    longitud=6,
    descripcion="Formato nuevo: 4 letras + 2 números (ej: BCDF12)"
)

# Formato antiguo de patentes de motocicletas chilenas
FORMATO_MOTOCICLETA_ANTIGUO = FormatoPatente(
    # Formato específico para motocicletas, que puede variar según normativa
    patron=r"^[BCDFGHJKLPRSTVWXYZ]{2}[1-9][0-9]{2}$",
    longitud=5,
    descripcion="Formato motocicleta: 2 letras + 3 números (ej: AB123)"
)

# Formato nuevo de patentes de motocicletas chilenas
FORMATO_MOTOCICLETA_NUEVO = FormatoPatente(
    # Formato específico para motocicletas, que puede variar según normativa
    # Pueden contener M, N y Q
    patron=r"^[BCDFGHJKLKMNPQRSTVWXYZ]{3}[1-9][0-9]$",
    longitud=5,
    descripcion="Formato motocicleta: 3 letras + 2 números (ej: ABC12)"
)

FORMATO_RUT = FormatoRut(
    # Formato específico para RUT chileno
    patron=r"^\d{1,8}-[0-9K]$",
    longitud=10,
    descripcion="Formato RUT: 1-8 dígitos + guion + dígito verificador (ej: 12345678-K)"
)

# # Formato remolques (REVISAR)
# FORMATO_REMOLQUE = FormatoPatente(
#     # Formato específico para remolques, que puede variar según normativa
#     patron=r"^[BCDFGHJKLKMNPQRSTVWXYZ]{2}[1-9][0-9]{2}$",
#     longitud=5,
#     descripcion="Formato remolque: 2 letras + 3 números (ej: AB123)"
# )

########################################################################
########################################################################
#
# Falta el formato de: Carabineros, Militares, Diplomáticos, etc.
#
########################################################################
########################################################################