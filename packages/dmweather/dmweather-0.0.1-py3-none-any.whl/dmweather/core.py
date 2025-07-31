
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from .exceptions import DMWeatherError, CiudadNoEncontradaError, APIError, ConfiguracionError

class ClimaApp:
    """
    DMWeather - Aplicación para obtener información del clima actual y pronóstico
    
    Esta clase permite obtener datos meteorológicos utilizando la API gratuita 
    de OpenWeatherMap.
    
    Attributes:
        api_key (str): Clave de API de OpenWeatherMap
        base_url (str): URL base para las consultas del clima
        geo_url (str): URL base para las consultas de geolocalización
    
    Example:
        >>> from dmweather import ClimaApp
        >>> app = ClimaApp("tu_api_key")
        >>> clima = app.clima_hoy("Asunción", "PY")
        >>> print(clima['temperatura'])
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa la aplicación con la API key de OpenWeatherMap
        
        Args:
            api_key (str): Tu API key de OpenWeatherMap
                          Obtén una gratuita en: https://openweathermap.org/api
        
        Raises:
            ConfiguracionError: Si la API key no es válida
        """
        if not api_key or not isinstance(api_key, str):
            raise ConfiguracionError("Se requiere una API key válida")
        
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
    
    def _obtener_coordenadas(self, ciudad: str, pais: str = "") -> Dict:
        """
        Obtiene las coordenadas geográficas de una ciudad
        
        Args:
            ciudad (str): Nombre de la ciudad
            pais (str, optional): Código del país (ISO 3166-1 alpha-2)
        
        Returns:
            Dict: Diccionario con lat, lon, nombre y país
            
        Raises:
            CiudadNoEncontradaError: Si no se encuentra la ciudad
            APIError: Si hay problemas con la API
        """
        try:
            query = f"{ciudad},{pais}" if pais else ciudad
            url = f"{self.geo_url}/direct"
            params = {
                'q': query,
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise APIError("API key inválida o expirada")
            elif response.status_code == 429:
                raise APIError("Límite de solicitudes excedido")
            
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise CiudadNoEncontradaError(f"No se encontró la ciudad: {ciudad}")
            
            return {
                'lat': data[0]['lat'],
                'lon': data[0]['lon'],
                'nombre': data[0]['name'],
                'pais': data[0]['country']
            }
            
        except requests.RequestException as e:
            raise APIError(f"Error en la solicitud de coordenadas: {str(e)}")
        except KeyError as e:
            raise APIError(f"Error en los datos de coordenadas: {str(e)}")
    
    def clima_hoy(self, ciudad: str, pais: str = "") -> Dict:
        """
        Obtiene el clima actual para hoy
        
        Args:
            ciudad (str): Nombre de la ciudad
            pais (str, optional): Código del país (ej: 'AR', 'PY', 'BR')
        
        Returns:
            Dict: Información completa del clima actual incluyendo:
                - ciudad: Nombre de la ciudad
                - pais: Código del país
                - fecha: Fecha y hora actual
                - temperatura: Temperatura en Celsius
                - sensacion_termica: Sensación térmica
                - humedad: Porcentaje de humedad
                - presion: Presión atmosférica en hPa
                - descripcion: Descripción del clima
                - viento_velocidad: Velocidad del viento en m/s
                - coordenadas: Coordenadas geográficas
        
        Raises:
            CiudadNoEncontradaError: Si la ciudad no existe
            APIError: Si hay problemas con la API
        
        Example:
            >>> app = ClimaApp("tu_api_key")
            >>> clima = app.clima_hoy("Madrid", "ES")
            >>> print(f"Temperatura: {clima['temperatura']}°C")
        """
        try:
            coordenadas = self._obtener_coordenadas(ciudad, pais)
            
            url = f"{self.base_url}/weather"
            params = {
                'lat': coordenadas['lat'],
                'lon': coordenadas['lon'],
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise APIError("API key inválida o expirada")
            elif response.status_code == 429:
                raise APIError("Límite de solicitudes excedido")
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'ciudad': coordenadas['nombre'],
                'pais': coordenadas['pais'],
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'temperatura': data['main']['temp'],
                'sensacion_termica': data['main']['feels_like'],
                'humedad': data['main']['humidity'],
                'presion': data['main']['pressure'],
                'descripcion': data['weather'][0]['description'],
                'icono': data['weather'][0]['icon'],
                'viento_velocidad': data['wind']['speed'],
                'viento_direccion': data['wind'].get('deg', 'N/A'),
                'visibilidad': data.get('visibility', 'N/A'),
                'coordenadas': {
                    'lat': coordenadas['lat'],
                    'lon': coordenadas['lon']
                }
            }
            
        except (CiudadNoEncontradaError, APIError):
            raise
        except Exception as e:
            raise DMWeatherError(f"Error al obtener clima de hoy: {str(e)}")
    
    def clima_mañana(self, ciudad: str, pais: str = "") -> Dict:
        """
        Obtiene el pronóstico del clima para mañana
        
        Args:
            ciudad (str): Nombre de la ciudad
            pais (str, optional): Código del país (ej: 'AR', 'PY', 'BR')
        
        Returns:
            Dict: Información del pronóstico para mañana incluyendo:
                - ciudad: Nombre de la ciudad
                - pais: Código del país
                - fecha_pronostico: Fecha y hora del pronóstico
                - temperatura: Temperatura prevista
                - temperatura_min: Temperatura mínima
                - temperatura_max: Temperatura máxima
                - sensacion_termica: Sensación térmica
                - humedad: Porcentaje de humedad
                - descripcion: Descripción del clima
                - probabilidad_lluvia: Probabilidad de lluvia (%)
                - coordenadas: Coordenadas geográficas
        
        Raises:
            CiudadNoEncontradaError: Si la ciudad no existe
            APIError: Si hay problemas con la API
        
        Example:
            >>> app = ClimaApp("tu_api_key")
            >>> clima = app.clima_mañana("Buenos Aires", "AR")
            >>> print(f"Mañana: {clima['temperatura_max']}°C máxima")
        """
        try:
            coordenadas = self._obtener_coordenadas(ciudad, pais)
            
            url = f"{self.base_url}/forecast"
            params = {
                'lat': coordenadas['lat'],
                'lon': coordenadas['lon'],
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise APIError("API key inválida o expirada")
            elif response.status_code == 429:
                raise APIError("Límite de solicitudes excedido")
            
            response.raise_for_status()
            data = response.json()
            
            # Buscar el pronóstico para mañana
            mañana = datetime.now() + timedelta(days=1)
            fecha_mañana = mañana.strftime('%Y-%m-%d')
            
            # Encontrar el pronóstico más cercano al mediodía de mañana
            pronostico_mañana = None
            for item in data['list']:
                fecha_item = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                hora_item = datetime.fromtimestamp(item['dt']).hour
                
                if fecha_item == fecha_mañana and 11 <= hora_item <= 15:
                    pronostico_mañana = item
                    break
            
            # Si no encuentra uno al mediodía, toma el primero del día siguiente
            if not pronostico_mañana:
                for item in data['list']:
                    fecha_item = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                    if fecha_item == fecha_mañana:
                        pronostico_mañana = item
                        break
            
            if not pronostico_mañana:
                raise DMWeatherError("No se encontró pronóstico para mañana")
            
            fecha_pronostico = datetime.fromtimestamp(pronostico_mañana['dt'])
            
            return {
                'ciudad': coordenadas['nombre'],
                'pais': coordenadas['pais'],
                'fecha_pronostico': fecha_pronostico.strftime('%Y-%m-%d %H:%M:%S'),
                'temperatura': pronostico_mañana['main']['temp'],
                'temperatura_min': pronostico_mañana['main']['temp_min'],
                'temperatura_max': pronostico_mañana['main']['temp_max'],
                'sensacion_termica': pronostico_mañana['main']['feels_like'],
                'humedad': pronostico_mañana['main']['humidity'],
                'presion': pronostico_mañana['main']['pressure'],
                'descripcion': pronostico_mañana['weather'][0]['description'],
                'icono': pronostico_mañana['weather'][0]['icon'],
                'viento_velocidad': pronostico_mañana['wind']['speed'],
                'viento_direccion': pronostico_mañana['wind'].get('deg', 'N/A'),
                'probabilidad_lluvia': pronostico_mañana.get('pop', 0) * 100,
                'coordenadas': {
                    'lat': coordenadas['lat'],
                    'lon': coordenadas['lon']
                }
            }
            
        except (CiudadNoEncontradaError, APIError):
            raise
        except Exception as e:
            raise DMWeatherError(f"Error al obtener clima de mañana: {str(e)}")

# Función de utilidad
def mostrar_clima(clima_data: Dict, tipo: str = "actual") -> None:
    """
    Función de utilidad para mostrar la información del clima de forma legible
    
    Args:
        clima_data (Dict): Datos del clima obtenidos de clima_hoy() o clima_mañana()
        tipo (str): Tipo de clima ("actual" o "mañana")
    
    Example:
        >>> from dmweather import ClimaApp, mostrar_clima
        >>> app = ClimaApp("tu_api_key")
        >>> clima = app.clima_hoy("Asunción", "PY")
        >>> mostrar_clima(clima, "actual")
    """
    print(f"\n=== CLIMA {tipo.upper()} ===")
    print(f"Ciudad: {clima_data['ciudad']}, {clima_data['pais']}")
    
    if tipo == "actual":
        print(f"Fecha actual: {clima_data['fecha']}")
    else:
        print(f"Pronóstico para: {clima_data['fecha_pronostico']}")
    
    print(f"Temperatura: {clima_data['temperatura']:.1f}°C")
    print(f"Sensación térmica: {clima_data['sensacion_termica']:.1f}°C")
    
    if 'temperatura_min' in clima_data:
        print(f"Temperatura mínima: {clima_data['temperatura_min']:.1f}°C")
        print(f"Temperatura máxima: {clima_data['temperatura_max']:.1f}°C")
    
    print(f"Descripción: {clima_data['descripcion'].title()}")
    print(f"Humedad: {clima_data['humedad']}%")
    print(f"Presión: {clima_data['presion']} hPa")
    print(f"Viento: {clima_data['viento_velocidad']} m/s")
    
    if 'probabilidad_lluvia' in clima_data:
        print(f"Probabilidad de lluvia: {clima_data['probabilidad_lluvia']:.0f}%")