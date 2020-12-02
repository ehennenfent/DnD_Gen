from PIL import Image
from glob import glob
from pathlib import Path
import progressbar

icons = {}
iconsize = 16

def convert_str_path(i):
    return str(Path(i).name).replace(".png", "")

print("Importing icons")
ibar = progressbar.ProgressBar()
for imagefile in ibar(glob('icon/*.png')):
    image = Image.open(imagefile)
    image = image.resize((iconsize, iconsize))
    icons[convert_str_path(imagefile)] = image

def update_icon_size(newsize):
    global icons
    if(newsize == 1):
        return icons
    icons = {}
    print("Re-scaling icons")
    ibar = progressbar.ProgressBar()
    for imagefile in ibar(glob('icon/*.png')):
        image = Image.open(imagefile)
        image = image.resize((iconsize * newsize, iconsize * newsize))
        icons[convert_str_path(imagefile)] = image
    return icons
