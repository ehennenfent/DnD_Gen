from PIL import Image
from glob import glob
import progressbar

icons = {}
iconsize = 16

print("Importing icons")
ibar = progressbar.ProgressBar()
for imagefile in ibar(glob('icon/*.png')):
    image = Image.open(imagefile)
    image = image.resize((iconsize, iconsize))
    icons[imagefile.replace('.png','').replace('icon/', '')] = image

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
        icons[imagefile.replace('.png','').replace('icon/', '')] = image
    return icons
