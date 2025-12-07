# 🚗 Computer Vision Smart Plate & Parking Detection

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-green?style=for-the-badge)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-orange?style=for-the-badge&logo=qt&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> **A dual-stream computer vision system designed to monitor parking lot occupancy and detect vehicle license plates simultaneously.**

<img width="1594" height="1003" alt="Screenshot 2025-12-07 190213" src="https://github.com/user-attachments/assets/a55541ee-404c-4c79-a838-1bc514a382bc" />

---

## 📖 Overview

This project integrates state-of-the-art Computer Vision models (**YOLOv8**) with a responsive desktop GUI (**PyQt6**) to create a seamless Parking Management System. It features a unique **"Neofetch-style" / Hacker Command Center** interface, automated PDF reporting, and real-time alerts via Telegram Bot.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.10+** (Recommended: 3.10 or 3.11)
* **Git** (for cloning the repository)
* **NVIDIA CUDA** (Optional, but recommended for GPU acceleration)
* **Telegram Bot** (To enable the auto-report feature, you must configure your Telegram Bot credentials in main.py)
* **Video Sample**: https://drive.google.com/drive/folders/1UG43fHYF7h3UN9WNLkR2-0F8osB2hVZe?usp=sharing

---

## 🚀 Configuration (Telegram Bot)

To enable the auto-report feature, you must configure your Telegram Bot credentials in main.py:
* **Open Telegram and search for @BotFather.**
* **Create a new bot with /newbot to get your API Token.**
* **Get your Chat ID (Send a message to your bot, then check** [ https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates ]
* **Open main.py and update the configuration section**

---

## 🎮 Dashboard Controls

* **Play/Stop Button** (Pauses or Resumes the video processing threads)
* **Print PDF Outcome** (Manually generates a PDF report saved locally in the project folder)
* **Auto-Report Countdown** (A visual timer indicating when the next report will be sent to Telegram)

---

## ✨ Key Features

### 1. 📹 Real-Time Monitoring
* **Dual-Stream Processing:** Leveraging multi-threading to handle License Plate Recognition (OCR) and Parking Lot Occupancy monitoring simultaneously without lag.
* **Vehicle Tracking:** Implements **SORT Algorithm** to track unique vehicles and prevent double counting.
* **Occupancy Detection:** Uses advanced computer vision techniques (Connected Components & Masking) to detect free/occupied parking spots accurately.

### 2. 🖥️ Interactive Dashboard (GUI)
* **MVC Architecture:** Built with **PyQt6** using a clean Model-View-Controller pattern for scalability.
* **Hacker Aesthetic:** "Neofetch-style" terminal displays logs, vehicle counts, and ASCII art visuals.
* **Responsive Design:** The interface automatically adjusts to fill the screen (Minimize/Maximize supported).

### 3. 🤖 Automation & IoT
* **Auto-Reporting:** Generates detailed PDF outcome reports automatically based on a countdown timer.
* **Telegram Integration:** Instantly sends the generated PDF report to your smartphone via a Telegram Bot every **10 seconds** (configurable).
* **Smart Controls:** Play/Pause functionality for video feeds and countdown timers.

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **CV / AI** | Ultralytics YOLOv8, OpenCV, SORT |
| **GUI** | PyQt6, QtAwesome |
| **Utilities** | Requests (API), NumPy, FilterPy |

---

## 📂 Project Structure

The project follows a clean **MVC** separation:

```text
Project-Folder/
│
├── main.py           # [Controller] Entry point, Threads, & Timer logic
├── backend.py        # [Model] YOLO detection, Tracking, & Telegram API
├── interface.py      # [View] GUI Design, Widgets, Stylesheets, & ASCII Art
│
├── samples/          # Video samples for testing
├── models/           # YOLO weights (.pt files)
├── Parking Lot/      # Mask images & parking utilities
├── Plate Numbers/    # License plate utilities
└── sort/             # SORT Tracking Algorithm
```

## ⚙️ Installation

### 1. Clone the Repositoryg
```
git clone https://github.com/dahnenek/smart-parking.git
cd smart-parking-cv
```

### 2. Set up Virtual Environment
```
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
* **⚠️ Important:** We strictly use numpy<2.0 to ensure compatibility with OpenCV and Ultralytics.
```
pip install ultralytics opencv-python PyQt6 qtawesome requests filterpy torch "numpy<2.0"
```

## 🚀 Configuration (Telegram Bot)
To enable the auto-report feature, you must configure your Telegram Bot credentials in ```main.py```:

### 1. Open Telegram and search for @BotFather

### 2. Create a new bot with /newbot to get your API Token 
``` /newbot ```

### 3. Get your Chat ID (Send a message to your bot, then check
```https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates```

### 4. Open [main.py] and update the configuration section:
```
# main.py (Inside MainWindow class)
self.BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE" 
self.CHAT_ID = "YOUR_CHAT_ID_HERE"             
self.REPORT_INTERVAL = 10  # Set auto-report interval in seconds
```
