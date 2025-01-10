import requests 
from bs4 import BeautifulSoup 
import csv 
import pandas as pd 

class NonValide(Exception): 
    def __init__(self, message="L'annonce n'est pas valide"): 
        self.message = message 
        super().__init__(self.message) 

def getsoup(url): # Fonction pour obtenir le contenu HTML d'une URL
    response = requests.get(url) 
    soup = BeautifulSoup(response.text, 'html.parser') #Convertit le texte de la réponse en objet BeautifulSoup ou on pourra naviguer dedans
    return soup

def prix(soup):
    try:
        prix_texte = soup.select_one('.product-price').text.strip() 
        if not prix_texte:
            raise NonValide("Le prix n'a pas été trouvé dans l'annonce")
        prix_numerique = int(prix_texte.replace('€', '').replace(' ', '')) 
        if prix_numerique < 10000:
            raise NonValide("Prix trop bas, probablement une annonce non valide")
        return str(prix_numerique)
    except (AttributeError, ValueError): 
        raise NonValide("Le prix n'a pas été trouvé ou est invalide dans l'annonce")

def ville(soup):
    try:
        details_texte = soup.select_one('h2.mt-0').text.strip()
        index = details_texte.rfind(", ") # Trouve l'index de la dernière virgule dans le texte
        if index == -1: # Si la virgule n'est pas trouvée, lève une exception
            raise NonValide("La ville n'a pas été trouvée dans l'annonce")
        ville_texte = details_texte[index + 2:] # Extrait le texte après la virgule et l'éspace
        return ville_texte
    except AttributeError:
        raise NonValide("La ville n'a pas été trouvée dans l'annonce")

def get_caracteristiques(soup): # Fonction pour obtenir les caractéristiques de l'annonce
    try:
        header = soup.find('p', class_='ad-section-title', string='Caractéristiques :')
        if not header:
            raise NonValide("Les caractéristiques n'ont pas été trouvées dans l'annonce")
        ul = header.find_next('ul', class_='list-inline')
        return ul
    except AttributeError:
        raise NonValide("Les caractéristiques n'ont pas été trouvées dans l'annonce")

def extract_caracteristique(ul, label): # Fonction pour extraire une caractéristique spécifique de l'annonce
    try:
        for li in ul.find_all('li'):
            if label in li.text:
                return li.find_all('span')[1].text.strip()# Retourne le texte du deuxième span dans le li
        return "-"
    except AttributeError:
        return "-"

def type(soup):
    ul = get_caracteristiques(soup)
    type_texte = extract_caracteristique(ul, 'Type')
    if type_texte not in ['Maison', 'Appartement']:
        raise NonValide("Le type n'est ni 'Maison' ni 'Appartement'")
    return type_texte

def surface(soup):
    ul = get_caracteristiques(soup)
    return extract_caracteristique(ul, 'Surface')

def nbrpieces(soup):
    ul = get_caracteristiques(soup)
    return extract_caracteristique(ul, 'Nb. de pièces')

def nbrchambres(soup):
    ul = get_caracteristiques(soup)
    return extract_caracteristique(ul, 'Nb. de chambres')

def nbrsdb(soup):
    ul = get_caracteristiques(soup)
    return extract_caracteristique(ul, 'Nb. de sales de bains')

def dpe(soup):
    ul = get_caracteristiques(soup)
    return extract_caracteristique(ul, 'Consommation d\'énergie (DPE)')

def informations(soup):
    try:
        ville_info = ville(soup)
        type_info = type(soup)
        surface_info = surface(soup)
        nbrpieces_info = nbrpieces(soup)
        nbrchambres_info = nbrchambres(soup)
        nbrsdb_info = nbrsdb(soup)
        dpe_info = dpe(soup)
        prix_info = prix(soup)
        
        return f"{ville_info},{type_info},{surface_info},{nbrpieces_info},{nbrchambres_info},{nbrsdb_info},{dpe_info},{prix_info}"
    except NonValide as e:
        raise NonValide(f"Annonce non conforme: {e}")
    
def  scrape_annonces(base_url, pages):
    annonces = []
    urls_vues = set()  
    for page in range(1, pages + 1):
        url = f"{base_url}/{page}"
        print(f"Scraping page: {page}")  
        soup = getsoup(url) # Obtenir le contenu HTML de l'URL
        links = soup.select('a[href^="/annonce-"]') # Sélectionner les liens des annonces
        print(f"Nombre de liens trouvés sur la page {page}: {len(links)}")  
        for link in links:
            annonce_url = link['href'] 
            if not annonce_url.startswith('http'): 
                annonce_url = f"https://www.immo-entre-particuliers.com{annonce_url}"
            if annonce_url not in urls_vues:  
                urls_vues.add(annonce_url)  
                print(f"Traitement de l'URL: {annonce_url}")  
                annonce_soup = getsoup(annonce_url) 
                try:
                    info = informations(annonce_soup)
                    annonces.append(info)
                    print(f"Annonce ajoutée: {info}")  
                except NonValide as e:
                    print(f"Annonce non conforme: {e}")
        print(f"Nombre total d'annonces après la page {page}: {len(annonces)}")  
    return annonces

def save_to_csv(filename, annonces):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Ville', 'Type', 'Surface', 'NbrPieces', 'NbrChambres', 'NbrSdb', 'DPE', 'Prix']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for annonce in annonces:
            writer.writerow(annonce.split(','))
            print(f"Annonce enregistrée: {annonce}")  

base_url = "https://www.immo-entre-particuliers.com/annonces/france-ile-de-france"
nombre_de_pages = 282  

annonces = scrape_annonces(base_url, nombre_de_pages)
save_to_csv("annonces_ile_de_france.csv", annonces)

# ==================== NETTOYAGE DES DONNÉES ====================

# Importer le contenu du CSV dans un DataFrame nommé annonces
annonces = pd.read_csv('annonces_ile_de_france.csv')
# Remplacer les valeurs manquantes dans 'DPE' par la valeur 'Vierge'
annonces['DPE'] = annonces['DPE'].replace('-', 'Vierge')
# Convertir les colonnes 'Surface', 'NbrPieces', 'NbrChambres', 'NbrSdb' en float
annonces['Surface'] = annonces['Surface'].str.replace(' m²', '').str.replace(' ', '').replace('-', None).astype(float)
annonces['NbrPieces'] = annonces['NbrPieces'].replace('-', None).astype(float)
annonces['NbrChambres'] = annonces['NbrChambres'].replace('-', None).astype(float)
annonces['NbrSdb'] = annonces['NbrSdb'].replace('-', None).astype(float)
# Remplacer les valeurs manquantes par la moyenne de chaque colonne
annonces['Surface'] = annonces['Surface'].fillna(annonces['Surface'].mean())
annonces['NbrPieces'] = annonces['NbrPieces'].fillna(annonces['NbrPieces'].mean())
annonces['NbrChambres'] = annonces['NbrChambres'].fillna(annonces['NbrChambres'].mean())
annonces['NbrSdb'] = annonces['NbrSdb'].fillna(annonces['NbrSdb'].mean())
# Supprimer les lignes restantes avec des valeurs manquantes si nécessaire
annonces = annonces.dropna()
# Utiliser la méthode des variables indicatrices pour les colonnes 'Type' et 'DPE'
annonces = pd.get_dummies(annonces, columns=['Type', 'DPE'])
# Convertir les colonnes booléennes en 0/1
annonces['Type_Maison'] = annonces['Type_Maison'].astype(int)
annonces['Type_Appartement'] = annonces['Type_Appartement'].astype(int)
annonces['DPE_A (< 50)'] = annonces['DPE_A (< 50)'].astype(int)
annonces['DPE_B (51 à 90)'] = annonces['DPE_B (51 à 90)'].astype(int)
annonces['DPE_C (91 à 150)'] = annonces['DPE_C (91 à 150)'].astype(int)
annonces['DPE_D (151 à 230)'] = annonces['DPE_D (151 à 230)'].astype(int)
annonces['DPE_E (231 à 330)'] = annonces['DPE_E (231 à 330)'].astype(int)
annonces['DPE_F (331 à 450)'] = annonces['DPE_F (331 à 450)'].astype(int)
annonces['DPE_Vierge'] = annonces['DPE_Vierge'].astype(int)
# Sauvegarder les données modifiées dans un nouveau fichier CSV
annonces.to_csv('annonces_ile_de_france_final.csv', index=False) #index = False pour ne pas sauvegarder l'index 1. 2. 3. ...
print("Données nettoyées et sauvegardées dans 'annonces_ile_de_france_final.csv'")


# ==================== TRAITEMENT DES VILLES ===================

# QUESTION 12 : Importation dans un DataFrame nommé villes 
villes = pd.read_csv('cities.csv')
# QUESTION 13 : Modification des valeurs

# Convertir en minuscules
annonces['Ville'] = annonces['Ville'].str.lower()
villes['label'] = villes['label'].str.lower()

# Supprimer espaces, tirets, apostrophes
annonces['Ville'] = annonces['Ville'].str.replace(" ", "")
annonces['Ville'] = annonces['Ville'].str.replace("-", "")
annonces['Ville'] = annonces['Ville'].str.replace("'", "") 

villes['label'] = villes['label'].str.replace(" ", "")
villes['label'] = villes['label'].str.replace("-", "")
villes['label'] = villes['label'].str.replace("'", "")

# Suppression des accents
accents = {"É": "e","é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ç": "c", "ù": "u", "ô": "o", "î": "i", "ï": "i", "ÿ": "y"} # Dictionnaire des accents
for accent, non_accent in accents.items(): # Parcours du dictionnaire des accents
    annonces['Ville'] = annonces['Ville'].str.replace(accent, non_accent) # Remplacement des accents dans les annonces
    villes['label'] = villes['label'].str.replace(accent, non_accent) # Remplacement des accents dans les villes

# Remplacer uniquement "Saint-" au début du nom de la ville
annonces['Ville'] = annonces['Ville'].str.replace("saint", "st")
villes['label'] = villes['label'].str.replace("saint", "st")
annonces['Ville'] = annonces['Ville'].replace("sts", "beautheilsts")

# Cas particuliers
annonces['Ville'] = annonces['Ville'].replace({
    'lechesnayrocquencourt': 'lechesnay',
    'eragnysuroise': 'eragny',
    'evrycourcouronnes': 'courcouronnes'
})
villes['label'] = villes['label'].replace({
    'lechesnayrocquencourt': 'lechesnay', 
    'eragnysuroise': 'eragny',
    'evrycourcouronnes': 'courcouronnes'
})

# Arrondissements de Paris
def gerer_arrondissements_paris(nom):
    if 'paris' in nom and ('eme' in nom or 'er' in nom):
        return 'paris'
    return nom
annonces['Ville'] = annonces['Ville'].apply(gerer_arrondissements_paris)

#==================== JOINTURES DES DEUX TABLES ====================
# Supprimer les doublons dans villes pour s'assurer qu'il y a une seule correspondance par ville
villes_unique = villes[['label', 'latitude', 'longitude']].drop_duplicates(subset=['label'])
# Fusionner uniquement sur 'latitude' et 'longitude'
annonces = annonces.merge(
    villes_unique, 
    left_on='Ville', 
    right_on='label', 
    how='left'
)
# Supprimer la colonne 'label' et 'Ville' qui ne sert plus
annonces = annonces.drop(columns=['Ville', 'label'])
# Sauvegarde du fichier nettoyé
annonces.to_csv('annonces_ile_de_france_final.csv', index=False)