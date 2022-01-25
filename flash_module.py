import sys
import time

from PyQt6.QtWidgets import (QMainWindow, QApplication, QComboBox, 
    QVBoxLayout, QWidget, QPushButton, QProgressBar, QLabel)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal

from tools import flash_module


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
            time.sleep(0.07)

        self.count = 0

    def stop(self):
        self.stopped = True


class FlashThread(QThread):

    flash_result_signal = pyqtSignal(int)
    module_name = 'none'

    french_name_to_binary_name = {
        'gate': 'gate',
        'carte moteurs bras': 'dxlv1',
        'carte moteurs tête': 'dxlv2',
        'pince gauche': 'left-gripper-force-sensor',
        'pince droite': 'right-gripper-force-sensor',
        'orbita': 'orbita',
    }

    def run(self):
        flash_result = flash_module(self.french_name_to_binary_name[self.module_name])
        self.flash_result_signal.emit(flash_result)

    def get_module_name(self, name):
        self.module_name = name


class MainWindow(QMainWindow):

    module_name_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setFixedSize(QSize(400, 200))
        self.setWindowTitle('Configuration carte électronique')

        self.progress_thread = ProgressThread()
        self.flash_thread = FlashThread()

        self.modules_list = QComboBox()
        self.modules_list.addItems(['gate', 'carte moteurs bras', 'carte moteurs tête', 'pince gauche', 'pince droite', 'orbita'])

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

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def flash(self):
        if not self.flash_thread.isRunning():
            self.module_name_signal.connect(self.flash_thread.get_module_name)
            self.module_name_signal.emit(self.modules_list.currentText())

            self.progress_thread.count_changed.connect(self.set_progress)
            self.progress_thread.start()

            self.flash_thread.flash_result_signal.connect(self.check_flash)
            self.flash_thread.start()

            self.flash_info_label.setText('')

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def check_flash(self, value):
        if value == -1:
            self.progress_thread.stop()
            self.progress_bar.setValue(0)
            self.flash_info_label.setText('Configuration échouée. \n Assurez vous que la carte est correctement branchée.')
        if value == 0:
            self.flash_info_label.setText('Configuration réussie. La carte peut être débranchée.')



app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()