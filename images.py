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
