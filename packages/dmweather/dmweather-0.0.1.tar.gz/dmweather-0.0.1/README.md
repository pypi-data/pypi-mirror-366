# DMWeather 🌤️

**DMWeather** es una librería Python simple y potente para obtener información meteorológica actual y pronósticos utilizando la API gratuita de OpenWeatherMap.

## 🚀 Características

- ✅ Obtener clima actual de cualquier ciudad del mundo
- ✅ Pronóstico del clima para mañana
- ✅ Datos en español
- ✅ Manejo robusto de errores
- ✅ Fácil de usar
- ✅ Documentación completa
- ✅ Tests incluidos

## 📦 Instalación

```bash
pip install dmweather
```

## 🔑 Configuración

1. Obtén tu API key gratuita en [OpenWeatherMap](https://openweathermap.org/api)
2. Regístrate y copia tu API key

## 🛠️ Uso básico

```python
from dmweather import ClimaApp

# Inicializar la aplicación
app = ClimaApp("tu_api_key_aqui")

# Obtener clima actual
clima_actual = app.clima_hoy("Asunción", "PY")
print(f"Temperatura: {clima_actual['temperatura']}°C")
print(f"Descripción: {clima_actual['descripcion']}")

# Obtener pronóstico para mañana
clima_mañana = app.clima_mañana("Buenos Aires", "AR")
print(f"Mañana: {clima_mañana['temperatura_max']}°C máxima")
print(f"Probabilidad de lluvia: {clima_mañana['probabilidad_lluvia']}%")
```

## 📊 Datos disponibles

### `clima_hoy(ciudad, pais="")`
Retorna un diccionario con:
- `ciudad`: Nombre de la ciudad
- `pais`: Código del país
- `fecha`: Fecha y hora actual
- `temperatura`: Temperatura en Celsius
- `sensacion_termica`: Sensación térmica
- `humedad`: Porcentaje de humedad
- `presion`: Presión atmosférica en hPa
- `descripcion`: Descripción del clima en español
- `viento_velocidad`: Velocidad del viento en m/s
- `coordenadas`: Coordenadas geográficas

### `clima_mañana(ciudad, pais="")`
Retorna un diccionario con todos los datos anteriores más:
- `temperatura_min`: Temperatura mínima
- `temperatura_max`: Temperatura máxima
- `probabilidad_lluvia`: Probabilidad de lluvia (%)

## 🎯 Ejemplos avanzados

### Usando la función de utilidad para mostrar datos

```python
from dmweather import ClimaApp, mostrar_clima

app = ClimaApp("tu_api_key")

# Obtener y mostrar clima actual
clima = app.clima_hoy("Madrid", "ES")
mostrar_clima(clima, "actual")

# Obtener y mostrar pronóstico
pronostico = app.clima_mañana("São Paulo", "BR")
mostrar_clima(pronostico, "mañana")
```

### Manejo de errores

```python
from dmweather import ClimaApp, CiudadNoEncontradaError, APIError

app = ClimaApp("tu_api_key")

try:
    clima = app.clima_hoy("CiudadInexistente")
except CiudadNoEncontradaError as e:
    print(f"Ciudad no encontrada: {e}")
except APIError as e:
    print(f"Error de API: {e}")
```

## 🧪 Tests

Para ejecutar los tests:

```bash
python -m pytest tests/
```

O usando unittest:

```bash
python -m unittest tests.test_dmweather -v
```

## 📋 Requisitos

- Python 3.7+
- requests >= 2.25.0
- API key de OpenWeatherMap (gratuita)

## 🌍 Códigos de país soportados

Usa códigos ISO 3166-1 alpha-2:
- `AR` - Argentina
- `PY` - Paraguay  
- `BR` - Brasil
- `ES` - España
- `US` - Estados Unidos
- etc.

## 🤝 Contribuir

1. Aca se debe poner donde contribuir en este caso no quiero aun que se contribuya

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🐛 Reportar bugs

Si encuentras algún bug, por favor crea un issue en [GitHub Issues](https://github.com/tu-usuario/dmweather/issues).

## 👨‍💻 Autor

**Danilo Ramon Mosqueira Cardozo** - [danilo855984@gmail.com](mailto:danilo855984@gmail.com)

---

⭐ ¡Dale una estrella si te gustó el proyecto!
"""