from djongo import models
from django.contrib.auth.models import User
from django.conf import settings


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    _id = models.ObjectIdField()
    BTC_amount = models.FloatField()
    USD_amount = models.FloatField()

    @classmethod
    def create(cls, user, BTC_amount, USD_amount):
        return cls(user=user, BTC_amount=BTC_amount, USD_amount=USD_amount).save()

    def __str__(self):
        return str(self.user.username)


class Order(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()
    status = models.CharField(max_length=12, default="PENDING")
    buy_sell = models.CharField(max_length=12, choices=[(
        'BUY', 'buy'), ('SELL', 'sell')], default='BUY')
    transactionId = models.PositiveIntegerField(blank=True)

    def orderValues(self) -> dict:
        modelDict: dict = {
            "id": self.id,
            "profile": self.profile,
            "onDate": self.datetime.strftime("%Y-%m-%d %H:%M"),
            "price": self.price,
            "quantity": self.quantity,
            "status": self.status,
            "buy_sell": self.buy_sell,
            "transactionId": self.transactionId,
        }
        return modelDict

    def __str__(self):
        id = self.profile.user_id
        s = User.objects.filter(id=id)[0]
        return s.username

    def publish(self):
        if self.buy_sell == 'sell' and self.profile.BTC_amount < self.quantity:
            self.delete()
            return 0
        elif self.buy_sell == 'buy' and (self.price*self.quantity) > self.profile.USD_amount:
            self.delete()
            return 0
        else:
            if self.buy_sell == 'buy':
                sellOrders = Order.objects.filter(buy_sell="sell").order_by('price')
                for sellorder in sellOrders:
                    if self.price >= sellorder.price and sellorder.quantity >= self.quantity and self.profile != sellorder.profile:
                        self.status = "EXECUTED"
                        sellorder.status = "EXECUTED"
                        self.transactionId = sellorder.id
                        sellorder.transactionId = self.id
                        self.profile.USD_amount -= (sellorder.price * self.quantity)
                        self.profile.BTC_amount += self.quantity
                        sellorder.profile.USD_amount += (sellorder.price * self.quantity)
                        sellorder.profile.BTC_amount -= self.quantity
                        sellorder.save()
                        sellorder.profile.save()
                        self.profile.save()
                        self.save()
                        break
                return self.save()

            if self.buy_sell == 'sell':
                buyOrders = Order.objects.filter(buy_sell="buy").order_by('price')
                for buyorder in buyOrders:
                    if self.price <= buyorder.price and self.profile != buyorder.profile:
                        self.status = "EXECUTED"
                        buyorder.status = "EXECUTED"
                        self.transactionId = buyorder.id
                        buyorder.transactionId = self.id
                        self.profile.USD_amount += (self.price * buyorder.quantity) 
                        self.profile.BTC_amount -= buyorder.quantity
                        buyorder.profile.USD_amount -= (self.price * buyorder.quantity)
                        buyorder.profile.BTC_amount += buyorder.quantity
                        buyorder.save()
                        buyorder.profile.save()
                        self.profile.save()
                        self.save()
                        break
                return self.save()


# Create your models here.
