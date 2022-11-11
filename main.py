import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import pywintypes, win32file, win32con

input_dir = Path('D:\\Desktop\\photos - Copy\\Extract\\Takeout\\Google Photos')

output_dir = Path('D:\\Desktop\\output')


def changeFileCreationTime(fname, newtime):
    wintime = pywintypes.Time(newtime)
    winfile = win32file.CreateFile(
        fname, win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)

    win32file.SetFileTime(winfile, wintime, None, None)

    winfile.close()


dupe_exp = re.compile(r'\(\d+\)')

for img in input_dir.glob('**/*'):
    if img.is_file() and not img.suffix == '.json':
        if img.suffix == "":
            continue

        img_path = str(img)

        error_count = -1

        base = img.name[:46]
        base = base.replace('-edited', '')

        dupe_count = dupe_exp.search(base)
        if dupe_count:
            dupe_count = dupe_count.group(0)
            base = base.replace(dupe_count, '')
            base += dupe_count

        meta_name = base + '.json'

        if not os.path.exists(img.parent / meta_name):
            meta_name = base.replace('.MP4', '.jpg') + '.json'

        meta_path = str(img.parent / meta_name)

        with open(meta_path) as f:
            data = json.load(f)
            if 'photoTakenTime' in data:
                creation_time = int(data['photoTakenTime']['timestamp'])
                changeFileCreationTime(img_path, creation_time)
                os.utime(img_path, (creation_time, creation_time))
                print(meta_name, creation_time)

            date = datetime.fromtimestamp(creation_time)
            month = date.month
            year = date.year

            month_dir = output_dir / str(year) / f'{year}-{month}'

            if not os.path.exists(month_dir):
                os.makedirs(month_dir)

            shutil.move(img_path, month_dir)
