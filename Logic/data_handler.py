# data_handler.py
import json

def save_character_data(file_path, character_name, character_pic_filename, pages):
    """
    Save all character data (including pages, backgrounds, and picker buttons)
    into a JSON file.
    """
    data = {
        "character_name": character_name,
        "character_pic_filename": character_pic_filename,
        "pages": []
    }

    for page_data in pages:
        page_entry = {
            "page_name": page_data["page_name"],
            "background_image": page_data["background_image"],
            "bg_scale_factor": page_data["bg_scale_factor"],
            "bg_offset_gx": page_data["bg_offset_gx"],
            "bg_offset_gy": page_data["bg_offset_gy"],
            "cell_size": page_data.get("cell_size", 40),  # Save the current grid cell size (default to 40 if missing)
            "buttons": []
        }
        for btn in page_data["buttons"]:
            button_dict = {
                "label": btn["label"],
                "grid_pos": list(btn["grid_pos"]),
                "size_in_cells": list(btn["size_in_cells"]),
                "shape": btn["shape"],
                "color": btn["color"],
                "command_mode": btn["command_mode"],
                "command_string": btn["command_string"],
                "opacity": btn["opacity"],
                "direction": btn["direction"]
            }
            page_entry["buttons"].append(button_dict)
        data["pages"].append(page_entry)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_character_data(file_path):
    """
    Load the character data from a JSON file and return it as a Python dict.
    This can then be used to recreate tabs, pages, backgrounds, and picker buttons.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data
