"""日程表：支持「指定时间(一次性)」与「固定时间(每天)」两类，提前10分钟+到点各提醒一次。"""
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
    TYPE = Qt.ItemDataRole.UserRole + 2
    DATE = Qt.ItemDataRole.UserRole + 3
    TIME = Qt.ItemDataRole.UserRole + 4
    EVENT = Qt.ItemDataRole.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []

    def roleNames(self):
        return {
            self.ID: b"sid",
            self.TYPE: b"stype",
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
            return it.get("id", "")
        if role == self.TYPE:
            return it.get("type", "daily")
        if role == self.DATE:
            return it.get("date", "")
        if role == self.TIME:
            return it.get("time", "")
        if role == self.EVENT:
            return it.get("event", "")
        return None

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()


class ScheduleManager(QObject):
    remind = Signal(str)

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
    def addOnce(self, date: str, time: str, event: str):
        """指定时间（一次性）：date YYYY-MM-DD, time HH:MM。"""
        item = {
            "id": str(int(time_mod.time() * 1000)),
            "type": "once",
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

    @Slot(str, str)
    def addDaily(self, time: str, event: str):
        """固定时间（每天）：time HH:MM。"""
        item = {
            "id": str(int(time_mod.time() * 1000)),
            "type": "daily",
            "date": "",
            "time": (time or "").strip(),
            "event": (event or "").strip(),
            "notified_pre_day": "",
            "notified_at_day": "",
        }
        if not item["time"] or not item["event"]:
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
        today = now.strftime("%Y-%m-%d")
        for it in self.model.items:
            if it.get("type") == "once":
                self._check_once(it, now, msgs)
            else:
                self._check_daily(it, now, today, msgs)
        if msgs:
            self._save()
        return msgs

    def _check_once(self, it, now, msgs):
        try:
            dt = datetime.strptime(f"{it['date']} {it['time']}", "%Y-%m-%d %H:%M")
        except Exception:  # noqa: BLE001
            return
        rem = (dt - now).total_seconds()
        if not it.get("notified_pre") and 0 < rem <= config.SCHEDULE_PRE_NOTIFY_SEC:
            it["notified_pre"] = True
            mins = max(1, int(round(rem / 60)))
            msgs.append(f"已经{now:%H:%M}了喵，还有约{mins}分钟就要「{it['event']}」啦哦")
        if not it.get("notified_at") and rem <= 0 and rem > -3600:
            it["notified_at"] = True
            msgs.append(f"已经{now:%H:%M}了喵，记得该「{it['event']}」哦")

    def _check_daily(self, it, now, today, msgs):
        try:
            dt = datetime.strptime(f"{today} {it['time']}", "%Y-%m-%d %H:%M")
        except Exception:  # noqa: BLE001
            return
        rem = (dt - now).total_seconds()
        if it.get("notified_pre_day") != today and 0 < rem <= config.SCHEDULE_PRE_NOTIFY_SEC:
            it["notified_pre_day"] = today
            mins = max(1, int(round(rem / 60)))
            msgs.append(f"已经{now:%H:%M}了喵，还有约{mins}分钟就要「{it['event']}」啦哦")
        if it.get("notified_at_day") != today and rem <= 0 and rem > -3600:
            it["notified_at_day"] = today
            msgs.append(f"已经{now:%H:%M}了喵，记得该「{it['event']}」哦")

    # ---- 持久化 ----
    def _load(self):
        try:
            with open(_SCHEDULE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data if isinstance(data, list) else []
            for it in items:
                if not it.get("type"):
                    it["type"] = "once" if it.get("date") else "daily"
                it.setdefault("notified_pre", False)
                it.setdefault("notified_at", False)
                it.setdefault("notified_pre_day", "")
                it.setdefault("notified_at_day", "")
            self.model.items = items
        except Exception:  # noqa: BLE001
            self.model.items = []

    def _save(self):
        try:
            with open(_SCHEDULE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.model.items, f, ensure_ascii=False, indent=2)
        except Exception:  # noqa: BLE001
            pass
