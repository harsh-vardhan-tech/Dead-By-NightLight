# main.py
import os, random
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, FadeTransition, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from settings import SCREEN_W, SCREEN_H, MAP_W, MAP_H, ASSET_DIR, NUM_GENERATORS, REPAIR_TIMES, FPS
from map import World
from entities import Player, NPC, Hunter
from generator import Generator
from utils import safe_image_widget, asset_path, distance, clamp

# Main Game Screen
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game"
        self.root_layer = FloatLayout(size=(SCREEN_W, SCREEN_H))
        self.add_widget(self.root_layer)

        # world viewport and world
        self.world = World(size=(MAP_W, MAP_H))
        self.world.pos = (0,0)
        self.viewport = Widget(size=(SCREEN_W, SCREEN_H), pos=(0,0))
        self.root_layer.add_widget(self.viewport)
        self.viewport.add_widget(self.world)

        # entities
        self.player = Player(200,200)
        self.world.add_widget(self.player)

        self.npcs = []
        for i in range(4):
            skill = random.choice(["noob","pro"])
            n = NPC(random.randint(300, MAP_W-200), random.randint(200, MAP_H-200), skill=skill)
            self.npcs.append(n)
            self.world.add_widget(n)

        self.hunter = Hunter(MAP_W - 320, MAP_H - 300)
        self.world.add_widget(self.hunter)

        # generators
        self.generators = []
        taken = []
        for i in range(NUM_GENERATORS):
            while True:
                gx = random.randint(150, MAP_W - 150 - 64)
                gy = random.randint(150, MAP_H - 150 - 64)
                if all(distance((gx,gy), t) >= 160 for t in taken):
                    taken.append((gx,gy)); break
            g = Generator((gx,gy), gid=i)
            self.generators.append(g)
            self.world.add_widget(g)
            # overlay progress on root_layer so always visible
            self.root_layer.add_widget(g.progress)

        # gate visual
        self.gate_pos = (MAP_W - 200, MAP_H//2)
        self.gate_widget = Widget(size=(120,160), pos=self.gate_pos)
        # draw gate (close)
        gate_close = asset_path("environment","gate_close.png")
        if os.path.exists(gate_close):
            from kivy.graphics import Rectangle
            with self.gate_widget.canvas:
                Rectangle(source=gate_close, pos=self.gate_widget.pos, size=self.gate_widget.size)
        else:
            from kivy.graphics import Color, Rectangle
            with self.gate_widget.canvas:
                Color(0.5,0.2,0.2,1); Rectangle(pos=self.gate_widget.pos, size=self.gate_widget.size)
        self.world.add_widget(self.gate_widget)
        self.gate_open = False

        # UI controls
        self.build_mobile_controls()

        # top-left info label
        self.info_label = Label(text="Health: 3  |  Generators: 0/{}".format(NUM_GENERATORS),
                                size_hint=(None,None), pos=(10, SCREEN_H - 40))
        self.root_layer.add_widget(self.info_label)

        # pause button
        self.pause_btn = Button(text="||", size_hint=(None,None), size=(70,70), pos=(SCREEN_W - 80, SCREEN_H - 80))
        self.pause_btn.bind(on_release=self.toggle_pause)
        self.root_layer.add_widget(self.pause_btn)

        # repair button (right bottom)
        self.repair_btn = Button(text="REPAIR", size_hint=(None,None), size=(140,80), pos=(SCREEN_W - 160, 20))
        self.repair_btn.bind(on_press=self.start_repair); self.repair_btn.bind(on_release=self.stop_repair)
        self.repair_btn.disabled = True
        self.root_layer.add_widget(self.repair_btn)

        self.running = False
        self.paused = False
        self.elapsed = 0.0
        Clock.schedule_interval(self.update, 1.0 / FPS)

    def build_mobile_controls(self):
        # simple 4-arrow buttons bottom-left
        btn_size = (100,100)
        pad_x = 18; pad_y = 18
        self.up = Button(text="↑", size_hint=(None,None), size=btn_size, pos=(pad_x+btn_size[0], pad_y+btn_size[1]))
        self.down = Button(text="↓", size_hint=(None,None), size=btn_size, pos=(pad_x+btn_size[0], pad_y))
        self.left = Button(text="←", size_hint=(None,None), size=btn_size, pos=(pad_x, pad_y))
        self.right = Button(text="→", size_hint=(None,None), size=btn_size, pos=(pad_x+2*btn_size[0], pad_y))
        for b,vec in ((self.up,(0,1)), (self.down,(0,-1)), (self.left,(-1,0)), (self.right,(1,0))):
            b.bind(on_press=lambda inst, v=vec: self.move_pressed(v))
            b.bind(on_release=lambda inst: self.move_released())
            self.root_layer.add_widget(b)

    def move_pressed(self, vec):
        dx,dy = vec
        self.player.vx = dx * self.player.speed
        self.player.vy = dy * self.player.speed

    def move_released(self):
        self.player.vx = 0; self.player.vy = 0

    def start_repair(self, *a):
        if not self.player.near_generator: return
        g = self.player.near_generator
        if g.fixed: return
        self.player.repairing = True

    def stop_repair(self, *a):
        self.player.repairing = False

    def toggle_pause(self, *a):
        self.paused = not self.paused
        if self.paused:
            App.get_running_app().sm.current = "pause"
        else:
            App.get_running_app().sm.current = "game"

    def start_game(self):
        # reset core state
        self.running = True; self.paused = False; self.elapsed = 0.0
        self.player.pos = (200,200); self.player.alive = True; self.player.hit_stage = 0; self.player.down_timer = 0.0
        self.hunter.pos = (MAP_W - 320, MAP_H - 300)
        # reset gens
        for g in self.generators:
            g.fixed = False; g.repair_progress = 0.0
            if g not in self.world.children: self.world.add_widget(g)
            if g.progress not in self.root_layer.children: self.root_layer.add_widget(g.progress)
        self.gate_open = False
        # ensure gate visual closed
        # (rebuild gate widget if necessary) - omitted heavy redraw for brevity

    def update(self, dt):
        if not self.running or self.paused: return
        self.elapsed += dt
        # update player
        self.player.update(dt)
        # update NPCs
        for n in self.npcs: n.update(dt)
        # hunter logic
        self.hunter.update(dt, self.player, self.npcs)

        # update generators repair_needed based on alive players (single player mode -> 1)
        alive_players = 1 if self.player.alive else 0
        # compute base
        if alive_players <= 1: base = REPAIR_TIMES[1]
        elif alive_players == 2: base = REPAIR_TIMES[2]
        elif alive_players == 3: base = REPAIR_TIMES[3]
        elif alive_players == 4: base = REPAIR_TIMES[4]
        else: base = REPAIR_TIMES[5]
        for g in self.generators:
            g.repair_needed = base
            g.update_ui()

        # detect player near generator
        self.player.near_generator = None
        for g in self.generators:
            if g.fixed: continue
            gx, gy = g.x + g.width/2, g.y + g.height/2
            px, py = self.player.center()
            if distance((gx,gy),(px,py)) < 90:
                self.player.near_generator = g
                self.repair_btn.disabled = False
                break
        if not self.player.near_generator:
            self.repair_btn.disabled = True
            self.player.repairing = False

        # repairing logic
        if self.player.repairing and self.player.near_generator:
            g = self.player.near_generator
            # if hunter close: interrupt
            if distance(self.hunter.center(), self.player.center()) < 140:
                self.player.repairing = False
            else:
                g.repair_progress += dt
                g.update_ui()
                if g.repair_progress >= g.repair_needed:
                    g.fixed = True
                    try:
                        self.world.remove_widget(g)
                    except Exception:
                        pass
                    try:
                        self.root_layer.remove_widget(g.progress)
                    except Exception:
                        pass
                    self.player.repairing = False

        # hunter attack handling
        if self.hunter.attack_cooldown <= 0:
            if distance(self.hunter.center(), self.player.center()) < 60 and self.player.alive:
                self.player.take_hit()
                self.hunter.attack_cooldown = 1.2
            else:
                for n in self.npcs:
                    if n.alive and distance(self.hunter.center(), n.center()) < 60:
                        # kill NPC instantly
                        n.alive = False
                        try: self.world.remove_widget(n)
                        except: pass
                        self.hunter.attack_cooldown = 1.2
                        break
        else:
            # cooldown counts down inside Hunter.update (call ensured)
            pass

        # lose condition
        if not self.player.alive:
            self.running = False
            App.get_running_app().sm.current = "lose"
            return

        # win condition: all gens fixed -> open gate -> if player reaches gate -> win
        all_fixed = all(g.fixed for g in self.generators)
        if all_fixed and not self.gate_open:
            self.open_gate()
        if self.gate_open:
            gx, gy = self.gate_widget.x, self.gate_widget.y
            if distance((gx,gy), self.player.center()) < 80:
                self.running = False
                App.get_running_app().sm.current = "win"
                return

        # camera follow (centers player)
        cam_x = clamp(self.player.center()[0] - SCREEN_W/2, 0, MAP_W - SCREEN_W)
        cam_y = clamp(self.player.center()[1] - SCREEN_H/2, 0, MAP_H - SCREEN_H)
        self.world.pos = (-cam_x, -cam_y)

        # update overlay info and progressbars
        fixed_count = sum(1 for g in self.generators if g.fixed)
        self.info_label.text = f"Health: {3 - max(0,self.player.hit_stage - 0)}  |  Generators: {fixed_count}/{NUM_GENERATORS}"
        for g in self.generators:
            g.update_ui()

    def open_gate(self):
        self.gate_open = True
        open_img = asset_path("environment","gate_open.png")
        if os.path.exists(open_img):
            try:
                self.world.remove_widget(self.gate_widget)
            except: pass
            from kivy.uix.widget import Widget
            gw = Widget(size=(120,160), pos=self.gate_pos)
            from kivy.graphics import Rectangle
            with gw.canvas:
                Rectangle(source=open_img, pos=gw.pos, size=gw.size)
            self.gate_widget = gw
            self.world.add_widget(self.gate_widget)
        # else if no asset, leave color change as is

# Menu/Pause/Win/Lose screens (simple)
class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fl = FloatLayout(); self.add_widget(fl)
        title = Label(text="[b][size=40]HORROR NIGHT[/size][/b]", markup=True, pos_hint={"center_x":0.5,"center_y":0.7})
        fl.add_widget(title)
        play = Button(text="PLAY", size_hint=(0.3,0.12), pos_hint={"center_x":0.5,"center_y":0.5})
        quitb = Button(text="QUIT", size_hint=(0.3,0.12), pos_hint={"center_x":0.5,"center_y":0.35})
        play.bind(on_release=self.start_game); quitb.bind(on_release=lambda *_: App.get_running_app().stop())
        fl.add_widget(play); fl.add_widget(quitb)
    def start_game(self, *a):
        App.get_running_app().sm.current = "game"
        App.get_running_app().game_screen.start_game()

class PauseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fl = FloatLayout(); self.add_widget(fl)
        Label(text="[b]PAUSED[/b]", markup=True, pos_hint={"center_x":0.5,"center_y":0.6})
        Button(text="RESUME", size_hint=(0.3,0.12), pos_hint={"center_x":0.5,"center_y":0.45},
               on_release=lambda *_: setattr(App.get_running_app().game_screen, "paused", False)).bind()
        Button(text="MAIN MENU", size_hint=(0.3,0.12), pos_hint={"center_x":0.5,"center_y":0.3},
               on_release=lambda *_: setattr(App.get_running_app().sm, "current", "menu")).bind()

class WinScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fl = FloatLayout(); self.add_widget(fl)
        Label(text="[b]YOU ESCAPED![/b]", markup=True, pos_hint={"center_x":0.5,"center_y":0.6})
        Button(text="MAIN MENU", size_hint=(0.3,0.12), pos_hint={"center_x":0.5,"center_y":0.4},
               on_release=lambda *_: setattr(App.get_running_app().sm, "current", "menu")).bind()

class LoseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fl = FloatLayout(); self.add_widget(fl)
        Label(text="[b]YOU DIED[/b]", markup=True, pos_hint={"center_x":0.5,"center_y":0.6})
        Button(text="MAIN MENU", size_hint=(0.3,0.12), pos_hint={"center_x":0.5,"center_y":0.4},
               on_release=lambda *_: setattr(App.get_running_app().sm, "current", "menu")).bind()

class HorrorApp(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        self.menu = MenuScreen(name="menu")
        self.game_screen = GameScreen(name="game")
        self.pause = PauseScreen(name="pause")
        self.win = WinScreen(name="win")
        self.lose = LoseScreen(name="lose")
        self.sm.add_widget(self.menu); self.sm.add_widget(self.game_screen)
        self.sm.add_widget(self.pause); self.sm.add_widget(self.win); self.sm.add_widget(self.lose)
        # keep references
        App.get_running_app = lambda : self
        return self.sm

if __name__ == "__main__":
    HorrorApp().run()

