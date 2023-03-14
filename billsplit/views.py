from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, GroupMember
from django.contrib.auth.models import User
from django.db import connection

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

    #get all groups that the user has not created but he is a member of along with the count of members in each group using sql
    cursor = connection.cursor()
    cursor.execute("SELECT billsplit_group.id, billsplit_group.name, billsplit_group.owner_id, COUNT(billsplit_groupmember.member_id) AS member_count FROM billsplit_group LEFT JOIN billsplit_groupmember ON billsplit_group.id = billsplit_groupmember.group_id WHERE billsplit_group.owner_id != %s GROUP BY billsplit_group.id, billsplit_group.name, billsplit_group.owner_id", [request.user.id])
    othetgroups = dictfetchall(cursor)
    print(othetgroups)
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
    for member in groupmembers:
        members.append(member.member)
    context = {
        'group': group,
        'members': members,
        'users': users
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