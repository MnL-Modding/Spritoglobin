from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).parent
FILES_DIR = SCRIPT_DIR / 'files'

MISSING_TEXTURE = Image.open(FILES_DIR / "missing texture.png")
