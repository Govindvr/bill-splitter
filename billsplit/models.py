from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groups")
    members = models.ManyToManyField(User,through="GroupMember", related_name="in_groups")
    date_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.group.name + " " + self.member.username
    
class Bill(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    bill_name = models.CharField(max_length=100)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_date = models.DateTimeField(auto_now_add=True)
    bill_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bills_paid")
    is_active = models.BooleanField(default=True)
    bill_participants = models.ManyToManyField(User, through="BillParticipant", related_name="bills_participated")
    def __str__(self):
        return self.bill_name

class BillParticipant(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.bill.bill_name + " " + self.participant.username