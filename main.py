import random
import numpy as np
import csv
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path

class AgentManager:
    """Gestionnaire pour stocker et charger plusieurs agents"""
    
    def __init__(self, dossier_agents="agents_sauvegardes"):
        self.dossier_agents = Path(dossier_agents)
        self.dossier_agents.mkdir(exist_ok=True)
    
    def sauvegarder_agent(self, agent):
        """Sauvegarde un agent avec son nom"""
        filename = self.dossier_agents / f"agent_{agent.nom}.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(agent, f)
        return filename
    
    def charger_agent(self, nom_agent):
        """Charge un agent par son nom"""
        filename = self.dossier_agents / f"agent_{nom_agent}.pkl"
        try:
            with open(filename, 'rb') as f:
                agent = pickle.load(f)
            return agent
        except FileNotFoundError:
            return None
    
    def lister_agents(self):
        """Liste tous les agents disponibles"""
        agents = []
        for fichier in self.dossier_agents.glob("agent_*.pkl"):
            nom_agent = fichier.stem.replace("agent_", "")
            try:
                with open(fichier, 'rb') as f:
                    agent = pickle.load(f)
                    agents.append({
                        'nom': nom_agent,
                        'parties_jouees': agent.parties_jouees,
                        'score': agent.score,
                        'date_creation': agent.date_creation,
                        'derniere_maj': agent.derniere_maj
                    })
            except:
                continue
        return agents
    
    def supprimer_agent(self, nom_agent):
        """Supprime un agent"""
        filename = self.dossier_agents / f"agent_{nom_agent}.pkl"
        if filename.exists():
            filename.unlink()
            return True
        return False


class Agent:
    def __init__(self, nom, score, max_sticks, epsilon=0.3, alpha=0.1, epsilon_decay=0.995):
        self.nom = nom
        self.score = score
        self.max_sticks = max_sticks
        self.epsilon = epsilon
        self.alpha = alpha
        self.epsilon_decay = epsilon_decay
        self.dictionnaire = self.create_a_dictionnary()
        self.choices = []
        self.positions_gagnantes = set(range(1, max_sticks+1, 4))
        self.historique_apprentissage = []
        self.parties_jouees = 0
        self.date_creation = datetime.now()
        self.derniere_maj = datetime.now()

    def create_a_dictionnary(self):
        training_pots = {}
        for i in range(1, self.max_sticks + 1):
            if i == 1:
                training_pots[i] = {'choix': [1], 'valeurs': [0.5], 'visites': [0]}
            elif i == 2:
                training_pots[i] = {'choix': [1, 2], 'valeurs': [0.5, 0.5], 'visites': [0, 0]}
            else:
                training_pots[i] = {'choix': [1, 2, 3], 'valeurs': [0.33, 0.33, 0.34], 'visites': [0, 0, 0]}
        return training_pots

    def take_sticks(self, sticks_remaining):
        if random.random() < self.epsilon:
            remove = self.exploration(sticks_remaining)
        else:
            remove = self.exploitation(sticks_remaining)
        
        if sticks_remaining in self.dictionnaire:
            index = self.dictionnaire[sticks_remaining]['choix'].index(remove)
            self.dictionnaire[sticks_remaining]['visites'][index] += 1
        
        print(f'Bâtons restants : {sticks_remaining}')  
        print(f'L\'agent {self.nom} a pris {remove} bâton(s).')
        self.choices.append((sticks_remaining, remove))
        return remove
    
    def exploration(self, sticks_remaining):
        if sticks_remaining == 1:
            return 1
        elif sticks_remaining == 2:
            return random.choice([1, 2])
        else:
            return random.choice([1, 2, 3])
        
    def exploitation(self, sticks_remaining):
        if sticks_remaining <= 4 or sticks_remaining in self.positions_gagnantes:
            return self.strategie_zone_critique(sticks_remaining)
        if sticks_remaining in self.dictionnaire:
            valeurs = self.dictionnaire[sticks_remaining]['valeurs']
            choix = self.dictionnaire[sticks_remaining]['choix']
            
            meilleur_index = np.argmax(valeurs)
            return choix[meilleur_index]
        else:
            return 1
    
    def strategie_zone_critique(self, sticks_remaining):
        if sticks_remaining % 4 == 0:
            return 1
        else:
            return sticks_remaining % 4
    
    def mettre_a_jour_valeurs(self, recompense):
        for i in range(len(self.choices)-1, -1, -1):
            state, action = self.choices[i]
            
            if state in self.dictionnaire:
                index = self.dictionnaire[state]['choix'].index(action)
                valeur_actuelle = self.dictionnaire[state]['valeurs'][index]
                
                if i == len(self.choices) - 1:
                    nouvelle_valeur = recompense
                else:
                    next_state, _ = self.choices[i+1]
                    if next_state in self.dictionnaire:
                        max_next_value = max(self.dictionnaire[next_state]['valeurs'])   
                        nouvelle_valeur = recompense + 0.9 * max_next_value
                    else:
                        nouvelle_valeur = recompense
                
                self.dictionnaire[state]['valeurs'][index] = (1 - self.alpha) * valeur_actuelle + self.alpha * nouvelle_valeur
    
    def mettre_a_jour_strategie(self, victoire, sticks_initiaux):
        recompense = 1.0 if victoire else -1.0
        self.mettre_a_jour_valeurs(recompense)
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(0.05, self.epsilon)
        self.parties_jouees += 1
        self.derniere_maj = datetime.now()
        
        self.historique_apprentissage.append({
            'partie': self.parties_jouees,
            'victoire': victoire,
            'sticks_initiaux': sticks_initiaux,
            'epsilon': self.epsilon,
            'strategie_utilisee': self.choices.copy()
        })
    
    def analyser_performance(self):
        if not self.historique_apprentissage:
            return "Aucune donnée d'apprentissage"
        
        victoires = sum(1 for app in self.historique_apprentissage if app['victoire'])
        taux_victoire = victoires / len(self.historique_apprentissage) * 100
        
        coups_critiques = 0
        coups_critiques_corrects = 0
        
        for app in self.historique_apprentissage:
            for state, action in app['strategie_utilisee']:
                if state <= 6:
                    coups_critiques += 1
                    if self.est_coup_optimal(state, action):
                        coups_critiques_corrects += 1
        
        taux_precision_critique = (coups_critiques_corrects / coups_critiques * 100) if coups_critiques > 0 else 0
        
        return (f"=== STATISTIQUES DE {self.nom.upper()} ===\n"
                f"Taux de victoire: {taux_victoire:.1f}% sur {len(self.historique_apprentissage)} parties\n"
                f"Précision zone critique: {taux_precision_critique:.1f}%\n"
                f"Epsilon actuel: {self.epsilon:.3f}\n"
                f"Parties totales: {self.parties_jouees}\n"
                f"Créé le: {self.date_creation.strftime('%Y-%m-%d %H:%M')}\n"
                f"Dernière mise à jour: {self.derniere_maj.strftime('%Y-%m-%d %H:%M')}")
        
    def est_coup_optimal(self, state, action):
        if state % 4 == 0:
            return action == 1
        else:
            return action == (state % 4)
    
    def get_dictionnaire_complet(self):
        return self.dictionnaire
    
    def save_dictionnaire_to_csv(self, filename=None):
        if filename is None:
            filename = f"agent_{self.nom}_dictionnaire.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Etat', 'Choix', 'Valeur Q', 'Visites'])
            for etat, donnees in sorted(self.dictionnaire.items()):
                for i, choix in enumerate(donnees['choix']):
                    writer.writerow([etat, choix, donnees['valeurs'][i], donnees['visites'][i]])


class Joueur:
    def __init__(self, nom, score):
        self.nom = nom
        self.score = score

    def taking_sticks(self, sticks_remaining):
        print(f'Bâtons restants : {sticks_remaining}')
        print('C\'est à votre tour de jouer.')
        
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
    def __init__(self, nombre_sticks_init):
        self.nombre_sticks = nombre_sticks_init
        self.joueur_turn = True
        self.historique = []

    def check_state(self):
        return self.nombre_sticks > 0

    def check_winner(self):
        if self.nombre_sticks == 0:
            dernier_joueur, _, _ = self.historique[-1]
            if dernier_joueur == "joueur":
                print('Bâtons restants : 0')
                print('Le joueur a pris le dernier bâton. Le joueur a gagné !')
                return "joueur"
            else:
                print('Bâtons restants : 0')
                print('L\'agent a pris le dernier bâton. L\'agent a gagné !')
                return "agent"
        return None

    def whos_begins(self):
        begins = random.choice(['joueur', 'agent'])
        self.joueur_turn = begins == 'joueur'
        print(f'{begins.capitalize()} commence.')
        return begins
    
    def jouer_tour(self, joueur, agent):
        if self.joueur_turn:
            remove = joueur.taking_sticks(self.nombre_sticks)
            self.nombre_sticks -= remove
            self.historique.append(('joueur', remove, self.nombre_sticks))
            self.joueur_turn = False
        else:
            remove = agent.take_sticks(self.nombre_sticks)
            self.nombre_sticks -= remove
            self.historique.append(('agent', remove, self.nombre_sticks))
            self.joueur_turn = True
        
        return self.check_winner()


def afficher_banniere():
    """Affiche une bannière stylisée"""
    print("\033[95m" + "="*65)
    print("\033[96m" + r"""
    ███╗   ██╗██╗███╗   ███╗     ██████╗  █████╗ ███╗   ███╗███████╗
    ████╗  ██║██║████╗ ████║    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝
    ██╔██╗ ██║██║██╔████╔██║    ██║  ███╗███████║██╔████╔██║█████╗  
    ██║╚██╗██║██║██║╚██╔╝██║    ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  
    ██║ ╚████║██║██║ ╚═╝ ██║    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
    ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

    """)
    print("\033[95m" + "="*65)
    print("\033[93m" + "     SYSTÈME D'APPRENTISSAGE PAR RENFORCEMENT")
    print("\033[95m" + "="*65 + "\033[0m")


def afficher_menu_principal():
    print("\n" + "\033[94m" + "="*50)
    print("🎮 MENU PRINCIPAL")
    print("="*50 + "\033[0m")
    print("\033[92m1.\033[0m Gérer les agents")
    print("\033[92m2.\033[0m Entraîner un agent")
    print("\033[92m3.\033[0m Tester un agent")
    print("\033[92m4.\033[0m Afficher les statistiques")
    print("\033[92m5.\033[0m Quitter")
    print("\033[94m" + "="*50 + "\033[0m")


def afficher_menu_agents():
    print("\n" + "\033[94m" + "="*50)
    print("🤖 GESTION DES AGENTS")
    print("="*50 + "\033[0m")
    print("\033[92m1.\033[0m Créer un nouvel agent")
    print("\033[92m2.\033[0m Lister les agents existants")
    print("\033[92m3.\033[0m Charger un agent")
    print("\033[92m4.\033[0m Supprimer un agent")
    print("\033[92m5.\033[0m Retour au menu principal")
    print("\033[94m" + "="*50 + "\033[0m")


def afficher_entete_section(titre):
    print("\n" + "\033[95m" + "═" * 60)
    print(f" {titre}")
    print("═" * 60 + "\033[0m")


def entrainer_agent(agent, nombre_parties):
    """Fonction pour entraîner l'agent avec un nombre spécifique de parties"""
    joueur = Joueur(nom="Player", score=0)
    parties = []
    
    afficher_entete_section(f"ENTRAÎNEMENT DE L'AGENT {agent.nom}")
    
    for partie in range(nombre_parties):  
        print(f"\n\033[93m=== Partie {partie + 1} ===\033[0m")
        jeu = Jeu(agent.max_sticks)
        
        premier_joueur = jeu.whos_begins()
        
        while jeu.check_state():
            gagnant = jeu.jouer_tour(joueur, agent)
            
            if gagnant:
                if gagnant == "agent":
                    agent.score += 1
                    agent.mettre_a_jour_strategie(True, agent.max_sticks)
                else:
                    joueur.score += 1
                    agent.mettre_a_jour_strategie(False, agent.max_sticks)
                
                parties.append({
                    'bâtons_initiaux': agent.max_sticks,
                    'premier_joueur': premier_joueur,
                    'gagnant': gagnant,
                    'historique': jeu.historique,
                    'score_agent': agent.score,
                    'score_joueur': joueur.score
                })
                
                print(f'\033[94mScore - {agent.nom}: {agent.score}, Joueur: {joueur.score}\033[0m')
                break
        
        agent.choices = []
    
    return parties


def sauvegarder_statistiques(parties, nom_agent, nom_fichier=None):
    if nom_fichier is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"statistiques_{nom_agent}_{timestamp}.csv"
    
    with open(nom_fichier, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Partie', 'Bâtons initiaux', 'Premier joueur', 'Gagnant', 'Nombre de tours', 'Coups joués'])
        
        for i, partie in enumerate(parties, 1):
            gagnant = partie['gagnant']
            premier = partie['premier_joueur']
            tours = len(partie['historique'])
            coups = "; ".join([f"{joueur}:{prise}(→{reste})" for joueur, prise, reste in partie['historique']])
            
            writer.writerow([i, partie['bâtons_initiaux'], premier, gagnant, tours, coups])
    
    return nom_fichier


def main():
    agent_manager = AgentManager()
    agent_actuel = None
    
    # Effacer l'écran et afficher la bannière
    os.system('cls' if os.name == 'nt' else 'clear')
    afficher_banniere()
    
    while True:
        afficher_menu_principal()
        choix = input("\033[92mVotre choix (1-5): \033[0m").strip()
        
        if choix == "1":
            # Gestion des agents
            while True:
                afficher_menu_agents()
                choix_agent = input("\033[92mVotre choix (1-5): \033[0m").strip()
                
                if choix_agent == "1":
                    # Créer un nouvel agent
                    afficher_entete_section("CRÉATION D'UN NOUVEL AGENT")
                    nom_agent = input("Nom du nouvel agent: ").strip()
                    if not nom_agent:
                        print("\033[91mLe nom ne peut pas être vide.\033[0m")
                        continue
                    
                    try:
                        nombre_sticks = int(input("Nombre de bâtons initiaux: "))
                    except ValueError:
                        print("\033[91mNombre invalide.\033[0m")
                        continue
                    
                    nouvel_agent = Agent(
                        nom=nom_agent, 
                        score=0, 
                        max_sticks=nombre_sticks,
                        epsilon=0.3,
                        alpha=0.1,
                        epsilon_decay=0.995
                    )
                    
                    agent_manager.sauvegarder_agent(nouvel_agent)
                    agent_actuel = nouvel_agent
                    print(f"\033[92mAgent '{nom_agent}' créé et sauvegardé avec succès!\033[0m")
                    break
                
                elif choix_agent == "2":
                    # Lister les agents
                    afficher_entete_section("LISTE DES AGENTS")
                    agents = agent_manager.lister_agents()
                    if not agents:
                        print("\033[93mAucun agent trouvé.\033[0m")
                    else:
                        for i, agent_info in enumerate(agents, 1):
                            print(f"\033[94m{i}. {agent_info['nom']} - {agent_info['parties_jouees']} parties - "
                                  f"Créé le {agent_info['date_creation'].strftime('%Y-%m-%d')}\033[0m")
                
                elif choix_agent == "3":
                    # Charger un agent
                    afficher_entete_section("CHARGEMENT D'AGENT")
                    nom_agent = input("Nom de l'agent à charger: ").strip()
                    agent_charge = agent_manager.charger_agent(nom_agent)
                    if agent_charge:
                        agent_actuel = agent_charge
                        print(f"\033[92mAgent '{nom_agent}' chargé avec succès!\033[0m")
                        break
                    else:
                        print(f"\033[91mAgent '{nom_agent}' non trouvé.\033[0m")
                
                elif choix_agent == "4":
                    # Supprimer un agent
                    afficher_entete_section("SUPPRESSION D'AGENT")
                    nom_agent = input("Nom de l'agent à supprimer: ").strip()
                    if agent_manager.supprimer_agent(nom_agent):
                        print(f"\033[92mAgent '{nom_agent}' supprimé avec succès!\033[0m")
                        if agent_actuel and agent_actuel.nom == nom_agent:
                            agent_actuel = None
                    else:
                        print(f"\033[91mAgent '{nom_agent}' non trouvé.\033[0m")
                
                elif choix_agent == "5":
                    break
                else:
                    print("\033[91mChoix invalide.\033[0m")
        
        elif choix == "2":
            # Entraîner un agent
            if agent_actuel is None:
                print("\033[91mAucun agent sélectionné. Veuillez d'abord créer ou charger un agent.\033[0m")
                continue
            
            try:
                nombre_parties = int(input("Nombre de parties d'entraînement: "))
                parties = entrainer_agent(agent_actuel, nombre_parties)
                
                print(f'\n\033[92mSession d\'entraînement de {agent_actuel.nom} terminée!\033[0m')
                print(agent_actuel.analyser_performance())
                
                # Sauvegarder l'agent après l'entraînement
                agent_manager.sauvegarder_agent(agent_actuel)
                
                # Sauvegarder les statistiques
                nom_fichier = sauvegarder_statistiques(parties, agent_actuel.nom)
                print(f"\033[94mStatistiques sauvegardées dans '{nom_fichier}'\033[0m")
                
            except ValueError:
                print("\033[91mVeuillez entrer un nombre valide.\033[0m")
        
        elif choix == "3":
            # Tester un agent
            if agent_actuel is None:
                print("\033[91mAucun agent sélectionné. Veuillez d'abord créer ou charger un agent.\033[0m")
                continue
            
            try:
                nombre_parties = int(input("Nombre de parties de test (sans apprentissage): "))
                ancien_epsilon = agent_actuel.epsilon
                agent_actuel.epsilon = 0  # Pas d'exploration, seulement exploitation
                
                parties = entrainer_agent(agent_actuel, nombre_parties)
                
                # Restaurer l'epsilon
                agent_actuel.epsilon = ancien_epsilon
                
                print(f'\n\033[92mSession de test de {agent_actuel.nom} terminée!\033[0m')
                victoires_test = sum(1 for p in parties if p['gagnant'] == 'agent')
                print(f"\033[94mRésultats du test: {victoires_test}/{nombre_parties} victoires "
                      f"({victoires_test/nombre_parties*100:.1f}%)\033[0m")
                
            except ValueError:
                print("\033[91mVeuillez entrer un nombre valide.\033[0m")
        
        elif choix == "4":
            # Afficher les statistiques
            if agent_actuel is None:
                print("\033[91mAucun agent sélectionné. Veuillez d'abord créer ou charger un agent.\033[0m")
                continue
            
            afficher_entete_section(f"STATISTIQUES DE {agent_actuel.nom.upper()}")
            print(agent_actuel.analyser_performance())
        
        elif choix == "5":
            # Sauvegarder avant de quitter
            if agent_actuel:
                agent_manager.sauvegarder_agent(agent_actuel)
            print("\033[92mMerci d'avoir utilisé le système d'apprentissage! Au revoir! 👋\033[0m")
            break
        
        else:
            print("\033[91mChoix invalide. Veuillez choisir entre 1 et 5.\033[0m")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[93mProgramme interrompu. Au revoir! 👋\033[0m")
    except Exception as e:
        print(f"\033[91mUne erreur est survenue: {e}\033[0m")