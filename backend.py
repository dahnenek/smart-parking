import sys
import os
import cv2
import numpy as np
import torch
import importlib.util
import time
import requests
from ultralytics import YOLO
from PyQt6.QtCore import QThread, pyqtSignal

# =================================================================================
# SETUP PATH & HELPER LOADERS
# =================================================================================

ROOT_DIR = os.getcwd()
PLATE_DIR = os.path.join(ROOT_DIR, "Plate Numbers")
PARKING_DIR = os.path.join(ROOT_DIR, "Parking Lot")
SAMPLES_DIR = os.path.join(ROOT_DIR, "samples")


def load_module_from_path(module_name, file_path):
    if not os.path.exists(file_path):
        print(f"ERROR: File tidak ditemukan di {file_path}")
        return None
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Load Utils
plate_utils = load_module_from_path("plate_utils", os.path.join(PLATE_DIR, "util.py"))
curr = os.getcwd()
try:
    os.chdir(PARKING_DIR)
    parking_utils = load_module_from_path("parking_utils", os.path.join(PARKING_DIR, "util.py"))
finally:
    os.chdir(curr)

get_car = plate_utils.get_car
read_license_plate = plate_utils.read_license_plate
get_parking_spots_bboxes = parking_utils.get_parking_spots_bboxes
empty_or_not = parking_utils.empty_or_not

sys.path.append(PLATE_DIR)
from sort.sort import Sort


# =================================================================================
# THREAD: TELEGRAM WORKER
# =================================================================================
class TelegramWorker(QThread):
    def __init__(self, bot_token, chat_id, file_path):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.file_path = file_path

    def run(self):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            if not os.path.exists(self.file_path):
                print("[TELEGRAM] Error: PDF File not found.")
                return

            with open(self.file_path, 'rb') as f:
                files = {'document': f}
                caption = '🚀 **SYSTEM AUTO-REPORT (10 Sec Interval)**\nStatus: Active'
                data = {'chat_id': self.chat_id, 'caption': caption}
                requests.post(url, data=data, files=files)
                print("[TELEGRAM] Auto-Report sent successfully!")

        except Exception as e:
            print(f"[TELEGRAM] Connection Error: {e}")


# =================================================================================
# THREAD: PLATE DETECTION
# =================================================================================
class PlateDetectionThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    plate_data_signal = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self._is_paused = False

    def toggle_pause(self):
        self._is_paused = not self._is_paused

    def run(self):
        device = 0 if torch.cuda.is_available() else 'cpu'
        mot_tracker = Sort()
        coco_model = YOLO(os.path.join(ROOT_DIR, 'yolov8n.pt'))
        try:
            lp_path = os.path.join(PLATE_DIR, 'models', 'license_plate_detector.pt')
            license_plate_detector = YOLO(lp_path)
        except:
            return

        # -------------------------------------------------------------------------
        # [NOTE CCTV - PLATE CAMERA]
        # Untuk menggunakan CCTV Realtime, ganti baris di bawah ini dengan URL RTSP.
        # Contoh RTSP: "rtsp://username:password@192.168.1.10:554/stream"
        # Contoh Webcam USB: 0  (angka nol)
        # -------------------------------------------------------------------------
        video_source = os.path.join(PLATE_DIR, 'sample.mp4')
        # video_source = "rtsp://admin:12345@192.168.1.55:554/cam1"  <-- Ganti seperti ini untuk CCTV

        cap = cv2.VideoCapture(video_source)
        vehicles = [2, 3, 5, 7]

        while self._run_flag:
            while self._is_paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                # [NOTE CCTV] Jika menggunakan CCTV, hapus logika loop ini (cap.set)
                # karena CCTV adalah live stream yang tidak ada "akhirnya".
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            detections = coco_model(frame, device=device, verbose=False)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])

            track_ids = mot_tracker.update(np.asarray(detections_)) if detections_ else np.empty((0, 5))

            for track in track_ids:
                x1, y1, x2, y2, track_id = track
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {int(track_id)}", (int(x1), int(y1) - 10), 0, 0.6, (0, 255, 0), 2)

            license_plates = license_plate_detector(frame, device=device, verbose=False)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate
                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

                if car_id != -1:
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                    lp_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                    if lp_crop.size > 0:
                        gray = cv2.cvtColor(lp_crop, cv2.COLOR_BGR2GRAY)
                        _, thresh = cv2.threshold(gray, 64, 255, cv2.THRESH_BINARY_INV)
                        text, score = read_license_plate(thresh)
                        if text is not None:
                            self.plate_data_signal.emit(int(car_id), text)

            self.change_pixmap_signal.emit(frame)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()


# =================================================================================
# THREAD: PARKING LOT
# =================================================================================
class ParkingLotThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    stats_signal = pyqtSignal(int, int, list)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self._is_paused = False

    def toggle_pause(self):
        self._is_paused = not self._is_paused

    def run(self):
        mask_path = os.path.join(PARKING_DIR, 'mask_1920_1080.png')
        if not os.path.exists(mask_path): return

        # -------------------------------------------------------------------------
        # [NOTE CCTV - PARKING CAMERA]
        # Untuk menggunakan CCTV Realtime, ganti baris di bawah ini dengan URL RTSP.
        # PENTING: Pastikan sudut pandang CCTV SAMA PERSIS dengan Masker yang Anda buat.
        # Jika kamera bergerak (PTZ), sistem masker tidak akan bekerja akurat.
        # -------------------------------------------------------------------------
        video_source = os.path.join(SAMPLES_DIR, 'parking_1920_1080_loop.mp4')
        # video_source = "rtsp://admin:12345@192.168.1.56:554/cam2" <-- Ganti untuk CCTV

        mask = cv2.imread(mask_path, 0)
        cap = cv2.VideoCapture(video_source)
        components = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)

        curr = os.getcwd()
        os.chdir(PARKING_DIR)
        try:
            spots = get_parking_spots_bboxes(components)
        finally:
            os.chdir(curr)

        spots_status = [None for j in spots]
        diffs = [None for j in spots]
        previous_frame = None
        frame_nmr = 0
        step = 30

        def calc_diff(im1, im2):
            return np.abs(np.mean(im1) - np.mean(im2))

        while self._run_flag:
            while self._is_paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                # [NOTE CCTV] Hapus baris ini jika menggunakan live stream
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if frame_nmr % step == 0 and previous_frame is not None:
                for spot_indx, spot in enumerate(spots):
                    x1, y1, w, h = spot
                    if y1 + h > frame.shape[0] or x1 + w > frame.shape[1]: continue
                    spot_crop = frame[y1:y1 + h, x1:x1 + w, :]
                    diffs[spot_indx] = calc_diff(spot_crop, previous_frame[y1:y1 + h, x1:x1 + w, :])

            if frame_nmr % step == 0:
                if previous_frame is None:
                    arr_ = range(len(spots))
                else:
                    arr_ = [j for j in np.argsort(diffs) if diffs[j] / np.amax(diffs) > 0.4]

                curr = os.getcwd()
                os.chdir(PARKING_DIR)
                try:
                    for spot_indx in arr_:
                        spot = spots[spot_indx]
                        x1, y1, w, h = spot
                        spot_crop = frame[y1:y1 + h, x1:x1 + w, :]
                        spots_status[spot_indx] = empty_or_not(spot_crop)
                finally:
                    os.chdir(curr)

                empty_list = [f"P{i + 1}" for i, s in enumerate(spots_status) if s]
                self.stats_signal.emit(len(empty_list), len(spots_status), empty_list)

            if frame_nmr % step == 0:
                previous_frame = frame.copy()

            for spot_indx, spot in enumerate(spots):
                status = spots_status[spot_indx]
                x1, y1, w, h = spots[spot_indx]
                color = (0, 255, 0) if status else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 2)
                cv2.putText(frame, f"P{spot_indx + 1}", (x1 + 5, y1 + 20), 0, 0.5, (255, 255, 255), 1)

            frame_nmr += 1
            self.change_pixmap_signal.emit(frame)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()