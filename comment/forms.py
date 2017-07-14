from django import forms
from .models import *



class CommentForm(forms.Form):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'class':'form-control', 'id':'content'}))
    #content = forms.CharField(label='', widget=forms.Textarea(attrs={'class':'form-control','id':'content'}))

