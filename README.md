![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-green?style=for-the-badge)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-orange?style=for-the-badge&logo=qt&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> **A dual-stream computer vision system designed to monitor parking lot occupancy and detect vehicle license plates simultaneously.**

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
* **Video Sample** (To enable the auto-report feature, you must configure your Telegram Bot credentials in main.py)

---

## 🚀 Configuration (Telegram Bot)

To enable the auto-report feature, you must configure your Telegram Bot credentials in main.py:
* **Open Telegram and search for @BotFather.**
* **Create a new bot with /newbot to get your API Token.**
* **Get your Chat ID (Send a message to your bot, then check** (https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates)
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
