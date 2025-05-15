import os
import json
import yaml
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox, Text, Scrollbar, VERTICAL, LEFT, RIGHT, Y, BOTH, END
from datetime import datetime
import time
import shutil
import sys
import webbrowser
from PIL import Image, ImageTk, ImageOps
from typing import Optional, Dict, Any, List, Tuple

# Constants for file paths and directories
CONFIG_PATH = "config.yaml"
BACKUP_DIR = "Save_Backup"
LOG_FILE = "missing_subcategories.log"
MAPPING_FILE = "ex33_mapping_full.yaml"  # Added constant for mapping file.
PICTOS_FILE = "pictos.txt"

def get_timestamp() -> str:
    """
    Generates a timestamp string in the formatMMDD-HHMMSS.

    Returns:
        str: The timestamp string.
    """
    return time.strftime("%Y%m%d-%H%M%S")


def patch_yaml_with_master() -> None:
    """
    Patches the 'ex33_mapping_full.yaml' file with data from 'pictos.txt'.

    This function reads data from 'ex33_mapping_full.yaml' and 'pictos.txt',
    and potentially merges or updates information in the YAML file based on
    the content of the text file.
    """
    try:
        with open(MAPPING_FILE, "r") as f:
            existing_yaml = yaml.safe_load(f)  # Load the existing YAML data
        with open(PICTOS_FILE, "r") as f:
            master_lines = f.readlines()  # Read lines from the text file

        # Example logic:  Update quantities based on pictos.txt
        for line in master_lines:
            parts = line.strip().split(" ", 1)  # Split into quantity and name
            if len(parts) == 2:
                try:
                    quantity = int(parts[0])
                    item_name = parts[1].strip()
                    for item in existing_yaml.get("items", []):
                        if item_name.lower() in item.get("name", "").lower():  # Partial match
                            #  Update a 'quantity' field if it exists, or add it.
                            item["quantity"] = quantity  # Add or update quantity
                            break #stop searching after finding one match
                except ValueError:
                    print(f"Skipping line: {line}. Invalid quantity.")

        # Save the modified YAML
        with open(MAPPING_FILE, "w") as f:
            yaml.dump(existing_yaml, f, allow_unicode=True)

    except FileNotFoundError as e:
        print(f"Error: {e}.  Required files not found for patching YAML.")
        #  Consider raising the exception or logging it.  For now, print.
    except yaml.YAMLError as e:
        print(f"Error: YAML error: {e}")
        #  Handle YAML parsing errors.



def load_config() -> Dict[str, Any]:
    """
    Loads configuration data from 'config.yaml'.  If the file does not exist,
    it returns a default configuration.

    Returns:
        Dict[str, Any]: The configuration data.
    """
    if not os.path.exists(CONFIG_PATH):
        #  Provide default values for all expected configuration options.
        return {
            "uesave_path": "",  #  Changed default to empty string
            "Allow_Updating": True,
            "Transparency": 0.7,
            "BackgroundColor": "#000001",
            "DarkMode": False, # Added default value for dark mode
        }
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: YAML error while loading config: {e}")
        #  Consider a more robust error handling strategy.
        return {  # Return default config on error to avoid crashing.
            "uesave_path": "",
            "Allow_Updating": True,
            "Transparency": 0.7,
            "BackgroundColor": "#000001",
            "DarkMode": False,
        }



def save_config(cfg: Dict[str, Any]) -> None:
    """
    Saves configuration data to 'config.yaml'.

    Args:
        cfg (Dict[str, Any]): The configuration data to save.
    """
    try:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(cfg, f)
    except yaml.YAMLError as e:
        print(f"Error: YAML error while saving config: {e}")
        #  Handle the error appropriately (e.g., show a message to the user).



class EX33SaveEditor(ctk.CTk):
    """
    Main class for the EX33 Save Editor application.
    """

    def __init__(self):
        super().__init__()
        self.title("EX33 Save Editor")
        self.geometry("1000x700")

        self.config = load_config()
        self.uesave_path = self.config.get("uesave_path", "")
        self.allow_updating = self.config.get("Allow_Updating", True)
        self.transparency = self.config.get("Transparency", 0.7)  # Load from config
        self.background_color = self.config.get("BackgroundColor", "#000001")  # Load from config
        self.dark_mode = self.config.get("DarkMode", False) # Load dark mode setting

        # Apply the theme
        self.set_theme(self.dark_mode)

        self._configure_uesave_path()  # Moved uesave path check to its own method

        self.mapping = self.load_mapping()
        self.items = self.mapping.get("items", [])

        self.validate_categories()

        self.input_vars = {}
        self.loaded_json = []
        self.original_data = {}
        self.save_file_path = None
        self.json_path = None

        self.categories = self.get_structured_categories()
        self.selected_main_category = ctk.StringVar()
        self.selected_sub_category = ctk.StringVar()
        self.search_var = ctk.StringVar()
        self.search_highlight = ctk.BooleanVar()

        self.build_ui()

    def set_theme(self, dark_mode: bool):
        """
        Sets the application theme (light or dark mode).

        Args:
            dark_mode (bool): True for dark mode, False for light mode.
        """
        self.dark_mode = dark_mode
        self.config["DarkMode"] = dark_mode #save the dark mode
        save_config(self.config)
        if self.dark_mode:
            ctk.set_appearance_mode("dark")
            self.json_bg_color = "black"
            self.json_fg_color = "white"
        else:
            ctk.set_appearance_mode("light")
            self.json_bg_color = "white"
            self.json_fg_color = "black"
        # Apply the theme to the JSON text widget.
        if hasattr(self, 'json_text'): #check if json_text is created.
            self.json_text.configure(bg=self.json_bg_color, fg=self.json_fg_color)

    def _configure_uesave_path(self) -> None:
        """
        Configures the path to the 'uesave' executable.  If not found,
        prompts the user to locate it.
        """
        if not self.uesave_path or not os.path.exists(self.uesave_path):
            messagebox.showwarning("Set uesave path", "Please locate your 'uesave' executable")
            path = filedialog.askopenfilename(
                title="Select uesave executable", filetypes=[("All Files", "*")]
            )
            if path:
                self.uesave_path = path
                self.config["uesave_path"] = path
                save_config(self.config)
        #Remove hardcoded path
        # # Force overwrite the path, comment out if not needed for production
        # self.uesave_path = "~/.cargo/bin/uesave"  #  Hardcoded path
        # self.config["uesave_path"] = self.uesave_path
        # save_config(self.config)

    def validate_categories(self) -> None:
        """
        Validates the categories in the item mapping.  If any items are missing
        subcategories, it logs them and optionally adds a default subcategory.
        """
        invalid_items = [item for item in self.items if "." not in item.get("category", "")]
        if invalid_items:
            with open(LOG_FILE, "w") as log:
                log.write("Missing subcategories detected:\n")
                for item in invalid_items:
                    log.write(f"- {item['name']} (category: {item.get('category')})\n")
            msg = "Some items are missing subcategories:\n" + "\n".join(
                f"- {item['name']} (category: {item.get('category')})" for item in invalid_items
            )
            should_fix = messagebox.askyesno(
                "Missing Subcategories Detected",
                msg + "\n\nWould you like to automatically add a default subcategory ('.Default') to them?\n\nThe application will restart after applying changes.",
            )
            if should_fix:
                for item in invalid_items:
                    item["category"] = item["category"] + ".Default"
                with open(MAPPING_FILE, "w") as f:
                    yaml.dump({"items": self.items}, f, allow_unicode=True)
                messagebox.showinfo("Updated", "Subcategories added. Restarting now...")
                self.destroy()
                python = sys.executable
                os.execl(python, python, *sys.argv)

    def load_mapping(self) -> Dict[str, Any]:
        """
        Loads the item mapping from 'ex33_mapping_full.yaml'.

        Returns:
            Dict[str, Any]: The item mapping data.
        """
        if self.allow_updating:
            patch_yaml_with_master()
        try:
            with open(MAPPING_FILE, "r") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error loading mapping: {e}")
            return {}  # Return empty dict on error to prevent crashing

    def get_structured_categories(self) -> Dict[str, List[str]]:
        """
        Structures the categories from the item mapping into a dictionary.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are main categories
            and values are lists of subcategories.
        """
        structured = {}
        for item in self.items:
            if "." in item["category"]:
                main, sub = item["category"].split(".", 1)
                structured.setdefault(main, set()).add(sub)
        return {k: sorted(v) for k, v in structured.items()}

    def build_ui(self) -> None:
        """
        Builds the user interface for the application.
        """
        # Toolbar
        toolbar = ctk.CTkFrame(self, height=40)
        toolbar.pack_propagate(False)
        toolbar.pack(pady=5, fill="x", padx=5)

        ctk.CTkButton(toolbar, text="Open Save File", command=self.load_sav).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Open JSON File", command=self.load_json).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Save JSON", command=self.save_json).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Export .sav", command=self.export_sav).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Open Log File", command=self.open_log_file).pack(side="left", padx=5)

        self.allow_update_check = ctk.CTkCheckBox(
            toolbar,
            text="Allow Updating",
            variable=ctk.BooleanVar(value=self.allow_updating),
            command=self.toggle_allow_updating,
        )
        self.allow_update_check.pack(side="left", padx=5)
        self.allow_update_check.bind(
            "<Enter>", lambda e: self.show_tooltip("Toggle auto-update of YAML mapping on startup")
        )
        self.allow_update_check.bind("<Leave>", lambda e: self.hide_tooltip())

        # Dark mode switch
        self.dark_mode_switch = ctk.CTkSwitch(
            toolbar,
            text="Dark Mode",
            variable=ctk.BooleanVar(value=self.dark_mode),
            command=self.toggle_dark_mode,
        )
        self.dark_mode_switch.pack(side="left", padx=5)

        # Transparency and color settings
        transparency_frame = ctk.CTkFrame(toolbar)
        transparency_frame.pack(side="left", padx=5)
        ctk.CTkLabel(transparency_frame, text="Transparency:").pack(side="left")
        self.transparency_var = ctk.DoubleVar(value=self.transparency)
        transparency_slider = ctk.CTkSlider(transparency_frame, from_=0, to=1, variable=self.transparency_var, command=self.set_transparency)
        transparency_slider.pack(side="left")

        # color_frame = ctk.CTkFrame(toolbar) #remove color frame
        # color_frame.pack(side="left", padx=5)
        # ctk.CTkLabel(color_frame, text="Background Color:").pack(side="left")
        # self.color_var = ctk.StringVar(value=self.background_color)
        # color_entry = ctk.CTkEntry(color_frame, textvariable=self.color_var, width=80)
        # color_entry.pack(side="left")
        # color_button = ctk.CTkButton(color_frame, text="Set Color", command=self.set_background_color)
        # color_button.pack(side="left")


        # Move Search Frame here, centered under toolbar
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(pady=5, anchor="center")
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left")
        ctk.CTkEntry(search_frame, textvariable=self.search_var, width=200).pack(side="left", padx=5)

        ctk.CTkCheckBox(search_frame, text="Highlight Matches", variable=self.search_highlight, command=self.refresh_inputs).pack(side="left")
        self.search_var.trace_add("write", lambda *_,: self.refresh_inputs())

        cat_frame = ctk.CTkFrame(self)
        cat_frame.pack(pady=5)
        ctk.CTkLabel(cat_frame, text="Category:").pack(side="left")
        ctk.CTkOptionMenu(cat_frame, variable=self.selected_main_category,
                          values=list(self.categories.keys()), command=self.update_subcategories).pack(side="left", padx=5)
        self.sub_category_menu = ctk.CTkOptionMenu(
            cat_frame, variable=self.selected_sub_category, values=[], command=self.refresh_inputs
        )
        self.sub_category_menu.pack(side="left", padx=5)

        # Background container
        background_container = ctk.CTkFrame(self)
        background_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Scroll frame that overlays the image
        self.scroll_frame = ctk.CTkScrollableFrame(master=background_container, width=480, height=500, fg_color="transparent") # Let background show through )
        self.scroll_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # Text widget for JSON display
        self.json_text = Text(background_container, wrap="none", bg=self.json_bg_color, fg=self.json_fg_color, height=30, width=60)
        self.json_text.pack(side=RIGHT, fill=BOTH, expand=True)

        # Scrollbar for the text widget
        json_scroll_y = Scrollbar(background_container, orient=VERTICAL, command=self.json_text.yview)
        json_scroll_y.pack(side=RIGHT, fill=Y)
        self.json_text.config(yscrollcommand=json_scroll_y.set)

        self.tooltip_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.tooltip_label.pack()

        self.refresh_inputs()

    def open_log_file(self):
        if os.path.exists(LOG_FILE):
            webbrowser.open(LOG_FILE)
        else:
            messagebox.showinfo("Log Not Found", "No log file exists yet.")

    def toggle_allow_updating(self):
        self.allow_updating = not self.allow_updating
        self.config["Allow_Updating"] = self.allow_updating
        save_config(self.config)

    def toggle_dark_mode(self):
        """
        Toggles between light and dark mode.
        """
        self.dark_mode = not self.dark_mode
        self.set_theme(self.dark_mode) #apply the theme
        self.refresh_inputs()  # Update input colors
        self.config["DarkMode"] = self.dark_mode
        save_config(self.config)

    def show_tooltip(self, text):
        self.tooltip_label.configure(text=text)

    def hide_tooltip(self):
        self.tooltip_label.configure(text="")

    def update_subcategories(self, main_cat):
        sub_cats = self.categories.get(main_cat, [])
        if sub_cats:
            self.selected_sub_category.set(sub_cats[0])
            self.sub_category_menu.configure(values=sub_cats)
        else:
            self.selected_sub_category.set("")
            self.sub_category_menu.configure(values=[])
        self.refresh_inputs()

    def refresh_inputs(self, *_):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.input_vars.clear()

        main = self.selected_main_category.get()
        sub = self.selected_sub_category.get()
        search_term = self.search_var.get().lower()

        if not main or not sub:
            return

        cat_key = f"{main}.{sub}"
        for item in self.items:
            if item["category"] != cat_key:
                continue
            if search_term and not (search_term in item["name"].lower() or search_term in item["save_key"].lower()):
                continue

            key = item["save_key"]
            val = self.get_value_from_json(key)
            var = ctk.StringVar(value=str(val))
            self.input_vars[key] = var
            label = ctk.CTkLabel(self.scroll_frame, text=item["name"], text_color="white")
            label.place(x=0, y=0, relwidth=1, relheight=1)
            if self.search_highlight.get() and search_term in item["name"].lower():
                label.configure(text_color="yellow")
            label.pack()

            entry = ctk.CTkEntry(
                self.scroll_frame,
                textvariable=self.input_vars[key],
                fg_color=self.json_bg_color,  # Use theme-aware colors
                text_color=self.json_fg_color,
            )
            entry.pack(fill="x", padx=10)


    def get_value_from_json(self, key_name):
        for entry in self.loaded_json:
            if entry.get("key", {}).get("Name") == key_name:
                return entry.get("value", {}).get("Int", "")
        return ""

    def set_value_in_json(self, key_name, new_value):
        for entry in self.loaded_json:
            if entry.get("key", {}).get("Name") == key_name:
                entry["value"]["Int"] = int(new_value)
                # Find the line number of the modified key
                line_number = self.find_json_key_line(key_name)
                if line_number:
                    self.json_text.see(f"{line_number}.0")  # Scroll to the line
                return
        self.loaded_json.append({"key": {"Name": key_name}, "value": {"Int": int(new_value)}})
        line_number = self.find_json_key_line(key_name)
        if line_number:
            self.json_text.see(f"{line_number}.0")

    def find_json_key_line(self, key_name):
        """
        Finds the line number of a given key in the JSON string in the text widget.
        """
        json_content = self.json_text.get("1.0", END)
        lines = json_content.splitlines()
        for i, line in enumerate(lines):
            if f'"Name": "{key_name}"' in line:
                return i + 1  # Line numbers start from 1
        return None  # Key not found

    def load_sav(self):
        sav_path = filedialog.askopenfilename(filetypes=[("Save Files", "*.sav")])
        if not sav_path:
            return

        self.current_sav_path = sav_path
        timestamp = get_timestamp()
        os.makedirs("Save_Backup", exist_ok=True)
        backup_sav = os.path.join("Save_Backup", f"{os.path.basename(sav_path).replace('.sav', f'_BACKUP-{timestamp}.sav')}")
        shutil.copy2(sav_path, backup_sav)

        json_path = sav_path.replace(".sav", ".json")
        self.current_json_path = json_path
        try:
            result = subprocess.run([self.uesave_path, "to-json", "-i", sav_path, "-o", json_path], capture_output=True, text=True)
        except FileNotFoundError:
            messagebox.showerror("Error", f"uesave not found at configured path: {self.uesave_path}.  Please check your config.yaml.")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        inv_map = data.get("root", {}).get("properties", {})
        maps = []
        for k, v in inv_map.items():
            if k.startswith("InventoryItems_") and isinstance(v, dict) and "Map" in v:
                maps.extend(v["Map"])

        self.full_json = data
        self.loaded_json = maps
        self.refresh_inputs()
        self.display_json() #show json

    def load_json(self):
        json_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not json_path:
            return
        self.current_json_path = json_path
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        inv_map = data.get("root", {}).get("properties", {})
        maps = []
        for k, v in inv_map.items():
            if k.startswith("InventoryItems_") and isinstance(v, dict) and "Map" in v:
                maps.extend(v["Map"])

        self.full_json = data
        self.loaded_json = maps
        self.refresh_inputs()
        self.display_json() #show json

    def save_json(self):
        if not self.current_json_path:
            messagebox.showerror("Error", "No loaded JSON to save.")
            return

        for key, var in self.input_vars.items():
            val = var.get().strip()
            if val:
                for entry in self.loaded_json:
                    if entry.get("key", {}).get("Name") == key:
                        entry["value"]["Int"] = int(val)
                        break
                else:
                    self.loaded_json.append({"key": {"Name": key}, "value": {"Int": int(val)}})

        for k, v in self.full_json.get("root", {}).get("properties", {}).items():
            if k.startswith("InventoryItems_") and isinstance(v, dict) and "Map" in v:
                v["Map"] = self.loaded_jsontimestamp = get_timestamp()
        os.makedirs(BACKUP_DIR, exist_ok=True)  # Ensure directory exists
        backup_json = os.path.join(BACKUP_DIR, f"{os.path.basename(self.current_json_path).replace('.json', f'_BACKUP-{timestamp}.json')}")
        try:
            shutil.copy2(self.current_json_path, backup_json)
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Failed to create backup: {e}")
            return

        with open(self.current_json_path, "w", encoding="utf-8") as f:
            json.dump(self.full_json, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("Saved", f"JSON saved and backup created at {backup_json}")

    def export_sav(self):
        if not self.current_json_path:
            messagebox.showerror("Error", "No JSON loaded to export.")
            return

        sav_path = self.current_json_path.replace(".json", ".sav")
        try:
            result = subprocess.run([self.uesave_path, "from-json", "-i", self.current_json_path, "-o", sav_path], capture_output=True, text=True)
            print("from-json stdout:", result.stdout)
            print("from-json stderr:", result.stderr)
            messagebox.showinfo("Done", "Save file exported successfully.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"uesave not found at configured path: {self.uesave_path}.  Please check your config.yaml.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export .sav: {e}")
            return

    def display_json(self):
        if self.full_json:
            self.json_text.delete("1.0", END)  # Clear previous text
            self.json_text.insert("1.0", json.dumps(self.full_json, indent=2, ensure_ascii=False))  # Insert new JSON
        else:
            self.json_text.delete("1.0", END)
            self.json_text.insert("1.0", "No JSON data loaded.")

    def set_transparency(self, value):
        self.transparency = value
        self.config["Transparency"] = value
        save_config(self.config)
        if sys.platform.startswith("win"):
            self.attributes("-transparentcolor", self.background_color)  # Keep the same transparent color
        elif sys.platform.startswith("darwin"):
             self.attributes("-transparent", True)
        else:
            try:
                self.attributes('-alpha', self.transparency)
            except Exception as e:
                print(f"Error setting transparency on Linux: {e}")

    # def set_background_color(self): #remove set_background_color
    #     color = self.color_var.get()
    #     try:
    #         self.configure(bg=color)
    #         self.background_color = color
    #         self.config["BackgroundColor"] = color
    #         save_config(self.config)
    #         if sys.platform.startswith("win"):
    #             self.attributes("-transparentcolor", color)  # Set transparent color on Windows
    #         self.configure(bg=color) #set the background color here too
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Invalid color: {color}.  Please use a valid color name or #RRGGBB format. Error: {e}")
    #         self.color_var.set(self.background_color)  # Reset to a valid color

if __name__ == "__main__":
    app = EX33SaveEditor()
    app.mainloop()
