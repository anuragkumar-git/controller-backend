from threading import Lock

telemetry_lock = Lock()

telemetry_state = {
    "fast": {
        "steering": 0,
        "throttle": 0,
        "brake": 0,
        "rpm": 0,
    },
    "medium": {
        "speed": 0,
        "gear": 0,
        "lights": False,
        "high_beam": False,
        "left_indicator": False,
        "right_indicator": False,
        "cruise": False,
    },
    "slow": {
        "fuel": 0,
        "damage": 0,
        "engine": False,
        "parking_brake": False,
        "game_time": "",
    },
}
