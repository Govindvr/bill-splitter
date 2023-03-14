from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='app-home'),
    path('dashboard/', views.dashboard, name='app-dashboard'),
    path('add_group/', views.add_group, name='app-add-group'),
    path('group/<int:group_id>/', views.group, name='app-group'),
    path('add_members/<int:group_id>/', views.add_members, name='app-add-members'),
    path('remove_member/<int:group_id>/<int:member_id>/', views.remove_member, name='app-remove-member'),
]