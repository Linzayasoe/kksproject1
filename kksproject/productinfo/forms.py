from .models import Product
from django import forms 

class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
    fields = ('name','price','in_stock',)
  
  def clean_price(self):
    price = self.cleaned_data['price']
    if price < 0:
      raise forms.ValidationError("စျေးနှုန်း သုညထက် ပိုကြီးရပါမည်။")
    return price