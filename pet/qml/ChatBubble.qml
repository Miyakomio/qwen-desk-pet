import QtQuick 2.15
import QtQuick.Controls 2.15

/* 对话气泡：显示最近一条用户消息 + 助手回复。
   高度由父级设定，内容超出时可滚动（带滚动条）。 */
Rectangle {
    id: bubble
    property string userText: ""       // 用户刚说的话
    property string fullText: ""       // 助手完整回复
    property bool thinking: false      // 是否正在思考
    property int shown: 0              // 打字机已显示的字符数
    property int _thinkIdx: 0
    property var thinkLines: [
        "小小的脑袋转成浆糊啦喵…",
        "唔…正在用力思考~",
        "转转小脑袋想想~",
        "啊…差点短路啦！",
        "脑袋瓜在冒烟中…",
        "嗯…让祈祈捋一捋~",
        "呜…想不出！再想想~",
    ]

    width: 204
    radius: 14
    border.color: "#ffd6e6"
    border.width: 1.5
    color: "white"
    opacity: 0.97
    Behavior on opacity { NumberAnimation { duration: 500 } }

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#ffffff" }
        GradientStop { position: 1.0; color: "#fff2f9" }
    }

    function beginTyping(text) {
        fullText = text
        shown = 0
        typeTimer.restart()
        flick.contentY = 0
    }

    Timer {
        id: typeTimer
        interval: 14
        repeat: true
        onTriggered: {
            bubble.shown += 1
            if (bubble.shown >= bubble.fullText.length) {
                typeTimer.stop()
                // 打完后自动滚到底部
                flick.contentY = flick.contentHeight - flick.height
            }
        }
    }

    // 思考文字轮换
    Timer {
        id: thinkTimer
        interval: 1300
        repeat: true
        running: bubble.thinking
        onTriggered: {
            bubble._thinkIdx = (bubble._thinkIdx + 1) % bubble.thinkLines.length
        }
    }

    Flickable {
        id: flick
        anchors.fill: parent
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        contentHeight: col.height + 22

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            visible: flick.contentHeight > flick.height
        }

        Column {
            id: col
            x: 11; y: 11
            width: flick.width - 22
            spacing: 5

            // 用户消息
            Text {
                width: parent.width
                text: bubble.userText !== "" ? "你：" + bubble.userText : ""
                color: "#b08a9a"
                font.pixelSize: 11
                wrapMode: Text.Wrap
                visible: text !== ""
            }

            // 助手回复（打字机）
            Text {
                width: parent.width
                text: bubble.fullText.slice(0, bubble.shown)
                color: "#333333"
                font.pixelSize: 13
                font.family: "Microsoft YaHei"
                lineHeight: 1.3
                wrapMode: Text.Wrap
                visible: !bubble.thinking
            }

            // 思考动画：可爱呆萌的旋转文字
            Text {
                visible: bubble.thinking
                anchors.left: parent.left
                text: bubble.thinkLines[bubble._thinkIdx]
                color: "#c9a0ae"
                font.pixelSize: 12
                font.family: "Microsoft YaHei"
            }
        }
    }

    // 气泡尾巴
    Canvas {
        x: parent.width - 52
        y: parent.height - 1
        width: 20; height: 14
        onPaint: {
            var c = getContext("2d")
            c.fillStyle = "#fff2f9"
            c.strokeStyle = "#ffd6e6"
            c.lineWidth = 1.5
            c.beginPath()
            c.moveTo(0, 0)
            c.lineTo(20, 0)
            c.lineTo(12, 13)
            c.closePath()
            c.fill()
            c.stroke()
        }
    }
}
