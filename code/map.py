# map.py
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from settings import MAP_W, MAP_H, ASSET_DIR
import os

class World(RelativeLayout):
    """Large scrollable world surface. Add objects/characters to this widget."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (MAP_W, MAP_H)
        # background grass (scale to map)
        grass = os.path.join(ASSET_DIR, "environment", "horror_night_grass.png")
        if os.path.exists(grass):
            bg = Image(source=grass, size=self.size, size_hint=(None,None), allow_stretch=True, keep_ratio=False)
            self.add_widget(bg)
        else:
            # fallback solid color
            with self.canvas:
                Color(0.06, 0.1, 0.03, 1)
                Rectangle(pos=self.pos, size=self.size)
        # optional mud patches
        mud = os.path.join(ASSET_DIR, "environment", "mud_land.png")
        if os.path.exists(mud):
            mud1 = Image(source=mud, size=(800,600), size_hint=(None,None), pos=(450,380))
            mud2 = Image(source=mud, size=(700,500), size_hint=(None,None), pos=(1200,160))
            self.add_widget(mud1); self.add_widget(mud2)

