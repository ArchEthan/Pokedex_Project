**cursor = sqliteConnection.cursor():**



Elle utilise une connexion SQLite existante, sqliteConnection est un objet de type connexion (créé en général avec sqlite3.connect(...)).
Il représente le lien entre un programme Python et la base de données SQLite.

Elle crée un curseur (cursor)
La méthode .cursor() crée un objet curseur.
Un curseur sert à envoyer des requêtes SQL à la base de données et à récupérer les résultats.
Sans curseur, on ne peut pas exécuter de requêtes SQL.
Elle stocke ce curseur dans la variable cursor
On va ensuite utiliser cette variable pour travailler avec la base de données.

