import cv2
import numpy as np
import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QDateTime
from PyQt6.QtGui import QImage, QPixmap, QFont

# =================================================================================
# ASSETS & STYLING
# =================================================================================

PARKING_ART = r"""
   ⢘⣾⣾⣿⣾⣽⣯⣼⣿⣿⣴⣽⣿⣽⣭⣿⣿⣿⣿⣿⣧
⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⣰⣯⣾⣿⣿⡼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿
⠀⠀⠛⠛⠋⠁⣠⡼⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁
⠀⠀⠀⠤⣶⣾⣿⣿⣿⣦⡈⠉⠉⠉⠙⠻⣿⣿⣿⣿⣿⠿⠁⠀
⠀⠀⠀⠀⠈⠟⠻⢛⣿⣿⣿⣷⣶⣦⣄⠀⠸⣿⣿⣿⠗⠀⠀⠀
⠀⠀⠀⠀⠀⣼⠀⠄⣿⡿⠋⣉⠈⠙⢿⣿⣦⣿⠏⡠⠂⠀⠀⠀
⠀⠀⠀⠀⢰⡌⠀⢠⠏⠇⢸⡇⠐⠀⡄⣿⣿⣃⠈⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⣻⣿⢫⢻⡆⡀⠁⠀⢈⣾⣿⠏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣿⣻⣷⣾⣿⣿⣷⢾⣽⢭⣍⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣼⣿⣿⣿⣿⡿⠈⣹⣾⣿⡞⠐⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠨⣟⣿⢟⣯⣶⣿⣆⣘⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡆⠀⠐⠶⠮⡹⣸⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

CAR_ART = r"""
   ⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
  ⠸⡇⠀⠿⡀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆ 
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠸⣼⡿ 
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀ 
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉ 
"""

STYLESHEET = """
QMainWindow { background-color: #000000; }
QWidget { font-family: 'Consolas', monospace; color: #00FF00; }

QFrame#SectionFrame { border: 1px solid #ffffff; background-color: #000000; }
QLabel#HeaderLabel {
    color: #ffffff; font-weight: bold; font-size: 12pt;
    padding: 5px; background-color: #000000; border-bottom: 1px solid #333;
}
QLabel#AsciiLabel { color: #00FF00; font-size: 10pt; font-weight: bold; }
QLabel#InfoLabel { color: #00FF00; font-size: 11pt; }
QTextEdit#Terminal { background-color: #000000; color: #00ff00; border: none; font-size: 10pt; }

/* Scrollbar Style */
QScrollBar:vertical { border: none; background: #111; width: 10px; }
QScrollBar::handle:vertical { background: #00FF00; min-height: 20px; }

/* Button Style */
QPushButton {
    background-color: #000000; color: #ffffff;
    border: 1px solid #ffffff; border-radius: 0px;
    padding: 10px 0px; font-size: 11pt; font-weight: bold;
}
QPushButton:hover { background-color: #333333; }
QPushButton:checked { background-color: #005500; }

/* Countdown Style */
QLabel#Countdown {
    color: #FFD700;
    font-weight: bold;
    font-size: 11pt;
    border: 1px solid #FFD700;
    padding: 10px;
}
"""


# =================================================================================
# WIDGET COMPONENTS
# =================================================================================

class VideoSection(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("SectionFrame")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(title)
        header.setObjectName("HeaderLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(30)

        self.video_label = QLabel("Waiting...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_label.setScaledContents(True)

        layout.addWidget(header)
        layout.addWidget(self.video_label)
        self.setLayout(layout)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        if cv_img is None or cv_img.size == 0: return

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        p = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()

        p = p.scaled(self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(p))


class PlateNeofetchWidget(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("SectionFrame")
        self.detected_ids = set()
        self.current_count = 0
        self.last_log = ""

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QLabel(title)
        header.setObjectName("HeaderLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(30)
        main_layout.addWidget(header)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)

        # ASCII
        self.ascii_label = QLabel(CAR_ART)
        self.ascii_label.setObjectName("AsciiLabel")
        self.ascii_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.ascii_label.setFont(QFont("Consolas", 10))

        # INFO
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        info_widget.setLayout(info_layout)

        self.lbl_count = QLabel("Vehicle Count: 0")
        self.lbl_count.setObjectName("InfoLabel")
        self.lbl_time = QLabel("Time: ...")
        self.lbl_time.setObjectName("InfoLabel")

        lbl_list = QLabel("Recognized Plates:")
        lbl_list.setObjectName("InfoLabel")
        lbl_list.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("Terminal")
        self.log_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        info_layout.addWidget(self.lbl_count)
        info_layout.addWidget(self.lbl_time)
        info_layout.addWidget(lbl_list)
        info_layout.addWidget(self.log_text, 1)

        content_layout.addWidget(self.ascii_label, 1)
        content_layout.addWidget(info_widget, 2)

        content_container = QWidget()
        content_container.setLayout(content_layout)
        main_layout.addWidget(content_container)
        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        self.lbl_time.setText(f"Time & Date: {QDateTime.currentDateTime().toString('HH:mm dd/MM/yyyy')}")

    @pyqtSlot(int, str)
    def update_plate_log(self, car_id, plate_text):
        is_new = False
        if car_id not in self.detected_ids:
            self.detected_ids.add(car_id)
            self.current_count = len(self.detected_ids)
            self.lbl_count.setText(f"Vehicle Count: {self.current_count}")
            is_new = True

        tag = " [NEW]" if is_new else ""
        log_entry = f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] Car {car_id} : {plate_text}{tag}"

        if log_entry != self.last_log:
            self.log_text.append(log_entry)
            self.last_log = log_entry
            self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())


class ParkingNeofetchWidget(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("SectionFrame")
        self.last_available = 0
        self.last_total = 0

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QLabel(title)
        header.setObjectName("HeaderLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(30)
        main_layout.addWidget(header)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)

        # ASCII
        self.ascii_label = QLabel(PARKING_ART)
        self.ascii_label.setObjectName("AsciiLabel")
        self.ascii_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.ascii_label.setFont(QFont("Consolas", 10))

        # INFO
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        info_widget.setLayout(info_layout)

        self.lbl_spots = QLabel("Available Spots: ...")
        self.lbl_spots.setObjectName("InfoLabel")
        self.lbl_percent = QLabel("Occupancy Rate : ...%")
        self.lbl_percent.setObjectName("InfoLabel")
        self.lbl_time = QLabel("Time: ...")
        self.lbl_time.setObjectName("InfoLabel")

        lbl_list = QLabel("Free Spots List:")
        lbl_list.setObjectName("InfoLabel")
        lbl_list.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")

        self.list_spots = QTextEdit()
        self.list_spots.setReadOnly(True)
        self.list_spots.setObjectName("Terminal")
        self.list_spots.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_spots.setFont(QFont("Consolas", 10))

        info_layout.addWidget(self.lbl_spots)
        info_layout.addWidget(self.lbl_percent)
        info_layout.addWidget(self.lbl_time)
        info_layout.addWidget(lbl_list)
        info_layout.addWidget(self.list_spots, 1)

        content_layout.addWidget(self.ascii_label, 1)
        content_layout.addWidget(info_widget, 2)

        content_container = QWidget()
        content_container.setLayout(content_layout)
        main_layout.addWidget(content_container)
        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        self.lbl_time.setText(f"Time & Date: {QDateTime.currentDateTime().toString('HH:mm dd/MM/yyyy')}")

    @pyqtSlot(int, int, list)
    def update_data(self, available, total, free_list):
        self.last_available = available
        self.last_total = total
        self.lbl_spots.setText(f"Available Spots: {available:03d}/{total}")
        if total > 0:
            self.lbl_percent.setText(f"Occupancy Rate : {((total - available) / total) * 100:.1f}%")

        if not free_list:
            self.list_spots.setText("FULL")
        else:
            col_count = 5
            formatted_lines = []
            for i in range(0, len(free_list), col_count):
                chunk = free_list[i:i + col_count]
                line = "".join([f"{spot:<8}" for spot in chunk])
                formatted_lines.append(line)
            self.list_spots.setText("\n".join(formatted_lines))


class FooterWidget(QFrame):
    def __init__(self, main_ref):
        super().__init__()
        self.main = main_ref
        self.setObjectName("SectionFrame")
        self.setFixedHeight(50)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        try:
            icon_pdf = qta.icon('fa5s.file-pdf', color='white')
            icon_play = qta.icon('fa5s.toggle-on', color='white')
        except:
            icon_pdf = icon_play = None

        self.btn_print = QPushButton("  Print PDF Outcome")
        if icon_pdf: self.btn_print.setIcon(icon_pdf)

        # COUNTDOWN LABEL (Pengganti Tombol Share)
        self.lbl_countdown = QLabel("AUTO-REPORT: --")
        self.lbl_countdown.setObjectName("Countdown")
        self.lbl_countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_play = QPushButton("  Play/Stop")
        if icon_play: self.btn_play.setIcon(icon_play)
        self.btn_play.setCheckable(True)

        # Size Policies
        self.btn_print.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_countdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.btn_play.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout.addWidget(self.btn_print, 1)
        layout.addWidget(self.lbl_countdown, 1)  # Tengah = Countdown
        layout.addWidget(self.btn_play, 1)
        self.setLayout(layout)

        self.btn_play.clicked.connect(self.main.toggle_playback)
        self.btn_print.clicked.connect(self.main.generate_pdf)