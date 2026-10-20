#!/usr/bin/env python3
"""Generate the Obscura Global Themes (Plasma look-and-feel packages), dark and light.
Usage: gen_lookandfeel.py [outdir]
"""
import json, pathlib, sys

# Qt6 font strings: family,pt,px,hint,weight,style,underline,strike,fixed,...
def font(family, pt=10, weight=400):
    return f"{family},{pt},-1,5,{weight},0,0,0,0,0,0,0,0,0,0,1"

DEFAULTS = """[kdeglobals][KDE]
widgetStyle=kvantum

[kdeglobals][General]
ColorScheme={scheme}
font={ui}
menuFont={ui}
toolBarFont={ui}
smallestReadableFont={small}
fixed={mono}

[kdeglobals][WM]
activeFont={title}

[kdeglobals][Icons]
Theme={icons}

[plasmarc][Theme]
name=Obscura

[Wallpaper]
Image=Obscura

[kcminputrc][Mouse]
cursorTheme=Obscura-Cursors

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__{scheme}
ButtonsOnLeft=M
ButtonsOnRight=IAX

[ksplashrc][KSplash]
Theme=org.obscura.{variant}.desktop
"""

SPLASH = '''/*
    Obscura splash. Colours come from the live palette, so one file serves dark and light
    and the accent bar follows the System Settings accent.
*/
import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: Kirigami.Theme.backgroundColor

    property int stage   // 1..6, advanced by Plasma as the session starts

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        // crop marks in the corners, like a print proof
        Repeater {
            model: 4
            Item {
                readonly property bool right: index % 2 === 1
                readonly property bool bottom: index > 1
                x: right ? root.width - 40 - 24 : 24
                y: bottom ? root.height - 40 - 24 : 24
                width: 40; height: 40
                Rectangle { width: 40; height: 1; y: bottom ? 39 : 0; color: Kirigami.Theme.textColor; opacity: 0.25 }
                Rectangle { width: 1; height: 40; x: right ? 39 : 0; color: Kirigami.Theme.textColor; opacity: 0.25 }
            }
        }

        Column {
            anchors.centerIn: parent
            spacing: Kirigami.Units.largeSpacing

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "OBSCURA"
                color: Kirigami.Theme.textColor
                font.family: "Archivo"
                font.weight: Font.Bold
                font.pixelSize: Kirigami.Units.gridUnit * 3
                font.letterSpacing: Kirigami.Units.gridUnit * 0.5
                textFormat: Text.PlainText
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "0" + Math.max(1, root.stage) + " / 06"
                color: Kirigami.Theme.textColor
                opacity: 0.6
                font.family: "Geist Mono"
                font.pixelSize: Kirigami.Units.gridUnit * 0.8
                font.letterSpacing: 2
                textFormat: Text.PlainText
            }
        }

        // hairline track with an accent fill that advances with the startup stage
        Rectangle {
            id: track
            width: Kirigami.Units.gridUnit * 16
            height: 1
            anchors.horizontalCenter: parent.horizontalCenter
            y: parent.height * 0.62
            color: Kirigami.Theme.textColor
            opacity: 0.2
        }
        Rectangle {
            height: 3
            anchors.verticalCenter: track.verticalCenter
            x: track.x
            width: track.width * Math.min(root.stage, 6) / 6
            color: Kirigami.Theme.highlightColor
            Behavior on width { NumberAnimation { duration: Kirigami.Units.longDuration * 2; easing.type: Easing.OutCubic } }
        }
    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0
        to: 1
        duration: Kirigami.Units.veryLongDuration * 2
        easing.type: Easing.InOutQuad
    }

    onStageChanged: if (stage === 2) introAnimation.running = true
}
'''

VARIANTS = {
    "dark": dict(scheme="ObscuraDark", icons="breeze-dark", name="Obscura Dark"),
    "light": dict(scheme="ObscuraLight", icons="breeze", name="Obscura Light"),
}


def write(root):
    for variant, v in VARIANTS.items():
        pkg = pathlib.Path(root) / f"org.obscura.{variant}.desktop"
        (pkg / "contents/splash").mkdir(parents=True, exist_ok=True)
        meta = {
            "KPackageStructure": "Plasma/LookAndFeel",
            "KPlugin": {
                "Authors": [{"Name": "Obscura"}],
                "Category": "",
                "Description": "Sharp-cornered theme with an editorial look. Follows the system accent; CachyOS green by default.",
                "Id": f"org.obscura.{variant}.desktop",
                "License": "MIT",
                "Name": v["name"],
                "Version": "0.1",
            },
            "X-Plasma-APIVersion": "2",
        }
        (pkg / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
        (pkg / "contents/defaults").write_text(DEFAULTS.format(
            variant=variant, scheme=v["scheme"], icons=v["icons"],
            ui=font("Inter", 11), small=font("Inter", 9), mono=font("Geist Mono", 11), title=font("Archivo", 11, 600)))
        (pkg / "contents/splash/Splash.qml").write_text(SPLASH)
        print("wrote", pkg)


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else "build/look-and-feel")
