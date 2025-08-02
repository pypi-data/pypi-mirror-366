# 📡 p2pshare

`p2pshare` is a lightweight, Python-based CLI tool for seamless file transfers between your PC and phone using a local Flask server and QR codes. No cloud, no login — just fast, private, peer-to-peer sharing over your local Wi-Fi.

---

## ✨ Features

- 🔁 Two-way file transfer: phone → PC and PC → phone
- 🌐 Local server (Flask + Waitress) for platform-agnostic access
- 📱 QR code generation for easy phone access
- 🪵 Logs file uploads with size and timestamp
- 🔒 No external hosting or third-party storage — fully offline if on same network

---

## 🚀 Getting Started

### 1. Clone and Install

```bash
pip install p2pshare-cli
```

### 2. Usage
📤 Send Files (Send a file from your phone to your computer)
```
p2pshare --send
```

📥 Receive Files (Send a file from your computer to your phone)
```
p2pshare --receive path/to/file.txt
```

A QR code and webpage will appear. Open it on your phone and upload a file. It will be saved in the uploads/ directory.

###⚙️ Options
```
| Flag       | Description                                     |
|------------|-------------------------------------------------|
| `--send`   | Send a file from PC to phone                    |
| `--receive`| Receive a file from phone to PC                 |
| `--time`   | Auto shutdown server after N seconds idle       |

p2pshare --receive --time 60
```

This shuts the server down after 60 seconds of no uploads.

All dependencies are auto-installed via pip install .

🧠 Why This Project?

Ever emailed yourself a file just to move it between your devices? p2pshare eliminates that pain. This tool makes peer-to-peer file sharing effortless with nothing but Python and a QR code.

