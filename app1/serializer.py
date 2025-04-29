from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'
        extra_kwargs = {'password': {'write_only': True}}
        
class MealSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    '''
    SerializerMethodField
    Serializerعشان نضيف حقل إضافي في الـ 
    Modelمش موجود بشكل مباشر فى ال 
    '''
    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'average_rating','image']
    def get_average_rating(self, obj):
        return obj.average_meal_rates()

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'meal', 'user', 'stars']