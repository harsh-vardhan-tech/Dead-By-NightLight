# entities.py
import os, math, random
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from settings import ASSET_DIR, PLAYER_SPEED, NPC_SPEED, HUNTER_SPEED
from utils import safe_image_widget, asset_path, distance, clamp

class Entity(Widget):
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    alive = BooleanProperty(True)
    entity_name = StringProperty("entity")

    def move(self, dt):
        if not self.alive: return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = clamp(self.x, 0, 1920 - self.width)
        self.y = clamp(self.y, 0, 1080 - self.height)

    def center(self):
        return (self.x + self.width/2, self.y + self.height/2)

class Player(Entity):
    def __init__(self, x=150, y=150, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "player"
        self.width = 64; self.height = 64
        self.pos = (x,y)
        # load default sprite (front)
        img = asset_path("player","front.png")
        if os.path.exists(img):
            w = Image(source=img, size=(self.width,self.height), size_hint=(None,None))
            self.add_widget(w)
        else:
            with self.canvas:
                Color(0.2,0.6,0.9,1)
                Rectangle(pos=self.pos, size=(self.width,self.height))
        self.speed = PLAYER_SPEED
        self.repairing = False
        self.near_generator = None
        self.hit_stage = 0   # 0 none, 1 first hit, 2 second hit, 3 dead
        self.down_timer = 0.0
        self.alive = True

    def update(self, dt):
        # handle down timer (slow movement)
        if self.down_timer > 0:
            self.down_timer -= dt
            factor = 0.3
        else:
            factor = 1.0
        # apply movement scaled externally via vx/vy; speed handled by input code
        self.vx = clamp(self.vx, -self.speed*factor, self.speed*factor)
        self.vy = clamp(self.vy, -self.speed*factor, self.speed*factor)
        self.move(dt)

    def take_hit(self):
        self.hit_stage += 1
        if self.hit_stage == 1:
            self.down_timer = 4.0  # slowed/down
        elif self.hit_stage == 2:
            self.down_timer = 4.0  # sustained penalty
        elif self.hit_stage >= 3:
            self.alive = False

class NPC(Entity):
    def __init__(self, x, y, skill="noob", **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "npc"
        self.width = 64; self.height = 64
        self.pos = (x,y)
        self.skill = skill
        img = asset_path(f"npc{'' if skill=='noob' else '_pro'}")
        # try the custom file names: npc1 folder images name not enforced; fallback colored
        img_file = None
        # prefer 'npc1/front.png' style if present in assets, else default box
        # We'll draw fallback rectangle for NPCs
        with self.canvas:
            Color(0.8,0.7,0.2 if skill=="pro" else 0.6, 1)
            Rectangle(pos=self.pos, size=(self.width,self.height))
        self.timer = random.uniform(0.5, 2.0)
        self.dir = (0,0)
        self.speed = NPC_SPEED * (1.2 if skill=="pro" else 1.0)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(0.6, 2.0)
            if random.random() < 0.75:
                ang = random.uniform(0, 2*math.pi)
                self.dir = (math.cos(ang), math.sin(ang))
            else:
                self.dir = (0,0)
        self.vx = self.dir[0] * self.speed
        self.vy = self.dir[1] * self.speed
        self.move(dt)

class Hunter(Entity):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "hunter"
        self.width = 84; self.height = 84
        self.pos = (x,y)
        self.speed = HUNTER_SPEED
        img = asset_path("hunter","front.png")
        if os.path.exists(img):
            w = Image(source=img, size=(self.width,self.height), size_hint=(None,None))
            self.add_widget(w)
        else:
            with self.canvas:
                Color(0.8, 0.1, 0.1, 1)
                Rectangle(pos=self.pos, size=(self.width,self.height))
        self.attack_cooldown = 0.0

    def update(self, dt, player, npcs):
        # choose target: player (if alive) else nearest alive npc
        target = player if player.alive else None
        if not target:
            min_d = float("inf"); tgt = None
            for n in npcs:
                if n.alive:
                    d = distance(self.center(), n.center())
                    if d < min_d:
                        min_d = d; tgt = n
            target = tgt
        if target:
            tx, ty = target.center()
            sx, sy = self.center()
            dx = tx - sx; dy = ty - sy
            dist = math.hypot(dx, dy) + 1e-6
            self.vx = (dx/dist) * self.speed
            self.vy = (dy/dist) * self.speed
        else:
            self.vx = self.vy = 0
        self.move(dt)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
