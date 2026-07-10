from telemetry.mock import get_mock_telemetry


def read_telemetry():
    return get_mock_telemetry()
    # return ets2_sdk.read()
