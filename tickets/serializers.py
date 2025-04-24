from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ticket, Comment, Category, Priority, Status

User = get_user_model()

# Serializer for the User model
# Used to represent user data in API responses, excluding sensitive fields.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Fields to include in the serialized output.
        # Excludes password and other sensitive fields for security.
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# Serializer for the Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # Include all fields from the Category model.
        fields = '__all__'


# Serializer for the Priority model
class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        # Include all fields from the Priority model.
        fields = '__all__'


# Serializer for the Status model
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        # Include all fields from the Status model.
        fields = '__all__'


# Serializer for the Comment model
# Includes nested UserSerializer for the author field.
class CommentSerializer(serializers.ModelSerializer):
    # Use UserSerializer to represent the author's details.
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        # Specify the fields to include in the serialized output.
        # Removed 'upvotes' and 'downvotes'
        fields = ['id', 'ticket', 'author', 'comment', 'created_at', 'updated_at']
        # Mark 'ticket' and 'author' as read-only because they are set internally
        # or based on the context (e.g., author set to the logged-in user).
        read_only_fields = ['ticket', 'author', 'created_at', 'updated_at']

    # Override create method to automatically set the author
    # based on the currently authenticated user making the request.
    def create(self, validated_data):
        # Set the author to the user from the request context.
        validated_data['author'] = self.context['request'].user
        # Call the superclass create method to save the comment.
        return super().create(validated_data)


# Serializer for the Ticket model
# Includes nested serializers for related fields like reporter, assignee, category, priority, status, and comments.
class TicketSerializer(serializers.ModelSerializer):
    # Use UserSerializer for reporter and assignee fields.
    reporter = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    # Allow assignee ID for assigning tickets.
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, allow_null=True
    )
    # Use respective serializers for category, priority, and status.
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True
    )
    priority = PrioritySerializer(read_only=True)
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=Priority.objects.all(), source='priority', write_only=True, allow_null=True
    )
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), source='status', write_only=True, allow_null=True
    )
    # Include comments related to the ticket, using CommentSerializer.
    # This is a read-only field; comments are managed via the CommentViewSet.
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        # Specify the fields to include in the serialized output.
        # Removed 'upvotes' and 'downvotes'.
        fields = [
            'id',
            'title',
            'description',
            'reporter',
            'assignee',
            'assignee_id',
            'category',
            'category_id',
            'priority',
            'priority_id',
            'status',
            'status_id',
            'created_at',
            'updated_at',
            'due_date',
            # Removed 'upvotes', 'downvotes'
            'comments',
        ]
        # Mark fields that should not be directly written via the API.
        # reporter is set automatically, comments are managed separately.
        read_only_fields = ['reporter', 'created_at', 'updated_at', 'comments']

    # Override create method to automatically set the reporter
    # based on the currently authenticated user making the request.
    def create(self, validated_data):
        # Set the reporter to the user from the request context.
        validated_data['reporter'] = self.context['request'].user
        # Call the superclass create method to save the ticket.
        return super().create(validated_data)