import random
import os
import pickle
from datetime import datetime
from pathlib import Path

class AgentMega:
    """Agent ultra-optimisé pour des millions de parties"""
    
    def __init__(self, nom, max_sticks=21, epsilon=0.3, alpha=0.1, epsilon_decay=0.99999):
        # Données minimales
        self.nom = nom
        self.max_sticks = max_sticks
        self.epsilon = epsilon
        self.alpha = alpha
        self.epsilon_decay = epsilon_decay
        
        # TABLE Q HYPER-OPTIMISÉE : liste plate pour accès O(1)
        self.q_table = self._init_mega_q_table()
        
        # Statistiques légères
        self.parties_jouees = 0
        self.victoires = 0
        self.dernier_etat = 0
        self.dernier_choix = 0
        
    def _init_mega_q_table(self):
        """Table Q sous forme de liste plate pour accès ultra-rapide"""
        # Structure: [valeur_q_choix1, valeur_q_choix2, valeur_q_choix3] pour chaque état
        q_table = []
        for sticks in range(self.max_sticks + 1):  # Index 0 à max_sticks
            if sticks == 0:
                q_table.extend([0.0, 0.0, 0.0])  # État 0 (fin de jeu)
            elif sticks == 1:
                q_table.extend([0.5, -1.0, -1.0])  # Seul choix 1 possible
            elif sticks == 2:
                q_table.extend([0.5, 0.5, -1.0])   # Choix 1 et 2
            else:
                q_table.extend([0.33, 0.33, 0.34]) # Choix 1, 2, 3
        return q_table
    
    def _get_q_index(self, sticks, choix):
        """Accès O(1) à la table Q"""
        return sticks * 3 + (choix - 1)
    
    def take_sticks(self, sticks_remaining):
        """Décision ultra-rapide"""
        if sticks_remaining <= 0:
            return 1
            
        # Epsilon-greedy ultra-rapide
        if random.random() < self.epsilon:
            remove = self._exploration_mega(sticks_remaining)
        else:
            remove = self._exploitation_mega(sticks_remaining)
        
        # Mémoriser pour l'apprentissage (sans historique lourd)
        self.dernier_etat = sticks_remaining
        self.dernier_choix = remove
        
        return remove
    
    def _exploration_mega(self, sticks):
        """Exploration sans overhead"""
        if sticks == 1:
            return 1
        elif sticks == 2:
            return random.choice([1, 2])
        else:
            return random.randint(1, 3)
    
    def _exploitation_mega(self, sticks):
        """Exploitation avec accès direct"""
        if sticks <= 4:
            return self._coup_optimal_mega(sticks)
        
        # Trouver le meilleur coup en O(1)
        start_idx = sticks * 3
        valeurs = self.q_table[start_idx:start_idx + 3]
        
        # Filtrer les coups valides
        coups_valides = []
        for i in range(min(3, sticks)):
            if valeurs[i] >= 0:  # -1 = coup invalide
                coups_valides.append((valeurs[i], i + 1))
        
        if coups_valides:
            return max(coups_valides)[1]
        else:
            return min(3, sticks)
    
    def _coup_optimal_mega(self, sticks):
        """Coup optimal mathématique"""
        if sticks % 4 == 0:
            return 1
        else:
            return sticks % 4
    
    def mettre_a_jour_immediate(self, recompense, next_sticks):
        """Mise à jour IMMÉDIATE sans historique"""
        if self.dernier_etat == 0:
            return
            
        idx = self._get_q_index(self.dernier_etat, self.dernier_choix)
        valeur_actuelle = self.q_table[idx]
        
        # Calcul nouvelle valeur
        if next_sticks > 0:
            next_start = next_sticks * 3
            max_next = max(self.q_table[next_start:next_start + 3])
            nouvelle_valeur = recompense + 0.9 * max_next
        else:
            nouvelle_valeur = recompense
        
        # Mise à jour
        self.q_table[idx] = (1 - self.alpha) * valeur_actuelle + self.alpha * nouvelle_valeur
        
        # Décroissance epsilon très lente
        if self.parties_jouees % 10000 == 0:
            self.epsilon *= self.epsilon_decay
            self.epsilon = max(0.001, self.epsilon)

class JeuMega:
    """Jeu ultra-rapide sans état complexe"""
    
    def __init__(self, max_sticks):
        self.sticks = max_sticks
        self.tour_joueur = random.choice([True, False])
    
    def jouer_partie_rapide(self, agent):
        """Une partie complète ultra-optimisée"""
        while self.sticks > 0:
            if self.tour_joueur:
                # Joueur aléatoire rapide
                prise = random.randint(1, min(3, self.sticks))
                self.sticks -= prise
                self.tour_joueur = False
                if self.sticks == 0:
                    return False, self.sticks  # Agent perd
            else:
                # Tour de l'agent
                prise = agent.take_sticks(self.sticks)
                prise = min(prise, self.sticks)
                self.sticks -= prise
                self.tour_joueur = True
                if self.sticks == 0:
                    return True, self.sticks  # Agent gagne
        
        return False, self.sticks

def entrainement_massif(agent, total_parties=1000000, checkpoint=100000):
    """
    Entraînement pour millions de parties
    """
    print(f"🚀 DÉMARRAGE ENTRAÎNEMENT MASSIF")
    print(f"🎯 Objectif: {total_parties:,} parties")
    print(f"💾 Checkpoint tous les {checkpoint:,} parties")
    print("=" * 50)
    
    debut = datetime.now()
    victoires = 0
    
    for partie in range(1, total_parties + 1):
        # Jeu rapide
        jeu = JeuMega(agent.max_sticks)
        victoire_agent, sticks_restants = jeu.jouer_partie_rapide(agent)
        
        # Mise à jour immédiate
        recompense = 1.0 if victoire_agent else -1.0
        agent.mettre_a_jour_immediate(recompense, sticks_restants)
        
        # Statistiques
        agent.parties_jouees += 1
        if victoire_agent:
            victoires += 1
            agent.victoires += 1
        
        # Affichage progression
        if partie % checkpoint == 0:
            taux_victoire = (victoires / partie) * 100
            temps_ecoule = (datetime.now() - debut).total_seconds()
            vitesse = partie / temps_ecoule if temps_ecoule > 0 else 0
            
            print(f"📊 {partie:,} parties - "
                  f"Victoires: {victoires:,} ({taux_victoire:.2f}%) - "
                  f"ε={agent.epsilon:.4f} - "
                  f"{vitesse:.1f} parties/sec")
    
    # Résultats finaux
    duree_totale = (datetime.now() - debut).total_seconds()
    vitesse_moyenne = total_parties / duree_totale
    
    print("=" * 50)
    print(f"🎉 ENTRAÎNEMENT TERMINÉ!")
    print(f"⏱️  Durée: {duree_totale:.1f} secondes")
    print(f"⚡ Vitesse moyenne: {vitesse_moyenne:.1f} parties/seconde")
    print(f"📈 Taux de victoire final: {(victoires/total_parties)*100:.2f}%")
    print(f"🎯 Epsilon final: {agent.epsilon:.5f}")
    
    return agent

def sauvegarder_agent_mega(agent, dossier="agents_mega"):
    """Sauvegarde ultra-rapide"""
    Path(dossier).mkdir(exist_ok=True)
    filename = Path(dossier) / f"mega_{agent.nom}_{agent.parties_jouees}.pkl"
    
    with open(filename, 'wb') as f:
        pickle.dump(agent, f)
    
    return filename

def charger_agent_mega(nom_agent, dossier="agents_mega"):
    """Chargement d'agent existant"""
    dossier_path = Path(dossier)
    if not dossier_path.exists():
        return None
    
    # Trouver le fichier le plus récent
    fichiers = list(dossier_path.glob(f"mega_{nom_agent}_*.pkl"))
    if not fichiers:
        return None
    
    fichier_recent = max(fichiers, key=lambda x: x.stat().st_mtime)
    
    with open(fichier_recent, 'rb') as f:
        return pickle.load(f)

# =============================================================================
# MODES D'ENTRAÎNEMENT POUR MILLIONS DE PARTIES
# =============================================================================

def mode_1_million():
    """Mode 1 million de parties"""
    print("🔰 MODE 1 MILLION DE PARTIES")
    agent = AgentMega("millionnaire", max_sticks=21)
    return entrainement_massif(agent, 1000000, 100000)

def mode_5_millions():
    """Mode 5 millions de parties"""
    print("🔥 MODE 5 MILLIONS DE PARTIES")
    agent = AgentMega("expert", max_sticks=21, epsilon_decay=0.999995)
    return entrainement_massif(agent, 5000000, 500000)

def mode_10_millions():
    """Mode 10 millions de parties"""
    print("🚀 MODE 10 MILLIONS DE PARTIES")
    agent = AgentMega("maitre", max_sticks=21, epsilon_decay=0.999999)
    return entrainement_massif(agent, 10000000, 1000000)

def mode_personnalise():
    """Mode personnalisé"""
    print("🎛️  MODE PERSONNALISÉ")
    
    try:
        parties = int(input("Nombre de parties (ex: 5000000): ") or "1000000")
        nom = input("Nom de l'agent: ") or "custom"
        max_sticks = int(input("Bâtons initiaux (21): ") or "21")
        
        agent = AgentMega(nom, max_sticks=max_sticks)
        checkpoint = max(parties // 10, 10000)
        
        return entrainement_massif(agent, parties, checkpoint)
    
    except ValueError:
        print("❌ Valeur invalide")
        return None

def afficher_menu_mega():
    """Menu pour entraînement massif"""
    print("\n" + "="*60)
    print("🤖 NIM - MODE ENTRAÎNEMENT MASSIF")
    print("="*60)
    print("1. 1 million de parties")
    print("2. 5 millions de parties") 
    print("3. 10 millions de parties")
    print("4. Mode personnalisé")
    print("5. Charger agent existant")
    print("6. Quitter")
    print("="*60)

def main_mega():
    """Programme principal pour entraînement massif"""
    os.system('clear')
    
    print("🎯 SYSTÈME NIM - ENTRAÎNEMENT MASSIF")
    print("   Optimisé pour millions de parties sur Raspberry Pi")
    print("   Vitesse estimée: 1,000-10,000 parties/seconde")
    
    agent_actuel = None
    
    while True:
        afficher_menu_mega()
        choix = input("Votre choix (1-6): ").strip()
        
        if choix == "1":
            agent_actuel = mode_1_million()
            if agent_actuel:
                sauvegarder_agent_mega(agent_actuel)
        
        elif choix == "2":
            agent_actuel = mode_5_millions()
            if agent_actuel:
                sauvegarder_agent_mega(agent_actuel)
        
        elif choix == "3":
            agent_actuel = mode_10_millions()
            if agent_actuel:
                sauvegarder_agent_mega(agent_actuel)
        
        elif choix == "4":
            agent_actuel = mode_personnalise()
            if agent_actuel:
                sauvegarder_agent_mega(agent_actuel)
        
        elif choix == "5":
            nom = input("Nom de l'agent à charger: ").strip()
            agent_actuel = charger_agent_mega(nom)
            if agent_actuel:
                print(f"✅ Agent '{agent_actuel.nom}' chargé")
                print(f"   Parties: {agent_actuel.parties_jouees:,}")
                print(f"   Victoires: {agent_actuel.victoires:,}")
            else:
                print("❌ Agent non trouvé")
        
        elif choix == "6":
            if agent_actuel:
                sauvegarder_agent_mega(agent_actuel)
            print("👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")

# =============================================================================
# SCRIPT DE TEST DE PERFORMANCE
# =============================================================================

def test_performance_extreme():
    """Test de performance pour voir la vitesse maximale"""
    print("🧪 TEST DE PERFORMANCE EXTRÊME")
    print("Lancement de 100,000 parties pour benchmark...")
    
    agent_test = AgentMega("test_perf")
    debut = datetime.now()
    
    victoires = 0
    for i in range(100000):
        jeu = JeuMega(21)
        victoire, _ = jeu.jouer_partie_rapide(agent_test)
        if victoire:
            victoires += 1
        
        # Mise à jour très occasionnelle
        if i % 1000 == 0:
            agent_test.epsilon *= 0.999
    
    duree = (datetime.now() - debut).total_seconds()
    vitesse = 100000 / duree
    
    print(f"✅ 100,000 parties en {duree:.2f} secondes")
    print(f"⚡ Vitesse: {vitesse:.0f} parties/seconde")
    print(f"📊 Victoires: {victoires} ({victoires/1000:.1f}%)")
    
    # Estimation pour plus de parties
    print(f"📈 Estimation 1M parties: {1000000/vitesse/60:.1f} minutes")
    print(f"📈 Estimation 10M parties: {10000000/vitesse/3600:.1f} heures")

if __name__ == '__main__':
    try:
        print("🤖 NIM - ENTRAÎNEMENT MASSIF")
        print("1. Menu principal")
        print("2. Test de performance (100,000 parties)")
        
        choix = input("Choix: ").strip()
        
        if choix == "2":
            test_performance_extreme()
        else:
            main_mega()
            
    except KeyboardInterrupt:
        print("\n🛑 Interrompu")
    except Exception as e:
        print(f"❌ Erreur: {e}")