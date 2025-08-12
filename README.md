# 🧠 **QuizBuzz! – First Player Reaction System for Game Shows**

Turn your PC into a fast-response buzzer station using original Buzz! hardware 🎮 — perfect for creating interactive quiz competitions like *Jeopardy!* or *Rischiatutto*!

---

## 🚀 Overview

**QuizBuzz!** is a Python app designed to instantly detect which player buzzes first using USB Buzz! controllers. It highlights the winner visually and plays their custom sound. This makes it ideal for educational games, quiz shows, team contests, or just fun family nights.

---

## ✨ Key Features

- 🎨 Full-screen visual interface with colorful player displays  
- 🔊 Custom sound playback (WAV or automatic beeps)  
- ⌨️ Easy keyboard control for round start, fullscreen toggle, and exit  
- 🧍 Name customization for each player from the GUI  
- 🔒 "Lockout" system that disables further inputs after the first buzz  
- ⚙️ Uses `hidapi` to read Buzz! controller data  
- ✅ Plug-and-play for Windows systems  

---

## 🖥 Requirements

- Python ≥ 3.7  
- Operating system: Windows 10 or 11  
- Python packages:
  ```bash
  pip install hidapi
  ```

---

## 🎬 How It Works

1. Plug in a Buzz! USB controller  
2. Run the Python script  
3. Press `SPACE` or `ENTER` to start a round  
4. The first player to press their buzzer is shown as the winner  
5. Press `SPACE` again to reset and start a new round  

---

## 🧩 Controls

| Key        | Action                    |
|------------|----------------------------|
| `SPACE`    | Start a new round          |
| `ENTER`    | Also starts a new round    |
| `F11`      | Toggle fullscreen mode     |
| `ESC`      | Quit the program           |

---

## 🎛 Player Settings

You can customize:

```python
PLAYER_NAMES = ["Red", "Blue", "Green", "Yellow"]
PLAYER_COLORS = ["#ff3b30", "#007aff", "#34c759", "#ffcc00"]
PLAYER_SOUNDS = ["buzzer_red.wav", "buzzer_blue.wav", ...]
```

The “🎛 Set Names” button in the GUI lets you change names directly in the app. You can also replace the `.wav` sound files with your own for personalized victory sounds.

---

## 🔍 Debugging & Expansion

Set `DEBUG_PRINT = True` to log incoming HID data. This is useful for extending the app to detect **all** button presses on the Buzz! controller (e.g., colored answer buttons) if you'd like to build a full Jeopardy! board interface.

---

## 💡 Suggested Use Cases

- Classroom quizzes with instant feedback  
- Game nights with friends or family  
- Competitive team events or fairs  
- Gamified training sessions  
- Community trivia contests  

---
---

## 🧩 Making Buzz! Controllers Recognizable on Windows

Some Buzz! USB controllers may not be immediately recognized by Windows as input devices. If your controller shows up as an **unknown device** or a **USB hub**, follow these steps to manually assign the correct driver:

### 🛠 Steps to Fix Recognition

1. Open **Device Manager** (`Win + X` → Device Manager)
2. Locate the Buzz! controller (usually listed as an unknown device with a ⚠️ yellow warning icon)
3. Right-click the device → **Properties**
4. Go to the **Driver** tab → click **Update Driver**
5. Choose **Browse my computer for driver software**
6. Select **Let me pick from a list of available drivers on my computer**
7. Choose **USB Input Device (HID)** and click **Next**

After this, your Buzz! controller should appear under **Bluetooth & other devices** as something like:

- `Logitech Buzz (tm) Controller V1`
- `BUZZ`
- or similar

Once recognized as a HID device, it will work seamlessly with QuizBuzz! and other compatible apps.

---
