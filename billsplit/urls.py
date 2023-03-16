from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='app-home'),
    path('dashboard/', views.dashboard, name='app-dashboard'),
    path('add_group/', views.add_group, name='app-add-group'),
    path('group/<int:group_id>/', views.group, name='app-group'),
    path('add_members/<int:group_id>/', views.add_members, name='app-add-members'),
    path('remove_member/<int:group_id>/<int:member_id>/', views.remove_member, name='app-remove-member'),
    path('add_split_member/<int:group_id>/<int:owner_id>', views.add_split_member, name='app-add-split-member'),
    path('add_bill/<int:group_id>/<int:owner_id>', views.add_bill, name='app-add-bill'),
    path('bill_details/<int:bill_id>', views.bill_details, name='app-bill-details'),
    path('mark_as_paid/<int:bill_id>/<int:participant_id>', views.mark_as_paid, name='app-mark-as-paid'),
]