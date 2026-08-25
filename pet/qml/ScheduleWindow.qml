import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

/* 日程表窗口：填写时间+事件，查看与删除。 */
Window {
    id: win
    width: 340
    height: 440
    title: "祈祈 · 日程表"
    color: "#fff7fb"

    // 标题栏
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 36
        color: "#ffe3ef"
        Text {
            anchors.centerIn: parent
            text: "📅 日程表（提前10分钟+到点 提醒）"
            color: "#c94f79"
            font.pixelSize: 13
            font.bold: true
            font.family: "Microsoft YaHei"
        }
    }

    property bool isOnce: false   // true=指定时间(一次性), false=固定时间(每天)

    // 输入区
    Column {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 14
        spacing: 12

        // 类型选择
        Row {
            spacing: 10
            Rectangle {
                width: 100; height: 28; radius: 14
                color: win.isOnce ? "#ff8fb3" : "#ffffff"
                border.color: "#ff8fb3"; border.width: 1
                Text { anchors.centerIn: parent; text: "指定时间"; color: win.isOnce ? "white" : "#c94f79"; font.pixelSize: 13 }
                MouseArea { anchors.fill: parent; onClicked: win.isOnce = true }
            }
            Rectangle {
                width: 100; height: 28; radius: 14
                color: win.isOnce ? "#ffffff" : "#ff8fb3"
                border.color: "#ff8fb3"; border.width: 1
                Text { anchors.centerIn: parent; text: "固定时间(每天)"; color: win.isOnce ? "#c94f79" : "white"; font.pixelSize: 13 }
                MouseArea { anchors.fill: parent; onClicked: win.isOnce = false }
            }
        }

        // 日期（仅指定时间时显示）
        Row {
            spacing: 10
            visible: win.isOnce
            Rectangle {
                width: 60; height: 28; radius: 6; color: "transparent"
                Text { anchors.centerIn: parent; text: "日期"; color: "#666666"; font.pixelSize: 12 }
            }
            TextField {
                id: dateInput
                width: 150; height: 28
                font.pixelSize: 13
                font.family: "Microsoft YaHei"
                placeholderText: "YYYY-MM-DD"
                placeholderTextColor: "#c0a6b2"
                color: "#333333"
                background: Rectangle { radius: 6; color: "white"; border.color: "#f0c8d8"; border.width: 1 }
            }
        }

        // 时间
        Row {
            spacing: 10
            Rectangle {
                width: 60; height: 28; radius: 6; color: "transparent"
                Text { anchors.centerIn: parent; text: "时间"; color: "#666666"; font.pixelSize: 12 }
            }
            TextField {
                id: timeInput
                width: 150; height: 28
                font.pixelSize: 13
                font.family: "Microsoft YaHei"
                placeholderText: "HH:MM"
                placeholderTextColor: "#c0a6b2"
                color: "#333333"
                background: Rectangle { radius: 6; color: "white"; border.color: "#f0c8d8"; border.width: 1 }
            }
        }

        // 事件
        Row {
            spacing: 10
            Rectangle {
                width: 60; height: 28; radius: 6; color: "transparent"
                Text { anchors.centerIn: parent; text: "事件"; color: "#666666"; font.pixelSize: 12 }
            }
            TextField {
                id: eventInput
                width: 150; height: 28
                font.pixelSize: 13
                font.family: "Microsoft YaHei"
                placeholderText: "要做什么…"
                placeholderTextColor: "#c0a6b2"
                color: "#333333"
                background: Rectangle { radius: 6; color: "white"; border.color: "#f0c8d8"; border.width: 1 }
                onAccepted: win.doAdd()
            }
        }
    }

    // 添加按钮
    Rectangle {
        id: addBtn
        anchors.top: parent.top
        anchors.topMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 14
        width: 84; height: 30; radius: 15
        color: "#ff8fb3"
        Text {
            anchors.centerIn: parent
            text: "添加日程"
            color: "white"
            font.pixelSize: 13
            font.bold: true
        }
        MouseArea {
            anchors.fill: parent
            onClicked: win.doAdd()
        }
    }

    // 日程列表
    ListView {
        id: list
        anchors.top: parent.top
        anchors.topMargin: 238
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 14
        clip: true
        spacing: 6
        model: scheduleModel

        delegate: Rectangle {
            width: list.width
            height: 44
            radius: 8
            color: "white"
            border.color: "#f0c8d8"
            border.width: 1

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2
                Text {
                    text: model.stype === "once" ? (model.sdate + "  " + model.stime) : ("每天 " + model.stime)
                    color: "#c94f79"
                    font.pixelSize: 12
                    font.bold: true
                }
                Text {
                    text: model.sevent
                    color: "#444444"
                    font.pixelSize: 13
                }
            }
            Rectangle {
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                width: 28; height: 28; radius: 14
                color: "#ffd9e4"
                Text {
                    anchors.centerIn: parent
                    text: "✕"
                    color: "#d64a74"
                    font.pixelSize: 12
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: scheduleManager.remove(index)
                }
            }
        }
    }

    function doAdd() {
        var t = timeInput.text.trim()
        var e = eventInput.text.trim()
        if (win.isOnce) {
            var d = dateInput.text.trim()
            if (d === "" || t === "" || e === "") {
                dateInput.placeholderText = d === "" ? "请填日期!" : "YYYY-MM-DD"
                timeInput.placeholderText = t === "" ? "请填时间!" : "HH:MM"
                eventInput.placeholderText = e === "" ? "请填事件!" : "要做什么…"
                return
            }
            scheduleManager.addOnce(d, t, e)
            dateInput.text = ""
        } else {
            if (t === "" || e === "") {
                timeInput.placeholderText = t === "" ? "请填时间!" : "HH:MM"
                eventInput.placeholderText = e === "" ? "请填事件!" : "要做什么…"
                return
            }
            scheduleManager.addDaily(t, e)
        }
        timeInput.text = ""
        eventInput.text = ""
    }
}
