from random import uniform
from django.http import HttpResponse, JsonResponse
from myapp.models import Order, Profile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(200)
        else:
            return HttpResponse(400)
    else:
        return HttpResponse("Send Post Request with username and password")


def registerView(request):
    if request.method == 'POST':
        rUsername = request.POST['username']
        rPassword = request.POST['password']
        newUser = User.objects.create(username=rUsername, password=rPassword)
        Profile.create(user=newUser, BTC_amount=uniform(
            1.0, 10.0), USD_amount=uniform(5000.0, 20000.0))
        return HttpResponse(200)
    else:
        return HttpResponse("Send Post Request with username and password for register new user")


@login_required(login_url='/login/')
def logoutView(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def UserOrderView(request):
    userid = request.user.id
    userprofile = Profile.objects.filter(user_id=userid)[0]
    query = Order.objects.filter(profile=userprofile)
    response = []
    for order in query:
        response.append({'id': order.id,        
                         "quantity": order.quantity,
                         "price": order.price,
                         'date': order.datetime.strftime("%Y-%m-%d %H:%M"),
                         'status': order.status,
                         'buy_sell': order.buy_sell,
                         })

    return JsonResponse(response, safe=False)


@login_required(login_url='/login/')
def activeOrdersView(request):
    query = Order.objects.all()
    response = []
    for order in query:
        response.append({'id': order.id,
                         'profile': order.profile.user_id,
                         "quantity": order.quantity,
                         "price": order.price,
                         'date': order.datetime.strftime("%Y-%m-%d %H:%M"),
                         'status': order.status,
                         'buy_sell': order.buy_sell,
                         })
    return JsonResponse(response, safe=False)


@login_required(login_url='/login/')
def walletView(request):
    userprofile = Profile.objects.filter(user_id=request.user.id)

    def calculateTrend() -> dict:
        """calculate the profit made by the user and returns a dict indicating the quantity earn if the value is positive an viceversa"""
        profileOrders = Order.objects.filter(profile=userprofile[0])
        trendUSD = 0.0
        trendBTC = 0.0
        for order in profileOrders:
            if order.buy_sell == 'buy' and order.status == 'EXECUTED':
                trendUSD -= order.price
                trendBTC += order.quantity
            elif order.buy_sell == 'sell' and order.status == 'EXECUTED':
                trendUSD += order.price
                trendBTC -= order.quantity
        return {'trendUSD': trendUSD, 'trendBTC': trendBTC}
    profileTrend = calculateTrend()
    response = {}
    response.update({
        "currentUSD": userprofile[0].USD_amount,
        "currentBTC": userprofile[0].BTC_amount,
        "trendUSD": profileTrend['trendUSD'],
        "trendBTC": profileTrend['trendBTC'],
    })
    return JsonResponse(response)


@login_required(login_url='/login/')
def publishOrderView(request):
    if request.method == 'POST':
        rQuantity = request.POST['quantity']
        rPrice = request.POST['price']
        rBuy_sell = request.POST['buy_sell']
        profile = Profile.objects.filter(user_id=request.user.id)[0]
        newOrder = Order.objects.create(quantity=float(rQuantity), price=float(
            rPrice), buy_sell=rBuy_sell, profile=profile)
        if newOrder.publish() == 0:
            return HttpResponse(400) #order is deleted because didn't respect parameters
        else:
            return HttpResponse(200)

    else:
        return HttpResponse("Send Post Request with username and password for register new user")


# Create your views here.
