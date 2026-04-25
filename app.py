from app import App
from app_components import clear_background
from app_components.dialog import KEYBOARD_BUTTONS
from events.input import BUTTON_TYPES, Buttons, ButtonDownEvent, ButtonUpEvent
from system.eventbus import eventbus
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
        self.button_states = Buttons(self)
        self.text = "Press confirm"
        self.initialized = False

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CONFIRM"]):
            # TODO: don't assume hexpansion port 4
            self.hexpansion_config = HexpansionConfig(4)
            self.init_keyboard()
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

    def background_update(self, delta):
        if self.initialized:
            self.update_keyboard()

    def draw(self, ctx):
        clear_background(ctx)
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.move_to(0, 0).gray(1).text(self.text)

    def init_keyboard(self):
        self.ADDR = 0x5F
        self.i2c = self.hexpansion_config.i2c
        self.text = "keyboard initialized"
        self.initialized = True

    def update_keyboard(self):
        buf = self.i2c.readfrom(self.ADDR, 1)
        keycode = buf[0]
        if keycode != 0:
            print(buf)
            print(keycode)
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
