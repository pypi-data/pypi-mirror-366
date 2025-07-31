
import unittest
from unittest.mock import patch, Mock
import sys
import os

# Agregar el directorio padre al path para importar dmweather
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dmweather.core import ClimaApp
from dmweather.exceptions import ConfiguracionError, DMWeatherError, CiudadNoEncontradaError, APIError

class TestDMWeather(unittest.TestCase):
    """Tests para la librería DMWeather"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.api_key = "test_api_key_123"
        self.app = ClimaApp(self.api_key)
    
    def test_inicializacion_correcta(self):
        """Test de inicialización correcta de ClimaApp"""
        app = ClimaApp("api_key_valida")
        self.assertEqual(app.api_key, "api_key_valida")
        self.assertIn("openweathermap.org", app.base_url)
    
    def test_inicializacion_sin_api_key(self):
        """Test que verifica error sin API key"""
        with self.assertRaises(ConfiguracionError):
            ClimaApp("")
        
        with self.assertRaises(ConfiguracionError):
            ClimaApp(None)
    
    @patch('dmweather.core.requests.get')
    def test_clima_hoy_exitoso(self, mock_get):
        """Test de obtención exitosa del clima actual"""
        # Mock para coordenadas
        mock_coordenadas = Mock()
        mock_coordenadas.json.return_value = [{
            'lat': -25.3040,
            'lon': -57.6094,
            'name': 'Asunción',
            'country': 'PY'
        }]
        mock_coordenadas.status_code = 200
        mock_coordenadas.raise_for_status = Mock()
        
        # Mock para clima
        mock_clima = Mock()
        mock_clima.json.return_value = {
            'main': {
                'temp': 25.5,
                'feels_like': 28.0,
                'humidity': 70,
                'pressure': 1013
            },
            'weather': [{
                'description': 'cielo claro',
                'icon': '01d'
            }],
            'wind': {
                'speed': 3.5,
                'deg': 180
            },
            'visibility': 10000
        }
        mock_clima.status_code = 200
        mock_clima.raise_for_status = Mock()
        
        # Configurar el mock para retornar diferentes respuestas
        mock_get.side_effect = [mock_coordenadas, mock_clima]
        
        resultado = self.app.clima_hoy("Asunción", "PY")
        
        self.assertEqual(resultado['ciudad'], 'Asunción')
        self.assertEqual(resultado['pais'], 'PY')
        self.assertEqual(resultado['temperatura'], 25.5)
        self.assertEqual(resultado['descripcion'], 'cielo claro')
        self.assertIn('fecha', resultado)
        self.assertIn('coordenadas', resultado)
    
    @patch('dmweather.core.requests.get')
    def test_ciudad_no_encontrada(self, mock_get):
        """Test para ciudad no encontrada"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with self.assertRaises(CiudadNoEncontradaError):
            self.app.clima_hoy("CiudadInexistente", "XX")
    
    @patch('dmweather.core.requests.get')
    def test_api_key_invalida(self, mock_get):
        """Test para API key inválida"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with self.assertRaises(APIError) as context:
            self.app.clima_hoy("Madrid", "ES")
        
        self.assertIn("API key inválida", str(context.exception))
    
    @patch('dmweather.core.requests.get')
    def test_limite_solicitudes_excedido(self, mock_get):
        """Test para límite de solicitudes excedido"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with self.assertRaises(APIError) as context:
            self.app.clima_hoy("París", "FR")
        
        self.assertIn("Límite de solicitudes", str(context.exception))

if __name__ == '__main__':
    # Ejecutar tests
    unittest.main(verbosity=2)