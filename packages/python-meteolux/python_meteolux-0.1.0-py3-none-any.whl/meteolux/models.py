"""API models."""

from datetime import date, datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class Icon(BaseModel):
  """Base icon."""

  id: int
  name: str


class Wind(BaseModel):
  """Wind model."""

  direction: str
  speed: str
  gusts: Optional[str] = None


class Temperature(BaseModel):
  """Temperature model."""

  temperature: Union[int, list[int]]
  humidex: Optional[str] = None
  felt: Optional[int] = None


class CurrentWeather(BaseModel):
  """Part of the global weather model."""

  date: datetime
  icon: Icon
  wind: Wind
  rain: str
  snow: str
  type: Literal['current'] = 'current'
  temperature: Temperature


class DailyWeather(BaseModel):
  """For the list of following days."""

  date: datetime
  icon: Icon
  wind: Wind
  rain: str
  snow: str
  type: Literal['daily'] = 'daily'
  temperature_min: Temperature = Field(..., alias='temperatureMin')
  temperature_max: Temperature = Field(..., alias='temperatureMax')
  sunshine: int
  uv_index: int = Field(..., alias='uvIndex')


class HourlyWeather(BaseModel):
  """For the list of following hours."""

  date: datetime
  icon: Icon
  wind: Wind
  rain: str
  snow: str
  type: Literal['hourly'] = 'hourly'
  temperature: Temperature


class Trend(BaseModel):
  """Forecast part of data."""

  date: date
  min_temp: float = Field(..., alias='minTemp')
  max_temp: float = Field(..., alias='maxTemp')
  precipitation: float


class Climatology(BaseModel):
  """History part of data."""

  date: datetime
  min_temp: float = Field(..., alias='minTemp')
  max_temp: float = Field(..., alias='maxTemp')
  precipitation: float
  mean_temp: float = Field(..., alias='meanTemp')
  sunshine: Optional[float] = None


class GraphicalData(BaseModel):
  """Graphical group of data."""

  history: list[Climatology]
  forecast: list[Trend]


class Vigilance(BaseModel):
  """Vigilance model."""

  datetime_start: datetime = Field(..., alias='datetimeStart')
  datetime_end: datetime = Field(..., alias='datetimeEnd')
  level: Literal[2, 3, 4]
  type: int
  group: int
  region: Literal['north', 'south', 'all']
  description: str


class RoadStatusItem(BaseModel):
  """Road status item model as per the spec."""

  date: Union[date, list[str]]
  description: str


class ImageOut(BaseModel):
  """Image with url."""

  date: datetime
  provider: str
  url: str = Field(..., max_length=2083, min_length=1)


class Radar(BaseModel):
  """Radar image model."""

  real_time: list[ImageOut] = Field(..., alias='realTime')
  forecast: list[ImageOut]


class Satellite(BaseModel):
  """Satellite image model."""

  infrared: list[ImageOut]
  visual: list[ImageOut]


class MoonIcon(BaseModel):
  """As different id are used."""

  id: str
  name: str


class Ephemeris(BaseModel):
  """Ephemeris model."""

  date: date
  sunrise: str
  sunset: str
  moonrise: str
  moonset: str
  sunshine: str
  moon_icon: MoonIcon = Field(..., alias='moonIcon')
  uv_index: int = Field(..., alias='uvIndex', ge=0.0, le=12.0)


class ATCReportForecast(BaseModel):
  """Forecast for ATC dashboard."""

  hourly: list['HourlyWindForecast']


class ATCReport(BaseModel):
  """Data for ATC dashboard."""

  forecast: ATCReportForecast


class HourlyWindForecast(BaseModel):
  """Hourly wind report, at different altitude (feet)."""

  date: datetime
  qnh: int
  wind: Wind
  wind1500: Wind
  wind2500: Wind
  wind5000: Wind
  wind10000: Wind


class BookmarkCity(BaseModel):
  """With additional info for mobile app ep."""

  id: int
  name: str
  region: Literal['N', 'S'] = 'S'
  canton: Literal[
    'Capellen', 'Clervaux', 'Diekirch', 'Echternach', 'Esch-sur-Alzette', 'Grevenmacher', 'Luxembourg', 'Mersch', 'Redange', 'Remich', 'Vianden', 'Wiltz'
  ]
  domain: Literal['villes', 'lieu', 'fluvial']
  lat: float
  long: float
  temperature: float
  icon: Icon


class Bookmarks(BaseModel):
  """Bookmarks model."""

  cities: list[BookmarkCity]
  nearest_city: Optional[BookmarkCity] = Field(None, alias='nearestCity')


class InObservation(BaseModel):
  """Observation from public users."""

  lat: float = Field(..., ge=-90.0, le=90.0)
  long: float = Field(..., ge=-180.0, le=180.0)
  description: str = Field(..., max_length=1024)
  weather: int


class SensorLevel(BaseModel):
  """Sensor level definition."""

  level_type: Literal['height_above_ground'] = Field(..., alias='levelType')
  unit: Literal['m']
  value: float = Field(..., ge=0.0)


class ObservationMetadata(BaseModel):
  """Sensor definition."""

  id: str
  name: str
  description: str
  data_type: Literal['realtime', 'climate'] = Field(..., alias='dataType')
  unit: Literal['m', 'm/s', '%', '1/10 kt', 'degC', 'degrees', 'ft', 'hPa', 'mm']
  category: Literal['Wind', 'Cloud Cover', 'Atmospheric pressure', 'Precipitation', 'Temperature', 'Humidity', 'Visibility']
  performance_category: Literal['A', 'B', 'C', 'D', 'E'] = Field(..., alias='performanceCategory')
  qualitycode: Literal[0, 1, 2, 3, 4, 5, 6, 7]
  timeoffsets: Literal['PT0H']
  timeresolution: Literal['PT1M', 'PT1H']
  sensorlevels: Optional[SensorLevel] = None


class ObservationMetadataResponse(BaseModel):
  """Elements metadata."""

  licence: list[str] = ['Creative Commons', 'https://creativecommons.org/public-domain/cc0/']
  doc_url: str = Field('/docs', alias='docUrl')
  data: list[ObservationMetadata]
  total_item_count: int = Field(1, alias='totalItemCount')
  quality_codes: dict[str, str] = Field({'0': 'Value is controlled and found O.K.'}, alias='qualityCodes')
  performance_category: dict[str, str] = Field(
    {'A': 'The sensor type fulfills the requirements from WMO/CIMOs on measurement accuracy, calibration and maintenance.'}, alias='performanceCategory'
  )


class ObservationResponseData(BaseModel):
  """Model to link gendata id to their values."""

  id: str
  value: Union[int, float]


class ObservationResponse(BaseModel):
  """Last Observations."""

  licence: list[str] = ['Creative Commons', 'https://creativecommons.org/public-domain/cc0/']
  doc_url: str = Field('/docs', alias='docUrl')
  data: list[ObservationResponseData]
  total_item_count: int = Field(1, alias='totalItemCount')
  timestamp: datetime


class OutCity(BaseModel):
  """City with translated name."""

  id: int
  name: str
  region: Literal['N', 'S'] = 'S'
  canton: Literal[
    'Capellen', 'Clervaux', 'Diekirch', 'Echternach', 'Esch-sur-Alzette', 'Grevenmacher', 'Luxembourg', 'Mersch', 'Redange', 'Remich', 'Vianden', 'Wiltz'
  ]
  domain: Literal['villes', 'lieu', 'fluvial']
  lat: float
  long: float


class VigilanceSettings(BaseModel):
  """User settings for notifications."""

  level: Literal[2, 3, 4]
  type_air: bool = Field(False, alias='typeAir')
  type_cold: bool = Field(False, alias='typeCold')
  type_flooding: bool = Field(False, alias='typeFlooding')
  type_heat: bool = Field(False, alias='typeHeat')
  type_ice: bool = Field(False, alias='typeIce')
  type_rain: bool = Field(False, alias='typeRain')
  type_snow: bool = Field(False, alias='typeSnow')
  type_storm: bool = Field(False, alias='typeStorm')
  type_wind: Optional[bool] = Field(None, alias='typeWind')
  zone_north: bool = Field(..., alias='zoneNorth')
  zone_south: bool = Field(..., alias='zoneSouth')


class User(BaseModel):
  """User model."""

  language: Literal['fr', 'de', 'en', 'lb']
  push_token: str = Field(..., alias='pushToken', max_length=50)
  push_morning: bool = Field(False, alias='pushMorning')
  push_evening: bool = Field(False, alias='pushEvening')
  device: str
  version: str
  buildversion: str
  vigilance: VigilanceSettings


class WeatherResponseForecast(BaseModel):
  """Forecast model."""

  current: CurrentWeather
  hourly: list[HourlyWeather]
  daily: list[DailyWeather]


class WeatherResponse(BaseModel):
  """Final weather output from the backend."""

  city: OutCity
  forecast: WeatherResponseForecast
  vigilances: list[Vigilance]
  road_status: list[RoadStatusItem] = Field(..., alias='roadStatus')
  ephemeris: Ephemeris
  radar: Radar
  satellite: Satellite
  data: GraphicalData
