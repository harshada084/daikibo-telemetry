import json
import unittest
import datetime

# ─────────────────────────────────────────────
# Load the three JSON files
# ─────────────────────────────────────────────
with open("./data-1.json", "r", encoding="utf-8") as f:
    jsonData1 = json.load(f)

with open("./data-2.json", "r", encoding="utf-8") as f:
    jsonData2 = json.load(f)

with open("./data-result.json", "r", encoding="utf-8") as f:
    jsonExpectedResult = json.load(f)


# ─────────────────────────────────────────────
# IMPLEMENT: Convert Format 1 → Unified Format
#
# Format 1 characteristics:
#   - deviceID / deviceType at top level (flat)
#   - timestamp is already epoch milliseconds (int)
#   - location is a slash-separated string:
#       "country/city/area/factory/section"
#   - operationStatus (flat) → data.status
#   - temp (flat)            → data.temperature
# ─────────────────────────────────────────────
def convertFromFormat1(jsonObject):
    # Split the location path into its five components
    locationParts = jsonObject["location"].split("/")

    return {
        "deviceID":   jsonObject["deviceID"],
        "deviceType": jsonObject["deviceType"],
        "timestamp":  jsonObject["timestamp"],          # already epoch ms — keep as-is
        "location": {
            "country": locationParts[0],
            "city":    locationParts[1],
            "area":    locationParts[2],
            "factory": locationParts[3],
            "section": locationParts[4]
        },
        "data": {
            "status":      jsonObject["operationStatus"],  # rename field
            "temperature": jsonObject["temp"]              # rename field
        }
    }


# ─────────────────────────────────────────────
# IMPLEMENT: Convert Format 2 → Unified Format
#
# Format 2 characteristics:
#   - device is a nested object: { id, type }
#   - timestamp is ISO 8601 string → must convert to epoch ms
#   - location fields are at top level (country, city, area, factory, section)
#   - data object already has the right shape { status, temperature }
# ─────────────────────────────────────────────
def convertFromFormat2(jsonObject):
    # Parse the ISO 8601 timestamp and convert to milliseconds since epoch (UTC)
    dt = datetime.datetime.strptime(jsonObject["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
    dt = dt.replace(tzinfo=datetime.timezone.utc)          # make timezone-aware (UTC)
    timestamp_ms = round(dt.timestamp() * 1000)            # seconds → milliseconds

    return {
        "deviceID":   jsonObject["device"]["id"],           # unwrap nested device object
        "deviceType": jsonObject["device"]["type"],
        "timestamp":  timestamp_ms,
        "location": {
            "country": jsonObject["country"],
            "city":    jsonObject["city"],
            "area":    jsonObject["area"],
            "factory": jsonObject["factory"],
            "section": jsonObject["section"]
        },
        "data": jsonObject["data"]                          # shape already matches — copy directly
    }


# ─────────────────────────────────────────────
# Router: detect format and dispatch
# ─────────────────────────────────────────────
def main(jsonObject):
    if jsonObject.get("device") is None:
        # No nested "device" key → Format 1
        return convertFromFormat1(jsonObject)
    else:
        # Has nested "device" key → Format 2
        return convertFromFormat2(jsonObject)


# ─────────────────────────────────────────────
# Unit Tests
# ─────────────────────────────────────────────
class TestSolution(unittest.TestCase):

    def test_sanity(self):
        """Expected result round-trips through JSON serialisation unchanged."""
        result = json.loads(json.dumps(jsonExpectedResult))
        self.assertEqual(result, jsonExpectedResult)

    def test_dataType1(self):
        """Format 1 (flat, epoch ms, slash location) converts correctly."""
        result = main(jsonData1)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 1 failed")

    def test_dataType2(self):
        """Format 2 (nested device, ISO timestamp, split location) converts correctly."""
        result = main(jsonData2)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 2 failed")


if __name__ == "__main__":
    unittest.main()
