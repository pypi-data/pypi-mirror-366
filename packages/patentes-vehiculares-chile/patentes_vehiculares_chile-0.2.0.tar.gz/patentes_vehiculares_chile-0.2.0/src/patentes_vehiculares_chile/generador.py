# Script para generar patentes vehiculares chilenas
import random
from .validador import calcular_dv
"""Generador de patentes vehiculares chilenas.
"""

# Generar patente vehiculo antiguo
def generar_patente_vehiculo_antiguo() -> str:
    return f"{random.choice('ABCDEFGHKLNMOPRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLNPRSTUVXYZW')}{random.randint(1000, 9999)}"

# Generar patente vehiculo nuevo
def generar_patente_vehiculo_nuevo() -> str:
    consonantes = 'BCDFGHJKLPRSTVWXYZ'
    return f"{''.join(random.choice(consonantes) for _ in range(4))}{random.randint(10, 99)}"

# Generar patente motocicleta antigua
def generar_patente_motocicleta_antigua() -> str:
    return f"{random.choice('BCDFGHJKLPRSTVWXYZ')}{random.choice('BCDFGHJKLPRSTVWXYZ')}{random.randint(100, 999)}"

# Generar patente motocicleta nueva
def generar_patente_motocicleta_nueva() -> str:
    return f"{random.choice('BCDFGHJKLKMNPQRSTVWXYZ')}{random.choice('BCDFGHJKLKMNPQRSTVWXYZ')}{random.randint(100, 999)}"

# Generar RUT chileno
def generar_rut() -> str:
    numero = random.randint(3000000, 25999999)
    digito_verificador = calcular_dv(str(numero))
    return f"{numero}-{digito_verificador}"