# WinAppDriver Python Demo – Automating Windows Desktop Menus

This minimal example shows how to automate a traditional Windows desktop application menu (e.g. `File → Page Setup…`) using **WinAppDriver** with the **Appium Python Client**.

---

## 1. Prerequisites

1. **Windows 10/11** (Pro or Enterprise recommended).
2. **WinAppDriver 1.2+** – download and start `WinAppDriver.exe` (listens on `http://127.0.0.1:4723`).
3. **Python 3.9+** with `pip` available.

## 2. Install dependencies

```powershell
cd PythonWinAppDriverDemo
pip install -r requirements.txt
```

## 3. Run the demo

```powershell
# Defaults: launches Notepad & clicks File → Page Setup…
python main.py

# Custom target & menu path (→ separated by "->")
python main.py "C:\\Path\\To\\YourApp.exe" "Help->About"
```

---

Feel free to adapt `menu_navigator.py` for more complex interactions – add waits, error handling, etc. 