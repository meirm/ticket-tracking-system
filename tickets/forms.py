from .models import Ticket, Comment
from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'
    
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'assignee', 'status', 'due_date']
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
        # We want to be able to assign only to active users
        self.fields['assignee'].queryset = self.fields['assignee'].queryset.filter(is_active=True)
        self.fields['due_date'].widget.attrs.update({'class': 'form-control'})
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})