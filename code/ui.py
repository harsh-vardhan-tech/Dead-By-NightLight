# ui.py
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fl = FloatLayout()
        self.add_widget(fl)
        title = Label(text="[b][size=40]HORROR NIGHT[/size][/b]", markup=True, pos_hint={"center_x":0.5,"center_y":0.7})
        fl.add_widget(title)
        play = Button(text="PLAY", size_hint=(0.32,0.12), pos_hint={"center_x":0.5,"center_y":0.5})
        quitb = Button(text="QUIT", size_hint=(0.32,0.12), pos_hint={"center_x":0.5,"center_y":0.35})
        fl.add_widget(play); fl.add_widget(quitb)
        play.bind(on_release=self.on_play)
        quitb.bind(on_release=lambda *_: App.get_running_app().stop())

    def on_play(self, *a):
        App.get_running_app().sm.current = "game"
        App.get_running_app().game_screen.start_game()

# Pause / Win / Lose screens are created in main.py to keep references simple.
# Keep ui.py small — main handles overlays (pause/resume/win/lose).

