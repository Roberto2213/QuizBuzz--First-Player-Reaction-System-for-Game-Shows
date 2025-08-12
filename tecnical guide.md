# ⚙️ Technical Guide – QuizBuzz Input Recognition & Architecture

This document provides an in-depth explanation of how the **QuizBuzz!** application detects and processes button presses from a Buzz! USB controller using Python and the `hidapi` library.

---

## 🔌 Buzz! Controller Setup – Getting Recognized on Windows

Before the app can process buzzer input, your Buzz! controller must be properly recognized by Windows as a Human Interface Device (HID).

If your device appears as “Unknown” or a generic “USB Hub,” follow this **driver assignment** process from [this helpful guide](https://steamcommunity.com/sharedfiles/filedetails/?l=bulgarian&id=1201404534):

### ✅ Manual Driver Assignment

1. Open **Device Manager**
2. Find the Buzz! controller (typically marked with ⚠️)
3. Right-click → **Properties** → **Driver** tab
4. Click **Update Driver**
5. Choose:  
   `→ Browse my computer for drivers`  
   `→ Let me pick from a list of available drivers on my computer`
6. Select **USB Input Device (HID)** and confirm

Your controller should now show up correctly and can be read by the app.

---

## 🧠 How the Program Detects Buzzes

Once the Buzz! controller is recognized, the app reads its input via the `hid` module in a **non-blocking polling loop**.

### 🧩 Step-by-Step Breakdown

#### 1. Device Detection

```python
def find_buzz_device():
    for d in hid.enumerate():
        prod = (d.get('product_string') or '').lower()
        manu = (d.get('manufacturer_string') or '').lower()
        if 'buzz' in prod or 'buzz' in manu:
            return d
```

✅ This scans all connected HID devices for the word "buzz" in product or manufacturer strings.

---

#### 2. Open the Device

```python
dev = hid.device()
dev.open(vendor_id, product_id, serial_number)
dev.set_nonblocking(True)
```

✅ The controller is opened and set to **non-blocking** so we can continually check for inputs without freezing the GUI.

---

#### 3. Polling Loop

Inside the `BuzzApp` class:

```python
def poll(self):
    for _ in range(MAX_READS_PER_TICK):
        data = self.dev.read(32)
        ...
        report = bytes(data)
```

✅ Every few milliseconds, the app reads a 32-byte HID input report from the controller. This data contains the status of each button.

---

#### 4. Decode Input

This is the core logic that identifies which button was pressed:

```python
def get_pressed_players(report: bytes) -> List[int]:
    mapping = [
        (2, 0x01, 0),  # Red
        (2, 0x20, 1),  # Blue
        (3, 0x80, 2),  # Green
        (3, 0x04, 3),  # Yellow
    ]
    return [idx for byte_idx, mask, idx in mapping if report[byte_idx] & mask]
```

✅ Each Buzz! controller has a unique byte pattern when a button is pressed. For example:

- Byte 2 with mask `0x01` means **Red player buzzed**
- Byte 3 with mask `0x80` means **Green player buzzed**

You can expand this mapping if you want to detect additional buttons (e.g., colored answer buttons).

---

#### 5. Lockout Logic

Once a valid button is detected:

```python
self.round.lockout(idx)  # Stop the round
self.declare_winner(idx)  # Show winner + play sound
```

✅ This prevents further input until a new round is started.

---

## 🔊 Sound Playback

Each player has a customizable victory sound:

```python
PLAYER_SOUNDS = ["buzzer_red.wav", "buzzer_blue.wav", ...]
winsound.PlaySound(path, winsound.SND_FILENAME)
```

✅ If the sound file is missing, a fallback `Beep()` sound is played.

---
