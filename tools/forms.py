from django import forms
from .models import ToolsTableOrder




class ToolsTableOrderForm(forms.ModelForm):

    class Meta:
        model = ToolsTableOrder
        fields =['width', 'height', 'show_number_of_products']