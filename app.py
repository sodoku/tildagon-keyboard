from app import App
from app_components import clear_background
from system.eventbus import eventbus
from events.input import BUTTON_TYPES, Buttons, Button, ButtonDownEvent, ButtonUpEvent
from machine import I2C

from .app_components_dialog import KEYBOARD_BUTTONS, TextDialog

# Based on https://gitlab.com/why2025/team-badge/firmware/-/blob/main/badgevms/drivers/tca8418.c
KEYCODES = [
    "NOTHING",
    "ESCAPE",  # 0x1
    "SQUARE",  # 0x2
    "TRIANGLE",  # 0x3
    "CROSS",  # 0x4
    "CIRCLE",  # 0x5
    "CLOUD",  # 0x6
    "DIAMOND",  # 0x7
    "DELETE",  # 0x8
    "0",  # 0x9
    "MINUS",  # 0xa
    "GRAVE",  # 0xb
    "1",  # 0xc
    "2",  # 0xd
    "3",  # 0xe
    "4",  # 0xf
    "5",  # 0x10
    "6",  # 0x11
    "7",  # 0x12
    "8",  # 0x13
    "9",  # 0x14
    "TAB",  # 0x15
    "Q",  # 0x16
    "W",  # 0x17
    "E",  # 0x18
    "R",  # 0x19
    "T",  # 0x1a
    "Y",  # 0x1b
    "U",  # 0x1c
    "I",  # 0x1d
    "O",  # 0x1e
    "FN",  # 0x1f
    "A",  # 0x20
    "S",  # 0x21
    "D",  # 0x22
    "F",  # 0x23
    "G",  # 0x24
    "H",  # 0x25
    "J",  # 0x26
    "K",  # 0x27
    "L",  # 0x28
    "SHIFT",  # 0x29
    "Z",  # 0x2a
    "X",  # 0x2b
    "C",  # 0x2c
    "V",  # 0x2d
    "B",  # 0x2e
    "N",  # 0x2f
    "M",  # 0x30
    "COMMA",  # 0x31
    "PERIOD",  # 0x32
    "LEFT",  # 0x33
    "DOWN",  # 0x34
    "RIGHT",  # 0x35
    "SLASH",  # 0x36
    "UP",  # 0x37
    "SHIFT",  # 0x38
    "SEMICOLON",  # 0x39
    "APOSTROPHE",  # 0x3a
    "ENTER",  # 0x3b
    "EQUALS",  # 0x3c
    "LCTRL",  # 0x3d
    "LGUI",  # 0x3e
    "ALT",  # 0x3f
    "BACKSLASH",  # 0x40
    "SPACE",  # 0x41
    "SPACE",  # 0x42
    "SPACE",  # 0x43
    "ALT",  # 0x44
    "P",  # 0x45
    "LEFTBRACKET",  # 0x46
    "UNKNOWN",  # 0x47
    "UNKNOWN",  # 0x48
    "UNKNOWN",  # 0x49
    "UNKNOWN",  # 0x4a
    "UNKNOWN",  # 0x4b
    "UNKNOWN",  # 0x4c
    "UNKNOWN",  # 0x4d
    "UNKNOWN",  # 0x4e
    "UNKNOWN",  # 0x4f
    "RIGHTBRACKET",  # 0x50
]


class KeyboardApp(App):
    def __init__(self):
        self.button_states = Buttons(self)
        self.initialized = False
        self.text = "HI"
        self.dialog = None
        self.displayed = False

    def _cancel_handler(self):
        # self.name = "world!"
        self.dialog._cleanup()
        self.dialog = None

    def _complete_handler(self):
        # self.name = self.dialog.text
        self.dialog._cleanup()
        self.dialog = None

    def update(self, delta):
        if self.initialized and not self.displayed:
            self.displayed = True
            self.dialog = TextDialog(
                "What is your name?",
                self,
                masked=False,
                on_complete=self._complete_handler,
                on_cancel=self._cancel_handler,
            )

        if self.initialized:
            # TODO: use interrupt and amount from 0x03
            # instead of doing this in update
            n = self.i2c.readfrom_mem(self.ADDR, 0x04, 1)
            pressed = bool(n[0] & 0x80)
            key = n[0] & 0x7F
            if key > 0:
                if pressed:
                    eventbus.emit(
                        ButtonDownEvent(
                            button=KEYBOARD_BUTTONS[KEYCODES[key]],
                        )
                    )
                else:
                    eventbus.emit(
                        ButtonUpEvent(
                            button=KEYBOARD_BUTTONS[KEYCODES[key]],
                        )
                    )
            if key != 0:
                print(pressed)
                print(key)
        if self.displayed:
            return
        if self.button_states.get(BUTTON_TYPES["CONFIRM"]):
            print("initializing keyboard")
            self.ADDR = 0x34
            self.i2c = I2C(4)
            # Based on https://github.com/Hack-a-Day/2025-Communicator_Badge/blob/main/firmware/badge/hardware/keyboard.py
            self.i2c.writeto_mem(
                self.ADDR, 0x1D, b"\xff"
            )  # KP_GPIO1 all ROW7:0 to KP matrix
            self.i2c.writeto_mem(
                self.ADDR, 0x1E, b"\xff"
            )  # KP_GPIO2 all COL7:0 to KP matrix
            self.i2c.writeto_mem(
                self.ADDR, 0x1F, b"\x03"
            )  # KP_GPIO3 all COL9:8 to KP matrix
            self.i2c.writeto_mem(
                self.ADDR, 0x01, b"\x91"
            )  # CFG Set the KE_IEN, INT_CFG, and AI bits
            # Clear Interrupts
            self.i2c.writeto_mem(self.ADDR, 0x02, b"\x01")  # INT_STAT K_INT 1 to clear
            print("initialized keyboard")
            self.text = "initialized"
            self.initialized = True
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

    def draw(self, ctx):
        clear_background(ctx)
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.move_to(0, 0).gray(1).text(self.text)
        if self.dialog:
            self.dialog.draw(ctx)


__app_export__ = KeyboardApp
