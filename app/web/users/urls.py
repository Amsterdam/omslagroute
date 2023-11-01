from .views import *
from django.urls import path


urlpatterns = [
    path('', UserList.as_view(), name='user_list'),
    path('organisatie/', FederationUserList.as_view(), name='federation_user_list'),
    path('<int:pk>', UserUpdateView.as_view(), name="update_user"),
    path('organisatie/<int:pk>/', FederationUserUpdateView.as_view(), name="update_federation_user"),

    path('nieuw/', UserCreationView.as_view(), name="create_user"),
    path('organisatie/nieuw/', UserCreationFederationView.as_view(), name="create_user_federation"),

    path('verwijder/<int:pk>', UserDelete.as_view(), name="delete_user"),
    path('organisatie/verwijder/<int:pk>', UserFederationDelete.as_view(), name="delete_federation_user"),
]
