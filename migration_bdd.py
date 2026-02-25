# migration_bdd.py
# Script de migration et correction de la base de données pokedex.db
# À exécuter UNE SEULE FOIS depuis le dossier du projet.
#
# Corrections effectuées :
#  1. Types traduits en français
#  2. url_image corrigées pour les Nidoran (F et M)
#  3. url_image corrigées pour Piafabec2, Psykokwak2, etc. (variantes)
#  4. Clés étrangères ajoutées (recréation des tables)
#  5. Nidoran nommés correctement (Nidoran♀ / Nidoran♂)

import sqlite3
import shutil
import os
from datetime import datetime

DB_PATH = 'pokedex.db'

# --- Sauvegarde automatique avant toute modification ---
backup_path = f'pokedex_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
shutil.copy2(DB_PATH, backup_path)
print(f'✅ Sauvegarde créée : {backup_path}')

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# ============================================================
# 1. TRADUCTION DES TYPES EN FRANÇAIS
# ============================================================
print('\n--- Traduction des types en français ---')
types_fr = {
    'Grass':     'Plante',
    'Fire':      'Feu',
    'Water':     'Eau',
    'Bug':       'Insecte',
    'Normal':    'Normal',
    'Poison':    'Poison',
    'Electric':  'Électrique',
    'Ground':    'Sol',
    'Fairy':     'Fée',
    'Fighting':  'Combat',
    'Psychic':   'Psy',
    'Rock':      'Roche',
    'Ghost':     'Spectre',
    'Ice':       'Glace',
    'Dragon':    'Dragon',
}
for en, fr in types_fr.items():
    cursor.execute("UPDATE type SET libelle_type = ? WHERE libelle_type = ?", (fr, en))
    if cursor.rowcount:
        print(f'  {en} → {fr}')
print('  Types traduits !')

# ============================================================
# 2. CORRECTION DES NOMS ET URL_IMAGE DES NIDORAN
# ============================================================
print('\n--- Correction des Nidoran ---')
# Nidoran femelle (id=29) et mâle (id=32)
cursor.execute("UPDATE pokemon SET nom = 'Nidoran♀', url_image = 'Nidoran_F.gif' WHERE idPokemon = 29")
cursor.execute("UPDATE pokemon SET nom = 'Nidoran♂', url_image = 'Nidoranm.gif' WHERE idPokemon = 32")
print('  Nidoran♀ (id=29) et Nidoran♂ (id=32) corrigés')

# ============================================================
# 3. CORRECTION DES URL_IMAGE MANQUANTES (substitutions proches)
# ============================================================
print('\n--- Correction des url_image manquantes ---')
corrections_images = {
    # id: (nom_pokemon, ancienne_url, nouvelle_url, raison)
    14:  ('Coconfort',  'Coconfort.gif',  'Chrysacier.gif',  'Pas d\'image dispo, utilise Chrysacier (même famille)'),
    22:  ('Rapasdepic', 'Rapasdepic.gif', 'Piafabec2.gif',   'Utilise variante Piafabec2'),
    44:  ('Ortide',     'Ortide.gif',     'Rafflesia2.gif',  'Pas d\'image dispo, utilise variante Rafflesia'),
    55:  ('Akwakwak',   'Akwakwak.gif',   'Psykokwak2.gif',  'Utilise variante Psykokwak2'),
    70:  ('Boustiflor', 'Boustiflor.gif', 'Chétiflor2.gif',  'Utilise variante Chétiflor2'),
    127: ('Scarabrute', 'Scarabrute.gif', 'Insécateur.gif',  'Pas d\'image dispo, utilise Insécateur (même famille)'),
}
for pid, (nom, old_url, new_url, raison) in corrections_images.items():
    if os.path.exists(f'images/{new_url}'):
        cursor.execute("UPDATE pokemon SET url_image = ? WHERE idPokemon = ?", (new_url, pid))
        print(f'  {nom} (id={pid}): {old_url} → {new_url} ({raison})')
    else:
        print(f'  ⚠️  {nom} (id={pid}): image {new_url} introuvable, ignoré')

# ============================================================
# 4. AJOUT DES CLÉS ÉTRANGÈRES MANQUANTES
#    SQLite ne permet pas d'ALTER TABLE pour ajouter des FK.
#    On recrée les tables concernées.
# ============================================================
print('\n--- Ajout des clés étrangères ---')

# -- Table pokemon : ajouter FK sur idType -> type(idType)
print('  Recréation de la table pokemon avec FK sur idType...')
cursor.executescript("""
    PRAGMA foreign_keys = OFF;

    -- Sauvegarde temporaire
    ALTER TABLE pokemon RENAME TO pokemon_old;

    -- Recréation avec FK
    CREATE TABLE pokemon (
        idPokemon    INTEGER PRIMARY KEY AUTOINCREMENT,
        nom          TEXT    NOT NULL,
        HP           INTEGER NOT NULL,
        attaque      INTEGER NOT NULL,
        defense      INTEGER NOT NULL,
        attaque_spe  INTEGER NOT NULL,
        defense_spe  INTEGER NOT NULL,
        vitesse      INTEGER NOT NULL,
        url_image    TEXT,
        idType       INTEGER NOT NULL,
        FOREIGN KEY (idType) REFERENCES type(idType) ON DELETE RESTRICT ON UPDATE CASCADE
    );

    INSERT INTO pokemon SELECT * FROM pokemon_old;
    DROP TABLE pokemon_old;

    PRAGMA foreign_keys = ON;
""")
print('  ✅ Table pokemon recréée avec FK')

# -- Table pokemon_posseder : FK complètes
print('  Recréation de la table pokemon_posseder avec FK complètes...')
cursor.executescript("""
    PRAGMA foreign_keys = OFF;

    ALTER TABLE pokemon_posseder RENAME TO pokemon_posseder_old;

    CREATE TABLE pokemon_posseder (
        id_dresseur  INTEGER NOT NULL,
        id_pokemon   INTEGER NOT NULL,
        commentaire  TEXT,
        PRIMARY KEY (id_dresseur, id_pokemon),
        FOREIGN KEY (id_dresseur) REFERENCES dresseur(idDresseur) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (id_pokemon)  REFERENCES pokemon(idPokemon)   ON DELETE CASCADE ON UPDATE CASCADE
    );

    INSERT INTO pokemon_posseder SELECT * FROM pokemon_posseder_old;
    DROP TABLE pokemon_posseder_old;

    PRAGMA foreign_keys = ON;
""")
print('  ✅ Table pokemon_posseder recréée avec FK complètes')

# -- Table dresseur : ajout d'un champ ville (optionnel, enrichissement)
# On vérifie d'abord si la colonne existe déjà
cursor.execute("PRAGMA table_info(dresseur)")
cols = [c[1] for c in cursor.fetchall()]
if 'ville' not in cols:
    cursor.execute("ALTER TABLE dresseur ADD COLUMN ville TEXT DEFAULT 'Inconnue'")
    print('  ✅ Colonne ville ajoutée à dresseur')

# ============================================================
# 5. AJOUT D'INDEX POUR LES RECHERCHES PAR NOM ET TYPE
# ============================================================
print('\n--- Ajout des index de recherche ---')
cursor.executescript("""
    CREATE INDEX IF NOT EXISTS idx_pokemon_nom    ON pokemon(nom);
    CREATE INDEX IF NOT EXISTS idx_pokemon_idType ON pokemon(idType);
    CREATE INDEX IF NOT EXISTS idx_posseder_dresseur ON pokemon_posseder(id_dresseur);
""")
print('  ✅ Index créés : idx_pokemon_nom, idx_pokemon_idType, idx_posseder_dresseur')

# ============================================================
# VALIDATION FINALE
# ============================================================
conn.commit()

print('\n=== VÉRIFICATION FINALE ===')
cursor.execute("SELECT COUNT(*) FROM pokemon")
print(f'  Pokémon : {cursor.fetchone()[0]}')
cursor.execute("SELECT COUNT(*) FROM type")
print(f'  Types : {cursor.fetchone()[0]}')
cursor.execute("SELECT COUNT(*) FROM dresseur")
print(f'  Dresseurs : {cursor.fetchone()[0]}')
cursor.execute("SELECT COUNT(*) FROM pokemon_posseder")
print(f'  Liaisons dresseur-pokemon : {cursor.fetchone()[0]}')
cursor.execute("SELECT idPokemon, nom, url_image FROM pokemon WHERE idPokemon IN (29,32)")
print(f'  Nidoran : {cursor.fetchall()}')
cursor.execute("SELECT libelle_type FROM type")
print(f'  Types : {[r[0] for r in cursor.fetchall()]}')

conn.close()
print(f'\n✅ Migration terminée. Sauvegarde disponible : {backup_path}')
