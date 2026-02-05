from tkinter import*
from tkinter.ttk import *
import sqlite3
import os


"""Fonction de connexion permettant de se connecter à la base pokedex
"""
def connexion():
    try:
        #connexion à la bdd
        sqliteConnection = sqlite3.connect('pokedex.db')
        return sqliteConnection
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)

"""<summary>Fonction de connexion à la bdd</summary>
"""
def deconnexion(sqliteConnection):
   if (sqliteConnection):
       #fermeture de la co
            sqliteConnection.close()
            print("The SQLite connection is closed")



"""<summary>La fonction va chercher la liste des pokemon dans la bdd</summary>
<return>Retourne un tableau contenant la liste des noms de pokemon</return>
"""
def RemplirListeDeroulantePokemon():
    sqliteConnection = connexion()
    cursor = sqliteConnection.cursor()
    #ecriture de la requéte
    sqlite_select_Query = "select nom from pokemon;"
    #execution de la requéte
    cursor.execute(sqlite_select_Query)
    #on place tout les enregistrements dans une variable record
    record = cursor.fetchall()
    #declaration du tableau qui va contenir les données a afficher dans la liste déroulante
    tabPoke = []
    #parcours notre tableau de retour de base de données et ajoute les éléments dans le tableau data
    for row in record:
        tabPoke.append(row[0])

    #on ferme le curseur
    cursor.close()
    deconnexion(sqliteConnection)

    #retourne le tableau
    return tabPoke   
"""<summary>Recupére et affiche les informations récupérer par la requéte</summary>

"""
def AffichezPokemon():
    
    sqliteConnection = connexion()
    cursor = sqliteConnection.cursor()
    #ecriture de la requéte, on récupére le contenu de la listeDeroulante avec la fonction .get()
    sqlite_select_Query = "select nom,HP,attaque,defense,attaque_spe,defense_spe,vitesse,url_image,libelle_type from pokemon INNER JOIN type ON type.idType = pokemon.idType WHERE nom ='" + listeDeroulantePokemon.get() + "';"
    #execution de la requéte
    cursor.execute(sqlite_select_Query)
    #on place tout les enregistrements dans une variable record
    record = cursor.fetchall()

    #la variable record est un tableau à plusieurs dimension, chaque case contient une information

    #on modifie la valeur de la StringVar "value_label_nom" avec une valeur du tableau
    value_label_nom.set(record[0][0])

    #on modifie la valeur de la StringVar "value_label_hp" avec une valeur du tableau
    value_label_hp.set("HP: "+ str(record[0][1]))
    #on modifie la valeur de la StringVar "value_label_attaque" avec une valeur du tableau + du texte
    value_label_attaque.set("Attaque: " + str(record[0][2]))
    #on modifie la valeur de la StringVar "value_label_defense" avec une valeur du tableau + du texte
    value_label_defense.set("Defense: " + str(record[0][3]))
    #on modifie la valeur de la StringVar "value_label_attaque_spe" avec une valeur du tableau + du texte
    value_label_attaque_spe.set("Attaque Spé: " + str(record[0][4]))
    #on modifie la valeur de la StringVar "value_label_defense_spe" avec une valeur du tableau + du texte
    value_label_defense_spe.set("Défense Spé: " + str(record[0][5]))
    #on modifie la valeur de la StringVar "value_label_vitesse" avec une valeur du tableau + du texte
    value_label_vitesse.set("Vitesse: " + str(record[0][6]))
    #on modifie la valeur de la StringVar "value_label_type" avec une valeur du tableau + du texte
    value_label_type.set("Type: " + str(record[0][8]))

    #construction du lien de l'image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lien_image = os.path.join(script_dir, "images", str(record[0][7]))

    #affichage de l'image
    img2 = PhotoImage(file=lien_image)
    image_pokemon.configure(image=img2)
    image_pokemon.image = img2
    

    print("SQLite Database Version is: ", record)
    #on ferme le curseur
    cursor.close()
    deconnexion(sqliteConnection)
    
"""<summary>Affiche dans le tree la liste des pokemon retourné par la requéte</summary>
"""

def AffichezListePokemon():
    
    sqliteConnection = connexion()
    cursor = sqliteConnection.cursor()
    #ecriture de la requéte
    sqlite_select_Query = "SELECT idPokemon,nom,HP,libelle_type FROM pokemon INNER JOIN type  ON type.idType = pokemon.idType WHERE nom LIKE '%" + var_texte_recherche.get() + "%' OR libelle_type LIKE '%" + var_texte_recherche.get() + "%';"
    #execution de la requéte
    cursor.execute(sqlite_select_Query)
    #on place tout les enregistrements dans une variable record
    record = cursor.fetchall()
    #vidange du tableau
    tree.delete(*tree.get_children())
    #on parcours le tableau record pour afficher et on insert une nouvelle ligne à chaque row. 
    for row in record:
        tree.insert('', 'end', iid=str(row[0]), text=str(row[1]),
                             values=(str(row[2]),
                                     str(row[3])))


    #on ferme le curseur
    cursor.close()
    #deconnexion de la bdd
    deconnexion(sqliteConnection)



#création de la fenetre Tkinter
fenetre=Tk()
fenetre.title("Pokédex")
#permet de modifier la taille de la fenétre
fenetre.geometry("900x850")

#configuration de la police et des couleurs par défaut
style = Style()
style.theme_use('clam')

# Configuration des couleurs
bg_color = '#f5f5f5'
fg_color = '#333333'
accent_color = '#FF0000'

# Configurer le style de la fenêtre
style.configure('TFrame', background=bg_color)
style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), background=bg_color, foreground=accent_color)
style.configure('Normal.TLabel', font=('Segoe UI', 10), background=bg_color, foreground=fg_color)
style.configure('TButton', font=('Segoe UI', 10), background='#e0e0e0')
style.configure('TCombobox', font=('Segoe UI', 10))
style.map('TButton', background=[('active', '#FF0000'), ('pressed', '#CC0000')])

# Ajouter un style pour le titre
style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), background=bg_color, foreground=accent_color)



"""
------Partie liste déroulante + Bouton Recherche-------------
"""

#récupération de la liste des pokemon dans la base de données avec la fonction RemplirListeDeroulantePokemon qui retoune un tableau.
tabPokemon=RemplirListeDeroulantePokemon()

#création du Label
label_recherche_poke=Label(fenetre,text="Sélectionner Pokémon:", style='Normal.TLabel')
#position du label
label_recherche_poke.place(x=20,y=15,width=130, height=25)

#  Création de la Combobox (liste déroulante) 
listeDeroulantePokemon = Combobox(fenetre, values=tabPokemon, state='readonly')
# Choisir l'élément qui s'affiche par défaut
listeDeroulantePokemon.current(0)
#position de la liste
listeDeroulantePokemon.place(x=160,y=15,width=180, height=25)

#bouton recherche qui appele la fonction AffichezPokemon
bouton_search=Button(fenetre, text="Voir détails", command=AffichezPokemon)
bouton_search.place(x=360,y=15,width=110, height=25)

"""
------FIN-------------
"""


"""
Partie affichage des informations d'une pokemon
"""


#création d'une variable StringVar
value_label_nom = StringVar()
#création du label
champ_label=Label(fenetre,textvariable=value_label_nom, style='Title.TLabel')
champ_label.place(x=20,y=55,width=420, height=35)

#image affichée à droite
image_pokemon = Label(fenetre, image="")
image_pokemon.place(x=480,y=55,width=400, height=280)

champ_label_info=Label(fenetre,text="Caractéristiques", style='Header.TLabel')
champ_label_info.place(x=20,y=95,width=420, height=20)

#création d'une variable StringVar
value_label_hp = StringVar()
champ_label_hp=Label(fenetre,textvariable=value_label_hp, style='Normal.TLabel')
champ_label_hp.place(x=20,y=120,width=420, height=18)

#création d'une variable StringVar
value_label_attaque = StringVar()
champ_label_attaque=Label(fenetre,textvariable=value_label_attaque, style='Normal.TLabel')
champ_label_attaque.place(x=20,y=140,width=420, height=18)

#création d'une variable StringVar
value_label_defense = StringVar()
champ_label_defense=Label(fenetre,textvariable=value_label_defense, style='Normal.TLabel')
champ_label_defense.place(x=20,y=160,width=420, height=18)

#création d'une variable StringVar
value_label_attaque_spe = StringVar()
champ_label_attaque_spe=Label(fenetre,textvariable=value_label_attaque_spe, style='Normal.TLabel')
champ_label_attaque_spe.place(x=20,y=180,width=420, height=18)

#création d'une variable StringVar
value_label_defense_spe = StringVar()
champ_label_defense_spe=Label(fenetre,textvariable=value_label_defense_spe, style='Normal.TLabel')
champ_label_defense_spe.place(x=20,y=200,width=420, height=18)

#création d'une variable StringVar
value_label_vitesse = StringVar()
champ_label_vitesse=Label(fenetre,textvariable=value_label_vitesse, style='Normal.TLabel')
champ_label_vitesse.place(x=20,y=220,width=420, height=18)

#création d'une variable StringVar
value_label_type = StringVar()
champ_label_type=Label(fenetre,textvariable=value_label_type, style='Normal.TLabel')
champ_label_type.place(x=20,y=240,width=420, height=18)
"""
-------------------FIN---------------------------------------
"""


"""
Partie recherche et affichage du tableau
"""
#création d'une variable StringVar
var_texte_recherche = StringVar()
label_recherche_liste=Label(fenetre, text="Filtrer par nom/type:", style='Normal.TLabel')
label_recherche_liste.place(x=20,y=345,width=140, height=20)
textBoxRecherche = Entry(fenetre, textvariable=var_texte_recherche, width=20, font=('Segoe UI', 10))
textBoxRecherche.place(x=170,y=345,width=150, height=25)
#bouton de recherche
bouton_affichez_pokemon=Button(fenetre, text="Filtrer liste", command=AffichezListePokemon)
bouton_affichez_pokemon.place(x=330,y=345,width=110, height=25)

#création de la grille d'affichage (tableau)
tree = Treeview(fenetre, columns=('HP', 'Type'))
 
 # Set the heading (Attribute Names)
tree.heading('#0', text='Pokemon')
tree.heading('#1', text='HP')
tree.heading('#2', text='Type')
# Specify attributes of the columns (We want to stretch it!)
tree.column('#0',width=150, stretch=YES)
tree.column('#1',width=50, stretch=YES)
tree.column('#2',width=100, stretch=YES)

#placement du tableau
tree.place(x=20,y=380,width=860, height=450)
"""-----------------FIN----------------------"""

#On démarre la boucle Tkinter qui s'interrompt quand on ferme la fenêtre
fenetre.mainloop()





