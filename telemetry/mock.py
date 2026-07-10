import math
import time


def get_mock_telemetry():

    t = time.time()

    return {
        "fast": {
            "steering": math.sin(t),
            "throttle": abs(math.sin(t)),
            "brake": abs(math.cos(t)),
            "rpm": 700 + abs(math.sin(t * 2)) * 1800,
        },
        "medium": {
            "speed": abs(math.sin(t)) * 90,
            "gear": int((t // 3) % 12) - 1,
            "lights": int(t) % 2 == 0,
            "high_beam": True,
            "left_indicator": int(t * 2) % 2 == 0,
            "right_indicator": False,
            "cruise": True,
        },
        "slow": {
            "fuel": 75 - (t % 75),
            "damage": 0,
            "engine": True,
            "parking_brake": False,
            "game_time": "14:32",
        },
    }
