# generator.py
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, BooleanProperty
from settings import GEN_W, GEN_H, ASSET_DIR, REPAIR_TIMES
import os

class Generator(Widget):
    repair_progress = NumericProperty(0.0)
    fixed = BooleanProperty(False)

    def __init__(self, pos, gid, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (GEN_W, GEN_H)
        self.pos = pos
        self.gid = gid
        self.repair_needed = REPAIR_TIMES.get(1, 30.0)  # default; will be updated by game loop per alive players
        self.repair_progress = 0.0
        self.fixed = False
        # visual
        img_file = os.path.join(ASSET_DIR, "environment", "generator.png")
        if os.path.exists(img_file):
            self.img = Image(source=img_file, size=self.size, size_hint=(None,None), pos=self.pos)
            self.add_widget(self.img)
        else:
            with self.canvas:
                Color(0.45, 0.45, 0.45, 1)
                Rectangle(pos=self.pos, size=self.size)
        # overlay progressbar (we will add this progressbar to a UI overlay in main)
        self.progress = ProgressBar(max=100, value=0, size=(GEN_W, 10), size_hint=(None, None), pos=(self.x, self.y - 14))

    def update_ui(self):
        # avoid divide by zero
        if self.repair_needed <= 0: self.progress.value = 100
        else:
            self.progress.value = min(100, (self.repair_progress / self.repair_needed) * 100)
        # keep progress positioned relative to generator widget
        self.progress.pos = (self.x, self.y - 16)
