# europarl
Python client for accessing and analyzing European Parliament data

[![Build](https://github.com/robincvlr/europarl/actions/workflows/main.yml/badge.svg)](https://github.com/robincvlr/europarl/actions/workflows/main.yml)

## Motivations
Building a Python wrapper to access the European Parliament's Europarl API is a powerful step toward democratizing access to legislative data and fostering transparency in European governance. By simplifying and streamlining the process of querying parliamentary information, such as debates, documents, voting records, and member data, this wrapper can empower researchers, journalists, civic tech developers, and engaged citizens alike.

## Europarl Swagger
https://data.europarl.europa.eu/en/developer-corner/opendata-api

## Installation
`pip install git+https://github.com/robincvlr/europarl.git`

## Example
```
from europarl.client import EuroparlClient

async with EuroparlClient() as client:
    status, data = await client.get(
        query="meps/show-current",
        limit=10,
        offset=0,
        country_of_representation="FR",
        format="application/ld+json",
    )
```
