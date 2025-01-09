# cookbook/schema.py
import graphene
from graphene_django import DjangoObjectType

from .models import Ticket, Comment
from django.contrib.auth.models import User

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("__all__")

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("__all__")


class TicketType(DjangoObjectType):
    class Meta:
        model = Ticket
        fields = ("__all__")

class Query(graphene.ObjectType):
    all_tickets = graphene.List(TicketType)
    all_comments = graphene.List(CommentType)
    all_users = graphene.List(UserType)
    # get individual ticket by id
    ticket = graphene.Field(TicketType, id=graphene.Int(required=True))
    # get individual comment by id
    comment = graphene.Field(CommentType, id=graphene.Int(required=True))
    # get individual user by id
    user = graphene.Field(UserType, id=graphene.Int(required=True))

    def resolve_ticket(root, info, id):
        try:
            if info.context.user.is_anonymous:
                return Ticket.objects.none()
            else:
                return Ticket.objects.get(pk=id)
        except Ticket.DoesNotExist:
            return None
        
    def resolve_comment(root, info, id):
        try:
            if info.context.user.is_anonymous:
                return Comment.objects.none()
            else:
                return Comment.objects.get(pk=id)
        except Comment.DoesNotExist:
            return None
        
    def resolve_user(root, info, id):
        try:
            if info.context.user.is_anonymous:
                return User.objects.none()
            else:
                return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    def resolve_all_users(root, info):
        # We can easily optimize query count in the resolve method
        if info.context.user.is_anonymous:
            return User.objects.none()
        else:
            return User.objects.all()

    def resolve_all_comments(root, info):
        # We can easily optimize query count in the resolve method
        if info.context.user.is_anonymous:
            return Comment.objects.none()
        else:
            return Comment.objects.select_related('ticket').all()

    def resolve_all_tickets(root, info):
        # We can easily optimize query count in the resolve method
        if info.context.user.is_anonymous:
            return Ticket.objects.none()
        else:
            return Ticket.objects.all()

schema = graphene.Schema(query=Query)