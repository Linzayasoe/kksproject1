from django.db import models
from productinfo.models import Product

class Receipt(models.Model):

  class PayBy(models.TextChoices):
    CASH ="cash"
    KPAY = "Kpay"

  class SaleType(models.TextChoices):
    RETAIL = "retail"
    WHOLESALE = "wholesale"

  v_code = models.CharField(max_length=20,unique=True,null=True,blank=True)
  customer = models.CharField(max_length=200,null=True,blank=True)
  pay_by = models.CharField(max_length=10,choices=PayBy.choices,default=PayBy.CASH)
  created_at = models.DateTimeField(auto_now_add=True)
  sale_type = models.CharField(max_length=10,choices=SaleType.choices,default=SaleType.RETAIL)


  # Receipt Voucher Code
  def save(self,*args,**kwargs):
    super().save(*args,**kwargs)
    if not self.v_code:
      self.v_code = f"v{self.pk:04d}"
      super().save(update_fields=['v_code'])

  # total amount
  @property
  def total_amount(self):
    return sum(item.total for item in self.items.all())

  def __str__(self):
    return f"{self.v_code} Receipt"

class ReceiptItem(models.Model):
  receipt = models.ForeignKey(Receipt,on_delete=models.CASCADE,related_name="items")
  product = models.ForeignKey(Product,on_delete=models.PROTECT)
  quantity = models.DecimalField(max_digits=10,decimal_places=2)
  unit_price = models.DecimalField(max_digits=10,decimal_places=2)

  @property
  def total(self):
    return self.quantity * self.unit_price

  def __str__(self):
    return f"{self.pk} ReceiptItem"
