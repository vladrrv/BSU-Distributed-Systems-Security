import winreg
import os


ENC = 'UTF-8'


class MSG:
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    EXP_SESS = "EXP_SESS"
    CODE_EXPIRED = "Code expired - sending new code"
    CODE_INVALID = "Invalid code"


class CMD:
    RECV = "RECV"
    SEND = "SEND"
    QUIT = "QUIT"


REG_PATH = r"Lab2"


def read_file(path):
    text = None
    if os.path.isfile(path):
        with open(path, 'r') as f:
            text = f.read()
    return text


def save_file(text, path):
    with open(path, 'w') as f:
        f.write(text)


def set_reg(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                      winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


def get_reg(name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                      winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None
