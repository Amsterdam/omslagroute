import logging

import requests

logger = logging.getLogger(__name__)

STADSDEEL_API_URL = "https://api.data.amsterdam.nl/v1/benkagg/adresseerbareobjecten/%s"


def get_stadsdeel(nummeraanduiding_id):
    try:
        response = requests.get(STADSDEEL_API_URL % nummeraanduiding_id, timeout=10)
        response.raise_for_status()
        return response.json().get("gebiedenStadsdeelNaam")
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Request error stadsdeel: {e}")
        return None
