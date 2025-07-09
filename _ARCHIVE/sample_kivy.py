import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

kivy.require("2.0.0")


class ExampleApp(App):
    def build(self):
        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        btn = Button(text="Click me", size_hint=(1, 0.2))
        btn.bind(on_press=self.show_message)
        main_layout.add_widget(btn)

        return main_layout

    def show_message(self, instance):
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup_layout.add_widget(Label(text="You clicked the button!"))

        close_btn = Button(text="Close", size_hint=(1, 0.2))
        popup_layout.add_widget(close_btn)

        popup = Popup(title="Message", content=popup_layout, size_hint=(0.5, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    ExampleApp().run()
