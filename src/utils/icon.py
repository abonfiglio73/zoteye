# -------------------------------------
# Module to create multi-size icons from pngs
# -------------------------------------

from pathlib import Path
from PIL import Image

APP_NAME = "ZotEye"
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR.parent.parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

ICON_SIZES = [(24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def generate_icon(image_name: str, output_name: str):
    img_path = IMAGES_DIR / image_name
    if not img_path.exists():
        print(f"Error: file {img_path} does not exist.")
        return False

    img = Image.open(img_path)
    output_path = ASSETS_DIR.parent / output_name
    img.save(output_path, sizes=ICON_SIZES)
    print(f"Generated icon: {output_path}")
    return True


if __name__ == "__main__":
    generate_icon(f"{APP_NAME}.png", f"{APP_NAME}.ico")
    generate_icon(f"{APP_NAME}_gray.png", "uninstall.ico")
