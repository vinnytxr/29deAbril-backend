from rest_framework import serializers
from ..models import Learning

class LearningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learning
        fields = '__all__'