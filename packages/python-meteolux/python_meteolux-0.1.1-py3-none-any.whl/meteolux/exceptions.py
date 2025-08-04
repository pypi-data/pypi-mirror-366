"""Custom exceptions for the MeteoLux API client."""


class MeteoLuxError(Exception):
  """Base exception for the MeteoLux API client."""


class NotFoundError(MeteoLuxError):
  """Raised when the API returns a 404 Not Found status."""

  def __init__(self, detail: str) -> None:
    """Initializes the NotFoundError with a detail message.

    Args:
        detail (str): The error message from the API.
    """
    self.detail = detail
    super().__init__(self.detail)


class ValidationError(MeteoLuxError):
  """Raised when there is a validation error in the Pydantic models."""

  def __init__(self, detail: str) -> None:
    """Initializes the ValidationError with a detail message.

    Args:
        detail (str): The error message from the API.
    """
    self.detail = detail
    super().__init__(self.detail)


class HTTPValidationError(MeteoLuxError):
  """Raised when the API returns a 422 Unprocessable Entity status."""

  def __init__(self, detail: str) -> None:
    """Initializes the HTTPValidationError with a detail message.

    Args:
        detail (str): The error message from the API.
    """
    self.detail = detail
    super().__init__(self.detail)


class HTTPError(MeteoLuxError):
  """A generic HTTP error."""

  def __init__(self, status_code: int, detail: str) -> None:
    """Initializes the HTTPError with a status code and detail message.

    Args:
        status_code (int): The HTTP status code.
        detail (str): The error message from the API.
    """
    self.status_code = status_code
    self.detail = detail
    super().__init__(f'HTTP Error {self.status_code}: {self.detail}')
