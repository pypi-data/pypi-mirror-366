# 🔐 burpDrop – Cross-Platform Burp Suite CA Certificate Installer for Android

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Gashaw%20Kidanu-orange)](#)

**burpDrop** is a professional-grade automation tool that simplifies installing [Burp Suite](https://portswigger.net/burp) CA certificates into **rooted Android devices or emulators**.
Built for **security professionals**, **pen testers**, and **mobile developers**, it automates certificate conversion, deployment, permission setting, and rebooting — all with robust logging and cross-platform support.

![burpDrop Workflow](https://via.placeholder.com/800x400?text=BurpDrop+Workflow+Diagram)

---

## ✨ Features

- ✅ One-command certificate installation
- 🔁 Converts Burp CA cert (DER → PEM → `.0`) with subject hash
- 📲 Pushes cert to `/system/etc/security/cacerts/` on Android device
- 🔒 Verifies ADB and OpenSSL availability
- 📦 Automatically cleans up temporary certificate files on exit
- 🧰 Interactive CLI with prompts and auto-validation
- 📜 Timestamped logging to `logs/` directory
- 🖥️ Cross-platform support: Windows, macOS, and Linux
- 🤖 **Magisk support**: Installs certificates to the systemless Magisk path.
- 🧪 **Dry-run mode**: Simulates the installation without making any changes.

---

## 📦 Requirements

- Python **3.7+**
- [ADB (Android Debug Bridge)](https://developer.android.com/studio/releases/platform-tools)
- [OpenSSL](https://www.openssl.org/) available in `PATH`
- Rooted Android device or emulator (e.g., [Genymotion](https://www.genymotion.com/))
- Burp Suite CA certificate exported as `.der` format

---

## 🚀 Installation

### Option 1: From PyPI (recommended)

```bash
pip install burpdrop
```

### Option 2: From source
```bash
git clone [https://github.com/Gashaw512/android-traffic-interception-guide](https://github.com/Gashaw512/android-traffic-interception-guide)
cd android-traffic-interception-guide/burpdrop
pip install .

```
> ✅ Tip: Use a Python virtual environment to avoid system conflicts.

## ⚙️ Quick Start

### 1. Export your Burp certificate

In **Burp Suite**:  
`Proxy → Proxy Settings/ Options → Import / Export CA Certificate`

- Choose **DER format**
- Save it as `burp.der`

---

### 2. Connect your Android device

- Enable **USB debugging** on your phone or emulator  
- Ensure `adb` is accessible from your terminal (i.e., added to your system `PATH`)

---
### 3. Install the certificate

Run:

```bash
burpdrop install

```

> You’ll be prompted to select the certificate file path

> The device will automatically reboot once the installation is successful
---
## 🧪 Example Usage

```bash

# Standard interactive install (prompt-based)
burpdrop install

# Install for Magisk systemless root
burpdrop install --magisk

# Simulate installation without making changes
burpdrop install --dry-run

# View recent logs
burpdrop logs

# Interactive configuration wizard (to set adb/openssl paths)
burpdrop config

# Set ADB and OpenSSL paths directly
burpdrop config --adb "/path/to/adb" --openssl "/path/to/openssl"

# Help
burpdrop help

```

---
## ⚠️ Troubleshooting

| Issue                          | Solution                                                                 |
|-------------------------------|--------------------------------------------------------------------------|
| ❌ `adb` not found             | Run `burpdrop config` to set the correct path                           |
| ❌ Certificate conversion fails| Make sure **OpenSSL** is installed and the cert is in **DER** format     |
| ❌ Device not detected         | Run `adb devices` to confirm connection; ensure **USB debugging** is enabled |
| ⚠️ `adb remount` fails        | Ensure your device/emulator is **rooted**. Use `adb root` if needed      |





| Issue | Solution | |-------------------------------|--------------------------------------------------------------------------| | ❌ adb not found | Run burpdrop config to set the correct path | | ❌ Certificate conversion fails| Make sure OpenSSL is installed and the cert is in DER format | | ❌ Device not detected | Run adb devices to confirm connection; ensure USB debugging is enabled | | ⚠️ adb remount fails | Ensure your device/emulator is rooted. Use adb root if needed | | ❌ ImportError on local run | Ensure you are running with pip install . or using the wrapper scripts (burpDrop.sh/.bat) |

> This will render as a neat table on GitHub. Let me know if you'd prefer a bullet list format or collapsible FAQs instead.
---
## 🔧 Configuration

o set up or override tool paths, use the config command:

```bash

burpdrop config

```
You can also manually edit the config.json file located inside the installed package (e.g., site-packages/burpdrop/scripts/config.json).

```json

{
  "adb_path": "/custom/path/to/adb",
  "openssl_path": "/custom/path/to/openssl"
}
```
---
## 📚 FAQ

### ❓ How do I export the certificate from Burp?

Go to:  
**Proxy → Options → Import/Export CA Certificate**  
- Choose **DER format**  
- Save the file (e.g., `burp.der`)

---

### ❓ My emulator isn’t rooted. What now?

`burpDrop` requires root access to push the certificate to `/system/`.  
Use one of the following:

- ✅ Genymotion (emulators are rooted by default)  
- ✅ Magisk-patched AVDs  
- ✅ Custom rooted emulator images

---

### ❓ `adb remount` fails?

This is usually due to **verity** being enabled on the system partition.  
Try running:

```bash
adb disable-verity
adb reboot
adb root
adb remount

```
---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!  
If you’d like to help improve **burpDrop**, follow these steps:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

📄 **CONTRIBUTING.md** – _coming soon_

For suggestions, feedback, or collaboration inquiries:  
📧 [kidanugashaw@gmail.com](mailto:kidanugashaw@gmail.com)

---

## 📝 License

Distributed under the **MIT License**.  
© 2025 [Gashaw Kidanu](https://github.com/yourusername).  
See the [LICENSE](LICENSE) file for full details.

---

## 👋 Final Notes

**burpDrop** is actively maintained and designed for extensibility.  
Whether you’re a red teamer, security engineer, or mobile developer —  
this tool streamlines the HTTPS interception process on Android.

> **Intercept with confidence. Secure with precision.**  
> — _burpDrop_

---



