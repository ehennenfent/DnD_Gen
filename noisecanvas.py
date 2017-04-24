from noise import snoise2
from tkinter import *

canvas_width = 512
canvas_height = 512
freq = canvas_width / 2

master = Tk()

w = Canvas(master, width=canvas_width, height=canvas_height)
w.pack()

img = PhotoImage(width=canvas_width, height=canvas_height)
w.create_image((canvas_width/2, canvas_height/2), image=img, state="normal")

r, g, b = 255, 255, 255
for x in range(canvas_width):
    for y in range(canvas_height):
        scale = (snoise2(x / freq, y / freq) + 1) / 2
        img.put("#%02x%02x%02x" % (r*scale,g*scale,b*scale), (x,y))

mainloop()
