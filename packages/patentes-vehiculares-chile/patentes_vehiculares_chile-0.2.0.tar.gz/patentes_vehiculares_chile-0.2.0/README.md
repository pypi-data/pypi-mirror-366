# Patentes Vehiculares Chile

Una librería Python para validar y trabajar con patentes vehiculares chilenas.

## Instalación

```bash
pip install patentes-vehiculares-chile
```

## Uso

### Validación de Patentes

```python
from patentes_vehiculares_chile import validar_patente, detectar_tipo_patente, limpiar_patente

# Validar una patente
es_valida = validar_patente("ABCD12")
print(es_valida)  # True

# Detectar tipo de patente
tipo = detectar_tipo_patente("AB1234")
print(tipo)  # TipoPatente.ANTIGUA

# Limpiar una patente
patente_limpia = limpiar_patente("  ab-12.34  ")
print(patente_limpia)  # "AB1234"
```

### Validación de RUT

```python
from patentes_vehiculares_chile import validar_rut, calcular_dv

# Validar un RUT
es_valido = validar_rut("12345678-5")
print(es_valido)  # True o False

# Calcular dígito verificador
dv = calcular_dv("12345678")
print(dv)  # "5"
```

### Generación de Patentes y RUT

```python
from patentes_vehiculares_chile import (
    generar_patente_vehiculo_antiguo,
    generar_patente_vehiculo_nuevo,
    generar_patente_motocicleta_antigua,
    generar_patente_motocicleta_nueva,
    generar_rut
)

# Generar patentes
patente_antigua = generar_patente_vehiculo_antiguo()
print(patente_antigua)  # "AB1234"

patente_nueva = generar_patente_vehiculo_nuevo()
print(patente_nueva)  # "BCDF12"

moto_antigua = generar_patente_motocicleta_antigua()
print(moto_antigua)  # "BC123"

moto_nueva = generar_patente_motocicleta_nueva()
print(moto_nueva)  # "BCD12"

# Generar RUT
rut = generar_rut()
print(rut)  # "12345678-5"
```

## Características

- **Validación de patentes vehiculares chilenas**
  - Soporte para formatos antiguos (AB1234) y nuevos (ABCD12)
  - Validación de motocicletas (formatos antiguos y nuevos)
  - Detección automática del tipo de patente

- **Validación de RUT chileno**
  - Validación completa con dígito verificador
  - Cálculo de dígito verificador

- **Generación de datos**
  - Generación de patentes válidas (vehículos y motocicletas)
  - Generación de RUT válidos

- **Utilidades**
  - Limpieza y normalización de patentes
  - Tipos de datos bien definidos

## Formatos Soportados

### Patentes de Vehículos
- **Antiguo (1845-2007)**: 2 letras + 4 números (ej: AB1234)
- **Nuevo (2008-2023)**: 4 consonantes + 2 números (ej: BCDF12)

### Patentes de Motocicletas
- **Antiguo**: 2 letras + 3 números (ej: BC123)
- **Nuevo**: 3 letras + 2 números (ej: BCD12)

### RUT Chileno
- **Formato**: 1-8 dígitos + guión + dígito verificador (ej: 12345678-5)

## API Reference

### Funciones de Validación
- `validar_patente(patente: str) -> bool`
- `es_formato_valido(patente: str) -> bool`
- `detectar_tipo_patente(patente: str) -> Optional[TipoPatente]`
- `validar_rut(rut: str) -> bool`
- `calcular_dv(rut_num: str) -> str`

### Funciones de Generación
- `generar_patente_vehiculo_antiguo() -> str`
- `generar_patente_vehiculo_nuevo() -> str`
- `generar_patente_motocicleta_antigua() -> str`
- `generar_patente_motocicleta_nueva() -> str`
- `generar_rut() -> str`

### Utilidades
- `limpiar_patente(patente: str) -> str`

### Tipos de Datos
- `TipoPatente`: Enum con valores `ANTIGUA` y `NUEVA`
- `FormatoPatente`: Estructura que define formatos de patentes
- `FormatoRut`: Estructura que define formato de RUT

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.