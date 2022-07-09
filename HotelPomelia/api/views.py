from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Energy
from rest_framework.viewsets import ModelViewSet
from .serializer import EnergySerializer
import redis

# set the web page where we will receive external information in Json format
class EnergyViewSet(ModelViewSet):
    serializer_class = EnergySerializer
    queryset = Energy.objects.all()

# define the home page
def home(request):
    return render(request, "api/index.html")

# create an account
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fisrtname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        email = request.POST.get('email')

        # account creation rules
        if User.objects.filter(username=username):
            messages.error(request, "Username already registered in our database, please provide another credential.")
            return render(request, "api/signup.html")
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered in our database, please provide another credential.")
            return render(request, "api/signup.html")
        if password != confirmpassword:
            messages.error(request, "the password provided does not match, use the same credential.")
            return render(request, "api/signup.html")
        if not username.isalnum():
            messages.error(request, "the Username contains not allowed characters, use only letters and numbers.")
            return render(request, "api/signup.html")

        myUser = User.objects.create_user(username, email, password)
        myUser.first_name = fisrtname
        myUser.last_name = lastname
        myUser.save()

        messages.success(request, "Your Account has been created now you can Login")

        return redirect('/signin/')

    return render(request, "api/signup.html")

# login setting
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            fName = user.first_name
            lName = user.last_name

            if User.is_staff:
                client = redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)
                ip = getClientIp(request)
                lastIp = client.get(ip)

                if lastIp is None:
                    client.set('name', str(User.last_name))
                    client.set('ip', ip)

                if lastIp != ip:
                    messages.error(request, "attention the access IP address is different"
                                            " from the one used previously!")
                    client.set('name', str(User.last_name))
                    client.set('ip', ip)

            watts = Energy.objects.filter().order_by('-date')

            totalProduced = []
            for watt in watts:
                totalProduced.append(float(watt.produced_energy_in_watt))
            sumTotalProduced = sum(totalProduced)

            totalConsumed = []
            for watt in watts:
                totalConsumed.append(float(watt.consumed_energy_in_watt))
            sumTotalConsumed = sum(totalConsumed)

            lastWatt = Energy.objects.last()

            return render(request, "api/Report-Chart.html", {'watts': watts,
                                                            'totalConsumed': sumTotalConsumed,
                                                            'totalProduced': sumTotalProduced,
                                                            'fName': fName,
                                                            'lName': lName,
                                                            'lastWatt': lastWatt})
        else:
            messages.error(request, "Username or Password are incorrect, please provide valid credentials")
            return render(request, "api/Signin.html")

    return render(request, "api/Signin.html")

# sign out option
def signout(request):
    logout(request)
    return redirect('home')

# report chart differentiated by user
@login_required(login_url='signin')
def ReportChart(request):

    if User.is_staff:
        client = redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)
        ip = getClientIp(request)
        lastIp = client.get(ip)

        if lastIp is None:
            client.set('name', str(User.last_name))
            client.set('ip', ip)

        if lastIp != ip:
            messages.error(request, "attention the access IP address is different"
                                    " from the one used previously!")
            client.set('name', str(User.last_name))
            client.set('ip', ip)


    watts = Energy.objects.filter().order_by('-date')

    response = []
    for watt in watts:
        response.append(
            {
                'datetime': watt.date,
                'wattProduced': watt.produced_energy_in_watt,
                'wattConsumed': watt.consumed_energy_in_watt,
                'hash': watt.hash
            }
        )

    totalProduced = []
    for watt in watts:
        totalProduced.append(float(watt.produced_energy_in_watt))
    sumTotalProduced = sum(totalProduced)

    totalConsumed = []
    for watt in watts:
        totalConsumed.append(float(watt.consumed_energy_in_watt))
    sumTotalConsumed = sum(totalConsumed)

    response.append(
        {
            'totalProduced': sumTotalProduced,
            'totalConsumed': sumTotalConsumed
        }
    )

    lastWatt = Energy.objects.last()

    return render(request, "api/Report-Chart.html", {'watts': watts,
                                                    'totalConsumed': sumTotalConsumed,
                                                    'totalProduced': sumTotalProduced,
                                                    'lastWatt': lastWatt})

# find the user's IP
def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip