from django.db import models
from django.conf import settings
from decimal import *

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Scripe(models.Model):
    scripename = models.CharField(max_length=100)
    currprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    highprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    lowprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    closeprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    volume = models.IntegerField(default=0)

    def __str__(self):
        return self.scripename

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    scripename = models.ForeignKey(Scripe, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    buyprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    investmentvalue = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    curprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    curvalue = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    profitloss = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def save(self, *args, **kwargs):
        self.investmentvalue = Decimal(self.buyprice) * Decimal(self.quantity)
        self.curvalue = Decimal(self.curprice) * Decimal(self.quantity)
        self.profitloss = Decimal(self.curvalue) - Decimal(self.investmentvalue)
        super(Portfolio,self).save(*args, **kwargs)

    @property
    def percentage(self):
        return round(Decimal(self.profitloss) * 100 / Decimal(self.investmentvalue),2)

class ContactUS(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.TextField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class Trade(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    scripename = models.ForeignKey(Scripe, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    buyprice = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)
    buysell = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)     
        

