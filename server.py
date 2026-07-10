import logging
from threading import Lock
from flask import Flask
from flask import send_from_directory
from flask_socketio import SocketIO
import vgamepad as vg
import os
from telemetry.broadcaster import start as startTelemetry

# Setup optimized logging to prevent terminal blocking
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="client", static_url_path="")
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):

    file_path = os.path.join(app.static_folder, path)

    if path and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)

    return send_from_directory(app.static_folder, "index.html")


# def index():
#     return send_from_directory(
#         app.static_folder,
#         "index.html"
#     )
# Initialize hardware and thread safety locks
gamepad = vg.VX360Gamepad()
gamepad_lock = Lock()

# BUTTON_MAP = {
#     'enter': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
#     'lane': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
#     'cruise': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
#     'trailer': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
#     'left_indicator': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
#     'right_indicator': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
#     'cruise_up': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
#     'cruise_down': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
#     'lights_low': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
#     'wipers': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
#     'hazard': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB
#     'lights_high': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
# }

BUTTON_MAP = {
    "enter": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "engine_start": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "hazard": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "trailer": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "retarder_down": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "retarder_up": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "cruise_down": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    "cruise_up": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    "left_indicator": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    "right_indicator": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    "lights_high": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "lights_low": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    
    "menu": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "modifier1": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
}

COMBO_MAP = {
    "horn": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    ],
    "parking_brake": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    ],
    "diff_lock": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    ],
    "wipers": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    ],
    "lift_axle": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    ],
    "side_mirrors": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    ],
    "services": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    ],
    "map": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    ],
    # "esc_quick_info": [
    #     vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    #     vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    # ],
    # Not working
    "adeptive_cruise": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    ],
    "interior_camera": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    ],
    "chasing_camera": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    ],
    "top_down_camera": [
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    ],
}


# Keep track of analog states to prevent axes overriding each other
current_axes = {"left_x": 0, "left_y": 0, "right_x": 0, "right_y": 0}


def rumble_callback(client, target, large_motor, small_motor, led_number, user_data):
    """
    Captures force feedback directly from the Windows OS / ETS 2.
    Matches the strict 6-argument signature required by vgamepad.
    """
    # large_motor and small_motor are passed directly as integers (0 to 255)
    # Send them straight to your connected phone via your socket emit
    socketio.emit("rumble", {"large": large_motor, "small": small_motor})


# Register the rumble callback with vgamepad
gamepad.register_notification(rumble_callback)


@socketio.on("connect")
def handle_connect():
    logger.info("Mobile Dashboard linked over link channel.")


@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Mobile Dashboard disconnected.")


@socketio.on("key_down")
def handle_key_down(data):
    if not data or not isinstance(data, dict):
        return
    key = data.get("key")

    with gamepad_lock:
        if key in BUTTON_MAP:
            # with gamepad_lock:
            # gamepad.press_button(button=BUTTON_MAP[key])
            gamepad.press_button(BUTTON_MAP[key])
            # logger.info(f"mapped button string: {key}")

            # gamepad.update()
        elif key in COMBO_MAP:
            for button in COMBO_MAP[key]:
                # gamepad.press_button(button=COMBO_MAP[key])
                gamepad.press_button(button)
                # logger.info(f"two mapped button string: {button}")
        else:
            logger.warning(f"Unmapped button string: {key}")
        gamepad.update()


@socketio.on("key_up")
def handle_key_up(data):
    if not data or not isinstance(data, dict):
        return
    key = data.get("key")

    # if key in BUTTON_MAP:
    #     with gamepad_lock:
    #         gamepad.release_button(button=BUTTON_MAP[key])
    #         gamepad.update()
    with gamepad_lock:

        if key in BUTTON_MAP:

            gamepad.release_button(BUTTON_MAP[key])
            # logger.info(f"mapped button string: {key}")

        elif key in COMBO_MAP:

            for button in COMBO_MAP[key]:
                gamepad.release_button(button)
                # logger.info(f"two mapped button string: {key}")

        else:
            logger.warning(f"Unmapped button string: {key}")
            return

        gamepad.update()


@socketio.on("input_tick")
def handle_input_tick(data):
    """
    Batched high-frequency event containing all joystick positions and pedals.
    Reduces context switching and mitigates network overhead.
    """
    if not data or not isinstance(data, dict):
        return

    # Extract inputs safely with defaults
    steer_val = data.get("steer", 0.0)
    look_x_val = data.get("look_x", 0.0)
    gas_val = data.get("gas", 0.0)
    brake_val = data.get("brake", 0.0)

    # Hard boundary clamping to prevent hardware out-of-bounds exceptions
    steer_val = max(-1.0, min(1.0, steer_val))
    look_x_val = max(-1.0, min(1.0, look_x_val))
    gas_val = max(0.0, min(1.0, gas_val))
    brake_val = max(0.0, min(1.0, brake_val))

    # Scale values to OS expectations
    current_axes["left_x"] = int(steer_val * 32767)
    current_axes["right_x"] = int(look_x_val * 32767)

    gas_byte = int(gas_val * 255)
    brake_byte = int(brake_val * 255)

    # Thread-safe atomic update of the virtual controller hardware state
    with gamepad_lock:
        gamepad.left_joystick(
            x_value=current_axes["left_x"], y_value=current_axes["left_y"]
        )
        gamepad.right_joystick(
            x_value=current_axes["right_x"], y_value=current_axes["right_y"]
        )
        gamepad.right_trigger(value=gas_byte)
        gamepad.left_trigger(value=brake_byte)
        gamepad.update()


if __name__ == "__main__":
    logger.info("ETS 2 ADVANCED CONTROLLER CORE OPERATIONAL")
    startTelemetry(socketio)
    # Using eventlet or gevent is highly recommended for production socket performance
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
