from django import forms
from .models import *

class ChangeCategoryForm(forms.Form):
    title = forms.ModelChoiceField(queryset=Category.objects.all())

class ChangeVendorForm(forms.Form):
    title = forms.ModelChoiceField(queryset=Supply.objects.all())

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields ="__all__"


class SizeAttributeForm(forms.ModelForm):
    class Meta:
        model = SizeAttribute
        fields =['title', 'qty']

    def update_product(self, sizeAttr):
        product = sizeAttr.product_related
        old_qty = sizeAttr.qty
        new_qty = self.cleaned_data.get('qty')
        qty = new_qty - old_qty
        product.qty += qty
        product.save()
        sizeAttr.qty += qty
        sizeAttr.save()


class CostumerForm(forms.ModelForm):
    class Meta:
        #title = forms.CharField(widget=forms.CharField(attrs={'class':'hello'}))
        model = Costumers
        fields ="__all__"


class CostumerEshopForm(forms.ModelForm):
    class Meta:
        #title = forms.CharField(widget=forms.CharField(attrs={'class':'hello'}))
        model = Costumers
        fields =['title','phone','phone1','cellphone','email','address','zip_code','description','category']
    def costumer_cat(self):
        self.category = 'c'

class Supplier_new(forms.ModelForm):


    class Meta:
        model = Supply
        fields = ('title','description','afm','phone','balance')

class CategoryNew(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'



class TaxesForm(forms.ModelForm):

    class Meta:
        model = TaxesCity
        fields = '__all__'




class CreateColor(forms.ModelForm):

    class Meta:
        model = Color
        fields = '__all__'


class CreateSize(forms.ModelForm):

    class Meta:
        model = Size
        fields = '__all__'

class ChangeQtyOrderForm(forms.ModelForm):

    class Meta:
        model = ChangeQtyOrder
        fields = '__all__'


class ChangeQtyOrderItemForm(forms.ModelForm):

    class Meta:
        model = ChangeQtyOrderItem
        fields = '__all__'

    def update_product(self, product):
        qty = self.cleaned_data.get('qty')
        product.qty += qty
        product.save()

    def update_size(self, size):
        qty = self.cleaned_data.get('qty')
        size.product_related.qty += qty
        size.product_related.save()
        size.qty += qty
        size.save()


class ChangeQtyOrderItemSizeForm(forms.ModelForm):

    class Meta:
        model = ChangeQtyOrderItemSize
        fields = '__all__'


    def update_product(self):
        product_size = self.cleaned_data.get('title')
        qty = self.cleaned_data.get('qty')
        product_size.qty += qty
        product_size.save()

        product = product_size.color.product
        product.reserve += qty
        product.save()

        product_color = product_size.color
        product_color.qty += qty
        product_color.save()



class BrandForm(forms.ModelForm):

    class Meta:
        model = Brands
        fields ='__all__'
        exclude =['width','height']



class CategorySiteForm(forms.ModelForm):
    class Meta:
        model = CategorySite
        fields = '__all__'

class ProductCharacteristicsForm(forms.ModelForm):
    object_id= forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = ProductCharacteristics
        fields = ['title','description','content_type','object_id']

class CharForm(forms.ModelForm):

    class Meta:
        model = Characteristics
        fields = '__all__'

class CharValForm(forms.ModelForm):

    class Meta:
        model = CharacteristicsValue
        fields = '__all__'


class CreatePhoto(forms.ModelForm):

    class Meta:
        model = ProductPhotos
        fields = '__all__'



