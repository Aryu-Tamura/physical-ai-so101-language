"""Readable Japanese overlays on actual MuJoCo-rendered frames."""

from pathlib import Path
import os
import numpy as np
import mujoco, imageio
from PIL import Image, ImageDraw, ImageFont

FONT = os.environ.get("PAI_JP_FONT", "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc")
PHASES = {
    "settle": "準備",
    "approach": "物体の上へ",
    "descend": "つかむ位置へ",
    "close": "グリッパを閉じる",
    "lift": "持ち上げて確認",
    "transfer": "移動",
    "lower": "置く位置へ",
    "release": "物体を離す",
    "retreat": "退避",
    "failure_detected": "持ち上げ失敗を検出",
}
FONTS = {n: ImageFont.truetype(FONT, n) for n in [16, 18, 20, 22, 24, 28, 32, 40, 48]}
BG = (13, 22, 32)
FG = (235, 242, 247)
MUTED = (158, 180, 195)
ACCENT = (82, 220, 185)


def wrap(text, width, font):
    lines = []
    line = ""
    for char in text:
        if char == "\n" or font.getlength(line + char) > width:
            lines.append(line)
            line = "" if char == "\n" else char
        else:
            line += char
    if line:
        lines.append(line)
    return lines


def card(title, lines, tag="PHYSICAL AI / SO-101"):
    im = Image.new("RGB", (1280, 720), BG)
    d = ImageDraw.Draw(im)
    d.text((52, 34), tag, font=FONTS[20], fill=ACCENT)
    d.line((52, 82, 1228, 82), fill=ACCENT, width=2)
    y = 130
    for l in wrap(title, 1170, FONTS[40]):
        d.text((52, y), l, font=FONTS[40], fill=FG)
        y += 60
    y += 35
    for line in lines:
        for l in wrap(line, 1170, FONTS[28]):
            d.text((52, y), l, font=FONTS[28], fill=FG)
            y += 43
        y += 18
    return im


class Recorder:
    def __init__(
        self, arm, path, text, title="言葉で動く SO-101", note="", intent=None
    ):
        self.arm = arm
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.renderer = mujoco.Renderer(arm.model, height=560, width=880)
        self.camera = mujoco.MjvCamera()
        self.camera.lookat[:] = [0.19, 0, 0.07]
        self.camera.distance = 0.76
        self.camera.azimuth = 145
        self.camera.elevation = -38
        self.opt = mujoco.MjvOption()
        self.opt.geomgroup[3:] = False
        self.writer = imageio.get_writer(
            str(path), fps=25, quality=8, macro_block_size=1
        )
        self.text = text
        self.title = title
        self.note = note
        self.intent = intent
        self.frames = 0
        self.last = None
        arm.frame_callback = self.capture

    def compose(self):
        self.renderer.update_scene(
            self.arm.data, camera=self.camera, scene_option=self.opt
        )
        self.renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = False
        scene = self.renderer.render()
        im = Image.new("RGB", (1280, 720), BG)
        im.paste(Image.fromarray(scene), (16, 100))
        d = ImageDraw.Draw(im)
        d.text((28, 24), self.title, font=FONTS[28], fill=FG)
        d.text(
            (28, 68),
            "MuJoCo / SO-101 / 接触物理シミュレーション",
            font=FONTS[18],
            fill=MUTED,
        )
        d.rounded_rectangle((912, 102, 1260, 658), radius=18, fill=(23, 38, 50))
        d.text((932, 124), "TEXT INSTRUCTION", font=FONTS[18], fill=ACCENT)
        y = 163
        for line in wrap(self.text, 304, FONTS[24]):
            d.text((932, y), line, font=FONTS[24], fill=FG)
            y += 36
        y += 30
        if self.intent:
            for label, val in [
                ("対象", self.intent.get("color")),
                ("移動先", self.intent.get("destination")),
            ]:
                d.text((932, y), f"{label}: {val}", font=FONTS[20], fill=MUTED)
                y += 33
        y = max(y + 25, 400)
        d.text((932, y), "実行状態", font=FONTS[18], fill=ACCENT)
        y += 32
        for line in wrap(PHASES.get(self.arm.phase, self.arm.phase), 304, FONTS[24]):
            d.text((932, y), line, font=FONTS[24], fill=FG)
            y += 35
        d.text(
            (932, 606),
            f"sim time  {self.arm.data.time:5.2f} s",
            font=FONTS[18],
            fill=MUTED,
        )
        d.text(
            (28, 672),
            self.note
            or "実時間再生 / 物体情報はシミュレータから取得 / 音声・画像認識なし",
            font=FONTS[18],
            fill=MUTED,
        )
        return im

    def capture(self, arm):
        self.last = self.compose()
        self.writer.append_data(np.asarray(self.last))
        self.frames += 1

    def hold(self, seconds):
        for _ in range(round(seconds * 25)):
            self.capture(self.arm)

    def close(self):
        self.arm.frame_callback = None
        self.writer.close()
        self.renderer.close()
