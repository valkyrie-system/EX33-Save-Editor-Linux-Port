# EX33 Save Editor

A powerful and evolving **save file editor for Clair Obscur: Expedition 33**, built in Python with a modern UI using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

---

### ⚠️ Alpha Notice

> **This is an early alpha release**  
> Features are still being implemented, and bugs are expected. Use at your own risk and always back up your saves.

---

## 🔧 What It Does

- 🔍 **Load and edit** decrypted `.json` save files.
- 💾 **Convert** `.sav` ↔ `.json` with the help of `uesave-rs`.
- 🧩 **Auto-maps** inventory, weapons, outfits, tints, haircuts, pictos, and more.
- 📁 **Creates backups** of `.sav` and `.json` files before saving.
- 📚 **Multi-level category filtering** (e.g., `Weapons > Lune`).
- ✅ **Search and highlight** by item name or save key.
- 📅 **Log generation** for items missing subcategories.
- 🧠 **Remembers your settings** with `config.yaml`.

---

## New Features

- Improved Search
- X11 and Wayland Compatible (KDE and Gnome)
- Fixed permission errors when running on linux during porting
- Streamlined Script
- removed need for only EXE files, added 'All File Types' selection for use with uesave-rs installed at ~/.cargo/bin/uesave

**Summary of Changes**

* **Configuration Enhancements**:
    * The `load_config` function now provides default values for `Transparency` (0.7) and `BackgroundColor` ("#000001") if these are not found in the configuration file.
    * The configuration file (`config.yaml`) is used to store and load transparency and background color settings.

* **UI Improvements**:
    * Added a transparency slider to the toolbar, allowing users to adjust the window's transparency. The slider's value is linked to the `transparency_var` (a `DoubleVar`). The `set_transparency` function is called when the slider value changes.
    * Added a background color input and button to the toolbar. The user can enter a color in "#RRGGBB" format in the entry field, and click the "Set Color" button to apply it. The entered color is stored in the `color_var` (a `StringVar`). The `set_background_color` function is called when the button is clicked.

* **Transparency Control**:
    * The `set_transparency` function is introduced to handle changes to the window's transparency. It updates the `transparency` attribute of the main window and also saves the new value to the configuration file. It uses `sys.platform` to apply the correct method for setting transparency on Windows, macOS, and Linux.
* **Background Color Control**:
    * The `set_background_color` function is introduced to handle changes to the window's background color. It updates the `background_color` attribute of the main window and also saves the new value to the configuration file. It uses `sys.platform` to apply the correct method for setting the background color on Windows, macOS, and Linux. An error message is shown if the user enters an invalid color format.

---

## 🧷 Requirements

- Python 3.10 or later
- [uesave-rs](https://github.com/trumank/uesave-rs/releases) binary (place or link to `uesave.exe`)
- Python libraries from `requirements.txt`

---

## 🛆 Installation

1. Download or clone this repository.
2. Download `uesave-r [uesave-rs releases](https://github.com/trumank/uesave-rs/releases).
3. Install Python dependencies (see below):

## Installing Python Requirements on Arch-based Systems

This guide will help you get the necessary Python stuff installed on your Arch-based system. Since these packages are in the AUR, we'll use an AUR helper.

Important: I'm assuming you've already got the AUR set up and an AUR helper like yay, paru, or trizen installed. If not, you'll need to head over to the Arch Wiki first to get that sorted out.
1. Install the Python Packages

To get started, open your terminal and use your AUR helper to install these Python packages:

yay -S python-customtkinter python-pyyaml python-pillow  # If you're using yay
# Or, if you're a paru user:
# paru -S python-customtkinter python-pyyaml python-pillow
# And for trizen folks:
# trizen -S python-customtkinter python-pyyaml python-pillow

These commands will install the required Python libraries:

    customtkinter

    PyYAML

    Pillow

2. Install uesave-rs

Next up, you'll need to install uesave. This is a Rust application, so you'll need to have Rust and Cargo installed. Installation from source is generally:

- `cargo install --git https://github.com/trumank/uesave-rs.git`

Just a heads up: Make sure Cargo's bin directory (~/.cargo/bin) is in your system's PATH.
3. Verify Installation

Finally, let's make sure everything's working. Run the Python script:

python ex33_save_editor.py

If you don't see any errors, you're good to go! This confirms that the Python packages are installed correctly and that you can run the editor.
## 📁 Files

- `ex33_save_editor.py` — Main application script.
- `ex33_mapping_full.yaml` — Save key mappings.
- `pictos.txt` — Optional master item list.
- `Save_Backup/` (Created automatically in this version if it does not exist)
- `config.yaml` — Auto-generated config storing preferences. (If using 'uesave.exe', should work also)
- `missing_subcategories.log` — Created if mappings are missing subcategories.

---

## ❌ Limitations

- Frame transparency and background blending is platform- and theme-dependent. - PARTIALLY FIXED
- Only supports inventory and related mappings for now.
- Requires decrypted `.json` files using `uesave-rs`.

## 🚨 Disclaimer

This tool is fan-made and not affiliated with the developers or publishers of *Clair Obscur: Expedition 33*.
No game content is included. I am also not the original creator, this is a fork. See: https://www.nexusmods.com/clairobscurexpedition33/mods/165?tab=description

---

## 💼 License

MIT License.

---

## 📆 Version

**Alpha v0.1**  
Future versions may include expanded item types, and full theme customization.
