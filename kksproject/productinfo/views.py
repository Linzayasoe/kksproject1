from django.shortcuts import render,redirect,get_object_or_404
from .models import Product
from .forms import ProductForm
from receiptinfo.models import Receipt,ReceiptItem
from django.db.models import Sum,F,ExpressionWrapper,DecimalField
from django.utils import timezone
from django.db.models.functions import Coalesce
#Product View & search filter
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

def index(request):

  # receipt Count
  count = Receipt.objects.count()
  kpay  = Receipt.objects.filter(pay_by='kpay').count()
  cash  = Receipt.objects.filter(pay_by="cash").count()


  # cash & kpay
  total = cash + kpay
  cash_pct = (cash / total * 100) if total else 0
  kpay_pct = (kpay / total * 100) if total else 0

  # retail & wholesale
  retail = Receipt.objects.filter(sale_type='retail').count()
  wholesale = Receipt.objects.filter(sale_type='wholesale').count()
  total_sale_type = retail + wholesale
  retail_pct = (retail / total_sale_type * 100) if total else 0
  wholesale_pct = (wholesale / total_sale_type * 100) if total else 0

  # last receipt
  last_receipt = Receipt.objects.order_by('-created_at')[:3]

  # highest amount 
  highest_amount = ReceiptItem.objects.filter(
    receipt__created_at__date=timezone.localdate()
  ).values(
    'product__name'
  ).annotate(
    qty=Sum('quantity'),
    amount=Sum(
        ExpressionWrapper(
            F('quantity') * F('unit_price'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )
  ).order_by('-amount')[:1]

  # today income
  today_income =ReceiptItem.objects.filter(
  receipt__created_at__date=timezone.localdate()
  ).aggregate(
    total=Coalesce(
        Sum(
            ExpressionWrapper(
                F('quantity') * F('unit_price'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        ),
        0,
        output_field=DecimalField(max_digits=20, decimal_places=2)
    )
  )['total']
  
  return render(request,'productinfo/index.html',{'count':count,'kpay':kpay,'cash':cash,'cash_pct':cash_pct,'kpay_pct':kpay_pct,'retail':retail,
  'wholesale':wholesale,'retail_pct':retail_pct,'wholesale_pct':wholesale_pct,'last_receipt':last_receipt,'highest_amount':highest_amount,'today_income':today_income})
