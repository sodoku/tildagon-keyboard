from app import App
from app_components import clear_background
from app_components.dialog import KEYBOARD_BUTTONS
from machine import I2C
from events.input import BUTTON_TYPES, Buttons, ButtonDownEvent
from system.eventbus import eventbus
from system.hexpansion.events import HexpansionRemovalEvent, HexpansionInsertionEvent
from system.hexpansion.config import *

CUSTOM_KEY_MAP = {
    13: "ENTER",
    27: "ESCAPE",
    32: "SPACE",
    180: "UP",
    181: "DOWN",
    182: "LEFT",
    183: "RIGHT",
}


class KeyboardApp(App):
    def __init__(self):
        self.ADDR = 0x5F
        self.button_states = Buttons(self)
        self.text = "Searching.."
        self.hexpansion_config = self.scan_for_hexpansion()
        eventbus.on(HexpansionInsertionEvent, self.handle_hexpansion_insertion, self)
        eventbus.on(HexpansionRemovalEvent, self.handle_hexpansion_removal, self)

    def handle_hexpansion_insertion(self, event):
        self.hexpansion_config = self.scan_for_hexpansion()

    def handle_hexpansion_removal(self, event):
        self.hexpansion_config = self.scan_for_hexpansion()

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

    def background_update(self, delta):
        if self.hexpansion_config:
            self.update_keyboard()

    def draw(self, ctx):
        clear_background(ctx)
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.move_to(0, 0).gray(1).text(self.text)

    def scan_for_hexpansion(self):
        for port in range(1, 7):
            print(f"Searching for keyboard on port: {port}")
            i2c = I2C(port)
            devices = i2c.scan()

            if self.ADDR not in devices:
                continue
            else:
                print("Found keyboard")

            self.text = "Found keyboard"
            return HexpansionConfig(port)

        self.text = "No keyboard found."
        return None

    def update_keyboard(self):
        buf = self.hexpansion_config.i2c.readfrom(self.ADDR, 1)
        keycode = buf[0]
        if keycode != 0:
            try:
                key = CUSTOM_KEY_MAP.get(keycode) or buf.decode()
                print(key)
                button = KEYBOARD_BUTTONS.get(key.upper())
                print(button)
                if button:
                    eventbus.emit(ButtonDownEvent(button=button))
            except UnicodeError:
                print("could not encode")


__app_export__ = KeyboardApp
