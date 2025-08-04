# 📞 Phone Number Validation & Formatter API (Python SDK)

The `phone-validator` library uses the official [GenderAPI Phone Number Validation & Formatter API](https://genderapi.io) to validate and format phone numbers from over 240 countries.

Whether your users enter phone numbers in various formats (e.g., `12128675309`, `+1 212 867 5309`, `001–212–867–5309`), this SDK intelligently detects, validates, and converts them into the standardized E.164 format (e.g., `+12128675309`).

---

## ✅ Features

- Converts phone numbers to **E.164** format  
- Validates if number is real and structurally possible  
- Detects number type: mobile, landline, VoIP, etc.  
- Identifies region/city based on area code  
- Includes country-level metadata (e.g. ISO code, carrier, city)  
- Built with Python, uses the `requests` package  

---

## 🔧 Installation

Install via pip:

```bash
pip install phone-validator
```

Or manually from GitHub:

```bash
git clone https://github.com/GenderAPI/phone-validator-python.git
cd phone-validator-python
pip install .
```

---

## 🚀 Usage

```python
from phone_validator import PhoneValidator

# Replace with your actual API key
API_KEY = "YOUR_API_KEY"

validator = PhoneValidator(api_key=API_KEY)

result = validator.validate(number="+1 212 867 5309", address="US")

print(result)
```

---

## 🧾 Input Parameters

### `validate(number, address=None)`

| Parameter | Type   | Required | Description                                                                 |
|-----------|--------|----------|-----------------------------------------------------------------------------|
| number    | string | ✅ Yes   | Phone number in any format                                                  |
| address   | string | Optional | ISO country code (`US`), full country name (`Turkey`), or city name (`Berlin`) — helps resolve local numbers |

**Example:**

```python
validator.validate("2128675309", "US")
```

---

## 🌐 API Response

```json
{
  "status": true,
  "remaining_credits": 15709,
  "expires": 0,
  "duration": "18ms",
  "regionCode": "US",
  "countryCode": 1,
  "country": "United States",
  "national": "(212) 867-5309",
  "international": "+1 212-867-5309",
  "e164": "+12128675309",
  "isValid": true,
  "isPossible": true,
  "numberType": "FIXED_LINE_OR_MOBILE",
  "nationalSignificantNumber": "2128675309",
  "rawInput": "+1 212 867 5309",
  "isGeographical": true,
  "areaCode": "212",
  "location": "New York City (Manhattan)"
}
```

---

## 📘 Response Field Reference

| Field                      | Description                                              |
|---------------------------|----------------------------------------------------------|
| `e164`                    | Number formatted in E.164 standard                       |
| `isValid`, `isPossible`   | Validity and structure confirmation                      |
| `numberType`              | Type of line: mobile, landline, VoIP, etc.              |
| `country`, `regionCode`   | Country name and ISO code                                |
| `location`, `areaCode`    | Geo-location details based on number                    |
| `carrier`                 | Carrier (if available)                                   |
| `rawInput`, `national`    | Original and normalized formats                          |
| `remaining_credits`       | API credits left in your account                         |

---

## 📄 License

This project is licensed under the terms of the MIT license.  
See the [LICENSE](./LICENSE) file for details.

---

## 🌍 Links

- 🧪 [API Playground](https://www.genderapi.io/docs-phone-validation-formatter-api)
