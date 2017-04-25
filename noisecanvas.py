from noise import snoise2
from tkinter import *

canvas_width = 1024
canvas_height = 1024
freq = canvas_width / 2

master = Tk()

w = Canvas(master, width=canvas_width, height=canvas_height)
w.pack()

img = PhotoImage(width=canvas_width, height=canvas_height)
w.create_image((canvas_width/2, canvas_height/2), image=img, state="normal")

print("Generating Height Map")
print("Generating Temperature Map")
print("Consolidating Colors")
print("Rendering")

r, g, b = 255, 255, 255
for x in range(canvas_width):
    for y in range(canvas_height):
        scale = (snoise2(x / freq, y / freq) + 1) / 2
        img.put("#%02x%02x%02x" % (int(r*scale),int(g*scale),int(b*scale)), (x,y))

mainloop()
