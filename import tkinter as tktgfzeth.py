import tkinter as tk
from tkinter import messagebox
from combat import Personnage, combat_tour_par_tour

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Combat rééquilibré")
        self.root.geometry("500x400")
        self.creer_widgets()

    def creer_widgets(self):
        tk.Label(self.root, text="Nom Perso 1 (fort, 5% esquive):").pack()
        self.nom1 = tk.Entry(self.root)
        self.nom1.pack()

        tk.Label(self.root, text="Nom Perso 2 (faible, 50% esquive):").pack()
        self.nom2 = tk.Entry(self.root)
        self.nom2.pack()

        tk.Button(self.root, text="Combattre !", command=self.lancer_combat).pack(pady=10)

        self.zone_log = tk.Text(self.root, height=15, width=60)
        self.zone_log.pack(pady=10)

    def lancer_combat(self):
        self.zone_log.delete("1.0", tk.END)
        # Perso1 = fort mais peu d'esquive
        p1 = Personnage(self.nom1.get() or "Perso1", pv=100, attaque=25, esquive=0.05)
        # Perso2 = faible mais beaucoup d'esquive
        p2 = Personnage(self.nom2.get() or "Perso2", pv=100, attaque=15, esquive=0.4)  # 50% d'esquive

        gagnant, log = combat_tour_par_tour(p1, p2)
        for ligne in log:
            self.zone_log.insert(tk.END, ligne + "\n")

        messagebox.showinfo("Résultat", f"Le gagnant est {gagnant.nom} !")

root = tk.Tk()
app = App(root)
root.mainloop()
