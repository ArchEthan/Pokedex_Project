# combat.py
import random

class Personnage:
    def __init__(self, nom, pv, attaque, esquive=0.05):
        """
        esquive: probabilité de esquiver une attaque (0.05 = 5%)
        """
        self.nom = nom
        self.pv = pv
        self.attaque = attaque
        self.esquive = esquive

    def frapper(self, autre):
        if random.random() < autre.esquive:  # l'autre peut esquiver
            return f"{autre.nom} a esquivé !"
        else:
            autre.pv -= self.attaque
            if autre.pv < 0:
                autre.pv = 0
            return f"{self.nom} inflige {self.attaque} à {autre.nom} (PV restants: {autre.pv})"

    def est_vivant(self):
        return self.pv > 0

def combat_tour_par_tour(perso1, perso2):
    tour = 1
    log = []
    while perso1.est_vivant() and perso2.est_vivant():
        if tour % 2 == 1:
            log.append(perso1.frapper(perso2))
        else:
            log.append(perso2.frapper(perso1))
        tour += 1
    gagnant = perso1 if perso1.est_vivant() else perso2
    return gagnant, log
