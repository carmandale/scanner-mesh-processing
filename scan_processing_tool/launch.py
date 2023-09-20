from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


def center_window(size=(1280, 800)):
    Window.maximize()
    system_max_size = Window.system_size

    #Window.size = size

    #Window.left = (system_max_size[0] - size[0]) * 0.5
    #Window.top = (system_max_size[1] - size[1]) * 0.5


def on_project_dir_text(instance, value):
    print(f"Project Dir: {value}")


def update_pose_test_height(instance, value):
    factor = 0.5625
    instance.height = value * factor


class ScanProcessingTool(App):
    def build(self):
        layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))
        buttons_color = (0.3, 0.3, 0.3, 1)

        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ LEFT LAYOUT ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        box_left = BoxLayout(orientation="vertical", size_hint=(0.25, 1), padding=(20,20,10,20))

        # PROJECT DIRECTORY
        project_label = Label(text="Project Directory", bold=True, halign="left", valign="middle", size_hint=(1, None), size=(100, 60))
        project_label.bind(size=project_label.setter('text_size'))
        project_dir_textinput = TextInput(size=(100, 50), size_hint=(1, None), multiline=False)
        project_dir_textinput.bind(text=on_project_dir_text)

        # SCANS LABEL
        scans_label = Label(text="Scan IDs", bold=True, halign="left", valign="middle", size_hint=(1, None), size=(100, 70))
        scans_label.bind(size=scans_label.setter('text_size'))

        # SCAN BUTTONS SCROLL VIEW
        scan_buttons_box = GridLayout(cols=1, spacing=5, size_hint_y=None)
        scan_buttons_box.bind(minimum_height=scan_buttons_box.setter('height'))
        scans_scrollview = ScrollView()

        for i in range(100):
            button = Button(text=f"Button{i}", font_size=32, background_color=buttons_color, size_hint_y=None, height=50)
            # button.bind(size=button.setter('text_size'))
            scan_buttons_box.add_widget(button)

        scans_scrollview.add_widget(scan_buttons_box)

        # ADD LEFT BOX WIDGETS
        box_left.add_widget(project_label)
        box_left.add_widget(project_dir_textinput)
        box_left.add_widget(scans_label)
        box_left.add_widget(scans_scrollview)

        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MID LAYOUT ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        box_mid = BoxLayout(orientation="vertical", size_hint=(0.5, 1), padding=(10,20,10,20))

        # SELECTED SCAN LABEL
        selected_scan_label = Label(text="Selected Scan", bold=True, halign="left", valign="middle", size_hint=(1, None), size=(100, 60))
        selected_scan_label.bind(size=selected_scan_label.setter('text_size'))

        # SCAN DATA
        scan_data_grid = GridLayout(cols=3, spacing=10, size_hint_y=None, height= 50+50+20)

        scan_data_grid_label_usda = Button(text="usda", disabled=True, size_hint_y=None, height=50, disabled_color=(0,1,0,1))
        scan_data_grid_label_tex0 = Button(text="tex0", disabled=True, size_hint_y=None, height=50, disabled_color=(0,1,0,1))
        scan_data_grid_label_blend = Button(text="blend", disabled=True, size_hint_y=None, height=50, disabled_color=(0,1,0,1))
        scan_data_grid_label_keypoints = Button(text="keypoints", disabled=True, size_hint_y=None, height=50, disabled_color=(0,1,0,1))
        scan_data_grid_label_rig = Button(text="rig", disabled=True, size_hint_y=None, height=50, disabled_color=(0,1,0,1))
        scan_data_grid_label_pose_test = Button(text="pose_test", disabled=True, size_hint_y=None, height=50, disabled_color=(0,1,0,1))

        # ADD SCAN DATA WIDGETS
        scan_data_grid.add_widget(scan_data_grid_label_usda)
        scan_data_grid.add_widget(scan_data_grid_label_tex0)
        scan_data_grid.add_widget(scan_data_grid_label_blend)
        scan_data_grid.add_widget(scan_data_grid_label_keypoints)
        scan_data_grid.add_widget(scan_data_grid_label_rig)
        scan_data_grid.add_widget(scan_data_grid_label_pose_test)

        # POSE TEST IMAGE
        scan_data_pose_test = Image(source="C:\\PROYECTOS\\GrooveJones_Scans\\FCDallas\\22091986\\photogrammetry\\22091986-pose_test.png", size_hint_y=None)
        scan_data_pose_test.bind(width=update_pose_test_height)

        # MID IMAGES BOX
        images_box = BoxLayout(orientation="horizontal", padding=(10,10,10,10))

        # FRONT IMAGE
        scan_data_front_image = Image(source="C:\\PROYECTOS\\GrooveJones_Scans\\FCDallas\\22091986\\photogrammetry\\22091986.png")
        
        # USDA IMAGE
        scan_data_usda_image = Image(source="C:\\PROYECTOS\\GrooveJones_Scans\\FCDallas\\22091986\\photogrammetry\\baked_mesh_tex0.png")
        
        # ADD IMAGES TO MID IMAGES BOX
        images_box.add_widget(scan_data_usda_image)
        images_box.add_widget(scan_data_front_image)

        # ADD WIDGETS TO MID BOX
        box_mid.add_widget(selected_scan_label)
        box_mid.add_widget(scan_data_grid)
        box_mid.add_widget(scan_data_pose_test)
        box_mid.add_widget(images_box)

        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ RIGHT LAYOUT ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        box_right = BoxLayout(orientation="vertical", size_hint=(0.25, 1), padding=(10,20,20,20))

        # ACTIONS LABEL
        actions_label = Label(text="Actions", bold=True, halign="left", valign="middle", size_hint=(1, None), size=(100, 60))
        actions_label.bind(size=actions_label.setter('text_size'))

        # ACTION BUTTONS
        action_buttons_box = GridLayout(cols=1, spacing=10, size_hint_y=0.16)

        action_button0 = Button(text="CleanUp V4", font_size=32, background_color=buttons_color)
        action_button1 = Button(text="CleanUp V4 - Bounding Box", font_size=32, background_color=buttons_color)
        action_button2 = Button(text="Rig Scan", font_size=32, background_color=buttons_color)

        # ADD BUTTONS TO ACTION BUTTONS BOX
        action_buttons_box.add_widget(action_button0)
        action_buttons_box.add_widget(action_button1)
        action_buttons_box.add_widget(action_button2)

        # RIGHT BLANK SPACE
        action_blank_box = BoxLayout(orientation="vertical", padding=(0,10,0,0))
        blank_label = Label(text="")
        action_blank_box.add_widget(blank_label)

        # ADD WIDGETS TO RIGHT BOX
        box_right.add_widget(actions_label)
        box_right.add_widget(action_buttons_box)
        box_right.add_widget(action_blank_box)

        # ADD MAIN WIDGETS
        center_window(size=(1280, 800))
        layout.add_widget(box_left)
        layout.add_widget(box_mid)
        layout.add_widget(box_right)

        return layout

if __name__ == "__main__":
    ScanProcessingTool().run()