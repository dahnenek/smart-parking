import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Pastikan file util.py ada di folder yang sama
try:
    from util import get_parking_spots_bboxes, empty_or_not
except ImportError:
    print("[CRITICAL ERROR] File 'util.py' tidak ditemukan di folder yang sama dengan script ini!")
    input("Tekan Enter untuk keluar...")
    sys.exit(1)


def calc_diff(im1, im2):
    return np.abs(np.mean(im1) - np.mean(im2))


# --- BAGIAN SETUP PATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
mask_path = os.path.join(current_dir, 'mask_1920_1080.png')
video_path = os.path.join(project_root, 'samples', 'parking_1920_1080_loop.mp4')

print("=" * 40)
print(f"System Check:")
print(f"Target Mask   : {mask_path}")
print(f"Target Video  : {video_path}")
print("=" * 40)
# -------------------------

# 1. CEK MASK
if not os.path.exists(mask_path):
    print(f"\n[ERROR] File Mask TIDAK DITEMUKAN!")
    sys.exit(1)

mask = cv2.imread(mask_path, 0)
if mask is None:
    print("\n[ERROR] File Mask gagal dibaca.")
    sys.exit(1)

# 2. CEK VIDEO
if not os.path.exists(video_path):
    print(f"\n[ERROR] File Video TIDAK DITEMUKAN!")
    sys.exit(1)

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("\n[ERROR] Video gagal dibuka.")
    sys.exit(1)

connected_components = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
spots = get_parking_spots_bboxes(connected_components)

spots_status = [None for j in spots]
diffs = [None for j in spots]

previous_frame = None

frame_nmr = 0
step = 30

print("\nMemulai video... Label parkir (P1, P2...) telah ditambahkan.")

while True:
    ret, frame = cap.read()

    if not ret:
        frame_nmr = 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
        if not ret:
            break

    if frame_nmr % step == 0 and previous_frame is not None:
        for spot_indx, spot in enumerate(spots):
            x1, y1, w, h = spot
            if y1 + h > frame.shape[0] or x1 + w > frame.shape[1]:
                continue
            spot_crop = frame[y1:y1 + h, x1:x1 + w, :]
            diffs[spot_indx] = calc_diff(spot_crop, previous_frame[y1:y1 + h, x1:x1 + w, :])

    if frame_nmr % step == 0:
        if previous_frame is None:
            arr_ = range(len(spots))
        else:
            arr_ = [j for j in np.argsort(diffs) if diffs[j] / np.amax(diffs) > 0.4]
        for spot_indx in arr_:
            spot = spots[spot_indx]
            x1, y1, w, h = spot
            spot_crop = frame[y1:y1 + h, x1:x1 + w, :]
            spot_status = empty_or_not(spot_crop)
            spots_status[spot_indx] = spot_status

    if frame_nmr % step == 0:
        previous_frame = frame.copy()

    # --- LOOP MENGGAMBAR KOTAK & LABEL ---
    for spot_indx, spot in enumerate(spots):
        spot_status = spots_status[spot_indx]
        x1, y1, w, h = spots[spot_indx]

        # Tentukan warna (Hijau = Kosong, Merah = Terisi)
        if spot_status:
            color = (0, 255, 0)  # Hijau
        else:
            color = (0, 0, 255)  # Merah

        # 1. Gambar Kotak
        frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 2)

        # 2. Tambahkan Label (ID)
        # Kita buat label "P" diikuti nomor indeks (misal: P1, P2, dst)
        label = f"P{spot_indx + 1}"

        # Hitung posisi teks (sedikit masuk ke dalam kotak di pojok kiri atas)
        text_x = x1 + 5
        text_y = y1 + 20

        # Gambar latar belakang hitam kecil di belakang teks agar tulisan terbaca jelas
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (text_x - 2, text_y - text_h - 2), (text_x + text_w + 2, text_y + 2), color, -1)

        # Tulis teks (Warna Putih atau Hitam tergantung kontras, disini Putih di atas blok warna)
        # Jika kotak hijau/merah, tulisan putih atau hitam agar kontras
        text_color = (255, 255, 255) if spot_status == False else (0, 0, 0)

        cv2.putText(frame, label, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

    # Info jumlah spot tersedia
    cv2.rectangle(frame, (80, 20), (550, 80), (0, 0, 0), -1)
    cv2.putText(frame, 'Available spots: {} / {}'.format(str(sum(spots_status)), str(len(spots_status))), (100, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.imshow('frame', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    frame_nmr += 1

cap.release()
cv2.destroyAllWindows()