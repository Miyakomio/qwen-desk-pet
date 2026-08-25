"""用于展示完整对话历史的 QAbstractListModel。"""
import time

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class MessageModel(QAbstractListModel):
    ROLE_ROLE = Qt.ItemDataRole.UserRole + 1
    ROLE_TEXT = Qt.ItemDataRole.UserRole + 2
    ROLE_TIME = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []  # list of (role, text, timestamp_ms)

    def roleNames(self):
        return {
            self.ROLE_ROLE: b"msgRole",
            self.ROLE_TEXT: b"text",
            self.ROLE_TIME: b"time",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._items)):
            return None
        msg_role, text, ts = self._items[index.row()]
        if role == self.ROLE_ROLE:
            return msg_role
        if role == self.ROLE_TEXT:
            return text
        if role == self.ROLE_TIME:
            return ts
        return None

    def add(self, msg_role: str, text: str, timestamp: int = None) -> None:
        ts = timestamp if timestamp is not None else int(time.time() * 1000)
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append((msg_role, text, ts))
        self.endInsertRows()

    def clear(self) -> None:
        self.beginResetModel()
        self._items = []
        self.endResetModel()
