import tkinter as tk
from tkinter import messagebox

def afficher():
    nom = entry.get()
    if nom:
        messagebox.showinfo("Résultat", f"Bonjour {nom} 👋")
    else:
        messagebox.showwarning("Attention", "Champ vide !")

root = tk.Tk()
root.title("Application complète")
root.geometry("500x400")

# Menu
menu_bar = tk.Menu(root)
menu_fichier = tk.Menu(menu_bar, tearoff=0)
menu_fichier.add_command(label="Quitter", command=root.quit)
menu_bar.add_cascade(label="Fichier", menu=menu_fichier)
root.config(menu=menu_bar)

# Frames
frame_top = tk.Frame(root, bg="#ddd", height=80)
frame_top.pack(fill="x")

frame_center = tk.Frame(root)
frame_center.pack(expand=True)

frame_bottom = tk.Frame(root, height=50)
frame_bottom.pack(fill="x")

# Widgets
tk.Label(frame_top, text="Bienvenue", font=("Arial", 20), bg="#ddd").pack(pady=20)

tk.Label(frame_center, text="Entrez votre nom :").pack(pady=5)
entry = tk.Entry(frame_center, width=30)
entry.pack(pady=5)

tk.Button(frame_center, text="Valider", command=afficher).pack(pady=15)

tk.Label(frame_bottom, text="© 2026 Mon App").pack(pady=10)

root.mainloop()
