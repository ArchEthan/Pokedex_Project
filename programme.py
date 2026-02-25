import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
from fenetre_combat import FenetreCombat

## Widgets tk uniquement
Label     = tk.Label
Button    = tk.Button
Entry     = tk.Entry
StringVar = tk.StringVar
Scrollbar = tk.Scrollbar
YES       = tk.YES

# Widgets ttk uniquement
Combobox  = ttk.Combobox
Treeview  = ttk.Treeview


# ----------------------------FONCTIONS BDD----------------------------

def connexion():
    try:
        return sqlite3.connect('pokedex.db')
    except sqlite3.Error as e:
        print("Erreur connexion:", e)

def deconnexion(conn):
    if conn:
        conn.close()

def RemplirListeDeroulantePokemon():
    """Retourne la liste de tous les noms pour la Combobox principale."""
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM pokemon ORDER BY idPokemon;")
    noms = [row[0] for row in cursor.fetchall()]
    cursor.close()
    deconnexion(conn)
    return noms

def RemplirListeDeroulanteTypes():
    """Retourne la liste de tous les types pour le filtre."""
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle_type FROM type ORDER BY libelle_type;")
    types = [row[0] for row in cursor.fetchall()]
    cursor.close()
    deconnexion(conn)
    return types

def AfficherDetailsPokemon(nom_pokemon):
    """Retourne le tuple complet d'un pokémon par son nom."""
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nom, p.HP, p.attaque, p.defense, p.attaque_spe, p.defense_spe, p.vitesse, p.url_image, t.libelle_type
        FROM pokemon p
        INNER JOIN type t ON t.idType = p.idType
        WHERE p.nom = ?;
    """, (nom_pokemon,))
    data = cursor.fetchone()
    cursor.close()
    deconnexion(conn)
    return data

def RechercherPokemons(recherche_nom, filtre_type):
    """Recherche dans le tableau par nom ET/OU type.
    - recherche_nom : texte libre (peut être vide)
    - filtre_type   : libelle_type exact, ou '' pour tous les types
    - Retourne [(idPokemon, nom, HP, libelle_type), ...]
    """
    conn = connexion()
    cursor = conn.cursor()
    if filtre_type:
        cursor.execute("""
            SELECT p.idPokemon, p.nom, p.HP, t.libelle_type
            FROM pokemon p
            INNER JOIN type t ON t.idType = p.idType
            WHERE p.nom LIKE ? AND t.libelle_type = ?
            ORDER BY p.idPokemon;
        """, (f'%{recherche_nom}%', filtre_type))
    else:
        cursor.execute("""
            SELECT p.idPokemon, p.nom, p.HP, t.libelle_type
            FROM pokemon p
            INNER JOIN type t ON t.idType = p.idType
            WHERE p.nom LIKE ?
            ORDER BY p.idPokemon;
        """, (f'%{recherche_nom}%',))
    data = cursor.fetchall()
    cursor.close()
    deconnexion(conn)
    return data


# ----------------------------FONCTIONS D'AFFICHAGE----------------------------

def AffichezPokemon():
    """Affiche la fiche du pokémon sélectionné dans la Combobox."""
    nom = listeDeroulantePokemon.get()
    if not nom:
        return
    data = AfficherDetailsPokemon(nom)
    if not data:
        return
    # details pokemon = (nom, HP, attaque, defense, attaque_spe, defense_spe, vitesse, url_image, type)
    value_label_nom.set(data[0])
    value_label_type.set(f"Type : {data[8]}")
    value_label_hp.set(f"HP : {data[1]}")
    value_label_attaque.set(f"Attaque : {data[2]}")
    value_label_defense.set(f"Défense : {data[3]}")
    value_label_atk_spe.set(f"Att. Spé : {data[4]}")
    value_label_def_spe.set(f"Déf. Spé : {data[5]}")
    value_label_vitesse.set(f"Vitesse : {data[6]}")

    # Image avec fond transparent
    try:
        lien_image = "images/" + str(data[7])
        img_pil = Image.open(lien_image)
        # Les images sont en mode P (palette PNG) avec un index de transparence.
        # Il faut convertir en RGBA avant le resize pour préserver la transparence.
        img_pil = img_pil.convert("RGBA")
        img_pil = img_pil.resize((180, 180), Image.LANCZOS)
        bg_hex = fenetre.cget('bg').lstrip('#')
        bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
        fond = Image.new("RGB", img_pil.size, bg_rgb)
        fond.paste(img_pil, mask=img_pil.split()[3])
        img_tk = ImageTk.PhotoImage(fond)
        image_pokemon.configure(image=img_tk)
        image_pokemon.image = img_tk
    except Exception as e:
        print(f"Image introuvable : {e}")
        image_pokemon.configure(image="")


def AffichezListePokemon():
    """Remplit le tableau selon les critères de recherche (nom + type)."""
    recherche = var_texte_recherche.get().strip()
    type_choisi = combo_filtre_type.get()
    if type_choisi == "Tous les types":
        type_choisi = ""

    resultats = RechercherPokemons(recherche, type_choisi)
    tree.delete(*tree.get_children())
    for row in resultats:
        tree.insert('', 'end', iid=str(row[0]), text=str(row[1]),
                    values=(str(row[2]), str(row[3])))
    var_compteur.set(f"{len(resultats)} pokémon trouvé(s)")


def ReinitialiserRecherche():
    """Vide les champs et réaffiche tous les pokémon."""
    var_texte_recherche.set("")
    combo_filtre_type.set("Tous les types")
    AffichezListePokemon()


def OuvrirCombat():
    """Ouvre la fenêtre de combat en parallèle (Toplevel)."""
    FenetreCombat(fenetre)


# ----------------------------FENÊTRE PRINCIPALE----------------------------

fenetre = tk.Tk()
fenetre.title("Pokédex — 1ère Génération")
fenetre.geometry("1000x700")
fenetre.configure(bg='#ebff5c')
fenetre.resizable(False, False)

# ----------------------------BARRE DU HAUT----------------------------
# -------------sélection pokémon individuel + bouton combat-------------

Label(fenetre, text="Fiche Pokémon :", font=("Arial", 11, "bold"),
      bg='#ebff5c').place(x=30, y=10)

tabPokemon = RemplirListeDeroulantePokemon()
listeDeroulantePokemon = Combobox(fenetre, values=tabPokemon, state="readonly")
listeDeroulantePokemon.current(0)
listeDeroulantePokemon.place(x=30, y=35, width=200, height=24)

Button(fenetre, text="Afficher", command=AffichezPokemon
       ).place(x=240, y=35, width=100, height=24)

Button(fenetre, text="⚔️  Lancer un Combat", command=OuvrirCombat
       ).place(x=360, y=35, width=180, height=24)

# ----------------------------FICHE DÉTAILLÉE (gauche) + IMAGE (droite)----------------------------

value_label_nom = StringVar()
Label(fenetre, textvariable=value_label_nom, font=("Arial", 14, "bold"), bg='#ebff5c').place(x=30, y=85, width=210)

value_label_type = StringVar()
Label(fenetre, textvariable=value_label_type, font=("Arial", 10, "italic"), bg='#ebff5c').place(x=30, y=112, width=210)

Label(fenetre, text="Statistiques :", font=("Arial", 10, "bold"), bg='#ebff5c').place(x=30, y=140)

value_label_hp      = StringVar()
value_label_attaque = StringVar()
value_label_defense = StringVar()
value_label_atk_spe = StringVar()
value_label_def_spe = StringVar()
value_label_vitesse = StringVar()

for i, var in enumerate([value_label_hp, value_label_attaque, value_label_defense, value_label_atk_spe, value_label_def_spe, value_label_vitesse]):
    Label(fenetre, textvariable=var, bg='#ebff5c').place(x=30, y=162 + i * 22, width=210)

image_pokemon = Label(fenetre, image="", bg='#ebff5c')
image_pokemon.place(x=260, y=85, width=180, height=180)

# ----------------------------ZONE DE RECHERCHE DANS LE TABLEAU----------------------------

Label(fenetre, text="Rechercher dans la liste :", font=("Arial", 11, "bold"),bg='#ebff5c').place(x=30, y=305)

Label(fenetre, text="Nom :", bg='#ebff5c').place(x=30, y=333)
var_texte_recherche = StringVar()
Entry(fenetre, textvariable=var_texte_recherche).place(x=80, y=333, width=160, height=24)

Label(fenetre, text="Type :", bg='#ebff5c').place(x=260, y=333)
types_liste = ["Tous les types"] + RemplirListeDeroulanteTypes()
combo_filtre_type = Combobox(fenetre, values=types_liste, state="readonly")
combo_filtre_type.set("Tous les types")
combo_filtre_type.place(x=310, y=333, width=150, height=24)

Button(fenetre, text="🔍 Rechercher", command=AffichezListePokemon).place(x=475, y=333, width=130, height=24)
Button(fenetre, text="✖ Réinitialiser", command=ReinitialiserRecherche).place(x=620, y=333, width=130, height=24)

var_compteur = StringVar(value="")
Label(fenetre, textvariable=var_compteur, font=("Arial", 9, "italic"), bg='#ebff5c').place(x=770, y=337)

# ----------------------------TABLEAU DE RÉSULTATS----------------------------

tree = Treeview(fenetre, columns=('HP', 'Type'))
tree.heading('#0', text='Pokémon')
tree.heading('#1', text='HP')
tree.heading('#2', text='Type')
tree.column('#0', width=200, stretch=YES)
tree.column('#1', width=70, stretch=YES)
tree.column('#2', width=130, stretch=YES)
tree.place(x=30, y=370, width=930, height=290)

scrollbar = Scrollbar(fenetre, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.place(x=960, y=370, height=290)

# ----------------------------CHARGEMENT INITIAL----------------------------

AffichezPokemon()       # fiche du 1er pokémon
AffichezListePokemon()  # tous les pokémon dans le tableau

fenetre.mainloop()
