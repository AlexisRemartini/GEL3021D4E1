from __future__ import absolute_import, unicode_literals

import urllib

from celery import shared_task
import cv2
import pytesseract
import os
import re
import unidecode
from main.Vision.ReconnaissanceDeTexte.detect_with_gd_ocr import DriveStorage
""""
Quelques liens utiles
    1 - https://www.murtazahassan.com/courses/opencv-projects/
    2 - https://www.inspection.gc.ca/exigences-en-matiere-d-etiquetage-des-aliments/etiquetage/industrie/etiquetage-nutritionnel/fra/1386881685057/1386881685870
    3 - https://www.canada.ca/fr/sante-canada/services/comprendre-etiquetage-aliments/tableau-valeur-nutritive.html
    
    Il vous donne également des renseignements sur les 13 principaux nutriments :

    les lipides
    les lipides saturés
    les lipides trans
    le cholestérol
    le sodium
    les glucides
    les fibres
    les sucres
    les protéines
    la vitamine A
    la vitamine C
    le calcium
    le fer
    
    Le saviez-vous?
    Il y a 13 principaux nutriments qui doivent figurer sur un tableau de la valeur nutritive. Cependant, voici une liste de certains des nutriments qui sont optionnels :

    le folate
    le magnésium
    la niacine
    le phosphore
    le potassium
    la riboflavine
    le sélénium
    la thiamine
    la vitamine B12
    la vitamine B6
    la vitamine D
    la vitamine E
    le zinc
"""
nutriments_principaux_13 = "lipides, lipides saturés,lipides trans, cholestérol, sodium, glucides, fibres, sucres, protéines, protein,carboxhydrate,sugar,sugars,calories,calorie,cholesterol, vitamine A,vitamine C, calcium, Fer"
nutriments_principaux_13 = nutriments_principaux_13.split(",")
nutriments_speciaux = "saturés, saturated, trans, polyinsaturés, oméga, monoinsaturés, fibres, sucres, B6, B-6, B12, B-12, vitamine,iron"
nutriments_speciaux = nutriments_speciaux.split(",")
nutriments_facultatifs = "folate, magnésium, niacine, phosphore, potassium, riboflavine, sélénium, thiamine, vitamine B12, vitamine B6, vitamine D, vitamine E, zinc" \
                         ",Apport,Sel,gras,matieres grasses,Pantothénate,Valeur,Valeur é, Valeur énergétique, carbo, fat, total, calo, Carbohydrate, Serving, energy,"
nutriments_facultatifs = nutriments_facultatifs.split(",")
unites = "g,mh,%,yg"
all = nutriments_principaux_13 + nutriments_facultatifs + nutriments_speciaux
ingr = "ingrédients,Ingredients,INGREDIENTS,INGRÉDIENTS,ingredients," \
           "Ingrédients,INGREDIENT,INGRÉDIENT,Ingredient," \
           "Ingrédient,Ingredient,Ingrédient"
ingr = ingr.split(",")

all = [unidecode.unidecode(i).lower() for i in all]
all = list(set(all))
all = [i.strip() for i in all]
# print(sorted(all))
ingr = [unidecode.unidecode(i).lower() for i in ingr]
ingr = list(set(ingr))


arret_val = "val,Val,VAL"
arret_ingr = "ING,ing,Ing"
arret_val = arret_val.split(",")
arret_ingr = arret_ingr.split(",")

'''
    CONFIGURATION DE LA COMMAND LINE DE PYTESSERACT
    VERIFIE SI ON UTILISE HEROKU OU PAS
'''
if os.environ.get("ENVIRONMENT", None) == "heroku":
    pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"
else:
    #le chemin de l'installation de tesseract
    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT", "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")

@shared_task
def detect_VN_ING(img_address=None, img_file=None, using_gd_ocr=0, fichier=None):
    img = img_file if img_file is not None else cv2.imread(img_address)
    # pytesseract only accept rgb, so we convert bgr to rgb

    img_array_cvt = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    boxes = pytesseract.image_to_data(img_array_cvt)

    #if fast == 0:
    hImg, wImg, _ = img_array_cvt.shape
    conf = r'--oem 3 --psm 6 outputbase digits'
    boxes = pytesseract.image_to_boxes(img_array_cvt, config=conf)
    boxes_splitted = boxes.splitlines()
    l1 = []
    l2 = []
    for b in boxes_splitted:
        b = b.split(' ')
        l1.append(tuple(b))
        l2.append(b[1:])
        # print(b)
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img_array_cvt, (x, hImg - y), (w, hImg - h), (50, 50, 255), 2)
        cv2.putText(img_array_cvt, b[0], (x, hImg - y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
    #######################################################################################################
    # boxes_splitted = boxes.splitlines()
    # text_splitted = []
    # l1 = []
    # l2 = []
    # for a,b in enumerate(boxes_splitted):
    #         #print(b)
    #         if a!=0:
    #             b = b.split()
    #             if len(b)==12:
    #                 x,y,w,h = int(b[6]),int(b[7]),int(b[8]),int(b[9])
    #                 l1.append((b[11], x, y, w, h))
    #                 l2.append([x, y, w, h])
    #                 # cv2.putText(img,b[11],(x,y-5),cv2.FONT_HERSHEY_SIMPLEX,1,(255,50, 50),2)
    #                 cv2.rectangle(img, (x,y), (x+w, y+h), (255, 50, 50), 2)
    #                 text_splitted.append(b[11])

    ###################################################################################################
    n =0
    Text= ""
    ingredients = []
    valeurs_nutritives = []
    Text_splitted = []
    if using_gd_ocr == 1:
        try :
            drive = DriveStorage()
        except Exception as e:
            ingredients = "impossible d'accéder aux crédits d'authentification"
            valeurs_nutritives = "impossible d'accéder aux crédits d'authentification"
        else:
            # with open(img_add, "rb") as file:
            lien = drive.upload_file(fichier)
            file = urllib.request.urlopen(lien)

            for line in file:
                decoded_line = line.decode("utf-8")
                Text_splitted.append(decoded_line)
            # detect_with_gd_ocr.process(img_address=img_address)
            # with open("output.txt", "r", encoding="utf-8") as file:
            #     Text_splitted = file.readlines()
            debut_ing = []
            debut_val = []
            fin_ing = 0
            fin_val = 0
            n = 0
            for i in Text_splitted:
                txt_to_search = unidecode.unidecode(i).lower()
                udec = unidecode.unidecode(i).lower()
                t_ingr = udec.find("ngred")
                t_val = udec.find("nutri")
                if t_ingr != -1:
                    debut_ing.append(n)
                if t_val != -1:
                    debut_val.append(n)
                for j in all:
                    if i.find(j) != -1:
                        fin_val = n
                n += 1
            # print("bornes ing: ", debut_ing, ": ", fin_ing)
            # print("bornes val: ", debut_val, ": ", fin_val)

            for deb in debut_ing:
                ingredients.append(Text_splitted[deb:deb+3])
            t = []
            for i in ingredients:
                for j in i:
                    t.append(j)
            ingredients = t
            ingredients = ",".join(ingredients)
            ingredients = cleaner(ingredients)
            # try:
            #     valeurs_nutritives = Text_splitted[min(debut_val):fin_val]
            # except:
            valeurs_nutritives = Text_splitted
            valeurs_nutritives = unidecode.unidecode(",".join(valeurs_nutritives)).lower()
            pos = []
            valeurs_nutritives_list = []
            for nutriment in all:
                try:
                    pos_c = re.search(nutriment, valeurs_nutritives).span()
                    pos.append(pos_c)
                except:
                    pass

            deb_vl = 0
            if len(pos) > 1:
                fin_vl = pos[1][0]
            else:
               fin_vl = pos[0][1]

            # print("valeurs_nutritivesvaleurs_nutritives", valeurs_nutritives)
            n = 0
            pos = sorted(pos)
            for i in pos:
                if n+1< len(pos):
                    valeurs_nutritives_list.append(valeurs_nutritives[i[0]: pos[n + 1][0]])
                n+=1

            valeurs_nutritives_list = list(set(valeurs_nutritives_list))
            valeurs_nutritives_classees = {}
            indices_val = []
            iv =0
            for j in all:
                if j != "" and j != " " and j != "\n":
                    valeurs_nutritives_classees[j] = []
                    for i in valeurs_nutritives_list:
                        if (unidecode.unidecode(i).replace(" ", "")).lower().find(j.strip()) != -1:
                            indices_val.append(iv)
                            t = re.search("[0-9].*", i)
                            if t:
                                valeurs_nutritives_classees[j].append(t.group())
                        iv += 1
            for k in list(valeurs_nutritives_classees):
                if valeurs_nutritives_classees[k] == []:
                    valeurs_nutritives_classees.pop(k)
            for k, v in valeurs_nutritives_classees.items():
                for i in range(len(v)):
                    v[i] = v[i].replace("9 ", "g ")
            valeurs_nutritives = valeurs_nutritives_classees
    else:
        Text = pytesseract.image_to_string(img)
        Text_splitted = Text.split('\n')
        # print('COUCOU Text_splitted:', Text_splitted)

        #VALEURS NUTRITIVES
        valeurs_nutritives = {}
        indices_val = []
        iv=0
        for j in all:
            valeurs_nutritives[j] = []
            for i in Text_splitted:
                if (unidecode.unidecode(i).replace(" ","")).lower().find(j.strip()) != -1:
                    indices_val.append(iv)
                    t = re.search("[0-9].*", i)
                    if t:
                        valeurs_nutritives[j].append(t.group())
                iv += 1
        for k in list(valeurs_nutritives):
            if valeurs_nutritives[k] == []:
                valeurs_nutritives.pop(k)
        for k, v in valeurs_nutritives.items():
            for i in range(len(v)):
                v[i] = v[i].replace("9 ", "g ")

        #INGREDIENTS
        debut = []
        for i in range(len(Text_splitted)):
            if re.search("ingr",unidecode.unidecode(Text_splitted[i]).lower()):
                debut.append(i)


        if len(debut) > 0:
            for deb in debut:
                ingredients.append(Text_splitted[deb:deb+4])
        t = []
        for j in ingredients:
            for i in j:
                t.append(i)
        ingredients = t
        ingredients = list(set(ingredients))
        ingredients = ",".join(ingredients).strip()
        ingredients = cleaner(ingredients)
    #
    # print("--------------------------------------TEXTE RECONNU---------------------------------------------")
    # for i in Text_splitted:
    #     print(i)
    # print("--------------------------------------VALEURS NUTRITIVES---------------------------------------------")
    #
    # if isinstance(valeurs_nutritives, dict):
    #     for k, v in valeurs_nutritives.items():
    #         print(k, v)
    # elif isinstance(valeurs_nutritives, list):
    #     for m in valeurs_nutritives:
    #         print(m)
    # print("--------------------------------------INGREDIENTS---------------------------------------------")
    # print("\n \n ingredients: ", ingredients)


    return img_array_cvt, Text, valeurs_nutritives, ingredients

def cleaner(ingredients):
    list_ingredients = ingredients
    n=0
    for i in list_ingredients:
        if i.isalpha() == False and i.isdigit() == False \
                and i != "%" and i != "," and i != "." and i != " " and i != "(" and i != ")":
            list_ingredients = list_ingredients.replace(i, ",")
    try:
        list_ingredients = unidecode.unidecode(list_ingredients).lower().replace("ingredients", "")
        list_ingredients = unidecode.unidecode(list_ingredients).lower().replace("ingredient", "")
    except:
        pass
    return list_ingredients

# img_add = "../../../media/images/produit01.jpg"
# img_add = "../../../media/images/produit04 (4).jpeg"
# img_add = "../../../media/images/produit04.png"
# img, Text, valeurs_nutritives, ingredients = detect_VN_ING(img_add, using_gd_ocr=1)
# cv2.imshow("img", img)
# cv2.waitKey(0)


@shared_task
def processus(img_adress=None, img_file=None):

    img = img_file if img_file is not None else cv2.imread(img_adress)
    # print(img)
    #pytesseract only accept rgb, so we convert bgr to rgb
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    ##Detecting characters and their position
    #print(pytesseract.image_to_string(img))
    ##character xpoint ypoint width heigth
    #print(pytesseract.image_to_boxes(img))

    #taille
    hImg, wImg,_ = img.shape
    ##character xpoint ypoint width heigth
    boxes = pytesseract.image_to_boxes(img)
    boxes_splitted = boxes.splitlines()
    boxes_stringed = pytesseract.image_to_string(img).splitlines()
    for b in boxes_splitted:
        #print(b)
        b = b.split(' ')
        x,y,w,h = int( b[1]), int(b[2]), int(b[3]),int(b[4])

        # cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 1)
        cv2.rectangle(img, (x,hImg - y), (w, hImg - h), (50, 50, 255), 2)

        #ecrire le caracteres dessus
        cv2.putText(img, b[0], (x, hImg - y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 255, 50), 2)

    cv2.imshow('result', img)
    cv2.waitKey(0)

    return (img, boxes_splitted, boxes_stringed)
# process(img_add)

@shared_task
def find_characters(img_adress=None, img_file=None):

    img = img_file if img_file is not None else cv2.imread(img_adress)
    # pytesseract only accept rgb, so we convert bgr to rgb
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #############################################
    #### Detecting Characters  ######
    #############################################
    hImg, wImg, _ = img.shape
    boxes = pytesseract.image_to_boxes(img)
    boxes_splitted = boxes.splitlines()
    for b in boxes_splitted:
        #print(b)
        b = b.split(' ')
        #print(b)
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (50, 50, 255), 2)
        # cv2.putText(img, b[0], (x, hImg - y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)

    return img, boxes_splitted

@shared_task
def find_only_digits(img_adress=None, img_file=None):

    img = img_file if img_file is not None else cv2.imread(img_adress)
    # pytesseract only accept rgb, so we convert bgr to rgb
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #############################################
    #### Detecting ONLY Digits  ######
    #############################################
    hImg, wImg,_ = img.shape
    conf = r'--oem 3 --psm 6 outputbase digits'
    boxes = pytesseract.image_to_boxes(img, config=conf)

    boxes_splitted = boxes.splitlines()
    for b in boxes_splitted:
        #print(b)
        b = b.split(' ')
        #print(b)
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img, (x,hImg- y), (w,hImg- h), (50, 255, 255), 2)
        cv2.putText(img,b[0],(x,hImg- y+25),cv2.FONT_HERSHEY_SIMPLEX,1,(50,50,255),2)

    return img, boxes_splitted

@shared_task
def find_nutrition_digits(img_adress=None, img_file=None):

    img = img_file if img_file is not None else cv2.imread(img_adress)
    # pytesseract only accept rgb, so we convert bgr to rgb
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hImg, wImg,_ = img.shape
    conf = r'--oem 3 --psm 6 outputbase digits'
    boxes = pytesseract.image_to_boxes(img, config=conf)
    boxes_splitted = boxes.splitlines()
    l1 = []
    l2 = []
    for b in boxes_splitted:
        b = b.split(' ')
        l1.append(tuple(b))
        l2.append(b[1:])
        #print(b)
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img, (x,hImg- y), (w,hImg- h), (50, 50, 255), 2)
        cv2.putText(img,b[0],(x,hImg- y+25),cv2.FONT_HERSHEY_SIMPLEX,1,(50,50,255),2)

    return img, boxes_splitted, l1, l2

###################################################################################
@shared_task
def detect_contours(img_adress=None, img_file=None):
    img = img_file if img_file is not None else cv2.imread(img_adress)
    # conversion en niveaux de gris(127,255,0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(gray,250,255,cv2.THRESH_BINARY_INV)

    contours,h = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    #key: figX, val = [contours, pointminHAUTGAUCHE, pointmaxBASDROITE)]
    sub_figures = {}
    key = "fig"
    n = 0
    xs = []
    ys = []
    point0 = 0
    point3 = 0
    points_plus_clairs = []
    fig_width = 0
    fig_heigth = 0
    for i in contours:
        if len(i)>2:
            for j in i:
                xs.append(j[0][0])
                ys.append(j[0][1])
                points_plus_clairs.append((j[0][0], j[0][1]))
                point0 = (min(xs), min(ys))
                point3 = (max(xs), max(ys))
                fig_width = abs(max(xs)-min(xs))
                fig_heigth = abs(max(ys)-min(ys))
            xs = []
            ys = []
            sub_figures[key+str(n)] = [i, point0, point3, fig_width, fig_heigth]
            n = n + 1
    return img, sub_figures

@shared_task
def mainproc(img_adress=None, img_file=None):
    img, sub_fig = detect_contours(img_adress=img_adress, img_file=img_file)
    img1, bc_splitted = find_characters(img_file=img)
    img2, Text, valeurs_nutritives, ingredients = detect_VN_ING(img_file=img)
    img4, bnd_splitted, bnd_l1, bnd_l2 = find_nutrition_digits(img_file=img2)

    return ingredients, img, img1, img2, img4
