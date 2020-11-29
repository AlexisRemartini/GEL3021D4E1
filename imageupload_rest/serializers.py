from io import BytesIO
import os

import cloudinary
import cloudinary.uploader
from rest_framework import serializers
from imageupload.models import UploadImage


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImage
        fields = ('pk','image','image_id')

    def create(self, validated_data):
        print('COUCOU CLOUDINARY_URL: %s' % os.environ.get('CLOUDINARY_URL', 'not found'))
        image_stream = BytesIO(validated_data["image"].read())
        result = cloudinary.uploader.upload(image_stream)
        uploaded_image = UploadImage.objects.create(image_id=result["public_id"])
        return uploaded_image


class ReconImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImage
        fields = ('pk',)
