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

    // 输入表格
    Grid {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 12
        columns: 2
        columnSpacing: 8
        rowSpacing: 8
        leftPadding: 4

        Text { text: "日期"; color: "#666666"; font.pixelSize: 12 }
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
        Text { text: "时间"; color: "#666666"; font.pixelSize: 12 }
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
        Text { text: "事件"; color: "#666666"; font.pixelSize: 12 }
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

    // 添加按钮
    Rectangle {
        id: addBtn
        anchors.top: parent.top
        anchors.topMargin: 150
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
        anchors.topMargin: 196
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
                    text: model.sdate + "  " + model.stime
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
        var d = dateInput.text.trim()
        var t = timeInput.text.trim()
        var e = eventInput.text.trim()
        if (d === "" || t === "" || e === "") {
            dateInput.placeholderText = d === "" ? "请填日期!" : "YYYY-MM-DD"
            timeInput.placeholderText = t === "" ? "请填时间!" : "HH:MM"
            eventInput.placeholderText = e === "" ? "请填事件!" : "要做什么…"
            return
        }
        scheduleManager.add(d, t, e)
        dateInput.text = ""
        timeInput.text = ""
        eventInput.text = ""
    }
}
