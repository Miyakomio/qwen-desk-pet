import QtQuick 2.15

/* 二次元桌宠角色 —— 使用现成透明素材帧。
   petFrameDir = 帧图所在目录, petFrameCount = 帧数(多帧循环=待机动画, 单帧=静态)。
   保留互动：摸头(爱心)、捏脸(红印)，并向外发出 interacted 信号。 */
Item {
    id: root
    width: 220
    height: 250

    property string emotion: "neutral"
    signal interacted(string kind)      // 摸头 / 捏脸
    property bool patting: false
    property bool poked: false
    property string _prevEmotion: "neutral"
    property int _frame: 0

    function pat() {
        interacted("pat")
        root._prevEmotion = root.emotion
        root.emotion = "love"
        root.patting = true
        resetTimer.restart()
    }
    function poke() {
        interacted("poke")
        root._prevEmotion = root.emotion
        root.emotion = "surprised"
        root.poked = true
        pokeSquish.restart()
        resetTimer.restart()
    }

    Timer {
        id: resetTimer
        interval: 1600
        repeat: false
        onTriggered: {
            root.emotion = root._prevEmotion
            root.patting = false
            root.poked = false
        }
    }

    function framePath(n) {
        var nn = n < 10 ? "0" + n : "" + n
        return petFrameDir + "/" + nn + ".png"
    }

    // 待机动画：多帧则循环切换
    Timer {
        id: idleTimer
        interval: 200
        repeat: true
        running: petFrameCount > 1
        onTriggered: {
            root._frame = (root._frame + 1) % petFrameCount
            charImg.source = root.framePath(root._frame + 1)
        }
    }

    // 角色图片（透明底，底部居中）
    Image {
        id: charImg
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        width: 200
        height: 177
        source: root.framePath(1)
        fillMode: Image.PreserveAspectFit
        smooth: true
        mipmap: true
    }

    // 摸头爱心特效
    Row {
        visible: root.patting
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: charImg.top
        anchors.bottomMargin: 2
        spacing: 10
        Repeater {
            model: 3
            Text {
                text: "❤"
                color: "#ff5b7f"
                font.pixelSize: 20
                SequentialAnimation on y {
                    loops: Animation.Infinite
                    NumberAnimation { from: 0; to: -34; duration: 900; easing.type: Easing.OutQuad }
                    NumberAnimation { from: -34; to: 0; duration: 0 }
                }
            }
        }
    }

    // 捏脸红印
    Rectangle {
        visible: root.poked
        x: 70; y: 120; width: 16; height: 9; radius: 5
        color: "#ff8c94"; opacity: 0.9
    }

    // 被捏时的轻微缩放抖动
    SequentialAnimation {
        id: pokeSquish
        NumberAnimation { target: root; property: "scale"; from: 1.0; to: 0.93; duration: 90 }
        NumberAnimation { target: root; property: "scale"; from: 0.93; to: 1.0; duration: 220 }
    }

    // ---------- 交互区（仅左键，右键留给拖动） ----------
    // 摸头：点住头部（上半部）
    MouseArea {
        x: 45; y: 86; width: 130; height: 88
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.PointingHandCursor
        onPressed: root.pat()
    }
    // 捏脸：点身体/脸（中下部）
    MouseArea {
        x: 55; y: 138; width: 110; height: 56
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.PointingHandCursor
        onPressed: root.poke()
    }
}
