# micronumpy

`micronumpy` es una reimplementación ultraligera y pura en Python de las funcionalidades más esenciales de la API de NumPy. Está diseñada para entornos donde las dependencias pesadas como el NumPy completo no son una opción, como dispositivos con recursos limitados o para proyectos que buscan la máxima portabilidad.

## Características Principales

- Objeto `ndarray` para cálculo numérico.
- Operaciones vectorizadas (`+`, `-`, `*`).
- Multiplicación de matrices con el operador `@`.
- Creación de arrays (`zeros`, `array`).
- Cero dependencias externas.

## Instalación

```bash
pip install .
