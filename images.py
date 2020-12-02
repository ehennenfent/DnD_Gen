from PIL import Image
from glob import glob
from pathlib import Path
import progressbar

icons = {}
iconsize = 16

print("Importing icons")
ibar = progressbar.ProgressBar()
for imagefile in ibar(glob('icon/*.png')):
    image = Image.open(imagefile)
    image = image.resize((iconsize, iconsize))
    path = Path(imagefile)

    icons[path.name.replace('.png','')] = image

print("Imported", len(icons), "Icons")
