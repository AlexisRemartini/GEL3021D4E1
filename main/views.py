from __future__ import absolute_import, unicode_literals

import os
from io import BytesIO
import cv2
import cloudinary
import cloudinary.uploader
import numpy as np
from django.shortcuts import render
from django.conf import settings

from .forms import ImageForm
from .Vision.ReconnaissanceDImages import yolo_object_detection
from .Vision.ReconnaissanceDeTexte import detect
from .Vision.ReconnaissanceParCodeBarre import barcode


def image_upload_view(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            # formulaires invalides sinon
            image = request.FILES.get("image")
            image_stream = BytesIO(image.read())
            obj = form.save(commit=False)
            obj.image = None

            # Get the current instance object to display in the template
            var = request.POST.get("vision")
            result = cloudinary.uploader.upload(image_stream)
            obj.image_id = result["public_id"]
            obj.save()

            image_stream.seek(0)
            file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            ingredients = None
            valeurs_nutritives = None
            fichier_json = ""
            barcode_str = None
            logos_detectes = []
            logo0 = None
            logo1 = None
            logo2 = None
            nutriments = None
            img_proc = None
            logos_detectes = []
            if var == "barcode":
                img_proc, barcode_str, text, fichier_json, nutriments = barcode.get_string_barcode(img_file=img)
            if var == "logos":
                # img_proc = img
                for i in settings.WEIGHTS:
                    logo, img_proc = yolo_object_detection.detect_logo(img_file=img,
                                                                        weigths=i[0],
                                                                        cfgs=settings.CFG,
                                                                        class_name=i[1])
                    logos_detectes.append(logo)
            else:
                s = 1
                v = request.POST.get("vitesse")
                if v == "non":
                    s = 0

                img_proc, Text, valeurs_nutritives, ingredients = detect.detect_VN_ING(
                    img_file=img,
                    using_gd_ocr=s,
                    fichier=image)

            img_proc = cv2.imencode(".png", img_proc)[1].tobytes()
            result = cloudinary.uploader.upload(img_proc, public_id=obj.image_id + "proc", overwrite=True)
            image_proc_id = result["public_id"]

            return render(request, 'main/index.html',
                          {'form': form,
                           'img_obj': {"title": obj.title, "url": cloudinary.CloudinaryImage(obj.image_id).build_url()},
                           'img_proc': cloudinary.CloudinaryImage(image_proc_id).build_url(),
                           'img_proc_ingredients': ingredients,
                           'img_proc_valeurs_nutritives': valeurs_nutritives,
                           'img_proc_logos': logos_detectes,
                           'barcode_datas': fichier_json,
                           'nutriments': nutriments,
                           'radio': var,
                           'barcode_str': barcode_str,
                           })
    else:
        form = ImageForm()
    print(form.errors)
    return render(request, 'main/index.html', {'form': form})
