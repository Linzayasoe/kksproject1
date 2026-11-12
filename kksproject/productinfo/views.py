from django.shortcuts import render,redirect,get_object_or_404
from .models import Product
from .forms import ProductForm


#Product View 
def product_view(request):
    search_product = request.GET.get("search","").strip()
    status = request.GET.get("status","all")
    db_product = Product.objects.all()
  
    if search_product:
      db_product = db_product.filter(name__icontains=search_product) | db_product.filter(code__icontains=search_product)
    if status == "in":
      db_product = db_product.filter(in_stock=True)
    elif status == "out":
      db_product = db_product.filter(in_stock=False)
  
    return render (request,'productinfo/product_view.html',{'search_product':search_product,'status':status,'db_product':db_product})
  

#Product Create
def product_create(request):
  if request.method == 'POST':
    product_form = ProductForm(data=request.POST)
    if product_form.is_valid():
      product_form.save()

  else:
    product_form = ProductForm()
  return render(request,'productinfo/product_create.html',{'product_form':product_form})

#Product Edit
def product_edit(request,pk):
  product = get_object_or_404(Product,pk=pk)
  print(product)
  if request.method == "POST":
    product_form = ProductForm(data=request.POST,instance=product)
    if product_form.is_valid():
      product_form.save()
      return redirect('product_view')
  else:
    product_form = ProductForm(instance=product)
  return render(request,'productinfo/product_edit.html',{'product_form':product_form, 'product':product})

# Product Delete
def product_delete(request,pk):
  product = get_object_or_404(Product,pk=pk)
  if request.method == "POST":
    product.delete()
    return redirect('product_view')
  return render(request,'productinfo/product_delete.html',{'product':product})


