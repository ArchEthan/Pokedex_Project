from tkinter import*
from tkinter.ttk import *
import sqlite3


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
    sqlite_select_Query = "select nom,HP,attaque,defense,url_image from pokemon  WHERE nom ='" + listeDeroulantePokemon.get() + "';"
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

    #construction du lien de l'image
    lien_image = "images/" + str(record[0][4])

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
    sqlite_select_Query = "SELECT idPokemon,nom,HP,libelle_type FROM pokemon INNER JOIN type  ON type.idType = pokemon.idType WHERE nom LIKE '%" + var_texte_recherche.get() + "%';"
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
#permet de modifier la taille de la fenétre
fenetre.geometry("800x800")
fenetre.configure(bg='#ebff5c')
#On crée un label(lignedetexte) souhaitant la bienvenue
#Note:lepremier paramètre passé au constructeur de Label est notre fenétre



"""
------Partie liste déroulante + Bouton Recherche-------------
"""
def leftclick(event):
    print(event.x)
    print("left")

fenetre.bind("<Button-1>", leftclick)   


#récupération de la liste des pokemon dans la base de données avec la fonction RemplirListeDeroulantePokemon qui retoune un tableau.
tabPokemon=RemplirListeDeroulantePokemon()
#  Création de la Combobox (liste déroulante) 
listeDeroulantePokemon = Combobox(fenetre, values=tabPokemon)
# Choisir l'élément qui s'affiche par défaut
listeDeroulantePokemon.current(0)
#positon de la liste
listeDeroulantePokemon.place(x=200,y=50,width=100, height=20)


#création du Label
label_recherche_poke=Label(fenetre,text="Rechercher Pokemon")
#postion du label
label_recherche_poke.place(x=50,y=50,width=150, height=20)

#bouton recherche qui appele la fonction AffichezPokemon
bouton_search=Button(fenetre, text="Rechercher", command=AffichezPokemon)
bouton_search.place(x=320,y=50,width=150, height=20)
"""
------FIN-------------
"""


"""
Partie affichage des informations d'un pokemon
"""


#création d'une variable StringVar
value_label_nom = StringVar()
#création du lbale
champ_label=Label(fenetre,textvariable=value_label_nom)
champ_label.place(x=50,y=130,width=200, height=20)

champ_label_info=Label(fenetre,text="Information")
champ_label_info.place(x=50,y=160,width=200, height=20)

#création d'une variable StringVar
value_label_hp = StringVar()
champ_label_hp=Label(fenetre,textvariable=value_label_hp)
champ_label_hp.place(x=50,y=190,width=200, height=20)

#création d'une variable StringVar
value_label_attaque = StringVar()
champ_label_attaque=Label(fenetre,textvariable=value_label_attaque)
champ_label_attaque.place(x=50,y=220,width=200, height=20)

#création d'une variable StringVar
value_label_defense = StringVar()
champ_label_defense=Label(fenetre,textvariable=value_label_defense)
champ_label_defense.place(x=50,y=250,width=200, height=20)

image_pokemon = Label(fenetre, image="")
image_pokemon.place(x=400,y=100,width=200, height=200)
"""
-------------------FIN---------------------------------------
"""


"""
Partie recherche et affichage du tableau
"""
#création d'une variable StringVar
var_texte_recherche = StringVar()
textBoxRecherche = Entry(fenetre, textvariable=var_texte_recherche, width=20)
textBoxRecherche.place(x=50,y=450,width=100, height=20)
#bouton de recherche
bouton_affichez_pokemon=Button(fenetre, text="Rechercher", command=AffichezListePokemon)
bouton_affichez_pokemon.place(x=170,y=450,width=150, height=20)

#création de la grille d'affichage (tableau)
tree = Treeview(fenetre, columns=('HP', 'Type'))

# Set the heading (Attribute Names)
tree.heading('#0', text='Pokemon')
tree.heading('#1', text='HP')
tree.heading('#2', text='Type')
# Specify attributes of the columns (We want to stretch it!)
tree.column('#0',width=150, stretch=YES)
tree.column('#1',width=30, stretch=YES)
tree.column('#2',width=70, stretch=YES)

#placement du tableau
tree.place(x=20,y=490,width=351, height=150)
"""-----------------FIN----------------------"""

#On démarre la boucle Tkinter qui s'interrompt quand on ferme la fenêtre
fenetre.mainloop()





