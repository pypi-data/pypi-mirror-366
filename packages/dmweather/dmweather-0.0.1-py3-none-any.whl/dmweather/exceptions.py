class DMWeatherError (Exception):
    "Excepcion base para excepciones DMWeather"
    pass

class CiudadNoEncontradaError(DMWeatherError):
    "La ciudad no se encuentra especificada"
    pass

class APIError (DMWeatherError):
    "Problemas con la API DE OpenWeatherMap"
    pass

class ConfiguracionError(DMWeatherError):
    "Problemas de configuracion"
    pass

