import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox

class ExampleApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        btn = QPushButton('Click me', self)
        btn.clicked.connect(self.show_message)
        vbox.addWidget(btn)

        self.setLayout(vbox)

        self.setWindowTitle('PyQt5 Example')
        self.show()

    def show_message(self):
        QMessageBox.information(self, 'Message', 'You clicked the button!')

def main():
    app = QApplication(sys.argv)
    ex = ExampleApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
