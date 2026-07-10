import time
from threading import Thread

from telemetry.provider import read_telemetry
from telemetry.state import telemetry_state
from telemetry.state import telemetry_lock


def telemetry_loop(socketio):

    FAST_RATE = 30
    MEDIUM_RATE = 10
    SLOW_RATE = 1

    fast_counter = 0
    medium_counter = 0
    slow_counter = 0

    while True:

        data = read_telemetry()

        with telemetry_lock:
            telemetry_state.update(data)

        socketio.emit("telemetry_fast", telemetry_state["fast"])

        # fast_counter += 1
        medium_counter += 1
        slow_counter += 1
        

        if medium_counter >= FAST_RATE // MEDIUM_RATE:

            socketio.emit("telemetry_medium", telemetry_state["medium"])

            medium_counter = 0

        if slow_counter >= FAST_RATE // SLOW_RATE:

            socketio.emit("telemetry_slow", telemetry_state["slow"])

            slow_counter = 0

        time.sleep(1 / FAST_RATE)


def start(socketio):

    Thread(target=telemetry_loop, args=(socketio,), daemon=True).start()
