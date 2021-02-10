import tkinter as tk

canvas = tk.Canvas()
canvas.pack()

def create_circle(s, r):
    x, y = s
    canvas.create_oval(x - r, y - r, x + r, y + r)

s = (150, 150)
d = 2

for i in range(1, 50):
    create_circle(s, 10 + i*d)

canvas.mainloop()