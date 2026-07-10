# # write an ssh script to turn both server on
# from flask import Flask
# from flask_socketio import SocketIO
# import pydirectinput

# # Disable the automatic safety pause to ensure inputs are instantaneous
# pydirectinput.PAUSE = 0.001

# app = Flask(__name__)
# # Allow CORS so your phone's browser can connect to this server
# socketio = SocketIO(app, cors_allowed_origins="*")

# @socketio.on('connect')
# def handle_connect():
#     print("Mobile device connected successfully!")

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("Mobile device disconnected.")

# @socketio.on('key_down')
# def handle_key_down(data):
#     key = data.get('key')
#     if key:
#         print(f"Pressing down: {key}")
#         pydirectinput.keyDown(key)

# @socketio.on('key_up')
# def handle_key_up(data):
#     key = data.get('key')
#     if key:
#         print(f"Releasing: {key}")
#         pydirectinput.keyUp(key)

# if __name__ == '__main__':
#     print("Starting ETS 2 Input Server...")
#     # host='0.0.0.0' allows external devices (your phone) to connect
#     socketio.run(app, host='0.0.0.0', port=5000, debug=False)

from flask import Flask
from flask_socketio import SocketIO
import vgamepad as vg

app = Flask(__name__)
# Enable CORS so your phone can talk to the backend over the USB network link
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the virtual Xbox 360 controller
gamepad = vg.VX360Gamepad() 

# Strict mapping table matching your latest React frontend strings
button_map = {
    'enter': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    'trailer': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    'cruise': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    'lane': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    'left_indicator': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    'right_indicator': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    'cruise_up': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    'cruise_down': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    'wipers': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    'lights_low': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    'lights_high': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    'hazard': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB
}

@socketio.on('connect')
def handle_connect():
    print("\n🟢 Mobile Dashboard successfully linked over USB!")

@socketio.on('disconnect')
def handle_disconnect():
    print("\n🔴 Mobile Dashboard disconnected.")

@socketio.on('key_down')
def handle_key_down(data):
    key = data.get('key')
    if key in button_map:
        print(f"📥 RECEIVED PRESS: {key} -> Mapping to Xbox hardware")
        gamepad.press_button(button=button_map[key])
        # print(f"📥   gamepad.press_button RECEIVED PRESS: {key} -> Mapping to Xbox hardware")
        gamepad.update()
        # print(f"📥 after update RECEIVED PRESS: {key} -> Mapping to Xbox hardware")
    else:
        print(f"⚠️ Warning: Received unmapped button string: {key}")

@socketio.on('key_up')
def handle_key_up(data):
    key = data.get('key')
    if key in button_map:
        print(f"📤 RECEIVED RELEASE: {key}")
        gamepad.release_button(button=button_map[key])
        gamepad.update()

@socketio.on('steer')
def handle_steer(data):
    val = data.get('value', 0.0) 
    # Scale from frontend float (-1.0 to 1.0) to Xbox joystick short integer (-32768 to 32767)
    x_val = int(val * 32767)
    gamepad.left_joystick(x_value=x_val, y_value=0)
    gamepad.update()

@socketio.on('pedals')
def handle_pedals(data):
    gas = data.get('gas', 0.0)    
    brake = data.get('brake', 0.0)
    # Scale from frontend float (0.0 to 1.0) to Xbox analog trigger byte (0 to 255)
    gamepad.right_trigger(value=int(gas * 255))
    gamepad.left_trigger(value=int(brake * 255))
    gamepad.update()

if __name__ == '__main__':
    print("--------------------------------------------------")
    print("     ETS 2 ADVANCED CONTROLLER SYSTEM STARTING     ")
    print("--------------------------------------------------")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)