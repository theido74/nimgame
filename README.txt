# Nim Game - Système d'Apprentissage par Renforcement

Ce projet propose une implémentation du jeu de Nim avec un agent capable d'apprendre à jouer grâce à l'apprentissage par renforcement (Q-learning). L'utilisateur peut créer, entraîner, tester et gérer plusieurs agents.

## Fonctionnalités

- **Gestion des agents** : création, sauvegarde, chargement, suppression.
- **Entraînement** : l'agent joue contre un joueur simulé et améliore sa stratégie.
- **Test** : évalue la performance de l'agent sans apprentissage.
- **Statistiques** : taux de victoire, précision en zone critique, historique d'apprentissage.
- **Interface console** : menus interactifs et affichage coloré.

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/nim_game.git
   cd nim_game/nim_game_done
   ```
2. Installez les dépendances :
   ```bash
   pip install numpy
   ```

## Utilisation

Lancez le programme principal :
```bash
python main.py
```

Suivez les instructions à l'écran pour :
- Créer ou charger un agent
- L'entraîner sur un nombre de parties
- Tester ses performances
- Consulter ses statistiques

## Structure du projet

- `main.py` : code principal, gestion des agents et du jeu.
- `agents_sauvegardes/` : dossier où les agents sont sauvegardés.
- Fichiers CSV : statistiques d'entraînement et dictionnaires Q des agents.

## Concepts pédagogiques

- **Q-learning** : l'agent apprend à maximiser ses chances de gagner en mettant à jour ses valeurs Q selon ses expériences.
- **Exploration vs exploitation** : l'agent choisit parfois des coups aléatoires pour explorer de nouvelles stratégies.
- **Gestion d'état** : chaque configuration du jeu est considérée comme un état pour l'agent.

## Licence

Ce projet est sous licence MIT.

## Auteur

Projet réalisé dans le cadre d'un enseignement sur l'apprentissage automatique et les jeux combinatoires.