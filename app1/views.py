from django.shortcuts import render,get_object_or_404
from django.views import View
from rest_framework import viewsets
from .models import*
from .serializer import*
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated,BasePermission
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,action
from rest_framework_simplejwt.views import TokenObtainPairView
from.authentication import IsAuthenticatedOrReadOnly
# Create your views here.


class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)
        User.objects.create_user(
            username=username,
            password=password
        )
        return Response({"message": f"User {username} created"})

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes=[AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data['refresh']
        access = response.data['access']
        response.set_cookie(
            key='access',
            value=access,
            max_age=60*60*24,
            path='/',
            secure=False,  # تأكد من ضبطه لـ True في بيئة HTTPS
            httponly=True,
            samesite='Lax'  # جرب 'Lax' أو 'None'
        )
        response.set_cookie(
            key='refresh',
            value=refresh,
            max_age=60*60*24,
            path='/',
            secure=False,  # تأكد من ضبطه لـ True في بيئة HTTPS
            httponly=True,
            samesite='Lax'  # جرب 'Lax' أو 'None'
        )
        return response

class ChangePasswordView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        old_pass=request.data.get("old")
        new_pass=request.data.get("new")
        user=request.user
        if not check_password(old_pass,user.password):
            return Response({"error": "Old password is incorrect."}, status=400)
        user.set_password(new_pass)
        user.save()
        refresh=RefreshToken.for_user(user)
        response= Response(
            {
                "message": "Password changed",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        )
        refresh = response.data['refresh']
        access = response.data['access']
        response.set_cookie(
            key='access',
            value=access,
            max_age=60*60*24,
            path='/',
            secure=False,  # تأكد من ضبطه لـ True في بيئة HTTPS
            httponly=True,
            samesite='Lax'  # جرب 'Lax' أو 'None'
        )
        response.set_cookie(
            key='refresh',
            value=refresh,
            max_age=60*60*24,
            path='/',
            secure=False,  # تأكد من ضبطه لـ True في بيئة HTTPS
            httponly=True,
            samesite='Lax'  # جرب 'Lax' أو 'None'
        )
        return response

class TokenRefreshCustomView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token missing"}, status=400)
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token  
            response = Response({
                "access": str(new_access_token),
            })
            response.set_cookie(
                key='access',
                value=str(new_access_token),
                max_age=60*60*24,  
                path='/',
                secure=False,  
                httponly=True,
                samesite='Lax',  
            )

            return response

        except Exception as e:
            return Response({"detail": "Invalid or expired refresh token"}, status=400)

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        response = Response({"message": "Loged out"})
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response
    
class MealView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    def get(self,request,id=0):
        if id !=0:
            meal=get_object_or_404(Meal,id=id)
            rates=Rating.objects.filter(meal=meal)
            data=[]
            for rate in rates:
                user=rate.user
                user=UserSerializer(user)
                
                data.append({
                    "stars":rate.stars,
                    "user":user.data
                })
            return Response(
                {
                    "id":meal.id,
                    'name':meal.name,
                    "description":meal.description,
                    "rates":data
                }
            )
        paginator=PageNumberPagination()
        paginator.page_size=5
        meals=Meal.objects.all()
        meals=paginator.paginate_queryset(meals,request)
        serializer=MealSerializer(meals, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self,request,id=None):
        if id:
            meal=get_object_or_404(Meal,id=id)
            stars=request.data.get('stars')
            user=request.user
            if not stars or not (1 <= stars <= 5):
                return Response({"detail": "Stars must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
            rate=Rating.objects.create(
                user=user,
                meal=meal,
                stars=stars,
                
            )
            meal=MealSerializer(meal)
            user=UserSerializer(user)
            return Response({
                "id": str(rate.id),
                "meal": meal.data, 
                "user": user.data,
                "stars": stars,
                
            },status=status.HTTP_201_CREATED)
        data={
            "name":request.data.get('name'),
            "description":request.data.get('description'),
            "image":request.FILES.get("image")

        }
        meal=MealSerializer(data=data)
        if meal.is_valid():
            meal.save()
            return Response(meal.data,status=status.HTTP_201_CREATED)
        return Response(meal.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,id):
        data={
            "name":request.data.get('name'),
            "description":request.data.get('description'),
            "image":request.FILES.get("image")
        }
        meal=get_object_or_404(Meal,id=id)
        meal=MealSerializer(meal,data=data,partial=True)
        if meal.is_valid():
            meal.save()
            return Response(meal.data,status=status.HTTP_200_OK)
        return Response(meal.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):
        if request.user.username=='admin':
            meal=get_object_or_404(Meal,id=id)
            meal.delete()
            return Response({"message": "Meal deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response("you are not admin to delete this",status=status.HTTP_405_METHOD_NOT_ALLOWED)

class RatingView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    def get(self,request,id=0):
        if id:
            rate=get_object_or_404(Rating,id=id)
            user=rate.user
            meal=rate.meal
            meal=MealSerializer(meal)
            user=UserSerializer(user)
            return Response({
                "id":rate.id,
                "meal":meal.data,
                "user":user.data,
                "stars":rate.stars
            })
        paginator=PageNumberPagination()
        paginator.page_size=5
        rates=Rating.objects.all()
        rates = paginator.paginate_queryset(rates, request)
        data = []
        for rate in rates:
            user=rate.user
            meal=rate.meal
            meal=MealSerializer(meal)
            user=UserSerializer(user)
            data.append({
                "id":rate.id,
                "meal":meal.data,
                "user":user.data,
                "stars":rate.stars
            })
        return paginator.get_paginated_response(data)
        
    def post(self,request):
        data={
            "meal":get_object_or_404(Meal,name=request.data.get("meal")).id,
            "user":request.user.id,
            "stars":request.data.get("stars"),
        }
        rate=RatingSerializer(data=data)
        if rate.is_valid():
            rate.save()
            user = rate.instance.user
            meal = rate.instance.meal
            meal=MealSerializer(meal)
            user=UserSerializer(user)
            return Response({
                "id":rate.instance.id,
                "meal":meal.data,
                "user":user.data,
                "stars":rate.instance.stars
            },status=status.HTTP_200_OK)
        return Response(rate.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    
    def patch(self,request,id):
        rate=get_object_or_404(Rating,id=id,user=request.user)
        data={
        "meal":get_object_or_404(Meal,name=request.data.get("meal"),).id,
        "stars":request.data.get("stars"),
        }
        rate=RatingSerializer(rate,data=data,partial=True)
        if rate.is_valid():
            rate.save()
            user = rate.instance.user
            meal = rate.instance.meal
            meal=MealSerializer(meal)
            user=UserSerializer(user)
            return Response({
            "id": str(rate.instance.id),
            "user": user.data,
            "meal": meal.data,
            "stars": rate.instance.stars,
            },status=status.HTTP_202_ACCEPTED)
        return Response(rate.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self,request,id):
        rate=get_object_or_404(Rating,id=id,user=request.user)
        rate.delete()
        return Response("deleted scssfully",status=status.HTTP_204_NO_CONTENT)
    
class Rate_Meal(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    def post(self,request,id):
        meal=get_object_or_404(Meal,id=id)
        rate=Rating.objects.create(
            user=request.user,
            meal=meal,
            stars=request.data.get("stars")
        )
        user=rate.user
        meal=rate.meal
        meal=MealSerializer(meal)
        user=UserSerializer(user)
        return Response(
            {
                "id":rate.id,
                "user":user.data,
                "meal":meal.data,
                "stars":rate.stars
            },
            status=status.HTTP_201_CREATED
        )

# class MealViewSet(viewsets.ModelViewSet):
#     permission_classes=[IsAuthenticatedOrReadOnly]
#     queryset=Meal.objects.all()
#     serializer_class=MealSerializer
    
    
#     @action(detail=True,methods=['POST'])
#     def rate_meal(self,request,pk=None):
#         meal=self.get_object()
#         stars=request.data.get("stars")
#         if not stars or not (1 <= stars <= 5):
#             return Response({"detail": "Stars must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
#         rate=Rating.objects.create(
#             meal=meal,
#             stars=stars,
#             user=request.user
#         )
#         serializer=RatingSerializer(rate)
#         return Response({"message":"Rate created"},serializer.data,status=status.HTTP_201_CREATED)
    
    
#     @action(detail=True,methods=["PATCH"])
#     def update_rate(self,request,pk=None):
#         rate=get_object_or_404(Rating,id=pk,user=request.user)
#         stars=request.data.get("stars")
#         if not stars or not (1 <= stars <= 5):
#             return Response({"detail": "Stars must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
#         rate.stars=stars
#         rate.save()
#         return Response({
#                 "message":"Rate updated",
#                 "id": str(rate.id),  
#                 "stars": rate.stars,
#                 "meal": rate.meal.name, 
#                 "user": rate.user.username
#             },status=status.HTTP_200_OK)
        
#     '''
#     if detail =True i need to send pk as parameter because in this case function deel with one object 
#     فهذا يعني أنك بتحدد أن الفانكشن دي هتتعامل مع كائن فردي  وليس مع مجموعة من الوجبات.  
#     لازم تحدد الـ ID للكائن الفردي في الـ URL لكي تستطيع الوصول له.
#     '''

# class RatingViewSet(viewsets.ModelViewSet):
#     permission_classes=[IsAuthenticatedOrReadOnly]
#     queryset=Rating.objects.all()
#     serializer_class=RatingSerializer
    
# class UserViewSet(viewsets.ModelViewSet):
#     permission_classes=[IsAuthenticatedOrReadOnly]
#     queryset=User.objects.all()
#     serializer_class=UserSerializer
    
#     def create(self, request, *args, **kwargs):
#         username=request.data.get("username")
#         password=request.data.get("password")
#         if User.objects.filter(username=username).exists():
#             return Response({"error":"user already exit"},status=status.HTTP_400_BAD_REQUEST)
#         user=User.objects.create_user(
#             username=username,
#             password=password
#         )
#         serializer=self.get_serializer(user)
#         return Response (serializer.data,status=status.HTTP_201_CREATED)

#     @action(detail=True,methods=["GET"])
#     def get_user_rates(self,request,pk=None):
#         user=get_object_or_404(User,id=pk)
#         rates=Rating.objects.filter(user=user)
#         data=[]
#         for rate in rates:
#             data.append({
#                 "user":user.username,
#                 "meal":rate.meal.name,
#                 "rate":rate.stars
#             })
#         return Response(data,status=status.HTTP_200_OK)
        
# class Cookie(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         name = request.data.get('name')
#         age = request.data.get('age')

#         response = Response({'message': 'Cookies set successfully'})
        
#         response.set_cookie(
#             key='name',
#             value=name,
#             max_age=60*60*24,     # يوم
#             path='/',
#             secure=False,         # خليه True في حالة HTTPS
#             httponly=True,
#             samesite='Lax'
#         )

#         response.set_cookie(
#             key='age',
#             value=age,
#             max_age=60*60*24,
#             path='/',
#             secure=False,
#             httponly=True,
#             samesite='Lax'
#         )

#         return response

#     def get(self, request):
#         name = request.COOKIES.get('name')
#         age = request.COOKIES.get('age')

#         return Response({

#             'name': name,
#             'age': age
#         })

