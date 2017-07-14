from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CostumerAccount


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Ονοματεπώνυμο')
    email = forms.EmailField(label='Email Address',widget=forms.EmailInput)
    email2 = forms.EmailField(label='Confirm email address', widget=forms.EmailInput)
    phone = forms.IntegerField(widget=forms.NumberInput)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm Password")

    class Meta:
        model = User
        fields =['username', 'email', 'email2','password','password2' ]

    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        email_qs = User.objects.filter(email = email)
        if email != email2:
            raise forms.ValidationError('Emails must match!')
        if email_qs.exists():
            raise forms.ValidationError('This email exists!')

        return email

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if password != password2:
            raise forms.ValidationError('The passwords dont match!')
        return password


class RegisterFormFromAdmin(forms.ModelForm):
    username = forms.CharField(label='Ονοματεπώνυμο')
    email = forms.EmailField(label='Email Address',widget=forms.EmailInput)
    email2 = forms.EmailField(label='Confirm email address', widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput,)
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm Password")
    phone = forms.CharField(widget=forms.NumberInput,required=False)
    phone1 = forms.CharField(widget=forms.NumberInput, required=False)
    cell = forms.CharField(widget=forms.NumberInput)
    address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=50)
    zip_code= forms.IntegerField()
    notes= forms.CharField(max_length=150,required=False)

    class Meta:
        model = User
        fields =['username', 'email', 'email2','password','password2',
                 'cell','phone','phone','phone1','address','city','zip_code','notes', ]

    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        email_qs = User.objects.filter(email = email)
        if email != email2:
            raise forms.ValidationError('Emails must match!')
        if email_qs.exists():
            raise forms.ValidationError('This email exists!')

        return email

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if password != password2:
            raise forms.ValidationError('The passwords dont match!')
        return password





class CreateCostumerFromAdmin(forms.ModelForm):
    username = forms.CharField(label='Ονοματεπώνυμο')
    email = forms.EmailField(label='Email Address',widget=forms.EmailInput, required=False)


    phone = forms.CharField(widget=forms.NumberInput,required=False)
    phone1 = forms.CharField(widget=forms.NumberInput, required=False)
    cell = forms.CharField(widget=forms.NumberInput, required=False)
    address = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=50, required=False)
    zip_code= forms.IntegerField(required=False)
    notes= forms.CharField(max_length=150,required=False)

    class Meta:
        model = User
        fields =['username', 'email',
                 'cell','phone','phone','phone1','address','city','zip_code','notes', ]


    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if password != password2:
            raise forms.ValidationError('The passwords dont match!')
        return password





class CreateCostumerPosForm(forms.ModelForm):
    is_eshop = forms.BooleanField(False, widget=forms.HiddenInput())
    class Meta:
        model = CostumerAccount
        fields =['first_name', 'last_name', 'shipping_address_1', 'shipping_city','phone','cellphone', 'is_eshop']







class CostumerProfileForm(forms.ModelForm):

    model = CostumerAccount
    fields =['first_name','last_name']




class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if self.username and self.password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Username is not correct')
            elif not user.check_password():
                raise forms.ValidationError('Password is incorrect')


        return super(LoginForm,self).clean(*args, **kwargs)


class CostumerPageEditDetailsForm(forms.ModelForm):
    first_name = forms.CharField(label='Ονομα', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label='Επίθετο', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_address_1 = forms.CharField(label='Διεύθυνση Αποστολής', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_city = forms.CharField(label='Πόλη', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_zip_code = forms.IntegerField(label='Ταχυδρομικός Κώδικας', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone = forms.IntegerField(label='Τηλέφωνο', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone1 = forms.IntegerField(label='Τηλέφωνο2', widget=forms.TextInput(attrs={'class':'form-control'}))
    cellphone = forms.IntegerField(label='Κινητό', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = CostumerAccount
        fields =['first_name', 'last_name', 'shipping_address_1' ,'shipping_city', 'shipping_zip_code', 'phone', 'phone1', 'cellphone']