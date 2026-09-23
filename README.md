<div align="center">
  <br>
  <h1>🛡️ AgeSmart Enterprise</h1>
  <p>
    <strong>Advanced Enterprise Account Verification & Fraud Prevention Suite</strong>
  </p>
  <br>
</div>

## 📌 Overview

**AgeSmart Enterprise** is a state-of-the-art desktop application built to streamline and secure the account verification process. Designed with a modern, dark-themed UI using `customtkinter`, the suite integrates seamlessly with the SmartWeb ecosystem to provide enterprise-grade device binding, fraud filtering, and intelligent workflow automation.

Leveraging advanced media processing and telemetry, AgeSmart empowers administrators and compliance teams to rapidly review, verify, and authenticate users while maintaining rigorous security standards.

## ✨ Core Capabilities

- 🔐 **Secure Authentication & Device Binding:** Cryptographically ties user sessions to specific hardware profiles to prevent credential sharing and unauthorized access.
- 🛑 **Intelligent Fraud Filter:** Proactively analyzes verification requests using heuristics and telemetry data to detect and flag suspicious activities.
- 🌊 **Smart Verification Workflow:** A streamlined, step-by-step verification pipeline equipped with real-time logging and media analysis (powered by OpenCV & FFmpeg).
- 🌐 **SmartWeb Integration:** Built-in two-way synchronization with the SmartWeb backend for real-time user validation, history tracking, and update enforcement.
- 🎨 **Modern Desktop UX:** A polished, fully responsive interface featuring an integrated console, media cards, and an intuitive stepper mechanism.

## 🛠️ Technology Stack

- **Framework:** Python 3.10+
- **UI Framework:** CustomTkinter (Modern GUI)
- **Media Processing:** OpenCV (Headless), Pillow, FFmpeg/FFprobe
- **Networking & API:** Requests, User-Agents
- **Distribution:** PyInstaller (Standalone Executables)

## 📁 Repository Structure

```text
AgeSmart Enterprise/
├── core/                # Core logic (Auth, Device Binding, Fraud Filter, Workflows)
├── services/            # Backend integration, History, Telemetry, and Logging
├── ui/                  # UI Components, Dialogs, Themes, and Custom Widgets
├── utilities/           # Helper scripts (Media handling, Metadata extraction, Exporting)
├── config.py            # Global configuration and environment settings
├── main.py              # Application entry point
├── build_production.py  # Build script for PyInstaller
└── pyproject.toml       # Project metadata and dependencies
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.10** or higher.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/taimurxai/agepy.git
   cd agepy
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   python main.py
   ```

## 📦 Building for Production

To create a standalone executable for deployment:

```bash
python build_production.py
```
*The compiled application will be generated in the `release/` directory.*

## 🔒 Security & Compliance

AgeSmart Enterprise is built with security-first principles. All telemetry is anonymized and securely transmitted. Access requires valid organizational credentials and is subject to device-level authorization gates.

---
*© 2026 AgeSmart Development Team. All rights reserved.*
