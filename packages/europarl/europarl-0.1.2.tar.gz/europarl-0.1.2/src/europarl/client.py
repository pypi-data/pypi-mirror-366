import uuid
from re import sub
from typing import Tuple

import aiohttp


def to_kebab(s: str) -> str:
    return "-".join(
        sub(
            r"(\s|_|-)+",
            " ",
            sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda mo: " " + mo.group(0).lower(),
                s,
            ),
        ).split()
    )


class EuroparlClient:
    """
    Asynchronous client for the European Parliament Open Data API.

    This class allows interaction with the Europarl Open Data API using asynchronous HTTP requests.
    It supports listing datasets, retrieving metadata, downloading datasets, and converting CSV data
    into pandas DataFrames.

    Example:
        async with EuroparlClient() as api:
            datasets = await api.get_datasets()
            df = await api.dataset_to_dataframe("example-dataset-id")
    """

    BASE_URL = "https://data.europarl.europa.eu/api"

    def __init__(self, version: str = "v2"):
        """
        Initialize the EuroparlClient without starting the aiohttp session.

        Args:
            version (str): API version
        """
        self.session = None
        self.user_agent = str(uuid.uuid4())
        self.version = version

    async def __aenter__(self):
        """
        Enter the asynchronous context manager and create the aiohttp session.

        Returns:
            EuroparlClient: The initialized API client.
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Exit the asynchronous context manager and close the aiohttp session.

        Args:
            exc_type: Exception type.
            exc: Exception instance.
            tb: Traceback object.
        """
        await self.session.close()

    async def get(self, query: str, **kwargs) -> Tuple[int, dict]:
        """
        Retrieve a list of available datasets from the API.

        Args:
            query (str): European Parliament API query
            **kwargs: Additional query parameters to include in the request.

        Returns:
            int: HTTP status code
            dict: A Response object json
        """
        url = f"{self.BASE_URL}/{self.version}/{query}"
        params_norm = {to_kebab(k): v for k, v in kwargs.items()}
        headers = {"User-Agent": f"{self.user_agent}", "accept": "application/ld+json"}
        async with self.session.get(url, params=params_norm, headers=headers) as resp:
            resp.raise_for_status()
            return resp.status, await resp.json()
