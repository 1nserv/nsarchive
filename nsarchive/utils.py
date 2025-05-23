import io
import math
import os
from PIL import Image

def open_asset(path: str) -> bytes:
    curr_dir = os.path.dirname(os.path.abspath(os.path.join(__file__)))
    asset_path = os.path.join(curr_dir, 'assets', path)

    image = Image.open(asset_path)
    val = io.BytesIO()

    image.save(val, format = 'PNG')

    return val.getvalue()

def compress_image(data: bytes, _max: int = 1000 ** 2) -> bytes:
    img = Image.open(io.BytesIO(data))
    size = 2 * ( math.floor(math.sqrt(_max),) )

    img.resize(size)

    val = io.BytesIO()
    img.save(val)

    return val.getvalue()

def warn(prompt: str):
    print("\033[1;33mWarning:\033[0m", prompt)