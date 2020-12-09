## GEL3021D4E1
DESIGN IV - projet Ali Quebec

# Dépendances à installer: 
Creer un virtual environment pour isoler localement nos packages et nos dépendences
``` bash
python3 -m venv env
```
``` bash
source env/bin/activate  # On Windows, use env\scripts\activate.bat
```
```bash
pip install -r requirements.txt
```
## Tesseract
installer tesseract dans le repertoire par défaut C:\Program Files\Tesseract-OCR ou alors le changer dans detect.py.

https://github.com/UB-Mannheim/tesseract/wiki

## Clé cloudinary
Rajouter dans les variables d'environnement la clé cloudinary 
## Fichiers .weights pour la détections de logos
https://drive.google.com/drive/folders/1bdG7JC8ITShO2RIjrGs-FbZtlANxaoBk?usp=sharing

# Lancer le serveur en local
```bash
python manage.py runserver
```

# Utilisation 1 - GUI

## 1 - Aller sur le lien
http://127.0.0.1:8000/

## 2.1 - Vision artificielle
choisir reconnaissance par vision et le type traitement
## 2.2 - Code barre
chosir reconnaissance de code barre
## 3 - Upload
choisir une image depuis votre ordinateur ou faire un glisser-déposer de l'image
## 4 - cliquer sur soumettre
la reconnaissance par vision artificielle fais deux types de traitements:
- une reconnaissance de texte (ingrédients et valeurs nutritives)
- ue reconnaissance de logos utilisant du machine learning

Pour la reconnaissance de logos, il faut obligatoirement créer un dossier 'weights' dans la racine contenant le projet et y insérer les différents fichiers .weights :
> dir  
  
  >> GEL30211D4E1
  
  >> weights/*.weigts

  
# Utilisation 2 - API
S'assurer que le serveur est bien lancé;

Ouvrir le fichier main/test_api.py;

changer le file_path par le chemin de l'image que vous souhaitez traiter;

Lancer(run) le fichier test_api.py

Vous pouvez également faire votre propre fichier de requêtes pour l'api ou passer par un autre service comme Postman; les adresses pour les différents traitements sont dans le fichier.


# Utilisation 3 - lien web heroku (en développement)
Il est possible de réaliser la plupart des étapes ci-dessus en se rendant sur le lien : http://alivisiond4.herokuapp.com/

Le traitement de la reconnaissance de logos n'y ait pas supporté par contre.


## divers

En cas de problèmes de librairies avec pyzbar, visitez ce lien.
https://github.com/NaturalHistoryMuseum/pyzbar/issues/13
