import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, GroupMember, Bill, BillParticipant
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

# Create your views here.
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def home(request):
    return render(request, 'billsplit/home.html')

@login_required(redirect_field_name='login', login_url='login')
def dashboard(request):
    cursor = connection.cursor()
    cursor.execute("SELECT billsplit_group.id, billsplit_group.name, billsplit_group.owner_id, COUNT(billsplit_groupmember.member_id) AS member_count FROM billsplit_group LEFT JOIN billsplit_groupmember ON billsplit_group.id = billsplit_groupmember.group_id WHERE billsplit_group.owner_id = %s GROUP BY billsplit_group.id, billsplit_group.name, billsplit_group.owner_id", [request.user.id])
    groups = dictfetchall(cursor)

    cursor = connection.cursor()
    cursor.execute("SELECT billsplit_group.id, billsplit_group.name, billsplit_group.owner_id, COUNT(billsplit_groupmember.member_id) AS member_count FROM billsplit_group LEFT JOIN billsplit_groupmember ON billsplit_group.id = billsplit_groupmember.group_id WHERE billsplit_group.owner_id != %s GROUP BY billsplit_group.id, billsplit_group.name, billsplit_group.owner_id", [request.user.id])
    othetgroups = dictfetchall(cursor)

    context = {
        'groups': groups,
        'othergroups': othetgroups
    }
    return render(request, 'billsplit/dashboard.html',context=context)

def add_group(request):
    if request.method == "POST":
        groupname = request.POST['groupname']
        group = Group.objects.create(name=groupname, owner=request.user)
        group.save()
        groupmember = GroupMember.objects.create(group=group, member=request.user)
        groupmember.save()

        return redirect('app-dashboard')
    return redirect('app-dashboard')

@login_required(redirect_field_name='login', login_url='login')
def group(request, group_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM auth_user WHERE id NOT IN (SELECT member_id FROM billsplit_groupmember WHERE group_id = %s)", [group_id])
    users = dictfetchall(cursor)
    
    group = Group.objects.get(id=group_id)
    groupmembers = GroupMember.objects.filter(group=group)
    members = []
    bills = Bill.objects.filter(group=group)
    for member in groupmembers:
        members.append(member.member)
    context = {
        'group': group,
        'members': members,
        'users': users,
        'bills': bills
    }
    return render(request, 'billsplit/group_details.html', context=context)

def add_members(request, group_id):
    if request.method == "POST":
        members = request.POST.getlist('users')
        for member_id in members:
            member = User.objects.get(id=member_id)
            group = Group.objects.get(id=group_id)
            groupmember = GroupMember.objects.create(group=group, member=member)
            groupmember.save()
    return redirect('app-group', group_id=group_id)

def remove_member(request, group_id, member_id):
    group = Group.objects.get(id=group_id)
    member = User.objects.get(id=member_id)
    groupmember = GroupMember.objects.get(group=group, member=member)
    groupmember.delete()
    return redirect('app-group', group_id=group_id)

@never_cache
def add_split_member(request, group_id, owner_id):
    response = HttpResponse()
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    if request.method == "POST":
        members = request.POST.getlist('members')
        amount = request.POST['amount']
        name = request.POST['name']
        participants = []
        for member in members:
            participants.append(User.objects.get(id=member))
        split_amount = float(amount)/len(participants)
        serial_members = json.dumps(members)

        context = {
            'amount': amount,
            'participants': participants,
            'split_amount': split_amount,
            'group_id': group_id,
            'owner_id': owner_id,
            'name': name,
            'serial_members': serial_members,

        }    
        return render(request, 'billsplit/add_bill.html', context=context)
    return response

def add_bill(request, group_id, owner_id):
    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('name')
        participants = request.POST.get('participants') 
        participants_obj = json.loads(participants)
     

        group = Group.objects.get(id=group_id)
        owner = User.objects.get(id=owner_id)
        bill = Bill.objects.create(group=group, bill_owner=owner, bill_amount=float(amount), bill_name=description)
        bill.save()
        for participant in participants_obj:
            user = User.objects.get(id=participant)
            user_amount = request.POST.get(participant)

            if user == owner:
                billparticipant = BillParticipant.objects.create(bill=bill, participant=user, paid=True, amount=float(user_amount))
            else:
                billparticipant = BillParticipant.objects.create(bill=bill, participant=user,amount=float(user_amount))
            billparticipant.save()
    return redirect('app-group', group_id=group_id)

def bill_details(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    billparticipants = BillParticipant.objects.filter(bill=bill)
    context = {
        'bill': bill,
        'billparticipants': billparticipants
    }
    return render(request, 'billsplit/bill_details.html', context=context)

@never_cache
def mark_as_paid(request,bill_id,participant_id):
    if request.user == Bill.objects.get(id=bill_id).bill_owner:
        billparticipant = BillParticipant.objects.get(bill_id=bill_id, participant_id=participant_id)
        billparticipant.paid = True
        billparticipant.save()
        participants = BillParticipant.objects.filter(bill_id=bill_id)
        flag = True
        for participant in participants:

            if participant.paid == False:
                flag = False
        if flag == True:
            bill = Bill.objects.get(id=bill_id)
            bill.is_active = False
            bill.save()
    return redirect('app-bill-details', bill_id=bill_id)