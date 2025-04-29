from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.db.models import Avg


# Create your models here.
class Meal (models.Model):
    name=models.CharField(max_length=50)
    description=models.TextField(max_length=500)
    image=models.ImageField( upload_to='meal_images',null=True,blank=True)
    # def average_meal_rates2(self):
    #     rates = Rating.objects.filter(meal=self)
    #     total = 0
    #     for rate in rates:
    #         total += rate.stars
    #     if rates.count() > 0:
    #         return total / rates.count()
    #     return 0

    def __str__(self):
        return self.name

    def average_meal_rates(self):
        result = Rating.objects.filter(meal=self).aggregate(Avg('stars'))
        return result['stars__avg'] or 0

class Rating(models.Model):
    meal=models.ForeignKey(Meal,  on_delete=models.CASCADE,related_name='meals')
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    stars=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    def __str__(self):
        return f"Rating for {self.meal}"
    class Meta:
        unique_together=[['user','meal'],]
        indexes = [
            models.Index(fields=['user', 'meal']),
        ]

