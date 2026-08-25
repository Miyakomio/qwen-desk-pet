import QtQuick 2.15
import QtQuick.Window 2.15

/* 展开的对话窗口：查看完整对话历史，可继续聊天。 */
Window {
    id: chatWin
    width: 340
    height: 500
    title: "祈りちゃん · 对话记录"
    color: "#fff7fb"

    property bool showSources: false

    function fmtTime(ms) {
        var d = new Date(ms)
        var now = new Date()
        if (d.getFullYear() === now.getFullYear() &&
            d.getMonth() === now.getMonth() &&
            d.getDate() === now.getDate()) {
            return Qt.formatDateTime(d, "HH:mm")
        }
        return Qt.formatDateTime(d, "MM-dd HH:mm")
    }

    // 标题栏提示
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 34
        color: "#ffe3ef"
        Text {
            anchors.centerIn: parent
            text: "💬 和祈りちゃん的对话"
            color: "#c94f79"
            font.pixelSize: 13
            font.bold: true
            font.family: "Microsoft YaHei"
        }
        // 来源开关（亮=回答附来源，灰=不附）
        Rectangle {
            id: srcBtn
            anchors.right: parent.right
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            width: 22; height: 22; radius: 11
            color: chatWin.showSources ? "#ff8fb3" : "#ffffff"
            border.color: "#f0b6cc"
            border.width: 1
            Text {
                anchors.centerIn: parent
                text: "源"
                font.pixelSize: 11
                font.bold: true
                color: chatWin.showSources ? "white" : "#999999"
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    chatWin.showSources = !chatWin.showSources
                    petBridge.setShowSources(chatWin.showSources)
                }
            }
        }
    }

    // 消息列表
    ListView {
        id: list
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: inputRow.top
        anchors.margins: 8
        clip: true
        spacing: 6
        model: messageModel
        cacheBuffer: 400

        onCountChanged: list.positionViewAtEnd()

        delegate: Column {
            width: list.width
            spacing: 2

            Row {
                width: parent.width
                spacing: 6
                // 头像：用户用「你」圆，桌宠用实际角色形象
                Rectangle {
                    width: 32; height: 32; radius: 16
                    clip: true
                    Image {
                        anchors.fill: parent
                        source: model.msgRole === "user" ? "" : (petFrameDir + "/01.png")
                        fillMode: Image.PreserveAspectCrop
                        visible: model.msgRole !== "user"
                    }
                    Rectangle {
                        anchors.fill: parent
                        radius: 16
                        color: "#e8f0fe"
                        visible: model.msgRole === "user"
                        Text {
                            anchors.centerIn: parent
                            text: "你"
                            color: "#4a76c9"
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }
                // 消息气泡
                Rectangle {
                    width: Math.min(list.width - 44, Math.max(60, msgText.implicitWidth + 18))
                    height: msgText.implicitHeight + 14
                    radius: 10
                    color: model.msgRole === "user" ? "#eef3fd" : "#ffffff"
                    border.color: model.msgRole === "user" ? "#c6d6f0" : "#ffd6e6"
                    border.width: 1
                    Text {
                        id: msgText
                        anchors.fill: parent
                        anchors.margins: 9
                        text: model.text
                        color: "#333333"
                        font.pixelSize: 13
                        font.family: "Microsoft YaHei"
                        wrapMode: Text.Wrap
                    }
                }
            }
            // 时间
            Text {
                anchors.left: parent.left
                anchors.leftMargin: 36
                text: chatWin.fmtTime(model.time)
                color: "#b6b6b6"
                font.pixelSize: 10
            }
        }
    }

    // 底部输入栏
    Rectangle {
        id: inputRow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 44
        color: "#ffffff"
        border.color: "#ffd6e6"
        border.width: 1

        TextInput {
            id: input
            anchors.left: parent.left
            anchors.right: sendBtn.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 12
            anchors.rightMargin: 6
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: 13
            font.family: "Microsoft YaHei"
            color: "#333333"
            selectByMouse: true
            onAccepted: doSend()
        }
        Text {
            anchors.fill: input
            anchors.leftMargin: 12
            verticalAlignment: Text.AlignVCenter
            text: "继续和祈りちゃん说…"
            color: "#c0a6b2"
            font.pixelSize: 13
            font.family: "Microsoft YaHei"
            visible: input.text === ""
            MouseArea { anchors.fill: parent; onClicked: input.forceActiveFocus() }
        }
        Rectangle {
            id: sendBtn
            anchors.right: parent.right
            anchors.rightMargin: 6
            anchors.verticalCenter: parent.verticalCenter
            width: 32; height: 32
            radius: 16
            color: "#ff8fb3"
            Text {
                anchors.centerIn: parent
                text: "➤"
                color: "white"
                font.pixelSize: 13
            }
            MouseArea {
                anchors.fill: parent
                onClicked: doSend()
            }
        }
    }

    function doSend() {
        var t = input.text
        if (t.trim() === "") return
        input.text = ""
        petBridge.sendMessage(t)
    }
}
