import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import argparse

def analyser_statistiques(fichier_statistiques):
    """Analyse les statistiques d'un fichier CSV produit par le jeu.

    Paramètre:
        fichier_statistiques (str): chemin vers le fichier CSV contenant les statistiques

    Retourne:
        pandas.DataFrame: le DataFrame chargé (utile pour tests ou post-traitement)
    """

    # Charger les données depuis le CSV
    df = pd.read_csv(fichier_statistiques)

    print("=== ANALYSE DES STATISTIQUES DU JEU ===")
    print(f"Nombre total de parties: {len(df)}")

    # 1) Répartition des gagnants
    gagnants = df['Gagnant'].value_counts()
    print(f"\n1. RÉPARTITION DES VICTOIRES:")
    for gagnant, count in gagnants.items():
        pourcentage = (count / len(df)) * 100
        print(f"   {gagnant}: {count} victoires ({pourcentage:.1f}%)")

    # 2) Avantage lié au premier joueur
    print(f"\n2. AVANTAGE DU PREMIER JOUEUR:")
    for premier in df['Premier joueur'].unique():
        sous_df = df[df['Premier joueur'] == premier]
        victories = sous_df['Gagnant'].value_counts()
        print(f"   Quand {premier} commence:")
        for gagnant, count in victories.items():
            pourcentage = (count / len(sous_df)) * 100
            print(f"     {gagnant} gagne {count} fois ({pourcentage:.1f}%)")

    # 3) Statistiques sur la longueur des parties
    print(f"\n3. LONGUEUR DES PARTIES:")
    print(f"   Moyenne: {df['Nombre de tours'].mean():.1f} tours")
    print(f"   Médiane: {df['Nombre de tours'].median()} tours")
    print(f"   Minimum: {df['Nombre de tours'].min()} tours")
    print(f"   Maximum: {df['Nombre de tours'].max()} tours")

    # 4) Génération des visualisations (sauvegarde en PNG)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Camembert : répartition des victoires
    axes[0, 0].pie(gagnants.values, labels=gagnants.index, autopct='%1.1f%%')
    axes[0, 0].set_title('Répartition des victoires')

    # Histogramme : distribution du nombre de tours
    axes[0, 1].hist(df['Nombre de tours'], bins=range(1, df['Nombre de tours'].max() + 2), alpha=0.7)
    axes[0, 1].set_xlabel('Nombre de tours')
    axes[0, 1].set_ylabel('Fréquence')
    axes[0, 1].set_title('Distribution de la longueur des parties')

    # Barres : victoires selon qui commence
    advantage_data = []
    for premier in df['Premier joueur'].unique():
        for gagnant in df['Gagnant'].unique():
            count = len(df[(df['Premier joueur'] == premier) & (df['Gagnant'] == gagnant)])
            advantage_data.append({'Premier': premier, 'Gagnant': gagnant, 'Count': count})

    advantage_df = pd.DataFrame(advantage_data)
    sns.barplot(x='Premier', y='Count', hue='Gagnant', data=advantage_df, ax=axes[1, 0])
    axes[1, 0].set_title('Victoires par premier joueur')

    # Boxplot : longueur des parties par gagnant
    sns.boxplot(x='Gagnant', y='Nombre de tours', data=df, ax=axes[1, 1])
    axes[1, 1].set_title('Longueur des parties par gagnant')

    plt.tight_layout()
    plt.savefig('analyse_statistiques.png', dpi=300)
    print(f"\nVisualisations sauvegardées dans 'analyse_statistiques.png'")

    # 5) Analyse de la stratégie de l'agent si le fichier dictionnaire correspondant existe
    try:
        # Construire le nom du fichier dictionnaire attendu
        base_name = fichier_statistiques.replace('statistiques_jeu_', '').replace('.csv', '')
        dictionnaire_file = f"agent_dictionnaire_{base_name}.csv"

        df_dict = pd.read_csv(dictionnaire_file)
        print(f"\n4. ANALYSE DE LA STRATÉGIE DE L'AGENT:")

        # Fonction utilitaire pour parser proprement les choix stockés en texte
        def parse_choices(x):
            # Gère NaN, chaînes vides et formats mal formés de façon robuste
            if pd.isna(x):
                return []
            if not isinstance(x, str):
                return []
            s = x.strip()
            # Supprimer des crochets si présents
            if s.startswith('[') and s.endswith(']'):
                s = s[1:-1]
            if s.strip() == '':
                return []
            parts = [p.strip() for p in s.split(',')]
            values = []
            for p in parts:
                if p == '':
                    continue
                # Retirer les guillemets s'il y en a
                p = p.strip("'\"")
                try:
                    values.append(int(p))
                except ValueError:
                    # Ignorer les tokens non entiers
                    continue
            return values

        # Appliquer le parsing sur la colonne attendue
        df_dict['Choix disponibles'] = df_dict['Choix disponibles'].apply(parse_choices)

        # Calculer une distribution des choix (préférences) par état
        preferences = {}
        for _, row in df_dict.iterrows():
            etat = row['Etat (bâtons restants)']
            choix = row['Choix disponibles']
            if choix:
                counter = Counter(choix)
                total = sum(counter.values())
                preferences[etat] = {choice: count/total for choice, count in counter.items()}

        # Afficher les préférences pour une sélection d'états critiques
        print("   Préférences de l'agent pour les états critiques:")
        etats_critiques = [1, 2, 3, 4, 5, 6, 7]
        for etat in etats_critiques:
            if etat in preferences:
                print(f"     {etat} bâtons: {preferences[etat]}")

    except FileNotFoundError:
        # Si le fichier dictionnaire n'existe pas, on ignore cette partie proprement
        print("Fichier dictionnaire de l'agent non trouvé. L'analyse de stratégie est ignorée.")

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyser les statistiques du jeu de bâtonnets')
    parser.add_argument('fichier', help='Fichier CSV contenant les statistiques')
    args = parser.parse_args()
    
    analyser_statistiques(args.fichier)