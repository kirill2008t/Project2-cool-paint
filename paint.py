import tkinter as tk

def change_color(color):
    global current_color
    current_color = color

def main():
    root = tk.Tk()
    root.title("coolpaint")
    
    global current_color
    current_color = 'black'

    canvas = tk.Canvas(root, width=800, height=600, bg='white')
    canvas.pack(side="top")

    last_x, last_y = None, None

    def start_draw(event):
        nonlocal last_x, last_y
        last_x, last_y = event.x, event.y

    def draw(event):
        nonlocal last_x, last_y
        canvas.create_line(last_x, last_y, event.x, event.y, fill=current_color, width=2)
        last_x, last_y = event.x, event.y

    def start_eraser(event):
        nonlocal last_x, last_y
        last_x, last_y = event.x, event.y

    def eraser(event):
        nonlocal last_x, last_y
        canvas.create_line(last_x, last_y, event.x, event.y, fill='white', width=2)
        last_x, last_y = event.x, event.y

    canvas.bind('<ButtonPress-1>', start_draw)
    canvas.bind('<B1-Motion>', draw)
    canvas.bind('<ButtonPress-3>', start_eraser)
    canvas.bind('<B3-Motion>', eraser)

    button_frame = tk.Frame(root)
    button_frame.pack(side="bottom")

    colors = ['red', 'green', 'blue', 'yellow']
    for color in colors:
        btn = tk.Button(button_frame, text=color.capitalize(), command=lambda col=color: change_color(col))
        btn.pack(side="left")

    root.mainloop()

if __name__ == "__main__":
    main()