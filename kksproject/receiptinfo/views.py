from django.shortcuts import render,redirect,get_object_or_404
from productinfo.models import Product
from .models import Receipt,ReceiptItem
from decimal import Decimal,InvalidOperation
from django.db import transaction
from django.contrib.auth.decorators import login_required

@login_required
def receipt_create(request):
  products = Product.objects.filter(in_stock=True)
  error = None
  form_data = {"sale_type":"retail","pay_by":"cash","customer":"","rows":[]}

  rows=[]
  if request.method == "POST":
    saletype = request.POST.get("sale_type","retail")
    payby = request.POST.get("pay_by","cash")
    customer = request.POST.get("customer","").strip() or None

    # Keep what was typed so the form can be refilled if there is an error
    form_data = {"sale_type":saletype,"pay_by":payby,"customer":customer or "","rows":[]}
    has_bad_row = False

    if saletype not in Receipt.SaleType.values: saletype = "retail"
    if payby not in Receipt.PayBy.values: payby = "cash"

    for pid,q,pr, in zip(
      request.POST.getlist("product"),
      request.POST.getlist("quantity"),
      request.POST.getlist("unit_price")
    ):

      if not pid and not q.strip():
        continue

      product = Product.objects.filter(pk=pid).first() if pid.isdigit() else None

      try:
        qty = Decimal(q)
      except InvalidOperation:
        qty = None

      bad = not product or qty is None or not qty.is_finite() or qty <= 0
      form_data["rows"].append({"product":pid,"quantity":q,"unit_price":pr,"bad":bad})

      # Check every row first. Nothing is saved if any row is wrong.
      if bad:
        has_bad_row = True
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

    if not form_data["rows"]:
      error = "ကုန်ပစ္စည်း အနည်းဆုံး တစ်ခု ထည့်ပါ။"
    elif has_bad_row:
      error = "ကုန်ပစ္စည်းနှင့် အရေအတွက် နှစ်ခုလုံး မှန်ကန်စွာ ဖြည့်ပါ။"
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
  return render(request,"receiptinfo/receipt_create.html",{"products":products,"error":error,"form_data":form_data})
 

@login_required
def receipt_view(request):
   receipt = Receipt.objects.filter(is_void=False).prefetch_related('items__product').order_by('-created_at')
   return render(request,'receiptinfo/receipt_view.html',{'receipt':receipt})

# receipt details
@login_required
def receipt_detail(request,pk):
   receipt = get_object_or_404(Receipt,pk=pk)
   return render(request,"receiptinfo/receipt_detail.html",{'receipt':receipt})

@login_required
def receipt_void(request,pk):
  void = get_object_or_404(Receipt,pk=pk)
  if request.method == "POST":
    void.is_void = True
    void.save(update_fields=['is_void'])
  return redirect('receipt_detail',pk=pk)
