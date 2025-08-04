# GTkinter 🧩  
> Simple. Clean. Pythonic GTK for humans.

[![PyPI version](https://img.shields.io/pypi/v/GTkinter?label=PyPI&color=blue)](https://pypi.org/project/GTkinter/)
[![License](https://img.shields.io/github/license/Code-Wizaard/GTkinter)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20GTK3-success)](https://www.gtk.org/)
[![Stars](https://img.shields.io/github/stars/Code-Wizaard/GTkinter?style=social)](https://github.com/Code-Wizaard/GTkinter)

---

## 🐍 What is GTkinter?

**GTkinter** is a Python library that wraps GTK in a beautiful, clean, and beginner-friendly interface — similar in spirit to Tkinter but powered by modern GTK.

It’s great for:
- 🧑‍💻 Beginners who hate GTK’s verbosity
- 🚀 Rapid prototyping
- 🧼 Keeping your GUI code clean and tidy
- 🧠 Learning GUI programming without headaches

---

## 🌟 Features

✅ Very simple API  
✅ Modern GTK3 under the hood  
✅ Automatic layout system (VBox / HBox)  
✅ Signal binding with Enums (type-safe!)  
✅ Easily extendable with your own widgets  
✅ PyPI installable (`pip install GTkinter`)  
✅ No XML, no Glade, no nonsense

---

## 📦 Installation

Make sure you have GTK3 and PyGObject installed on your **Linux system**:

### On Arch-based distros:
```bash
sudo pacman -S gtk3 gobject-introspection
```

### On Debian/Ubuntu:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0
```

### Then:
```bash
pip install GTkinter
```

---

## 🧪 Example

```python
from GTkinter import App, Window, Button, Label, VBox
from GTkinter.enums import Events

app = App()
win = Window("Hello GTkinter", 300, 200)

layout = VBox()
label = Label("Click the button")
btn = Button("Click me")

def on_click(button):
    label.set_text("You clicked me!")

btn.connect(Events.CLICKED, on_click)

layout.add(label)
layout.add(btn)
win.set_child(layout)

win.connect(Events.DESTROY, lambda w: exit(0))

app.run(win)

```


---

## 🧠 API Overview

| Component | Description                      |
|----------|----------------------------------|
| `App`    | Your main GTK application        |
| `Window` | A top-level window               |
| `Button` | A clickable button               |
| `Label`  | A text label                     |
| `VBox`   | Vertical layout container        |
| `HBox`   | Horizontal layout container      |
| `Events`  | Enum for signal types (clicked, etc.) |

---

## 💡 Why GTkinter?

GTK is great. But it’s also:
- Verbose
- Hard to teach
- Ugly without Glade

GTkinter changes that by:
- Wrapping complex APIs in minimal classes
- Making it feel like Tkinter (but better looking)
- Emphasizing readability and flow

---

## 🧑‍💻 Contributing

Pull requests are welcome!  
If you have a suggestion or want to extend the widget set, open an issue or PR.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) file.

---

## 📎 Related Projects

- [PyGObject](https://pygobject.readthedocs.io/) – Python bindings for GObject and GTK
- [GTK](https://www.gtk.org/) – The GTK GUI toolkit

---

## ❤️ Credits

Built with love by **@Code-Wizaard**  
Contributions & stars are appreciated 🌟


