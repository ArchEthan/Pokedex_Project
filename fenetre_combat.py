# fenetre_combat.py
# Fenêtre de combat Pokémon — s'ouvre en parallèle de la fenêtre principale
# Utilise la logique de combat.py (classe Personnage)

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
from combat import Personnage, combat_tour_par_tour

# Widgets tkinter classiques
Label      = tk.Label
Button     = tk.Button
Text       = tk.Text
Scrollbar  = tk.Scrollbar
StringVar  = tk.StringVar
# Widgets ttk
Combobox   = ttk.Combobox
Progressbar = ttk.Progressbar


# ----------------------------FONCTIONS BDD----------------------------

def connexion():
    try:
        return sqlite3.connect('pokedex.db')
    except sqlite3.Error as e:
        print("Erreur connexion:", e)

def deconnexion(conn):
    if conn:
        conn.close()

def get_liste_dresseurs():
    """Retourne [(idDresseur, nom), ...]"""
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT idDresseur, nom FROM dresseur ORDER BY nom;")
    data = cursor.fetchall()
    cursor.close()
    deconnexion(conn)
    return data

def get_pokemon_du_dresseur(idDresseur):
    """Retourne les pokémon du dresseur via pokemon_posseder.
    Colonnes retournées : (idPokemon, nom, HP, attaque, defense, vitesse, url_image)
    """
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.idPokemon, p.nom, p.HP, p.attaque, p.defense, p.vitesse, p.url_image
        FROM pokemon p
        INNER JOIN pokemon_posseder pp ON pp.id_pokemon = p.idPokemon
        WHERE pp.id_dresseur = ?
        ORDER BY p.nom;
    """, (idDresseur,))
    data = cursor.fetchall()
    cursor.close()
    deconnexion(conn)
    return data

def get_pokemon_sauvage_aleatoire():
    """Retourne un pokémon aléatoire depuis toute la table pokemon."""
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT idPokemon, nom, HP, attaque, defense, vitesse, url_image
        FROM pokemon ORDER BY RANDOM() LIMIT 1;
    """)
    data = cursor.fetchone()
    cursor.close()
    deconnexion(conn)
    return data


# ----------------------------CLASSE FENÊTRE DE COMBAT----------------------------

class FenetreCombat:

    BG     = '#1a1a2e'
    FG     = '#eaeaea'
    ACCENT = '#e94560'
    BLEU   = '#4fc3f7'
    BG_LOG = '#16213e'

    def __init__(self, fenetre_principale):
        self.fenetre = tk.Toplevel(fenetre_principale)
        self.fenetre.title("⚔️ Combat Pokémon")
        self.fenetre.geometry("820x660")
        self.fenetre.configure(bg=self.BG)
        self.fenetre.resizable(False, False)

        # Données
        self.dresseurs_data        = []
        self.pokemon_dresseur_data = []
        self.personnage_joueur     = None
        self.personnage_sauvage    = None
        self._hp_joueur_max        = 1
        self._hp_sauvage_max       = 1
        self.combat_en_cours       = False

        self._construire_interface()
        self._charger_dresseurs()

    # ----------------------------INTERFACE----------------------------

    def _construire_interface(self):
        bg, fg, accent, bleu = self.BG, self.FG, self.ACCENT, self.BLEU

        Label(self.fenetre, text="⚔️  COMBAT POKÉMON  ⚔️", font=("Courier", 18, "bold"), bg=bg, fg=accent).place(x=0, y=10, width=820)

        # ---- CÔTÉ JOUEUR (gauche) ----
        Label(self.fenetre, text="Dresseur :", font=("Courier", 10), bg=bg, fg=fg).place(x=30, y=55)
        self.combo_dresseur = Combobox(self.fenetre, state="readonly")
        self.combo_dresseur.place(x=30, y=75, width=210, height=26)
        self.combo_dresseur.bind("<<ComboboxSelected>>", self._on_dresseur_selectionne)

        Label(self.fenetre, text="Pokémon :", font=("Courier", 10), bg=bg, fg=fg).place(x=30, y=112)
        self.combo_pokemon = Combobox(self.fenetre, state="readonly")
        self.combo_pokemon.place(x=30, y=132, width=210, height=26)

        self.img_joueur = Label(self.fenetre, bg=bg)
        self.img_joueur.place(x=65, y=168, width=120, height=120)

        self.var_nom_joueur = StringVar(value="---")
        Label(self.fenetre, textvariable=self.var_nom_joueur, font=("Courier", 12, "bold"), bg=bg, fg=bleu).place(x=20, y=298, width=250)

        self.var_hp_joueur = StringVar(value="HP : --")
        Label(self.fenetre, textvariable=self.var_hp_joueur, font=("Courier", 10), bg=bg, fg=fg).place(x=20, y=322, width=250)

        self.var_stats_joueur = StringVar(value="")
        Label(self.fenetre, textvariable=self.var_stats_joueur, font=("Courier", 9), bg=bg, fg=fg).place(x=20, y=344, width=250)

        Label(self.fenetre, text="HP", font=("Courier", 8), bg=bg, fg=fg).place(x=20, y=366)
        self.barre_joueur = Progressbar(self.fenetre, orient=tk.HORIZONTAL, mode='determinate')
        self.barre_joueur.place(x=20, y=383, width=210, height=14)

        # ---- VS au centre ----
        Label(self.fenetre, text="VS", font=("Courier", 28, "bold"), bg=bg, fg=accent).place(x=360, y=235, width=100)

        # ---- CÔTÉ SAUVAGE (droite) ----
        Label(self.fenetre, text="Pokémon Sauvage :", font=("Courier", 10), bg=bg, fg=fg).place(x=560, y=55)

        self.img_sauvage = Label(self.fenetre, bg=bg)
        self.img_sauvage.place(x=630, y=168, width=120, height=120)

        self.var_nom_sauvage = StringVar(value="???")
        Label(self.fenetre, textvariable=self.var_nom_sauvage, font=("Courier", 12, "bold"), bg=bg, fg=accent).place(x=560, y=298, width=250)

        self.var_hp_sauvage = StringVar(value="HP : --")
        Label(self.fenetre, textvariable=self.var_hp_sauvage, font=("Courier", 10), bg=bg, fg=fg).place(x=560, y=322, width=250)

        self.var_stats_sauvage = StringVar(value="")
        Label(self.fenetre, textvariable=self.var_stats_sauvage, font=("Courier", 9), bg=bg, fg=fg).place(x=560, y=344, width=250)

        Label(self.fenetre, text="HP", font=("Courier", 8), bg=bg, fg=fg).place(x=560, y=366)
        
        self.barre_sauvage = Progressbar(self.fenetre, orient=tk.HORIZONTAL, mode='determinate')
        self.barre_sauvage.place(x=560, y=383, width=210, height=14)

        # ---- BOUTONS ----
        Button(self.fenetre, text="🎲 Lancer le combat", command=self._lancer_combat).place(x=150, y=425, width=190, height=34)

        Button(self.fenetre, text="⚔️ Attaquer",command=self._attaquer).place(x=150, y=472, width=190, height=34)

        Button(self.fenetre, text="🔄 Nouveau combat", command=self._nouveau_combat).place(x=480, y=472, width=190, height=34)

        # ---- JOURNAL ----
        Label(self.fenetre, text="Journal de combat :", font=("Courier", 9), bg=bg, fg=fg).place(x=30, y=520)

        self.log = Text(self.fenetre, bg=self.BG_LOG, fg='#a0d8ef', font=("Courier", 9), state=tk.DISABLED)
        self.log.place(x=30, y=538, width=760, height=100)

    # ----------------------------CHARGEMENT DONNÉES----------------------------

    def _charger_dresseurs(self):
        self.dresseurs_data = get_liste_dresseurs()
        self.combo_dresseur['values'] = [d[1] for d in self.dresseurs_data]

        if self.dresseurs_data:
            self.combo_dresseur.current(0)
            self._on_dresseur_selectionne(None)

    def _on_dresseur_selectionne(self, event):
        """Quand on change de dresseur, recharge uniquement ses pokémon."""
        idx = self.combo_dresseur.current()
        if idx < 0:
            return
        
        idDresseur = self.dresseurs_data[idx][0]
        self.pokemon_dresseur_data = get_pokemon_du_dresseur(idDresseur)
        self.combo_pokemon['values'] = [p[1] for p in self.pokemon_dresseur_data]

        if self.pokemon_dresseur_data:
            self.combo_pokemon.current(0)
        else:
            self.combo_pokemon.set('')
            self._log("⚠️  Ce dresseur ne possède aucun Pokémon !")

    def _charger_image(self, url_image, label_widget):
        """Charge un PNG en mode palette (P) avec transparence correcte."""
        try:
            lien = "images/" + str(url_image)
            hex_c = self.BG.lstrip('#')
            bg_rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
            img_pil = Image.open(lien)

            # Conversion RGBA avant resize : préserve l'index de transparence palette
            img_pil = img_pil.convert("RGBA")
            img_pil = img_pil.resize((120, 120), Image.LANCZOS)
            fond = Image.new("RGB", img_pil.size, bg_rgb)
            fond.paste(img_pil, mask=img_pil.split()[3])  # canal alpha comme masque
            photo = ImageTk.PhotoImage(fond)
            label_widget.configure(image=photo, text="")
            label_widget.image = photo

        except Exception as e:
            print(f"Image introuvable ({url_image}): {e}")
            label_widget.configure(image="", text="?")

    # ----------------------------LOGIQUE DE COMBAT----------------------------

    def _lancer_combat(self):
        idx = self.combo_pokemon.current()
        if idx < 0:
            messagebox.showwarning("Attention", "Sélectionnez un dresseur et un Pokémon !")
            return

        poke_j = self.pokemon_dresseur_data[idx]
        # (idPokemon, nom, HP, attaque, defense, vitesse, url_image)
        self.personnage_joueur = Personnage(nom=poke_j[1], pv=poke_j[2], attaque=poke_j[3])
        self._hp_joueur_max = poke_j[2]

        poke_s = get_pokemon_sauvage_aleatoire()
        self.personnage_sauvage = Personnage(nom=poke_s[1], pv=poke_s[2], attaque=poke_s[3])
        self._hp_sauvage_max = poke_s[2]

        # Affichage joueur
        self.var_nom_joueur.set(poke_j[1])
        self.var_hp_joueur.set(f"HP : {self.personnage_joueur.pv}")
        self.var_stats_joueur.set(f"ATK:{poke_j[3]}  DEF:{poke_j[4]}  VIT:{poke_j[5]}")
        self._charger_image(poke_j[6], self.img_joueur)
        self._maj_barre(self.barre_joueur, self.personnage_joueur.pv, self._hp_joueur_max)

        # Affichage sauvage
        self.var_nom_sauvage.set(poke_s[1])
        self.var_hp_sauvage.set(f"HP : {self.personnage_sauvage.pv}")
        self.var_stats_sauvage.set(f"ATK:{poke_s[3]}  DEF:{poke_s[4]}  VIT:{poke_s[5]}")
        self._charger_image(poke_s[6], self.img_sauvage)
        self._maj_barre(self.barre_sauvage, self.personnage_sauvage.pv, self._hp_sauvage_max)

        self.combat_en_cours = True
        self._log("=" * 55)
        self._log(f"🎮 {poke_j[1]} (Dresseur) VS {poke_s[1]} (Sauvage) !")

    def _attaquer(self):
        """Un tour complet : joueur attaque, le sauvage contre-attaque."""
        if not self.combat_en_cours:
            self._log("⚠️  Lancez d'abord un combat !")
            return

        # Joueur attaque
        msg = self.personnage_joueur.frapper(self.personnage_sauvage)
        self._log(f"▶ {msg}")

        # Sauvage contre-attaque si encore en vie
        if self.personnage_sauvage.est_vivant():
            msg = self.personnage_sauvage.frapper(self.personnage_joueur)
            self._log(f"▶ {msg}")

        # Mise à jour affichage
        self.var_hp_joueur.set(f"HP : {max(0, self.personnage_joueur.pv)}")
        self.var_hp_sauvage.set(f"HP : {max(0, self.personnage_sauvage.pv)}")
        self._maj_barre(self.barre_joueur, self.personnage_joueur.pv, self._hp_joueur_max)
        self._maj_barre(self.barre_sauvage, self.personnage_sauvage.pv, self._hp_sauvage_max)

        # Fin de combat
        j_mort = not self.personnage_joueur.est_vivant()
        s_mort = not self.personnage_sauvage.est_vivant()
        if j_mort and s_mort:
            self._log("💀 Match nul ! Les deux Pokémon sont K.O. !")
            self.combat_en_cours = False
        elif s_mort:
            self._log(f"🏆 Victoire ! {self.personnage_joueur.nom} a vaincu {self.personnage_sauvage.nom} !")
            self.combat_en_cours = False
        elif j_mort:
            self._log(f"💀 Défaite... {self.personnage_joueur.nom} est K.O. !")
            self.combat_en_cours = False

    def _nouveau_combat(self):
        """Remet tout à zéro."""
        self.combat_en_cours = False
        self.personnage_joueur = None
        self.personnage_sauvage = None
        for var, val in [(self.var_nom_joueur, "---"), (self.var_nom_sauvage, "???"),(self.var_hp_joueur, "HP : --"), (self.var_hp_sauvage, "HP : --"), (self.var_stats_joueur, ""), (self.var_stats_sauvage, "")]:
            var.set(val)
        for lbl in [self.img_joueur, self.img_sauvage]:
            lbl.configure(image="", text="")
            lbl.image = None
        self.barre_joueur['value'] = 0
        self.barre_sauvage['value'] = 0
        self._log("🔄 Prêt pour un nouveau combat !")

    # ----------------------------UTILITAIRES----------------------------

    def _maj_barre(self, barre, hp_actuel, hp_max):
        if hp_max > 0:
            barre['value'] = max(0, (hp_actuel / hp_max) * 100)

    def _log(self, message):
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)
