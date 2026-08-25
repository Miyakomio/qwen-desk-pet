"""二次元桌宠入口：加载 QML 窗口、建立托盘，桥接 Python<->QML。"""
import os
import sys
import traceback

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from pet import config
from pet.bridge import PetBridge

_DEBUG_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pet_debug.log")


def _log(msg: str) -> None:
    try:
        with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def _make_icon() -> QIcon:
    """程序化生成一个圆圆的二次元头像作为托盘/窗口图标。"""
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#6b4a3a"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(8, 4, 48, 44)        # 头发
    p.setBrush(QColor("#ffe3d3"))
    p.drawEllipse(12, 14, 40, 40)      # 脸
    p.setBrush(QColor("#3a2b2b"))
    p.drawEllipse(20, 26, 8, 9)        # 左眼
    p.drawEllipse(36, 26, 8, 9)        # 右眼
    p.setBrush(QColor("#ffb3c7"))
    p.drawEllipse(18, 38, 8, 5)        # 腮红
    p.drawEllipse(38, 38, 8, 5)
    p.end()
    return QIcon(pix)


def main():
    # pythonw(无控制台) 下 stdout/stderr 为 None，重定向到空设备避免崩溃
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    _log("=== 启动 ===")
    print("[pet] starting...")
    print("[pet] window will appear at bottom-right; icon in system tray.")
    app = QApplication(sys.argv)
    app.setApplicationName("QwenDeskPet")

    engine = QQmlApplicationEngine()
    bridge = PetBridge()
    engine.rootContext().setContextProperty("petBridge", bridge)
    engine.rootContext().setContextProperty("messageModel", bridge.messageModel)

    # 桌宠形象帧目录与帧数
    pets_dir = os.path.join(os.path.dirname(__file__), "resources", "pets", config.PET_CHARACTER)
    if not os.path.isdir(pets_dir):
        pets_dir = os.path.join(os.path.dirname(__file__), "resources", "pets", "codex")
    frame_files = sorted(
        f for f in os.listdir(pets_dir)
        if f.lower().endswith(".png") and f[:2].isdigit()
    )
    engine.rootContext().setContextProperty("petFrameDir", QUrl.fromLocalFile(pets_dir).toString())
    engine.rootContext().setContextProperty("petFrameCount", len(frame_files))
    engine.rootContext().setContextProperty("configIdleSemi", config.IDLE_SEMI_MS)
    engine.rootContext().setContextProperty("configIdleHide", config.IDLE_HIDE_MS)
    _log(f"形象: {config.PET_CHARACTER} 帧数={len(frame_files)} 目录={pets_dir}")

    qml_dir = os.path.join(os.path.dirname(__file__), "qml")
    qml_path = os.path.join(qml_dir, "PetWindow.qml")
    _log(f"QML 路径: {qml_path}")
    engine.load(QUrl.fromLocalFile(qml_path))
    if not engine.rootObjects():
        _log("错误: QML 加载失败")
        print("加载 QML 失败", file=sys.stderr)
        sys.exit(-1)

    window = engine.rootObjects()[0]

    # 展开的对话窗口（默认隐藏，由桌宠上的按钮唤出）
    engine.load(QUrl.fromLocalFile(os.path.join(qml_dir, "ChatWindow.qml")))
    if len(engine.rootObjects()) >= 2:
        chat_win = engine.rootObjects()[-1]
        chat_win.hide()
        engine.rootContext().setContextProperty("chatWindow", chat_win)

    _log(f"窗口已创建: {type(window).__name__}, 尺寸 {window.width()}x{window.height()}")

    # 应用更小尺寸
    window.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    # 显式显示并置顶，默认放在右下角
    window.show()
    window.raise_()
    try:
        screen = app.primaryScreen()
        geo = screen.availableGeometry()
        window.setX(geo.x() + geo.width() - window.width() - 60)
        window.setY(geo.y() + geo.height() - window.height() - 40)
    except Exception as e:  # noqa: BLE001
        _log(f"定位窗口失败(非致命): {e}")
    _log(f"窗口 visible={window.isVisible()} 位置=({window.x()},{window.y()})")
    print(f"[pet] window shown: visible={window.isVisible()}")

    # 系统托盘：关闭窗口后可从托盘唤出
    try:
        icon = _make_icon()
        tray = QSystemTrayIcon(icon, app)
        tray.setToolTip("祈りちゃん · Qwen 二次元桌宠")
        menu = QMenu()
        show_action = QAction("显示/隐藏桌宠", menu)
        show_action.triggered.connect(
            lambda: window.show() if not window.isVisible() else window.hide()
        )
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(app.quit)
        menu.addAction(show_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        tray.setContextMenu(menu)
        tray.activated.connect(
            lambda reason: window.show() if reason == QSystemTrayIcon.Trigger else None
        )
        tray.show()
        _log("托盘已建立")
    except Exception as e:  # noqa: BLE001
        _log(f"托盘建立失败(非致命): {e}")

    _log("进入事件循环")
    print("[pet] running. press Ctrl+C or tray 'exit' to quit.")
    print("[pet] if you see no pet window, check the tray icon near the clock.")
    sys.stdout.flush()
    try:
        sys.exit(app.exec())
    except Exception:  # noqa: BLE001
        _log("运行出错: " + traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
