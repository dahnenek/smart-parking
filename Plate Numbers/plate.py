from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort
from util import get_car, read_license_plate
import torch

# Cek GPU
if torch.cuda.is_available():
    device = 0
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = 'cpu'
    print("GPU not found, using CPU.")

mot_tracker = Sort()

# Load models
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('./models/license_plate_detector.pt')

cap = cv2.VideoCapture('./sample.mp4')

vehicles = [2, 3, 5, 7]

# --- TAMBAHAN: Memori untuk menyimpan plat yang sudah dibaca ---
# Format: {car_id: "Nopol_Teks"}
known_plates = {}

ret = True
while ret:
    ret, frame = cap.read()
    if ret:
        # 1. Deteksi Kendaraan
        detections = coco_model(frame, device=device, verbose=False)[0]
        detections_ = []

        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])

        # 2. Tracking
        if len(detections_) > 0:
            track_ids = mot_tracker.update(np.asarray(detections_))
        else:
            track_ids = np.empty((0, 5))

        # Visualisasi Mobil
        for track in track_ids:
            x1, y1, x2, y2, track_id = track
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Tampilkan ID dan Plat (jika sudah tahu) di layar video
            label = f"Car {int(track_id)}"
            if track_id in known_plates:
                label += f" | {known_plates[track_id]}"

            cv2.putText(frame, label, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 3. Deteksi Plat Nomor
        license_plates = license_plate_detector(frame, device=device, verbose=False)[0]

        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # Cari tahu plat ini milik mobil ID berapa
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

            if car_id != -1:
                # Gambar kotak plat nomor (tetap digambar agar terlihat terdeteksi)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

                # --- LOGIKA UTAMA: Cek apakah mobil ini sudah pernah dibaca platnya ---
                if car_id not in known_plates:
                    # Jika BELUM dikenal, lakukan proses crop & OCR
                    license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                    # Pastikan crop tidak kosong (kadang koordinat bisa error di tepi frame)
                    if license_plate_crop.size > 0:
                        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                        _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255,
                                                                     cv2.THRESH_BINARY_INV)

                        license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                        if license_plate_text is not None:
                            # 1. Simpan ke memori
                            known_plates[car_id] = license_plate_text
                            # 2. Print HANYA SEKALI ini saja
                            print(f"[BARU] Car {car_id} detected: {license_plate_text}")

                # (Opsional) Jika Anda ingin teks tetap muncul di layar video walau sudah diprint
                # Anda bisa mengambilnya dari variable known_plates (sudah dihandle di bagian visualisasi mobil di atas)

        # 4. Tampilkan Video
        cv2.namedWindow('License Plate Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('License Plate Detection', 1280, 720)
        cv2.imshow('License Plate Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()