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
    'right arm': ['r_shoulder_pitch', 'r_shoulder_roll', 'r_arm_yaw',
                  'r_elbow_pitch', 'r_forearm_yaw',
                  'r_wrist_pitch', 'r_wrist_roll',
                  'r_gripper'],
    'left arm': ['l_shoulder_pitch', 'l_shoulder_roll', 'l_arm_yaw',
                 'l_elbow_pitch', 'l_forearm_yaw',
                 'l_wrist_pitch', 'l_wrist_roll',
                 'l_gripper'],
    'head': ['l_antenna', 'r_antenna'],
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
            time.sleep(0.044)

        self.count = 0

    def stop(self):
        self.stopped = True


class FlashThread(QThread):

    flash_result_signal = pyqtSignal(int)
    robot_part = 'none'
    motor_name = 'none'

    def run(self):
        flash_result = flash_motor(self.robot_part, self.motor_name)
        self.flash_result_signal.emit(flash_result)

    def get_motor_info(self, info):
        self.robot_part = info['robot_part']
        self.motor_name = info['motor_name']


class TabWidgetCreator(QWidget):

    module_name_signal = pyqtSignal(dict)

    def __init__(self, widget_name: str):
        super().__init__()
        self.widget_name = widget_name

        self.progress_thread = ProgressThread()
        self.flash_thread = FlashThread()

        self.modules_list = QComboBox()
        self.modules_list.addItems(motors_per_part[widget_name])

        flash_button = QPushButton('Flash')
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

    def check_flash(self, value):
        if value == -1:
            self.progress_thread.stop()
            self.progress_bar.setValue(0)
            self.flash_info_label.setText("Flash failed. Make sure the motor is connected.")
        if value == 0:
            self.flash_info_label.setText("Flash succeeded. The motor can be safely unplugged.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(QSize(400, 200))
        self.setWindowTitle('Motor Flashing')

        tabs = QTabWidget()
        tabs.setMovable(True)

        for part in ['right arm', 'left arm', 'head']:
            tabs.addTab(TabWidgetCreator(part), part)

        self.setCentralWidget(tabs)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
