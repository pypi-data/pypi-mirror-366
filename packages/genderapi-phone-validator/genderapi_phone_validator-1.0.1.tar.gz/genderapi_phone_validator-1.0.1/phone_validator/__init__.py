import requests

class PhoneValidator:
    """
    Python SDK for GenderAPI.io - Phone Number Validation

    This SDK allows you to validate, format, and analyze phone numbers globally.
    It communicates with the GenderAPI Phone Number Validation & Formatter API,
    enabling metadata extraction such as:
      - E.164 formatted number
      - Region/country detection
      - Number type (mobile, landline, VoIP, etc.)
      - Carrier detection
      - Validity check

    """

    def __init__(self, api_key, base_url="https://api.genderapi.io"):
        """
        Initialize the PhoneValidator SDK.

        :param api_key: Your GenderAPI API key (as a Bearer token).
        :param base_url: Base URL of the GenderAPI service (default: https://api.genderapi.io).
        """
        self.api_key = api_key
        self.base_url = base_url

    def validate(self, number, address=""):
        """
        Validate and analyze a phone number.

        :param number: The phone number to validate (in international or local format).
        :param address: Optional IP address or country code to assist in region detection.
        :return: A dictionary containing metadata such as validity, region, type, and more.
        """
        return self._post_request(
            "/api/phone",
            {
                "number": number,
                "address": address
            }
        )

    def _post_request(self, endpoint, payload):
        """
        Internal helper to send POST requests to the API.

        Automatically handles:
          - Bearer token authentication
          - Cleaning of None values in payload
          - Error detection for server failures (5xx)
          - JSON parsing

        :param endpoint: API endpoint path (e.g., "/api/phone")
        :param payload: Dictionary of parameters to send in the request body.
        :return: Parsed JSON response as a Python dictionary.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [500, 502, 503, 504, 408]:
            # Raise HTTPError for server-side issues and timeouts
            response.raise_for_status()
        else:
            try:
                return response.json()
            except ValueError:
                raise ValueError("Response content is not valid JSON.")
