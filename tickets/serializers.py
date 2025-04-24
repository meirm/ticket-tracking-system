from rest_framework import serializers
from .models import Ticket, Comment, Category, Priority, Status
from django.contrib.auth.models import User, Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email'] # Add more fields if needed

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['id', 'name']

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'closed']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) # Display author details
    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all(), write_only=True) # For creating comments

    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'author', 'comment', 'created_at', 'updated_at', 'upvotes', 'downvotes']
        read_only_fields = ['author', 'created_at', 'updated_at'] # Author set automatically

class TicketSerializer(serializers.ModelSerializer):
    # Make relationships readable, but accept IDs for writing
    issuer = UserSerializer(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True), allow_null=True, required=False)
    assigned_group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), allow_null=True, required=False)
    priority = serializers.PrimaryKeyRelatedField(queryset=Priority.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())

    # Add nested comments for detail view
    comments = CommentSerializer(many=True, read_only=True)
    # Use StringRelatedField for readable names in list views if preferred
    assignee_username = serializers.StringRelatedField(source='assignee.username', read_only=True)
    assigned_group_name = serializers.StringRelatedField(source='assigned_group.name', read_only=True)
    priority_name = serializers.StringRelatedField(source='priority.name', read_only=True)
    category_name = serializers.StringRelatedField(source='category.name', read_only=True)
    status_name = serializers.StringRelatedField(source='status.name', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'issuer', 'assignee', 'assigned_group', 'permissions',
            'priority', 'category', 'status', 'title', 'description',
            'created_at', 'updated_at', 'due_date', 'upvotes', 'downvotes',
            'hidden', 'comments',
            # Read-only fields for convenience
            'assignee_username', 'assigned_group_name', 'priority_name',
            'category_name', 'status_name',
        ]
        read_only_fields = ['issuer', 'created_at', 'updated_at', 'comments'] # Issuer set automatically

    # Add validation if needed, e.g., assignee must be in assigned_group
    def validate(self, data):
        assignee = data.get('assignee')
        assigned_group = data.get('assigned_group')
        if assignee and assigned_group:
            if not assignee.groups.filter(id=assigned_group.id).exists():
                raise serializers.ValidationError("Assignee must belong to the assigned group.")
        return data 