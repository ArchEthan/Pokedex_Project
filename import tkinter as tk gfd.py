import tkinter as tk

def ouvrir_fenetre():
    top = tk.Toplevel(root)
    top.title("Fenêtre Arène de combat")
    top.geometry("1900x1000")

    tk.Label(top, text="Ceci est une autre fenêtre").pack(pady=20)
    tk.Button(top, text="Fermer", command=top.destroy).pack(pady=10)

root = tk.Tk()
root.title("Fenêtre principale")
root.geometry("1900x1000")

menu_bar = tk.Menu(root)
menu_fichier = tk.Menu(menu_bar, tearoff=0)
menu_fichier.add_command(label="Ouvrir", command=ouvrir_fenetre)
menu_fichier.add_command(label="Quitter", command=root.quit)

menu_bar.add_cascade(label="Fichier", menu=menu_fichier)
root.config(menu=menu_bar)

root.mainloop()
