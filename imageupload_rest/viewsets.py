import os
from io import BytesIO

import cv2
from django.conf import settings
import numpy as np
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import parsers
from rest_framework.decorators import action

import cloudinary
import cloudinary.uploader
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from imageupload_rest import serializers
from imageupload.models import UploadImage
from main.Vision.ReconnaissanceDImages import yolo_object_detection
from main.Vision.ReconnaissanceDeTexte import detect
from main.Vision.ReconnaissanceParCodeBarre import barcode


class UploadImageViewset(viewsets.ModelViewSet):
    queryset = UploadImage.objects.all()
    serializer_class = serializers.UploadImageSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_serializer_class(self):
        if self.action == 'reconImage':
            return serializers.ReconImageSerializer
        return self.serializer_class

    @swagger_auto_schema(
        operation_description='Apply recognition algorithm to previously uploaded image',
        operation_id='apply_image_recognition',
        manual_parameters=[openapi.Parameter(
                            name="gd_ocr",
                            in_=openapi.IN_QUERY,
                            type=openapi.TYPE_NUMBER,
                            required=False,
                            default=0,
                            description="Technologie OCR (0: normal, 1: google_ocr)"
                            )],
        responses={400: 'Execution failed or image is invalid',
                   200: 'Success'},
    )
    @action(detail=True, methods=['post'])
    def reconImage(self, request, pk=None):
        image = self.get_object()
        if image is not None:
            img_array, img_stream = self.validate_image(image)

            logos_detectes = []
            weigths = [
                os.path.join(settings.WEIGHTS_ROOT, "lait_du_canada.weights"),
                os.path.join(settings.WEIGHTS_ROOT, "aliment_prepare_au_quebec.weights"),
                os.path.join(settings.WEIGHTS_ROOT, "rain_fores.weights")
            ]
            cfgs = "main/Vision/ReconnaissanceDImages/yolov3_testing.cfg"
            logo0, img_proc = yolo_object_detection.detect_logo(img_file=img_array,
                                                                weigths=weigths[0],
                                                                cfgs=cfgs,
                                                                class_name="Lait du canada")
            logo1, img_proc = yolo_object_detection.detect_logo(img_file=img_array,
                                                                weigths=weigths[1],
                                                                cfgs=cfgs,
                                                                class_name="Aliment préparé au Québec")
            logo2, img_proc = yolo_object_detection.detect_logo(img_file=img_array,
                                                                weigths=weigths[2],
                                                                cfgs=cfgs,
                                                                class_name="Rain Forest Alliance")
            logos_detectes.append(logo0)
            logos_detectes.append(logo1)
            logos_detectes.append(logo2)

            gd_ocr_param = request.query_params.get('gd_ocr', 0)
            response = {}
            status_code = status.HTTP_200_OK
            try:
                gd_ocr_param = int(gd_ocr_param)
            except ValueError:
                response = {'statut': 'echec', 'reason': 'Invalid gd_ocr. Should be a number.'}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                img_proc, Text, valeurs_nutritives, ingredients = detect.detect_VN_ING(
                    img_file=img_array, using_gd_ocr=gd_ocr_param, fichier=img_stream)
                response = {'statut': 'success', 'Ingrédients': ingredients,'Valeurs nutritives': valeurs_nutritives, 'img_proc_logos': logos_detectes}
            return Response(response, status=status_code)
        else:
            return Response({'statut': 'echec'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reconBarcode(self, request, pk=None):
        image = self.get_object()
        if image is not None:
            img, _ = self.validate_image(image)
            code_barre = barcode.get_string_barcode(img_file=img)
            return Response(code_barre[3], status=status.HTTP_200_OK)
        else:
            return Response({'statut': 'echec'}, status=status.HTTP_400_BAD_REQUEST)

    def validate_image(self, image):
        image = cloudinary.CloudinaryImage(image.image_id)
        r = requests.get(image.url, stream=True)
        print(image.url)
        if r.ok:
            r.raw.decode_content = True
            img_stream = BytesIO(r.raw.read())
            file_bytes = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            img_stream.seek(0)
            return img, img_stream 
        return None, None