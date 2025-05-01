from django.urls import path,include
from.views import*
from django.conf import settings
from django.conf.urls.static import static
# routers
from rest_framework import routers
# meal_router = routers.DefaultRouter()
# rating_router = routers.DefaultRouter()
# user_router=routers.DefaultRouter()

# meal_router.register('', MealViewSet)     # هنا meals مش فاضية
# rating_router.register('', RatingViewSet) # هنا ratings مش فاضية
# user_router.register('',UserViewSet)

from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenBlacklistView

urlpatterns = [
    
    path('signup/',SignupView.as_view()),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh-token/', TokenRefreshCustomView.as_view(), name='refresh_token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/',ChangePasswordView.as_view(),name='change_password'),
    
    path('meals/',MealView.as_view(),name='meals'),
    path('meals/<int:id>/',MealView.as_view(),name='meals'),
    path('rate_meal/<int:id>/',MealView.as_view(),name='rate_meal'),
    path("rate_meal_2/<int:id>/",Rate_Meal.as_view(),name='rate_meal'),

    #special case from post method
    #can used normal post rather than it but to be more clear
    
    path('rates/',RatingView.as_view(),name='rates'),
    path('rates/<str:id>/',RatingView.as_view(),name='rates'),
    
    
    path('moc/',MOC.as_view())
    # path('meals/viewset/', include(meal_router.urls)),
    # path('rates/viewset/', include(rating_router.urls)),
    # path('users/viewset/', include(user_router.urls)),
    
    # path('cookie/',Cookie.as_view(),name='cookie'),
]
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
