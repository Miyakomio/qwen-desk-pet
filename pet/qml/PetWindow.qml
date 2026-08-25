import QtQuick 2.15
import QtQuick.Window 2.15

/* 二次元桌宠主窗口：透明、无边框、置顶、可拖动、紧凑布局。 */
Window {
    id: root
    width: 220
    height: 330
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowType.Tool
    color: "transparent"

    property var patLines: ["嘿嘿~ ♥", "摸摸~", "好舒服呀~", "爱你~ ♥"]
    property var pokeLines: ["呀！", "别捏啦~", "唔…", "痛痛~"]
    property var idleSince: Date.now()

    Timer {
        id: idleTimer
        interval: 400
        repeat: true
        running: true
        onTriggered: root.checkIdle()
    }

    function markActive() {
        root.idleSince = Date.now()
        root.checkIdle()
    }
    function checkIdle() {
        // 正在输入/输入框有焦点时，始终保持显示，不隐藏
        if (input.activeFocus) {
            bubble.opacity = 1
            inputRow.opacity = 1
            expandBtn.opacity = 1
            closeBtn.opacity = 1
            return
        }
        var el = Date.now() - root.idleSince
        var t, btnT
        if (el > configIdleHide) { t = 0; btnT = 0 }        // 隐身（按钮一起藏）
        else if (el > configIdleSemi) { t = 0.45; btnT = 1 } // 半透明
        else { t = 1; btnT = 1 }
        bubble.opacity = t
        inputRow.opacity = t
        expandBtn.opacity = btnT
        closeBtn.opacity = btnT
    }

    // 背景拖拽层（左/右键都可拖动；点击/触碰会唤回界面）
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        property var startPos
        onPositionChanged: (mouse) => {
            if (pressed) {
                root.x += mouse.x - startPos.x
                root.y += mouse.y - startPos.y
            }
        }
        onPressed: (mouse) => { startPos = Qt.point(mouse.x, mouse.y); root.markActive() }
    }

    // 展开对话记录按钮（置顶，打开独立对话窗口）
    Rectangle {
        id: expandBtn
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.topMargin: 24
        anchors.leftMargin: 8
        width: 22; height: 22
        radius: 11
        color: "transparent"
        Behavior on opacity { NumberAnimation { duration: 500 } }
        Text {
            anchors.centerIn: parent
            text: "☰"
            color: "#bbbbbb"
            font.pixelSize: 14
        }
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onClicked: { chatWindow.show(); chatWindow.raise(); chatWindow.requestActivate() }
        }
    }

    // 关闭按钮（置顶）
    Rectangle {
        id: closeBtn
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 24
        anchors.rightMargin: 8
        width: 22; height: 22
        radius: 11
        color: "transparent"
        Behavior on opacity { NumberAnimation { duration: 500 } }
        Text {
            anchors.centerIn: parent
            text: "✕"
            color: "#bbbbbb"
            font.pixelSize: 13
        }
        MouseArea {
            anchors.fill: parent
            onClicked: root.hide()
        }
    }

    // 角色（底部居中，带轻微浮动动画；更小）
    Character {
        id: character
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: inputRow.top
        anchors.bottomMargin: -4
        scale: 0.5
        transformOrigin: Item.Bottom

        SequentialAnimation on anchors.bottomMargin {
            loops: Animation.Infinite
            running: true
            NumberAnimation { from: -4; to: -9; duration: 1400; easing.type: Easing.InOutSine }
            NumberAnimation { from: -9; to: -4; duration: 1400; easing.type: Easing.InOutSine }
        }
    }

    // 对话气泡（固定高度、可滚动）
    ChatBubble {
        id: bubble
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 34
        height: 88
    }

    // 互动反应小气泡（在人物左边显示，独立于对话气泡，几秒后消失）
    Rectangle {
        id: reaction
        visible: false
        opacity: 0
        anchors.left: parent.left
        anchors.leftMargin: 4
        anchors.verticalCenter: character.verticalCenter
        anchors.verticalCenterOffset: -40
        radius: 11
        color: "#fff3fa"
        border.color: "#ffb7d0"
        border.width: 1.5
        height: reactionText.implicitHeight + 14
        width: reactionText.implicitWidth + 22
        z: 20

        Text {
            id: reactionText
            anchors.centerIn: parent
            font.pixelSize: 12
            font.family: "Microsoft YaHei"
            color: "#444444"
        }
        Behavior on opacity { NumberAnimation { duration: 450 } }
        onOpacityChanged: { if (reaction.opacity <= 0) reaction.visible = false }
        Timer { id: reactionHide; interval: 2500; repeat: false; onTriggered: reaction.opacity = 0 }

        function show(text) {
            reactionText.text = text
            reaction.visible = true
            reaction.opacity = 1
            reactionHide.restart()
        }
    }

    // 输入栏
    Rectangle {
        id: inputRow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 8
        height: 28
        radius: 14
        color: "white"
        border.color: "#ffd6e6"
        border.width: 2
        Behavior on opacity { NumberAnimation { duration: 500 } }

        TextInput {
            id: input
            anchors.left: parent.left
            anchors.right: sendBtn.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 14
            anchors.rightMargin: 6
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: 13
            font.family: "Microsoft YaHei"
            color: "#333333"
            selectByMouse: true
            onActiveFocusChanged: if (activeFocus) root.markActive()
            onTextChanged: root.markActive()
            onAccepted: doSend()
        }

        Text {
            anchors.fill: input
            anchors.leftMargin: 14
            verticalAlignment: Text.AlignVCenter
            text: "和祈りちゃん说点什么…"
            color: "#c0a6b2"
            font.pixelSize: 13
            font.family: "Microsoft YaHei"
            visible: input.text === ""
            MouseArea {
                anchors.fill: parent
                onClicked: { input.forceActiveFocus(); root.markActive() }
            }
        }

        Rectangle {
            id: sendBtn
            anchors.right: parent.right
            anchors.rightMargin: 3
            anchors.verticalCenter: parent.verticalCenter
            width: 26; height: 26
            radius: 13
            color: "#ff8fb3"
            Text {
                anchors.centerIn: parent
                text: "➤"
                color: "white"
                font.pixelSize: 12
            }
            MouseArea {
                anchors.fill: parent
                onClicked: doSend()
            }
        }
    }

    function pick(arr) { return arr[Math.floor(Math.random() * arr.length)] }

    function doSend() {
        var t = input.text
        if (t.trim() === "") return
        input.text = ""
        root.markActive()
        petBridge.sendMessage(t)
    }

    Component.onCompleted: {
        petBridge.userMessage.connect(function (t) { bubble.userText = t; root.markActive() })
        petBridge.botMessage.connect(function (t) { bubble.thinking = false; bubble.beginTyping(t); root.markActive() })
        petBridge.thinking.connect(function (b) { bubble.thinking = b; root.markActive() })
        petBridge.emotion.connect(function (e) { character.emotion = e })
        // 互动：摸头 / 捏脸（用独立弹幕，不打断气泡的思考和回复）
        character.interacted.connect(function (kind) {
            reaction.show(kind === "pat" ? pick(patLines) : pick(pokeLines))
            root.markActive()
        })
        // 欢迎语
        bubble.beginTyping("你好呀~ 我是祈りちゃん(✿◡‿◡) 来和我聊聊吧！")
        root.markActive()
    }
}
