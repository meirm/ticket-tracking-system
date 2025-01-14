from django.db import models
from django.forms import ValidationError


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
class Category(models.Model):
    # define the plural name
    class Meta:
        verbose_name_plural = "categories"
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Priority(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Status(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    


# Create your models here.
class Ticket(models.Model):
    issuer = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='issued_tickets')
    assignee = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='assignee_tickets')
    assigned_group = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, blank=True)
    # Store *nix-like permissions in octal, e.g. 0o750
    permissions = models.PositiveSmallIntegerField(default=0o750)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE, default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def user_has_permission(self, user, perm_type='r'):
        """
        perm_type can be 'r', 'w', or 'x' to check read, write, or execute permission.
        """
        # 1) Issuer always has read access
        if perm_type == 'r' and user == self.issuer:
            return True
        
        # 2) Determine whether 'user' is the owner, group, or others
        if user == self.assignee:
            # user bits => shift right by 6, then mask off bottom 3 bits
            bits = (self.permissions >> 6) & 0b111
        elif self.assigned_group and user.groups.filter(id=self.assigned_group.id).exists():
            # group bits => shift right by 3
            bits = (self.permissions >> 3) & 0b111
        else:
            # others bits
            bits = self.permissions & 0b111

        # 3) Map 'r', 'w', 'x' to the appropriate bit
        # rwx => r=4, w=2, x=1
        if perm_type == 'r':
            return bool(bits & 0b100)
        elif perm_type == 'w':
            return bool(bits & 0b010)
        elif perm_type == 'x':
            return bool(bits & 0b001)
        
        return False
    
    def set_permissions(self, user_bits, group_bits, others_bits):
        """
        Set permission bits in octal form (e.g., user_bits=7, group_bits=5, others_bits=0).
        """
        # user_bits <= 7, group_bits <= 7, others_bits <= 7
        # e.g., user_bits=7 => 0b111, group_bits=5 => 0b101, others_bits=0 => 0b000
        perm = (user_bits << 6) | (group_bits << 3) | others_bits
        self.permissions = perm
        self.save()
        
    def clean(self):
        super().clean()
        if self.assignee and self.assigned_group:
            if self.assigned_group not in self.assignee.groups.all():
                raise ValidationError("Assignee must belong to the assigned group.")
    
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.comment
    

class Changes(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='changes')
    actor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.change