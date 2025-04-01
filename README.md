# Projet de scraping et traitement de données immobilières

Ce projet a pour objectif de collecter, nettoyer et enrichir des données d'annonces immobilières en Île-de-France, en vue d'une analyse ou d'une utilisation en machine learning.

## Contenu du projet

- **Scraping (`projet.py`)** : extraction des données depuis le site immo-entre-particuliers.com (ville, type, surface, pièces, DPE, prix...).
- **Nettoyage** : traitement des valeurs manquantes, conversion des types, encodage des variables catégorielles.
- **Fusion géographique** : ajout de la latitude et longitude via un fichier `cities.csv` de référence.
- **Résultat final** : un fichier `annonces_ile_de_france_final.csv` propre et aussi exploitable.

## Fichiers

- `projet.py` : script principal de scraping, nettoyage et fusion.
- `annonces_ile_de_france.csv` : données brutes après scraping.
- `annonces_ile_de_france_final.csv` : données nettoyées et enrichies.
- `cities.csv` : base de correspondance ville → coordonnées GPS.
- `partie3.ipynb` : carnet Jupyter complémentaire (analyse ou apprentissage à compléter).

## Objectifs

- Créer une base de données immobilières fiable
- Préparer les données pour des modèles de prédiction (ex : estimation du prix)

## Technologies utilisées

- Python, BeautifulSoup, pandas, requests, CSV
