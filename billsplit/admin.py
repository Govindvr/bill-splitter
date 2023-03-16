from django.contrib import admin
from .models import Group, GroupMember, Bill, BillParticipant

# Register your models here.
 
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(Bill)
admin.site.register(BillParticipant)

