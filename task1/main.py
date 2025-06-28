from datetime import datetime
import json
import logging
import unittest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

####### DATA LOADING #######
with open("data-1.json", "r") as f:
    data_format_1 = json.load(f)

with open("data-2.json", "r") as f:
    data_format_2 = json.load(f)

with open("data-result.json", "r") as f:
    expected_output = json.load(f)
####### DATA LOADING #######

####### CONVERSION FUNCTIONS #######

def transform_format_1(entry):
    """
    Transforms a telemetry record from Format 1 to the standard structure.

    This function handles flat-format data and parses the slash-separated location string
    into individual nested keys for clarity and structure.

    Args:
        entry (dict): Input telemetry data in format 1.

    Returns:
        dict: A cleaned and structured telemetry dictionary.
    """
    logging.info(f"Transforming from format 1: {entry}")
    try:
        country, city, area, factory, section = entry["location"].split("/")
        formatted = {
            "deviceID": entry["deviceID"],
            "deviceType": entry["deviceType"],
            "timestamp": entry["timestamp"],
            "location": {
                "country": country,
                "city": city,
                "area": area,
                "factory": factory,
                "section": section
            },
            "data": {
                "status": entry["operationStatus"],
                "temperature": entry["temp"]
            }
        }
        logging.info(f"Format 1 transformation successful: {formatted}")
        return formatted
    except Exception as e:
        logging.error(f"Error parsing Format 1: {e}")
        return None


def transform_format_2(entry):
    """
    Transforms a telemetry record from Format 2 to the standard structure.

    This function converts nested fields and handles ISO timestamp parsing.

    Args:
        entry (dict): Input telemetry data in format 2.

    Returns:
        dict: A structured telemetry dictionary in the target format.
    """
    logging.info(f"Transforming from format 2: {entry}")
    try:
        iso_time = entry["timestamp"]
        timestamp_ms = int(datetime.fromisoformat(iso_time.replace("Z", "+00:00")).timestamp() * 1000)

        formatted = {
            "deviceID": entry["device"]["id"],
            "deviceType": entry["device"]["type"],
            "timestamp": timestamp_ms,
            "location": {
                "country": entry["country"],
                "city": entry["city"],
                "area": entry["area"],
                "factory": entry["factory"],
                "section": entry["section"]
            },
            "data": entry["data"]
        }
        logging.info(f"Format 2 transformation successful: {formatted}")
        return formatted
    except Exception as e:
        logging.error(f"Error parsing Format 2: {e}")
        return None

####### CONVERSION FUNCTIONS #######

####### MAIN ROUTINE #######

def convert(data):
    """
    Detects the data format and delegates to the appropriate transformation function.
    """
    if "device" in data:
        return transform_format_2(data)
    else:
        return transform_format_1(data)

####### MAIN ROUTINE #######

####### UNIT TESTS #######

class TestTransformation(unittest.TestCase):

    def test_identity_check(self):
        self.assertEqual(json.loads(json.dumps(expected_output)), expected_output)

    def test_format_1_conversion(self):
        result = convert(data_format_1)
        self.assertEqual(result, expected_output, "Format 1 conversion mismatch.")

    def test_format_2_conversion(self):
        result = convert(data_format_2)
        self.assertEqual(result, expected_output, "Format 2 conversion mismatch.")

####### UNIT TESTS #######

if __name__ == "__main__":
    unittest.main()
