"""日程表：独立窗口填写时间+事件，提前10分钟与到点时提醒。"""
import json
import os
import time as time_mod
from datetime import datetime

from PySide6.QtCore import (QAbstractListModel, QModelIndex, QObject, Qt,
                            QTimer, Signal, Slot)

from .. import config

_SCHEDULE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schedule.json")


class ScheduleModel(QAbstractListModel):
    ID = Qt.ItemDataRole.UserRole + 1
    DATE = Qt.ItemDataRole.UserRole + 2
    TIME = Qt.ItemDataRole.UserRole + 3
    EVENT = Qt.ItemDataRole.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []   # list of dict

    def roleNames(self):
        return {
            self.ID: b"sid",
            self.DATE: b"sdate",
            self.TIME: b"stime",
            self.EVENT: b"sevent",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.items)):
            return None
        it = self.items[index.row()]
        if role == self.ID:
            return it["id"]
        if role == self.DATE:
            return it["date"]
        if role == self.TIME:
            return it["time"]
        if role == self.EVENT:
            return it["event"]
        return None

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()


class ScheduleManager(QObject):
    remind = Signal(str)     # 需要显示的提醒文案（由桥接层转成气泡消息）

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ScheduleModel(self)
        self._load()
        if config.SCHEDULE_ENABLED:
            self._timer = QTimer(self)
            self._timer.setInterval(config.SCHEDULE_CHECK_INTERVAL_MS)
            self._timer.timeout.connect(self._on_check)
            self._timer.start()

    @Slot(str, str, str)
    def add(self, date: str, time: str, event: str):
        item = {
            "id": str(int(time_mod.time() * 1000)),
            "date": (date or "").strip(),
            "time": (time or "").strip(),
            "event": (event or "").strip(),
            "notified_pre": False,
            "notified_at": False,
        }
        if not item["date"] or not item["time"] or not item["event"]:
            return
        self.model.items.append(item)
        self.model.refresh()
        self._save()

    @Slot(int)
    def remove(self, index: int):
        if 0 <= index < len(self.model.items):
            del self.model.items[index]
            self.model.refresh()
            self._save()

    def _on_check(self):
        for msg in self.checkDue():
            self.remind.emit(msg)

    def checkDue(self):
        msgs = []
        now = datetime.now()
        for it in self.model.items:
            try:
                dt = datetime.strptime(f"{it['date']} {it['time']}", "%Y-%m-%d %H:%M")
            except Exception:  # noqa: BLE001
                continue
            rem = (dt - now).total_seconds()
            # 提前10分钟告知（一次）
            if not it["notified_pre"] and 0 < rem <= config.SCHEDULE_PRE_NOTIFY_SEC:
                it["notified_pre"] = True
                mins = max(1, int(round(rem / 60)))
                msgs.append(f"祈祈提醒：还有约{mins}分钟就要「{it['event']}」啦~")
            # 到时间提醒（一次）
            if not it["notified_at"] and rem <= 0 and rem > -3600:
                it["notified_at"] = True
                msgs.append(f"时间到啦！该「{it['event']}」啦~")
        if msgs:
            self._save()
        return msgs

    # ---- 持久化 ----
    def _load(self):
        try:
            with open(_SCHEDULE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.model.items = data if isinstance(data, list) else []
        except Exception:  # noqa: BLE001
            self.model.items = []

    def _save(self):
        try:
            with open(_SCHEDULE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.model.items, f, ensure_ascii=False, indent=2)
        except Exception:  # noqa: BLE001
            pass
