"""Module principal du jeu Nim.

Ce module contient les classes Agent, Joueur et Jeu ainsi que les
fonctions utilitaires pour sauvegarder les statistiques.

Les commentaires dans ce fichier sont écrits en français pour un usage
éducatif (étudiants).
"""

import random
import numpy as np
import csv
import os
from datetime import datetime


class Agent:
    """Agent qui joue au jeu et apprend via un dictionnaire simple.

    Le dictionnaire associe à chaque état (nombre de bâtons restants)
    une liste de choix possible (1,2,3) pondérés par répétition.
    """

    def __init__(self, nom, score, max_sticks):
        # Nom de l'agent (ex: "AI")
        self.nom = nom
        # Score accumulé lors des parties d'entraînement
        self.score = score
        # Nombre maximum de bâtons initial (utilisé pour construire le dictionnaire)
        self.max_sticks = max_sticks
        # Dictionnaire d'apprentissage : pour chaque état (n bâtons restants)
        # on conserve une liste de choix (1,2,3) pondérés
        self.dictionnaire = self.create_a_dictionnary()
        # Liste temporaire des choix effectués pendant une partie
        self.choices = []

    def create_a_dictionnary(self):
        # Initialise le dictionnaire d'entraînement avec des choix équilibrés
        training_pots = {}
        for i in range(1, self.max_sticks + 1):
            # Pour 1 bâton possible, l'agent ne peut prendre que 1
            if i == 1:
                training_pots[i] = np.tile([1], self.max_sticks).tolist()
            # Pour 2 bâtons possibles, on autorise 1 ou 2
            elif i == 2:
                training_pots[i] = np.tile([1, 2], self.max_sticks).tolist()
            # Sinon, on autorise 1, 2 ou 3 (valeurs initiales en apprentissage)
            else:
                training_pots[i] = np.tile([1, 2, 3], self.max_sticks).tolist()
        return training_pots

    def take_sticks(self, sticks_remaining):
        # Choisit un nombre de bâtons à prendre en se basant sur le dictionnaire
        if sticks_remaining in self.dictionnaire and len(self.dictionnaire[sticks_remaining]) > 0:
            list_state = self.dictionnaire[sticks_remaining]
            remove = random.choice(list_state)

            # Si le choix est invalide (par ex. 3 alors qu'il ne reste que 2)
            # on l'enlève du dictionnaire pour éviter de le recréer trop souvent
            if remove > sticks_remaining:
                self.dictionnaire[sticks_remaining].remove(remove)
                # Réessayer si d'autres choix restent
                if len(self.dictionnaire[sticks_remaining]) > 0:
                    return self.take_sticks(sticks_remaining)
                else:
                    # Valeur de repli
                    remove = 1

            # Affichage d'état (utile pour debug / console)
            print(f'Bâtons restants : {sticks_remaining}')
            print(f'L\'agent a pris {remove} bâton(s).')
            # Mémoriser le choix pour récompense/pénalité après la partie
            self.choices.append((sticks_remaining, remove))
            return remove
        else:
            # Si aucun enregistrement, prendre 1 par défaut
            remove = 1
            print(f'Bâtons restants : {sticks_remaining}')
            print(f'L\'agent a pris {remove} bâton(s).')
            self.choices.append((sticks_remaining, remove))
            return remove

    def update_dictionnary(self, choice):
        # Permet d'ajouter un choix au dictionnaire pour l'état courant
        if hasattr(self, 'sticks_remaining') and self.sticks_remaining in self.dictionnaire:
            self.dictionnaire[self.sticks_remaining].append(choice)

    def get_dictionnaire_complet(self):
        return self.dictionnaire

    def save_dictionnaire_to_csv(self, filename="agent_dictionnaire.csv"):
        # Sauvegarde le dictionnaire de l'agent au format CSV
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Etat (bâtons restants)', 'Choix disponibles'])
            for etat, choix in sorted(self.dictionnaire.items()):
                writer.writerow([etat, choix])


class Joueur:
    """Représente le joueur humain (ici simulé via des choix aléatoires).

    Le comportement peut être remplacé par une saisie utilisateur si besoin.
    """

    def __init__(self, nom, score):
        # Représente le joueur humain (ou un joueur simulé)
        self.nom = nom
        self.score = score

    def taking_sticks(self, sticks_remaining):
        # Interaction console: affiche l'état et simule un choix aléatoire
        print(f'Bâtons restants : {sticks_remaining}')
        print('C\'est à votre tour de jouer.')

        # Règles : on ne peut pas prendre plus de bâtons qu'il n'en reste
        if sticks_remaining == 1:
            remove = 1
            print('Vous devez prendre 1 bâton.')
        elif sticks_remaining == 2:
            remove = random.choice([1, 2])
            print(f'Vous pouvez prendre 1 ou 2 bâtons, vous avez pris {remove}.')
        else:
            remove = random.choice([1, 2, 3])
            print(f'Vous pouvez prendre 1, 2 ou 3 bâtons, vous avez pris {remove}.')

        print('Le joueur a pris', remove, 'bâton(s).')
        return remove


class Jeu:
    """Classe représentant une partie de Nim simple."""

    def __init__(self, nombre_sticks_init):
        # État courant du jeu : nombre de bâtons restants
        self.nombre_sticks = nombre_sticks_init
        # Booléen indiquant si c'est au tour du joueur humain
        self.joueur_turn = True
        # Historique des coups pour la sauvegarde des statistiques
        self.historique = []

    def check_state(self):
        # Retourne True si la partie n'est pas terminée
        return self.nombre_sticks > 0

    def check_winner(self, player_took_last):
        # Si aucun bâton ne reste, déterminer le gagnant
        if self.nombre_sticks == 0:
            if player_took_last:
                print('Bâtons restants : 0')
                print('L\'agent a gagné !')
                return "agent"
            else:
                print('Le joueur a gagné !')
                return "joueur"
        return None

    def whos_begins(self):
        # Choix aléatoire du premier joueur
        begins = random.choice(['joueur', 'agent'])
        self.joueur_turn = begins == 'joueur'
        print(f'{begins.capitalize()} commence.')
        return begins

    def jouer_tour(self, joueur, agent):
        # Effectue un tour en appelant la méthode appropriée selon le joueur
        if self.joueur_turn:
            remove = joueur.taking_sticks(self.nombre_sticks)
            self.nombre_sticks -= remove
            # Ajouter l'événement à l'historique : (qui, prise, reste)
            self.historique.append(('joueur', remove, self.nombre_sticks))
            self.joueur_turn = False
            return remove
        else:
            remove = agent.take_sticks(self.nombre_sticks)
            self.nombre_sticks -= remove
            self.historique.append(('agent', remove, self.nombre_sticks))
            self.joueur_turn = True
            return remove


def sauvegarder_statistiques(parties, nom_fichier="statistiques_jeu.csv"):
    # Écrit les statistiques de toutes les parties dans un CSV
    with open(nom_fichier, 'w', newline='',encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Partie', 'Bâtons initiaux', 'Premier joueur', 'Gagnant', 'Nombre de tours', 'Coups joués'])

        for i, partie in enumerate(parties, 1):
            gagnant = partie['gagnant']
            premier = partie['premier_joueur']
            tours = len(partie['historique'])
            # Format lisible des coups : joueur:prise(→reste)
            coups = "; ".join([f"{joueur}:{prise}(→{reste})" for joueur, prise, reste in partie['historique']])

            writer.writerow([i, partie['bâtons_initiaux'], premier, gagnant, tours, coups])


if __name__ == "__main__":
    # Demander les paramètres à l'utilisateur
    try:
        nombre_sticks_init = int(input("Nombre de bâtons initiaux: "))
        nombre_parties = int(input("Nombre de parties à jouer: "))
    except ValueError:
        print("Veuillez entrer des nombres valides.")
        exit(1)

    agent = Agent(nom="AI", score=0, max_sticks=nombre_sticks_init)
    joueur = Joueur(nom="Player", score=0)

    parties = []

    for partie in range(nombre_parties):
        print(f"\n=== Partie {partie + 1} ===")
        jeu = Jeu(nombre_sticks_init)

        premier_joueur = jeu.whos_begins()

        while jeu.check_state():
            remove = jeu.jouer_tour(joueur, agent)

            # Vérification de l'état et du gagnant après chaque tour
            gagnant = jeu.check_winner(not jeu.joueur_turn)
            if gagnant:
                if gagnant == "agent":
                    agent.score += 1
                    # Renforcer les bons choix de l'agent
                    for choice in agent.choices:
                        index = choice[0]
                        value = choice[1]
                        if index in agent.dictionnaire:
                            agent.dictionnaire[index].extend([value] * 2)
                else:
                    joueur.score += 1
                    # Pénaliser les mauvais choix de l'agent
                    for choice in agent.choices:
                        index = choice[0]
                        value = choice[1]
                        if index in agent.dictionnaire and value in agent.dictionnaire[index]:
                            agent.dictionnaire[index].remove(value)

                # Enregistrer les données de la partie
                parties.append({
                    'bâtons_initiaux': nombre_sticks_init,
                    'premier_joueur': premier_joueur,
                    'gagnant': gagnant,
                    'historique': jeu.historique,
                    'score_agent': agent.score,
                    'score_joueur': joueur.score
                })

                print(f'Score - Agent: {agent.score}, Joueur: {joueur.score}')
                break

        # Réinitialiser les choix de l'agent pour la prochaine partie
        agent.choices = []

    print(f'\nScore final - Agent: {agent.score}, Joueur: {joueur.score}')
    print(f"Entraînement terminé après {nombre_parties} parties.")

    # Sauvegarder les statistiques
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"statistiques_jeu_{timestamp}.csv"
    sauvegarder_statistiques(parties, filename)
    print(f"Statistiques sauvegardées dans '{filename}'")

    # Sauvegarder le dictionnaire de l'agent
    agent_dictionnaire_file = f"agent_dictionnaire_{timestamp}.csv"
    agent.save_dictionnaire_to_csv(agent_dictionnaire_file)
    print(f"Dictionnaire de l'agent sauvegardé dans '{agent_dictionnaire_file}'")