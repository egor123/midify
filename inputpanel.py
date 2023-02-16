import tkinter as tk
import threading


def open_input(input, callback):
    def draw_window(input, callback=None):
        root = tk.Tk()
        root.overrideredirect(True)
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.bind('<Escape>', lambda _: root.destroy())

        window = tk.Canvas(root, bg='#2e2e2e', highlightthickness=0)
        window.pack(expand=1, fill=tk.BOTH)
        window.after(1, lambda: window.focus_force())

        def on_return(e):
            val = entry.get()
            root.destroy()
            callback(val)

        entry = tk.Entry(window, bg="#2e2e2e", font=(
            'Cascadia 16'), fg="white", border=0)
        entry.insert(0, input)
        entry.bind("<Return>", on_return)
        entry.focus()
        entry.pack(fill=tk.X, side="bottom")

        def loop():
            if [t.name for t in threading.enumerate()].count("InputThread") > 1:
                root.quit()
            else:
                root.after(1, loop)
        root.after(1, loop)
        root.mainloop()

    t = threading.Thread(target=draw_window, args=((input, callback,)))
    t.name = "InputThread"
    t.daemon = True
    t.start()
