import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager
from PIL import Image


class ScanItem(BoxLayout):
    app = ObjectProperty(None)
    text = StringProperty()
    scan_folder = StringProperty()
    image_path = StringProperty()
    scan_id = StringProperty()



SCAN_FOLDER = "/Volumes/scanDrive3/takes"

Builder.load_string('''
<ScanItem>:
    size_hint_y: None
    height: dp(450)  # Update the height to accommodate the larger image
    spacing: dp(8)
    orientation: 'vertical'
    Image:
        id: scan_image
        source: root.image_path if root.image_path != '' else 'default_image.png'
        size_hint_y: 1.8
        allow_stretch: True
        keep_ratio: True
    Button:
        text: root.text
        on_release: root.app.launch_run_shots_gui(root.scan_folder)
        background_color: 0, 0, 0, 0
        size_hint_y: 0.9
    Label:
        text: root.scan_id
        size_hint_y: 0.2  # Increase the height to avoid overlapping
        text_size: self.size  # Limit the text width to the size of the Label
        halign: 'center'  # Align text horizontally to the center
        valign: 'middle'  # Align text vertically to the middle
        shorten: True  # Shorten the text if it's too long to fit the width
        color: rgba('#000000')


<ScanScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(8)
        padding: dp(8)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(48)
            Button:
                text: 'Refresh'
                on_release: app.refresh_scan_list()
        ScrollView:
            effect_cls: 'ScrollEffect'
            scroll_type: ['bars', 'content']
            bar_width: '10dp'
            scroll_speed: 2
            GridLayout:
                id: scan_list
                app: root.app
                cols: 4
                spacing: dp(8)
                padding: dp(8)
                size_hint_y: None
                height: self.minimum_height
''')




width, height = 400, 400
color = (64, 64, 64)  # dark gray
image = Image.new(mode="RGB", size=(width, height), color=color)
image.save("default_image.png")



class ScanThumbnail(BoxLayout):
    scan_id = StringProperty()
    _image = ObjectProperty(None)
    _label = ObjectProperty(None)

class ScanList(BoxLayout):
    app = ObjectProperty(None)

class ScanScreen(Screen):
    app = ObjectProperty(None)

class ScannerMonitorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScanScreen(app=self, name='scan_screen'))
        return sm

    def on_start(self):
        self.refresh_scan_list()

    def get_scan_image_and_id(self, folder_path):
        folder = os.path.basename(folder_path)
        scan_id = folder
        image_path = os.path.join(folder_path, "photogrammetry", f"{scan_id}.png")

        if os.path.exists(image_path):
            return image_path, scan_id
        else:
            return "", f"{scan_id} (pending)"


    def refresh_scan_list(self):
        scan_screen = self.root.get_screen('scan_screen')
        scan_list = scan_screen.ids.scan_list
        scan_list.clear_widgets()

        folders = [os.path.join(SCAN_FOLDER, folder) for folder in os.listdir(SCAN_FOLDER)]
        # Filter out non-folders, hidden files/folders, and unwanted folders
        folders = [folder for folder in folders if os.path.isdir(folder) and not os.path.basename(folder).startswith('.') and os.path.basename(folder) not in ["allScansToday", "allScans"]]
        # Sort folders by creation time in descending order (newest first)
        folders.sort(key=lambda x: os.stat(x).st_ctime, reverse=True)

        for folder_path in folders:
            image_path, scan_id = self.get_scan_image_and_id(folder_path)
            scan_item = ScanItem(app=self, text=scan_id, scan_folder=folder_path, image_path=image_path, scan_id=scan_id)
            scan_list.add_widget(scan_item)


    def launch_run_shots_gui(self, scan_folder):
        import subprocess
        scan_id = os.path.basename(scan_folder)
        subprocess.Popen(["python", "/Volumes/scanDrive3/software/scannermeshprocessing-2023/runShotsGUI.py", "--scan_id", scan_id, "--base_path", SCAN_FOLDER])


if __name__ == '__main__':
    ScannerMonitorApp().run()

