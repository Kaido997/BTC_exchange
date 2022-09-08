from datetime import datetime
from pprint import pprint
from django.test import TestCase, Client
from myapp.models import Profile, Order
from django.contrib.auth.models import User
from random import uniform
from faker import Faker
from django.urls import reverse
import json


def makeRandomUserWithOrder(orderType, quantity=1.0, price=5000.0, BTC_amount=uniform(1.0, 10.0), USD_amount=uniform(5000.0, 10000.0)):
    fake = Faker()
    user_username = fake.first_name_male()
    User.objects.create_user(username=user_username, password='testpsw')
    user = User.objects.latest("id")

    Profile.create(user=user, BTC_amount=BTC_amount, USD_amount=USD_amount)
    p = Profile.objects.filter(user_id=user.id)[0]

    order = Order.objects.create(
        profile=p,
        price=price,
        quantity=quantity,
        buy_sell=orderType)
    order.save()
    return user_username


class authTestCase(TestCase):
    c = Client()

    def test_user_can_register(self):
        response = self.c.post(
            '/register/', {'username': 'test', 'password': 'testpsw'})
        self.assertEqual(json.loads(response.content), 200)

    def test_user_can_login(self):
        User.objects.create_user(username="test", password="testpsw")
        response = self.c.post(
            '/login/', {'username': 'test', 'password': 'testpsw'})
        self.assertEqual(json.loads(response.content), 200)


class ProfileTestCase(TestCase):

    def setUp(self):
        User.objects.create(username='test', password='testpassword')
        s = User.objects.all()
        Profile.create(user=s[0], BTC_amount=uniform(
            1.0, 10.0), USD_amount=uniform(5000.0, 10000.0))

    def test_user_has_BTC_quantity(self):
        queryset = Profile.objects.all()
        tst = False
        btc = 0.0
        for _object in queryset:
            if not 1.000 <= _object.BTC_amount <= 10.000:
                tst = True
                btc = _object.BTC_amount
                break
        self.assertEqual(
            tst, False, f"BTC quantity should be lower than 10 and it is {btc}")


class OrderTestCase(TestCase):

    def setUp(self):
        self.c = Client()

    def test_order_is_correct(self):
        makeRandomUserWithOrder('sell', 1.0, 5000.0)
        makeRandomUserWithOrder('buy', 1.0, 5000.0)
        randomOrders = Order.objects.all()
        randomProfiles = Profile.objects.all()
        for order in randomOrders:
            self.assertIn(order.profile, randomProfiles,
                          "order profile is not present in current profiles")
            self.assertTrue(5000.0 <= order.price <= 20000.0,
                            f"order price is out of range current price is {order.price}")
            self.assertTrue(1.0 <= order.quantity <= 10.0,
                            f"order quantity is out of range current quantity is {order.quantity}")
        # for o in randomOrders:
            # pprint(o.orderValues())

    def test_order_can_execute(self):
        Order.objects.all().delete()
        makeRandomUserWithOrder('sell', 1.0, 5000.0)
        makeRandomUserWithOrder('buy', 1.0, 5000.0)
        testOrders = Order.objects.all()
        testOrders[0].publish()
        for o in testOrders:
            # pprint(o.orderValues())
            self.assertEqual(o.status, 'EXECUTED')

    def test_order_transaction_is_correct(self):
        Order.objects.all().delete()
        makeRandomUserWithOrder('buy', 1.0, 5000.0)
        makeRandomUserWithOrder('sell', 1.0, 5000.0)
        sellprofile = Order.objects.filter(buy_sell="sell")[0].profile
        buyprofile = Order.objects.filter(buy_sell="buy")[0].profile
        sellprofilecredit = {
            'usd': sellprofile.USD_amount,
            'btc': sellprofile.BTC_amount,
        }
        buyprofilecredit = {
            'usd': buyprofile.USD_amount,
            'btc': buyprofile.BTC_amount,
        }

        orders = Order.objects.all()
        orders[0].publish()

        sellorder = Order.objects.filter(buy_sell="sell")[0]
        self.assertEqual(sellorder.profile.USD_amount,
                         sellprofilecredit['usd']+5000.0)
        self.assertEqual(sellorder.profile.BTC_amount,
                         sellprofilecredit['btc']-1.0)

        buyorder = Order.objects.filter(buy_sell="buy")[0]
        self.assertEqual(buyorder.profile.USD_amount,
                         buyprofilecredit['usd']-5000.0)
        self.assertEqual(buyorder.profile.BTC_amount,
                         buyprofilecredit['btc']+1.0)

    def test_transaction_2BTC_5000USD(self):
        Order.objects.all().delete()
        makeRandomUserWithOrder('buy', 2.0, 5000.0, BTC_amount=2.0, USD_amount=10000)
        makeRandomUserWithOrder('sell', 4.0, 5000.0, BTC_amount=6.0, USD_amount=5000)
        sellprofile = Order.objects.filter(buy_sell="sell")[0].profile
        buyprofile = Order.objects.filter(buy_sell="buy")[0].profile

        sellprofilecredit = {
            'usd': sellprofile.USD_amount,
            'btc': sellprofile.BTC_amount,
        }
        buyprofilecredit = {
            'usd': buyprofile.USD_amount,
            'btc': buyprofile.BTC_amount,
        }

        orders = Order.objects.all()
        orders[1].publish()

        sellorder = Order.objects.filter(buy_sell="sell")[0]
        self.assertEqual(sellorder.profile.USD_amount,
                         sellprofilecredit['usd']+10000.0, f'seller has : {sellorder.profile.USD_amount} USD')
        self.assertEqual(sellorder.profile.BTC_amount,
                         sellprofilecredit['btc']-2.0, f'seller has : {sellorder.profile.BTC_amount} BTC')

        buyorder = Order.objects.filter(buy_sell="buy")[0]
        self.assertEqual(buyorder.profile.USD_amount,
                         buyprofilecredit['usd']-10000.0, f'buyer has : {buyorder.profile.USD_amount} USD')
        self.assertEqual(buyorder.profile.BTC_amount,
                         buyprofilecredit['btc']+2.0, f'buyer has : {buyorder.profile.BTC_amount} BTC')    

    def test_no_transactions_are_made(self):
        Order.objects.all().delete()
        makeRandomUserWithOrder('buy', 2.0, 5000.0, BTC_amount=2.0, USD_amount=10000)
        makeRandomUserWithOrder('sell', 4.0, 10000.0, BTC_amount=6.0, USD_amount=5000)
        sellprofile = Order.objects.filter(buy_sell="sell")[0].profile
        buyprofile = Order.objects.filter(buy_sell="buy")[0].profile

        sellprofilecredit = {
            'usd': sellprofile.USD_amount,
            'btc': sellprofile.BTC_amount,
        }
        buyprofilecredit = {
            'usd': buyprofile.USD_amount,
            'btc': buyprofile.BTC_amount,
        }

        orders = Order.objects.all()
        orders[0].publish()

        sellorder = Order.objects.filter(buy_sell="sell")[0]
        self.assertEqual(sellorder.profile.USD_amount,
                         sellprofilecredit['usd'], f'seller has : {sellorder.profile.USD_amount} USD')
        self.assertEqual(sellorder.profile.BTC_amount,
                         sellprofilecredit['btc'], f'seller has : {sellorder.profile.BTC_amount} BTC')
        self.assertEqual(sellorder.status, 'PENDING')

        buyorder = Order.objects.filter(buy_sell="buy")[0]
        self.assertEqual(buyorder.profile.USD_amount,
                         buyprofilecredit['usd'], f'buyer has : {buyorder.profile.USD_amount} USD')
        self.assertEqual(buyorder.profile.BTC_amount,
                         buyprofilecredit['btc'], f'buyer has : {buyorder.profile.BTC_amount} BTC')
        self.assertEqual(buyorder.status, 'PENDING')

    
    def test_user_cant_make_order(self):
        new_user = User.objects.create_user(username="test", password="test")
        new_prof = Profile.create(user=new_user, BTC_amount=uniform(
            1.0, 1.0), USD_amount=uniform(5000.0, 10000.0))
        self.c.login(username="test", password='test')

        self.testorder = {
            'quantity': 2.0,
            'price': 6000.0,
            'buy_sell': 'sell',
        }

        response = self.c.post("/publish/", self.testorder)
        # print(Order.objects.latest('datetime').orderValues())
        self.assertEqual(json.loads(response.content), 400)

    def test_user_can_make_order(self):
        new_user = User.objects.create_user(username="test", password="test")
        new_prof = Profile.create(user=new_user, BTC_amount=uniform(
            1.0, 1.0), USD_amount=uniform(5000.0, 10000.0))
        self.c.login(username="test", password='test')

        self.testorder = {
            'quantity': 1.0,
            'price': 6000.0,
            'buy_sell': 'sell',
        }

        response = self.c.post("/publish/", self.testorder)
        # print(Order.objects.latest('datetime').orderValues())
        self.assertEqual(json.loads(response.content), 200)


class WalletTestCase(TestCase):

    def setUp(self):
        self.c = Client()

    def test_user_can_get_wallet_trend(self):
        makeRandomUserWithOrder('buy', 1.0, 5000.0)
        makeRandomUserWithOrder('sell', 1.0, 5000.0)
        s = self.c.login(username=User.objects.all()[
                         0].username, password='testpsw')
        response = self.c.get(reverse('wallet'), follow=True)
        deResp = json.loads(response.content)
        self.assertEqual(type(deResp["currentUSD"]),
                         float, f"{response.content}")
        self.assertEqual(type(deResp["currentBTC"]),
                         float, f"{response.content}")

    def test_wallet_trend_value_is_correct(self):
        testuser1 = makeRandomUserWithOrder('buy', 1.0, 5000.0)
        testuser2 = makeRandomUserWithOrder('sell', 1.0, 5000.0)
        Order.objects.all()[0].publish()
        s = self.c.login(username=testuser2, password='testpsw')
        response = self.c.get(reverse('wallet'), follow=True)
        deResp = json.loads(response.content)
        print(deResp)
        self.assertEqual(deResp["trendUSD"], 5000.0, f"{response.content}")
        self.assertEqual(deResp["trendBTC"], -1.0, f"{response.content}")



# Create your tests here.
