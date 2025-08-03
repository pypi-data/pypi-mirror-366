"""A Python client for the MeteoLux API."""
import typing
from typing import Any, Optional

import httpx

from .exceptions import NotFoundError
from .models import (
  ATCReport,
  Bookmarks,
  InObservation,
  ObservationMetadataResponse,
  ObservationResponse,
  User,
  WeatherResponse,
)


class AsyncMeteoLuxClient:
  """A Python client for the MeteoLux API, built with httpx and Pydantic.

  This client is generated from the OpenAPI specification and provides
  methods for all available endpoints, returning structured Pydantic models.
  """

  def __init__(self, base_url: str = 'https://metapi.ana.lu/api/v1') -> None:
    """Initializes the client with the base URL.

    Args:
        base_url (str): The base URL for the API.
    """
    self.base_url = base_url
    self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

  async def _request(self, method: str, endpoint: str, response_model: Optional[Any] = None, **kwargs: Any) -> Any:
    """Internal method to handle all API requests and common error handling.

    Args:
        method (str): The HTTP method (e.g., "GET", "POST").
        endpoint (str): The API endpoint path.
        response_model (Optional[Any]): The Pydantic model to use for response parsing.
        **kwargs: Additional arguments for the httpx request (e.g., params, json).

    Returns:
        Any: The Pydantic model instance or raw JSON data.

    Raises:
        NotFoundError: If the API returns a 404 Not Found status code.
        httpx.HTTPStatusError: If the response status code is another error.
        httpx.RequestError: For network-related issues.
    """
    try:
      response = await self.client.request(method, endpoint, **kwargs)
      response.raise_for_status()

      if response.status_code == 204:
        return None

      data = response.json()
      if response_model:
        return response_model.model_validate(data)
      return data

    except httpx.HTTPStatusError as exc:
      if exc.response.status_code == 404:
        raise NotFoundError(detail=exc.response.text) from exc

      raise
    except httpx.RequestError:
      raise

  # --- ATC Endpoints ---

  async def get_atc_report(self) -> ATCReport:
    """Get data for the ATC dashboard.

    Corresponds to GET /atc/report.

    Returns:
        ATCReport: An ATCReport Pydantic model instance.
    """
    endpoint = '/atc/report'
    return await self._request('GET', endpoint, response_model=ATCReport)

  # --- HVD Endpoints ---

  async def get_observations_hvd(self) -> ObservationResponse:
    """Return last minute observation data.

    Corresponds to GET /hvd/observations.

    Returns:
        ObservationResponse: An ObservationResponse Pydantic model instance.
    """
    endpoint = '/hvd/observations'
    return await self._request('GET', endpoint, response_model=ObservationResponse)

  async def get_observations_metadata_hvd(self) -> ObservationMetadataResponse:
    """Return observations metadata.

    Corresponds to GET /hvd/observations/metadata.

    Returns:
        ObservationMetadataResponse: An ObservationMetadataResponse Pydantic model instance.
    """
    endpoint = '/hvd/observations/metadata'
    return await self._request('GET', endpoint, response_model=ObservationMetadataResponse)

  async def get_station_information_hvd(self, station_id: str) -> list[Any]:
    """Return station information, by ID.

    Corresponds to GET /hvd/stations/{station_id}.

    Args:
        station_id (str): The ID of the station to retrieve.

    Returns:
        Any: Station data from the response. The OpenAPI spec indicates the return type is a list of Stations.
    """
    endpoint = f'/hvd/stations/{station_id}'
    return await self._request('GET', endpoint)

  async def get_all_station_information_hvd(self) -> list[Any]:
    """Return all station information.

    Corresponds to GET /hvd/stations.

    Returns:
        list[Any]: A list of station objects. The OpenAPI spec indicates the return type is a list of Stations.
    """
    endpoint = '/hvd/stations'
    return await self._request('GET', endpoint)

  # --- MetApp Endpoints ---

  async def get_weather(self, langcode: str = 'fr', city: Optional[int] = None, lat: Optional[float] = None, long: Optional[float] = None) -> WeatherResponse:
    """Get weather for a city/language or lat/long.

    Corresponds to GET /metapp/weather.

    Args:
        langcode (str): The language code (fr, de, en, lb).
        city (Optional[int]): The city ID.
        lat (Optional[float]): Latitude.
        long (Optional[float]): Longitude.

    Returns:
        WeatherResponse: A WeatherResponse Pydantic model instance.
    """
    endpoint = '/metapp/weather'
    params: dict[str, str] = {'langcode': langcode}
    if city is not None:
      params['city'] = str(city)
    if lat is not None:
      params['lat'] = str(lat)
    if long is not None:
      params['long'] = str(long)
    return await self._request('GET', endpoint, params=params, response_model=WeatherResponse)

  async def update_user(self, user_data: User) -> None:
    """Add or update a user's token and preferences.

    Corresponds to POST /metapp/user.

    Args:
        user_data (User): A Pydantic User model instance.
    """
    endpoint = '/metapp/user'
    await self._request('POST', endpoint, json=user_data.model_dump(by_alias=True))

  async def get_bookmarks(self, langcode: str = 'fr', lat: Optional[float] = None, long: Optional[float] = None) -> Bookmarks:
    """Return all cities and the closest one if lat/long are given.

    Corresponds to GET /metapp/bookmarks.

    Args:
        langcode (str): The language code (fr, de, en, lb).
        lat (Optional[float]): Latitude.
        long (Optional[float]): Longitude.

    Returns:
        Bookmarks: A Bookmarks Pydantic model instance.
    """
    endpoint = '/metapp/bookmarks'
    params: dict[str, str] = {'langcode': langcode}
    if lat is not None:
      params['lat'] = str(lat)
    if long is not None:
      params['long'] = str(long)
    return await self._request('GET', endpoint, params=params, response_model=Bookmarks)

  async def get_interface_texts(self, lang: typing.Literal['fr', 'de', 'en', 'lb'] = 'fr') -> dict[str, Any]:
    """Return translated interface texts for the mobile app.

    Note: The spec for this endpoint's response is an un-typed object.

    Corresponds to GET /metapp/text.

    Args:
        lang (str): The language code (fr, de, en, lb).

    Returns:
        dict[str, Any]: A dictionary with translated strings.
    """
    endpoint = '/metapp/text'
    params = {'lang': lang}
    return await self._request('GET', endpoint, params=params)

  async def stream_image(self, filename: str) -> httpx.Response:
    """Stream an image from the cluster.

    Corresponds to GET /metapp/image/{filename}.

    Args:
        filename (str): The name of the image file.

    Returns:
        httpx.Response: The raw httpx Response object to handle streaming.
    """
    endpoint = f'/metapp/image/{filename}'
    return await self.client.get(endpoint, timeout=10.0)

  async def get_observations_metapp(self) -> list[Any]:
    """Return participative observations in the last 30 minutes.

    Note: The spec for this endpoint's response is an array of untyped objects.

    Corresponds to GET /metapp/observations.

    Returns:
        list[Any]: A list of objects.
    """
    endpoint = '/metapp/observations'
    return await self._request('GET', endpoint)

  async def add_observation(self, observation_data: InObservation) -> str:
    """Add a new observation.

    Corresponds to POST /metapp/observation.

    Args:
        observation_data (InObservation): An InObservation Pydantic model instance.

    Returns:
        str: The successful response message.
    """
    endpoint = '/metapp/observation'
    return await self._request('POST', endpoint, json=observation_data.model_dump())

  async def close(self) -> None:
    """Closes the httpx client."""
    await self.client.aclose()
