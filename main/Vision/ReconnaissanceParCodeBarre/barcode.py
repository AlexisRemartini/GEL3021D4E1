from __future__ import absolute_import, unicode_literals
from celery import shared_task
from pyzbar import pyzbar
import cv2
import requests
import json

path = "/D4/media/images/produit01.jpg"
@shared_task
def get_string_barcode(img_address=None, img_file=None):
    # img_file = np.array(img_file)
    image = img_file if img_file is not None else cv2.imread(img_address)
    barcodes = pyzbar.decode(image)
    barcodeData = ""

    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)

        barcodeData = barcode.data.decode("utf-8")

        text = barcodeData
        cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # cv2.imshow("Image", image)
        # cv2.waitKey(0)

    url = "https://world.openfoodfacts.org/api/v0/product/[" + barcodeData + "].json"
    marque = "None"
    product_name = "None"
    nutriments = "None"
    ingredients = "None"
    countries = "None"

    try:
        response = requests.get(url)
        data = json.loads(response.content)
        marque = data['product']['brands']
        product_name = data['product']['product_name']
        nutriments = data['product']['nutriments']
        ingredients = data['product']['ingredients_text']
        countries = data['product']['countries']
    except:
        # print("Please enter a valide code")
        pass
    description = ["Product brand", "Product name", "Ingredients", "Countries"]
    information = [marque, product_name, ingredients, countries]
    fichier = dict(zip(description, information))

    if len(barcodeData) < 2 or text == ""  or len(text)< 2:
        barcodeData = "0000000000"
        text = "Product not found"
        fichier = "Product not found"

    return image, barcodeData, text, fichier, nutriments

# a, b, c = get_string_barcode(path)
#
# print(a, b, c)