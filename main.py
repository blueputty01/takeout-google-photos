import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import pywintypes
import win32file
import win32con
from tkinter import filedialog
from tkinter import *

root = Tk()
root.withdraw()
# input_dir = filedialog.askdirectory()
# output_dir = filedialog.askdirectory()

input_dir = 'D:\\Desktop\\Takeout\\Takeout\\Google Photos'
output_dir = 'D:\\Desktop\\Photos'

# input_dir = input("Input directory: ")
# output_dir = input("Output directory: ")

input_dir = Path(input_dir)
output_dir = Path(output_dir)


def change_file_creation_time(fname, newtime):
    wintime = pywintypes.Time(newtime)
    winfile = win32file.CreateFile(
        fname, win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)

    win32file.SetFileTime(winfile, wintime, None, None)

    winfile.close()


dupe_exp = re.compile(r'\(\d+\)')

# create a map of names to their file names
meta_map = {}


def get_root(file):
    file_name = file.name
    dupe_count = dupe_exp.search(file_name)
    if dupe_count:
        dupe_count = dupe_count.group(0)
        file_name = file_name.replace(dupe_count, '') 
    else: 
        dupe_count = ''
    root_name = file_name.split('.')[0].split('-edit')[0]
    root_name = root_name + dupe_count
    return root_name


for meta_file in input_dir.glob('**/*.json'):
    meta_root = get_root(meta_file)
    meta_map[meta_root] = meta_file


for img in input_dir.glob('**/*'):
    if img.is_file() and not img.suffix == '.json':
        img_path = str(img)

        error_count = -1

        # base = img.name[:46]
        img_root = get_root(img)
        try: 
            meta_path = meta_map[img_root]
        except KeyError as e:
            print("No metadata found for " + img_path)
            move_dir = output_dir / 'unorganized'

            if not os.path.exists(move_dir):
                os.makedirs(move_dir)

            shutil.move(img_path, move_dir)

            continue

        with open(meta_path) as f:
            data = json.load(f)
            if 'photoTakenTime' in data:
                creation_time = int(data['photoTakenTime']['timestamp'])
                change_file_creation_time(img_path, creation_time)
                os.utime(img_path, (creation_time, creation_time))

            date = datetime.fromtimestamp(creation_time)
            print(img_root, date)
            month = date.month
            year = date.year

            month_dir = output_dir / str(year) / f'{year}-{month}'

            if not os.path.exists(month_dir):
                os.makedirs(month_dir)
            while(os.path.exists(month_dir / img.name)):
                error_count += 1
                new_name = img.name + f'({error_count})'
                new_path = month_dir / new_name
                print(img_path + " already exists in " + str(month_dir))
            
            shutil.move(img_path, new_path)
