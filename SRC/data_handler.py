# data_handler.py
import json


def save_character_data(file_path, character_name, pages):
    """Save character data to a JSON file."""
    data = {
        "character":character_name,
        "pages":[
            {
                "page":page_name,
                "buttons":[
                    {
                        "button":button.text(),
                        "grid_x":grid_x,
                        "grid_y":grid_y,
                        "width":width,
                        "height":height,
                    }
                    for button, (grid_x, grid_y, width, height) in page.buttons
                ],
            }
            for page_name, page in pages.items()
        ],
    }
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_character_data(file_path):
    """Load character data from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)
