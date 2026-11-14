from django.db import models

# Create your models here.
class Product(models.Model):
  code = models.CharField(max_length=20,unique=True,null=True,blank=True)
  name = models.CharField(max_length=200)
  price = models.IntegerField()
  in_stock = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  

  def __str__(self):
    return f"{self.code} - {self.name}"

  def save(self,*args,**kwargs):
    super().save(*args,**kwargs)
    if not self.code:
      self.code = f"k{self.pk:04d}"
      super().save(update_fields=['code'])