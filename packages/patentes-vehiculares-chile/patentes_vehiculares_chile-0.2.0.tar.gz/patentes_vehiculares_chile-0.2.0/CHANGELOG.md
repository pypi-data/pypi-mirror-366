# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [No publicado]

### Agregado
- Soporte para validación de RUT chileno
- Función `calcular_dv` para calcular dígito verificador de RUT
- Función `validar_rut` para validar RUT chilenos
- Soporte para motocicletas (formatos antiguos y nuevos)
- Función `generar_rut` para generar RUT aleatorios válidos
- Función `generar_patente_motocicleta_antigua` 
- Función `generar_patente_motocicleta_nueva`
- Tipo `FormatoRut` para definir estructura de RUT
- Constante `FORMATO_RUT` con patrón de validación

### Cambiado
- Mejorada la función `limpiar_patente` para remover más caracteres especiales
- Actualizado `pyproject.toml` con información de contacto correcta
- Actualizada estructura del proyecto en `ESTRUCTURA.md`
- Refinados los patrones regex para mayor precisión en validación

### Corregido
- Importaciones correctas en `__init__.py`
- Patrones de validación para motocicletas según normativa chilena
- Documentación de ejemplos de uso

## [0.2.0] - 2025-07-31

### Agregado
- Funcionalidad inicial para validar patentes vehiculares chilenas
- Soporte para formatos antiguos (AB1234) y nuevos (ABCD12)
- Generador de patentes aleatorias válidas
- Función para detectar el tipo de patente
- Utilidad para limpiar y normalizar patentes
- Soporte para formatos de motocicletas
- Validación y generación de RUT chilenos

## [0.1.0] - 2025-07-29

### Agregado
- Primera versión de la librería
- Validación básica de patentes vehiculares chilenas
- Generación de patentes aleatorias básica
- Documentación inicial
- Estructura base del proyecto