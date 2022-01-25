import sys
import time

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
    QComboBox,
    QProgressBar,
    QVBoxLayout,
)
from tools import flash_motor

motors_per_part = {
    'bras droit': ['épaule droite 10', 'épaule droite 11', 'biceps droit 12',
                   'coude droit 13', 'avant-bras droit 14',
                   'poignet droit 15', 'poignet droit 16',
                   'pince droite 17'],
    'bras gauche': ['épaule gauche 20', 'épaule gauche 21', 'biceps gauche 22',
                    'coude gauche 23', 'avant-bras gauche 24',
                    'poignet gauche 25', 'poignet gauche 26',
                    'pince gauche 27'],
    'tête': ['antenne gauche 30', 'antenne droite 31'],
}


class ProgressThread(QThread):

    count_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.count = 0
        self.stopped = False

    def run(self):
        self.stopped = False
        self.count = 0

        while not self.stopped and self.count <= 100:
            self.count += 1
            self.count_changed.emit(self.count)
            time.sleep(0.045)

        self.count = 0

    def stop(self):
        self.stopped = True


class FlashThread(QThread):

    flash_result_signal = pyqtSignal(str)
    robot_part = 'none'
    motor_name = 'none'
    motor_type = 'none'

    def run(self):
        flash_result = flash_motor(self.robot_part, self.motor_name, self.motor_type)
        self.flash_result_signal.emit(flash_result)

    def get_motor_info(self, info):
        self.robot_part = info['robot_part']
        self.motor_name = info['motor_name']
        if self.robot_part == 'tête':
            self.motor_type = 'dxl320'
        else:
            self.motor_type = 'dxl'


class TabWidgetCreator(QWidget):

    module_name_signal = pyqtSignal(dict)

    def __init__(self, widget_name: str):
        super().__init__()
        self.widget_name = widget_name

        self.progress_thread = ProgressThread()
        self.flash_thread = FlashThread()

        self.modules_list = QComboBox()
        self.modules_list.addItems(motors_per_part[widget_name])

        flash_button = QPushButton('Configurer')
        flash_button.clicked.connect(self.flash)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(200, 80, 250, 20)

        self.flash_info_label = QLabel()
        self.flash_info_label.setScaledContents(True)
        self.flash_info_label.setAlignment(Qt.AlignmentFlag.AlignJustify)

        layout = QVBoxLayout()
        layout.addWidget(self.modules_list)
        layout.addWidget(flash_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.flash_info_label)

        self.setLayout(layout)

    def flash(self):
        if not self.flash_thread.isRunning():
            self.module_name_signal.connect(self.flash_thread.get_motor_info)
            self.module_name_signal.emit({
                'robot_part': self.widget_name,
                'motor_name': self.modules_list.currentText(),
                })

            self.progress_thread.count_changed.connect(self.set_progress)
            self.progress_thread.start()

            self.flash_thread.flash_result_signal.connect(self.check_flash)
            self.flash_thread.start()

            self.flash_info_label.setText("")

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def check_flash(self, msg):
        if msg != 'Motor configuré.':
            self.progress_thread.stop()
            self.progress_bar.setValue(0)
        self.flash_info_label.setText(msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(QSize(400, 200))
        self.setWindowTitle('Configuration moteur')

        tabs = QTabWidget()
        tabs.setMovable(True)

        for part in ['bras droit', 'bras gauche', 'tête']:
            tabs.addTab(TabWidgetCreator(part), part)

        self.setCentralWidget(tabs)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
