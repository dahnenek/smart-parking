import sys
import os

# SET ENVIRONMENT VARIABLE FIRST
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import QDateTime, QTimer

# IMPORT DARI FILE LAIN
from backend import PlateDetectionThread, ParkingLotThread, TelegramWorker
from interface import STYLESHEET, VideoSection, PlateNeofetchWidget, ParkingNeofetchWidget, FooterWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Parking & Plate Recognition System")
        self.resize(1280, 800)

        # CONFIG TELEGRAM
        self.BOT_TOKEN = "8337767417:AAE__ZBepSFqb5Sx0RX8RLE3fd3oEaET3Iw"
        self.CHAT_ID = "999508285"
        self.REPORT_INTERVAL = 10  # Detik
        self.current_countdown = self.REPORT_INTERVAL

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)

        self.plate_video = VideoSection("Real-Time Plate Scanning")
        self.parking_video = VideoSection("Parking Lot")
        self.plate_terminal = PlateNeofetchWidget("Plate Terminal")
        self.parking_terminal = ParkingNeofetchWidget("Parking Terminal")

        grid_layout.addWidget(self.plate_video, 0, 0)
        grid_layout.addWidget(self.parking_video, 0, 1)
        grid_layout.addWidget(self.plate_terminal, 1, 0)
        grid_layout.addWidget(self.parking_terminal, 1, 1)

        grid_layout.setRowStretch(0, 60)
        grid_layout.setRowStretch(1, 40)

        self.footer = FooterWidget(self)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.footer)

        self.start_threads()

        # TIMER COUNTDOWN (Looping 1 Detik)
        self.report_timer = QTimer(self)
        self.report_timer.timeout.connect(self.update_countdown)
        self.report_timer.start(1000)

    def update_countdown(self):
        self.current_countdown -= 1
        self.footer.lbl_countdown.setText(f"AUTO-REPORT: {self.current_countdown:02d}s")

        if self.current_countdown <= 0:
            self.process_auto_telegram()
            self.current_countdown = self.REPORT_INTERVAL  # Reset

    def process_auto_telegram(self):
        print("[SYSTEM] Sending Auto-Report...")
        pdf_path = self.generate_pdf(silent=True)
        self.tele_worker = TelegramWorker(self.BOT_TOKEN, self.CHAT_ID, pdf_path)
        self.tele_worker.start()

    def start_threads(self):
        self.thread_plate = PlateDetectionThread()
        self.thread_plate.change_pixmap_signal.connect(self.plate_video.update_image)
        self.thread_plate.plate_data_signal.connect(self.plate_terminal.update_plate_log)
        self.thread_plate.start()

        self.thread_parking = ParkingLotThread()
        self.thread_parking.change_pixmap_signal.connect(self.parking_video.update_image)
        self.thread_parking.stats_signal.connect(self.parking_terminal.update_data)
        self.thread_parking.start()

    def toggle_playback(self):
        self.thread_plate.toggle_pause()
        self.thread_parking.toggle_pause()
        if self.footer.btn_play.isChecked():
            self.footer.btn_play.setText("  PAUSED (Resume)")
            self.footer.btn_play.setStyleSheet("background-color: #550000; color: white; border: 1px solid white;")
        else:
            self.footer.btn_play.setText("  Play/Stop")
            self.footer.btn_play.setStyleSheet("background-color: #000000; color: white; border: 1px solid white;")

    def generate_pdf(self, silent=False):
        filename = "Outcome_Report.pdf"
        timestamp = QDateTime.currentDateTime().toString("dd MMM yyyy HH:mm:ss")

        plate_log = self.plate_terminal.log_text.toPlainText().replace("\n", "<br>")
        spots_log = self.parking_terminal.list_spots.toPlainText().replace("\n", "<br>")
        count = self.plate_terminal.current_count
        avail = self.parking_terminal.last_available
        total = self.parking_terminal.last_total

        html = f"""
        <html><head><style>
            body {{ font-family: sans-serif; }} h1 {{ text-align: center; }}
            .box {{ border: 1px solid #000; padding: 10px; margin-bottom: 10px; }}
            .terminal {{ font-family: monospace; background: #eee; padding: 10px; font-size: 9pt; }}
        </style></head><body>
            <h1>System Report</h1>
            <p style="text-align:center">{timestamp}</p>
            <div class="box"><h3>Plate Recognition</h3>
                <p>Count: {count}</p><div class="terminal">{plate_log}</div>
            </div>
            <div class="box"><h3>Parking System</h3>
                <p>Available: {avail}/{total}</p><div class="terminal">{spots_log}</div>
            </div>
        </body></html>
        """
        document = QTextDocument()
        document.setHtml(html)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)
        document.print(printer)

        if not silent:
            QMessageBox.information(self, "Success", f"PDF Saved: {os.path.abspath(filename)}")
        return filename

    def closeEvent(self, event):
        self.thread_plate.stop()
        self.thread_parking.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())