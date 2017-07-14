from django import forms
from PoS.models import PaymentMethod,Shipping
from .models import  WelcomePage, FrontPageMessages, Footer, SiteSettings
from newsletter.models import NewsLetterEmail

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True, label='Ονομα', widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=70, required=True, label='Επίθετο', widget=forms.TextInput(attrs={'class':'form-control'}))
    city = forms.CharField(max_length=70,required=True, label='Πόλη', widget=forms.TextInput(attrs={'class':'form-control'}))
    address = forms.CharField(max_length=100, required=True, label='Διευθυνση', widget=forms.TextInput(attrs={'class':'form-control'}))
    state = forms.CharField(max_length=100, label='Νομός (Προαιρετικό)',required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    zip = forms.IntegerField(required=True, label='ΤΚ', widget=forms.NumberInput(attrs={'class':'form-control'}))
    cell_phone = forms.IntegerField(required=True, label='Κινητό', widget=forms.NumberInput(attrs={'class':'form-control'}))
    phone = forms.IntegerField(label='Σταθερό (Προαιρετικό)',required=False, widget=forms.NumberInput(attrs={'class':'form-control'}))
    email = forms.EmailField(label='Email (Προαιρετικό)', required=False, widget=forms.EmailInput(attrs={'class':'form-control'}))
    notes = forms.CharField( required=False, label='Γράψτε ότι θέλετε', widget=forms.Textarea(attrs={'class':'form-control'}))
    delivery = forms.CharField(required=True,)
    payment = forms.CharField(required=True,)


class NewsLetterForm(forms.ModelForm):
    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={'class':'form-control'}))
    class Meta:
        model = NewsLetterEmail
        fields = ['email']
    def clean_email(self):
        cleaned_data = super(NewsLetterForm, self).clean()
        email = cleaned_data.get('email')
        if email:
            exists = NewsLetterEmail.objects.filter(email = email)
            if exists:
                raise forms.ValidationError('Το email %s έχει εγγραφεί ήδη.'%(email))
        return cleaned_data

class WelcomePageForm(forms.ModelForm):
    class Meta:
        model = WelcomePage
        fields = '__all__'


class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'

class FrontPageMessagesForm(forms.ModelForm):
    class Meta:
        model = FrontPageMessages
        fields = '__all__'

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'


