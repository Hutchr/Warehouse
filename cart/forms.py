from django import forms

class ProductAddToCartForm(forms.Form):
    qty =forms.IntegerField(widget=forms.TextInput(attrs={'size':2,
                                                          'value':1,
                                                          'class':'qty',
                                                          'maxlength':5}),
                                                          min_value=1)
    product_slug = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, request = None, *args, **kwargs):
        self.request = request
        super(ProductAddToCartForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError('Πρέπει να ενεργοποιήσης τα cookies.')
        return self.cleaned_data