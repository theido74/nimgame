# Projet Nim Game - Analyse des statistiques

Ce dépôt contient un petit projet étudiant pour analyser les statistiques d'un jeu de bâtonnets (Nim). Le code fourni permet de charger un fichier CSV de statistiques et de générer des visualisations ainsi que d'analyser la stratégie d'un agent si un fichier dictionnaire est disponible.

## Fichiers importants

- `nimgame/main.py` : point d'entrée du projet (jeu / simulation selon implémentation).
- `nimgame/stats.py` : script d'analyse des statistiques (exécuté depuis la ligne de commande).
- `statistiques_jeu_YYYYMMDD_HHMMSS.csv` : exemple de fichier de statistiques généré par les simulations (nommage attendu).
- `agent_dictionnaire_YYYYMMDD_HHMMSS.csv` : dictionnaire de l'agent (optionnel) contenant les choix par état.
- `analyse_statistiques.png` : fichier généré par `stats.py` contenant les graphiques.

## Prérequis

- Python 3.10+ recommandé
- Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

## Utilisation

Exécuter l'analyse des statistiques :

```bash
python -m nimgame.stats statistiques_jeu_YYYYMMDD_HHMMSS.csv
```

Le script imprime des résumés dans la console et sauvegarde `analyse_statistiques.png` dans le répertoire courant.

Si un fichier `agent_dictionnaire_YYYYMMDD_HHMMSS.csv` portant le même suffixe que le fichier de statistiques est présent, le script tentera d'analyser les préférences de l'agent et affichera des ratios de choix par état.

## Pour les étudiants

- Lire le code dans `nimgame/stats.py` pour comprendre comment les données sont nettoyées et visualisées.
- Essayez de générer vos propres fichiers de statistiques depuis `nimgame/main.py` (si fourni) ou créez un CSV de test.
- Modifiez et expérimentez les graphiques (matplotlib/seaborn) pour apprendre la visualisation des données.

## Dépannage

- Si vous avez une erreur `ModuleNotFoundError`, assurez-vous d'avoir installé le fichier `requirements.txt` dans l'environnement Python actif.
- Si `analyse_statistiques.png` ne s'affiche pas, vérifiez que le script a les droits d'écriture dans le répertoire courant.

---

Fait pour un usage pédagogique — signé: ton assistant de dev.
