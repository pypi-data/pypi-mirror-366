
# pyexecutable_gen

A lightweight, configurable **PyInstaller wrapper** for Python developers who want to package their scripts into standalone executables using Python code instead of CLI.
 
> Author: [its-me-abi](https://github.com/its-me-abi)  
> Date: May 14, 2025

---

## 📦 What is this?

`pyexecutable_gen.py` provides a `builder` class to programmatically invoke PyInstaller with custom configurations,  
by doing it we can turn a python script into a executable file   
supporting:

- One-file / one-dir builds
- Hidden imports
- Data folder mapping
- Custom icons and console toggling
- Clean builds and custom PyInstaller flags

---
## 🤝 Documentation
[ full documentation is available in wiki](https://github.com/its-me-abi/pyexecutable/wiki)  
## 🛠 Installation


```bash
pip install pyexecutable_gen
```
or download this project by git comand (or download by browser as zip and extract )
```
git clone https://github.com/its-me-abi/pyexecutable_gen.git
```

---

## 🚀 Quick Start

```python
from pyexecutable_gen import builder

b = builder("your_script.py")
b.set_console(False)
b.set_onedir(True)
b.set_icon("icon.ico")
b.set_loglevel("DEBUG")
b.set_data_folders("assets", "assets")
b.set_hidden_import("your_dynamic_module")
# b.set_extra_args("--heloo its_extra_argument")  # you can set more argumnts as string.only use when functionality not available by api
b.set_collect_all("a_big_package_with_submodules")
if b.build_executable():
    print("✅ Build succeeded!")
else:
    print("❌ Build failed.")

```

---

## 🔧 Features

- ✅ No CLI required
- 📂 Cross-platform data folder support
- 🪄 Hidden import handling
- 🖼 Set icon with `.ico` file
- 🧵 Toggle between GUI and console mode
- 🔍 Control build verbosity via log levels
- 🧹 Optional clean builds


---



## 🪪 License

MIT License – See `LICENSE.md` for details.
