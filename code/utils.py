# utils.py
import os, math, random
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from settings import ASSET_DIR

def asset_path(*parts):
    """Build path to asset; safe join."""
    return os.path.join(ASSET_DIR, *parts)

def safe_image_widget(rel_path, size=(64,64)):
    """Return an Image widget if the file exists, else a colored placeholder Widget.
    The returned widget has size_hint=(None,None) and given size.
    """
    full = asset_path(*rel_path.split("/"))
    if os.path.exists(full):
        return Image(source=full, size_hint=(None, None), size=size)
    # fallback rectangle
    w = Widget(size_hint=(None, None), size=size)
    with w.canvas:
        Color(random.uniform(0.2,0.9), random.uniform(0.2,0.9), random.uniform(0.2,0.9), 1)
        Rectangle(pos=w.pos, size=w.size)
    # keep fallback drawn correctly when pos/size change
    def _upd(inst, _):
        inst.canvas.clear()
        with inst.canvas:
            Color(random.uniform(0.2,0.9), random.uniform(0.2,0.9), random.uniform(0.2,0.9), 1)
            Rectangle(pos=inst.pos, size=inst.size)
    w.bind(pos=_upd, size=_upd)
    return w

def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def clamp(v,a,b):
    return max(a, min(b, v))

