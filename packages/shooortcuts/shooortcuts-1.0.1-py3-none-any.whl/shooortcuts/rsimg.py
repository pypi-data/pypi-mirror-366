import argparse
import os
import shutil
from concurrent.futures import ProcessPoolExecutor

from PIL import Image


def resize(path, dst_path, long_side):
    if os.path.exists(dst_path):
        return

    ext = os.path.splitext(path)[1].lower()
    if ext in {".mp4", ".ts", ".mp3", ".mov", ".psd"}:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(path, dst_path)
        return

    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        print(f"skip file type[{ext}]: {path}")
        return

    im = Image.open(path)
    w, h = im.size

    if w < 500 or h < 500:
        print(f"skip file of resolution[{w}, {h}]: {path}")
        return

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if max(w, h) <= long_side:
        new_w = w
        new_h = h
        shutil.copy(path, dst_path)
    elif w > h:
        new_w = long_side
        new_h = int(h * new_w / w)
        try:
            im.resize((new_w, new_h)).save(dst_path)
        except OSError as err:
            if "cannot write mode RGBA as JPEG" in str(err):
                im.convert("RGB").save(dst_path)
        except Exception as err:
            print(err)
    else:
        new_h = long_side
        new_w = int(w * new_h / h)
        try:
            im.resize((new_w, new_h)).save(dst_path)
        except OSError as err:
            if "cannot write mode RGBA as JPEG" in str(err):
                im.convert("RGB").save(dst_path)
        except Exception as err:
            print(err)
    print(f"{path}[{w}, {h}] --> {dst_path}[{new_w}, {new_h}] {os.path.exists(dst_path)}")


def rsimg_command():
    parser = argparse.ArgumentParser(description="Resize images in a directory")
    parser.add_argument("dir", help="Directory containing images to resize")
    parser.add_argument("--long-side", type=int, default=1920, help="Target size for the longest side (default: 1920)")
    parser.add_argument("--no-concurrent", action="store_true", help="Disable concurrent processing")
    args = parser.parse_args()

    rsimg_command_impl(args.dir, args.long_side, not args.no_concurrent)


def rsimg_command_impl(dir, long_side, concurrent: bool = True):
    dir = os.path.abspath(dir)
    resized_dir = f"{dir}_resized"
    os.makedirs(resized_dir, exist_ok=True)

    pool = ProcessPoolExecutor(16)
    for top, dirs, files in os.walk(dir):
        if "__MACOSX" in top:
            continue
        for file in files:
            path = os.path.join(top, file)
            dst_path = path.replace(dir, resized_dir)
            if not os.path.exists(dst_path):
                if concurrent:
                    pool.submit(resize, path, dst_path, long_side)
                else:
                    resize(path, dst_path, long_side)
    pool.shutdown(wait=True)
