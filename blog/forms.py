from django import forms
from .models import *
from PIL import Image
from django.core.files import File



class PostCreate(forms.ModelForm):
    title = forms.CharField(label="Τίτλος 'Αθρου", widget=forms.TextInput(attrs={'onkeyup':"myTitle()",}))
    lead_content = forms.CharField(label='Πρώτα Σχόλια', widget=forms.Textarea(attrs={'onkeyup':"myLeadCon()",}))
    content = forms.CharField(label='Βασικό Κείμενο', widget=forms.Textarea(attrs={'onkeyup':"myCon()",}))
    #content = forms.CharField(label='Βασικό Κείμενο', widget=FroalaEditor(attrs={'onkeyup':"myCon()",}))
    #user = forms.ChoiceField(widget=forms.HiddenInput())
    #publish = forms.DateTimeField(widget=forms.DateTimeField())
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['publish', 'user']

class PostTagForm(forms.ModelForm):

    class Meta:
        model = PostTags
        fields= '__all__'

class PostCategoryForm(forms.ModelForm):

    class Meta:
        model = PostCategory
        fields = '__all__'


class CreateBlogOnFly(forms.ModelForm):
    title = forms.CharField(required=True, label='Ονομασία', widget=forms.TextInput(attrs={'class': 'form-group'}))
    #user = forms.ChoiceField(required=True, widget=forms.ChoiceInput(attrs={'class': 'form-group'}))
    class Meta:
        model = Post
        fields = '__all__'

class PhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = BlogGallery
        fields = ('file', 'x', 'y', 'width', 'height', )
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'image/*'  # this is not an actual validation! don't rely on that!
            })
        }

    def save(self):
        photo = super(PhotoForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(photo.file.path)

        return photo

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = "__all__"

class GalleryForm(forms.ModelForm):
    class Meta:
        model = BlogGallery
        fields = '__all__'