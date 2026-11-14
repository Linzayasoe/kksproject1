from django.shortcuts import render,redirect,get_object_or_404
from productinfo.models import Product
from .models import Receipt,ReceiptItem
from decimal import Decimal,InvalidOperation
from django.db import transaction

# Create your views here.
def receipt_create(request):
  products = Product.objects.all()
  error = None

  rows=[]
  if request.method == "POST":
    saletype = request.POST.get("sale_type","retail")
    payby = request.POST.get("pay_by","cash")
    customer = request.POST.get("customer","").strip() or None

    for pid,q,pr, in zip(
      request.POST.getlist("product"),
      request.POST.getlist("quantity"),
      request.POST.getlist("unit_price")
    ):
      product = Product.objects.filter(pk=pid).first() if pid else None

      try:
        qty = Decimal(q)
      except (InvalidOperation,TypeError):
        continue
      if not product or qty <= 0:
          continue

      price = product.price
      if saletype == "wholesale" and pr.strip():
        try:
          typed = Decimal(pr)
          if typed > 0:
            price = typed
        except InvalidOperation:
          pass

      rows.append((product,qty,price))

    if not rows:
      error = "ကုန်ပစ္စည်း အနည်းဆုံး တစ်ခု ထည့်ပါ။"
    else:
      with transaction.atomic():
          receipt = Receipt.objects.create(
            sale_type=saletype,
            pay_by=payby,
            customer=customer
          )
          for product,qty,pr in rows:
            receiptItem = ReceiptItem.objects.create(
              receipt=receipt,
              product=product,
              quantity=qty,
              unit_price=pr
            )
      return redirect('receipt_detail',pk=receipt.pk)
  return render(request,"receiptinfo/receipt_create.html",{"products":products,"error":error})


def receipt_view(request):
   receipt = Receipt.objects.all()
   return render(request,'receiptinfo/receipt_view.html',{'receipt':receipt})

# receipt details
def receipt_detail(request,pk):
   receipt = get_object_or_404(Receipt,pk=pk)
   return render(request,"receiptinfo/receipt_detail.html",{'receipt':receipt})