from time import sleep

import ctypes

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class DirectKey:
    NUMERAL_1 = 0x02
    NUMERAL_2 = 0x03
    NUMERAL_3 = 0x04
    NUMERAL_4 = 0x05
    NUMERAL_5 = 0x06
    q = 0x10
    w = 0x11
    e = 0x12
    r = 0x13
    t = 0x14
    u = 0x18
    o = 0x16
    x = 0x2D
    BACK = 0x0E
    NUM_0 = 0x52
    ADD = 0x4E
    NUM_PLUS = ADD
    SUBSTRACT = 0x4A
    NUM_MINUS = SUBSTRACT
    SPACE = 0x39
    d = 0x20
    NUMLOCK = 0x45
    p = 0x19
    a = 0x1e
    F12 = 0x58

# Actuals Functions
# Keyboard Scan Hex Codes:
# http://www.gamespp.com/directx/directInputKeyboardScanCodes.html
def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def toggle_key(hexKeyCode):
    press_key(hexKeyCode)
    sleep(0.05)
    release_key(hexKeyCode)
    sleep(0.05)
    