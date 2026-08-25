"""系统使用时长辅助（Windows）：读取距上次用户输入(鼠标/键盘)的毫秒数。"""
import ctypes


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def system_idle_ms() -> int:
    """返回系统自上次用户输入以来经过的毫秒数；失败时返回 0。"""
    try:
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return int(ctypes.windll.kernel32.GetTickCount() - info.dwTime)
    except Exception:  # noqa: BLE001
        pass
    return 0
