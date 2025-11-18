from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),   # ✅ must point to your view
    path("logout/", views.logout_view, name="logout"),

    path("users/<int:user_id>/delete/", views.delete_user, name="delete-user"),


    # ========= Admin board =======
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path('petition-list', views.petition_list, name="petition-list"),
    path('user-list', views.user_list, name="user-list"),
    # urls.py
    path("petition-detail/<int:pk>/", views.petition_detail, name="petition-detail"),




    # =========  board =======
    path("board/", views.board_view, name="board"),
    path("petitions/", views.user_petitions, name="user_petitions"),
    path("my-petitions/", views.my_petitions, name="my_petitions"),
    path("signed-petitions/", views.signed_petitions, name="signed_petitions"),
    path("sign-petition/<int:petition_id>/", views.sign_petition, name="sign_petition"),
    path("signed-petitions/", views.signed_petitions, name="signed-petitions"),
]
