import tkinter as tk

def create_circle(s, r):
    # s - tuple[x, y], r - polomer
    canvas.create_oval(s[0] - r, s[1] - r, s[0] + r, s[1] + r)
    canvas.create_text(s[0], s[1], text=f'r = {r}', font='Arial 9')

def snowman(mid, r1, r1):
    # vytvori snehulaka ze 2 kouli (menis na vetsi)
    if r1 < r2:
        # s_x = touch_x (menime vysku)
        # s_y = touch_y +- r (menime o pulku kruhu abychom se dostali ke stredu)
        create_circle((touch[0], touch[1] - r1), r1)
        create_circle((touch[0], touch[1] + r2), r2)
    else:
        create_circle((touch[0], touch[1] - r2), r2)
        create_circle((touch[0], touch[1] + r1), r1)
# driver code
canvas = tk.Canvas()
canvas.pack()
# vars
touch = [150, 150]
first = 30
second = 50
# main func
snowman(touch, first, second)

canvas.mainloop()