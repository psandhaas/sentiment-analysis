import requests

import pandas as pd
import smart_open
import yaml


def get_BTplenarprotokolle_2023():
    plenarprotokoll_text = "https://search.dip.bundestag.de/api/v1/plenarprotokoll-text?f.datum.start=2023-01-01&f.zuordnung=BT&format=json&apikey=GmEPb1B.bfqJLIhcGAsH9fTJevTglhFpCoZyAAAdhp"

    # Plenarprotokolle im BT seit 01.01.23
    with requests.get(plenarprotokoll_text) as r:
        return pd.DataFrame.from_records(r.json()["documents"])


def get_API_components():
    """Loads API documentation of DIP from URL and returns it as a dictionary."""
    # read API documentation from YAML file and return as dict
    with smart_open.open(
        "https://search.dip.bundestag.de/api/v1/openapi.yaml", "r"
    ) as f:
        return (doc := yaml.safe_load(f))["components"]


def expected_response_params(api_endpoint):
    """Resolves references to schema-classes and returns an explicit interface
    of the expected response parameters.

    See search.dip.bundestag.de/api/v1/swagger-ui/#/Plenarprotokolle/getPlenarprotokollTextList
    for a list of valid endpoints.

    Returns
    -------
        `response_params` : dict
        Dictionary containing attributes that a non-empty API-response of the given `api_endpoint`
        is expected to have.
    """
    # expected params of responses for endpoint
    response_params = {}
    for dict in (api_schemas := get_API_components()["schemas"])[api_endpoint][
        "allOf"
    ]:  # parent classes
        for key, val in dict.items():
            if key == "$ref":
                # follow the link and unpack attributes
                for attr_name, attr_info in api_schemas[
                    (
                        parent := str(val).split("#/components/schemas/")[-1]
                    )  # noqa
                ]["properties"].items():
                    if attr_name in response_params:
                        response_params[attr_name].update(attr_info)
                    else:
                        response_params[attr_name] = attr_info
    return response_params
