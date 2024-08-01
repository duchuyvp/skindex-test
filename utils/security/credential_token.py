import abc
import dataclasses
import os
from typing import Any

import jwt

from .. import configuration


@dataclasses.dataclass
class AbstractToken(abc.ABC):
    """Abstract base class for token objects.

    Attributes:
        token (str, optional): The token string. Defaults to None.

    Args:
        data (dict[str, Any]): The data dictionary associated with the token.
        token (str): The token string.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Examples:
        >>> token = AbstractToken(
        ...     data={
        ...         "key1": "value1",
        ...         "key2": "value2",
        ...     },
        ...     token="example_token",
        ... )
        >>> token.token
        'example_token'
        >>> token.data
        {'key1': 'value1', 'key2': 'value2'}

    Note:
        - Abstract base class for creating specific token objects.
        - `data` dictionary contains additional data associated with the token.
        - `token` attribute stores the token string.
    """

    def __init__(self, data: dict[str, Any], token: str):
        self.data = data
        self.token = token


class AbstractTokenFactory(abc.ABC):
    """Abstract base class for token factories."""

    secret: str
    algorithm: str

    def __init__(self, secret: str, algorithm: str):
        self.secret = secret
        self.algorithm = algorithm

    def encode(self, data: dict, *args, **kwargs) -> AbstractToken:
        """Encodes the provided data into a token object using the implemented _encode method.

        Args:
            data (str): The data to be encoded into a token object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Type[AbstractToken]: The encoded token object.

        Raises:
            None.
        """
        token = self._encode(data, *args, **kwargs)
        return token

    def decode(self, token: AbstractToken | str, *args, **kwargs) -> dict[str, Any]:
        """Decodes the provided token or token object using the implemented _decode method.

        Args:
            token (Type[AbstractToken] | str): The token or token object to be decoded.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: The decoded data.

        Raises:
            None.
        """
        data = self._decode(token, *args, **kwargs)
        return data

    @abc.abstractmethod
    def _encode(self, data: dict, *args, **kwargs) -> AbstractToken:
        """Abstract method that should be implemented to encode the data into a token object.

        Args:
            data (str): The data to be encoded into a token object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Type[AbstractToken]: The encoded token object.

        Raises:
            NotImplementedError: This method is meant to be implemented by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _decode(self, token: AbstractToken | str, *args, **kwargs) -> dict[str, Any]:
        """Decode the token or token object and return the decoded data.

        Args:
            token (Type[AbstractToken] | str): The token or token object to be decoded.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: The decoded data.

        Raises:
            NotImplementedError: This method is meant to be implemented by subclasses.
        """
        raise NotImplementedError


class JwtToken(AbstractToken):
    """Represents a JSON Web Token (JWT) token used for authentication and authorization in web
    applications.

    Attributes:
        token (str): The JWT token string.
        expiration (datetime.datetime): The token's expiration date and time.
        claims (dict): A dictionary containing the token's claims (payload).
    """


class JwtTokenFactory(AbstractTokenFactory):
    """Factory for creating and decoding JSON Web Tokens (JWTs)."""

    def __init__(
        self,
        secret: str | None = None,
        algorithm: str | None = None,
        from_env: bool = False,
    ):
        config = configuration.get_config().get("security", {}).get("context", {})
        secret = secret or config.get("secret")
        algorithm = algorithm or config.get("algorithm")

        if from_env:
            secret = os.environ["JWT_SECRET"]
            algorithm = os.environ["JWT_ALGORITHM"]

        if secret is None or algorithm is None:
            raise ValueError("secret and algorithm must be set")

        super().__init__(secret, algorithm)

    def _encode(self, data: dict, *args, **kwargs) -> JwtToken:
        token = jwt.encode(data, self.secret, self.algorithm)
        return JwtToken(data=data, token=token)

    def _decode(self, token: JwtToken | str, *args, **kwargs) -> dict[str, Any]:
        if isinstance(token, JwtToken):
            token = token.token
        data = jwt.decode(token, self.secret, [self.algorithm])
        return data
