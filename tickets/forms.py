from .models import Ticket, Comment
from django import forms
from django.contrib.auth.models import Group, User
class DateInput(forms.DateInput):
    input_type = 'date'
    
class TicketForm(forms.ModelForm):
    assigned_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'assigned_group', 'assignee', 'status', 'due_date']
        widgets = {
            'due_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['due_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['assigned_group'].queryset = Group.objects.all().order_by('name')

        # Initialize assignee queryset
        self.fields['assignee'].queryset = User.objects.filter(is_active=True).order_by('username')

        if 'assigned_group' in self.data:
            try:
                group_id = int(self.data.get('assigned_group'))
                self.fields['assignee'].queryset = self.fields['assignee'].queryset.filter(groups__id=group_id).order_by('username')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.assigned_group:
            self.fields['assignee'].queryset = self.fields['assignee'].queryset.filter(groups__id=self.instance.assigned_group.id).order_by('username')

    def save(self, commit=True):
        ticket = super().save(commit=False)
        ticket.assigned_group = self.cleaned_data.get('assigned_group')
        if commit:
            ticket.save()
        return ticket
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})