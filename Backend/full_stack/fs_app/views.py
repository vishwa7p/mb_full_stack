from django.shortcuts import render
# Create your views here.
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, DeleteView
from django.views.generic.base import View
from datetime import datetime, timedelta
import jwt
from .models import User
from .sending_email import send_otp
from django.core.cache import cache
from django.contrib.auth.models import Group


class Registration(TemplateView):
    template_name = 'index.html'

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        company = request.POST.get("company")
        dob = request.POST.get("dob")
        address = request.POST.get("address")
        password = request.POST.get("password")
        users = User()
        users.first_name = first_name
        users.last_name = last_name
        users.email = email
        users.username = email
        users.company = company
        users.address = address
        users.dob = dob
        users.set_password(password)
        my_group = Group.objects.get(name="Manager")
        my_group.user_set.add(users.id)
        send_otp.delay(email)
        users.save()
        return redirect('/mb_demoapp/home')


class AddEmployee(TemplateView):
    template_name = 'add-form.html'

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        dob = request.POST.get("dob")
        address = request.POST.get("address")
        city = request.POST.get("city")
        password = request.POST.get("password")
        users = User()
        users.first_name = first_name
        users.last_name = last_name
        users.email = email
        users.username = email
        users.mobile_number = mobile
        users.address = address
        users.dob = dob
        users.city = city
        users.set_password(password)
        users.save()
        return redirect('/mb_demoapp/home')


class EmpDeleteView(DeleteView):
    model = User
    template_name = "delete.html"
    success_url = reverse_lazy('emp-list')


class EmployeeDetails(View):

    def get(self, request):
        context = {}
        users = User.objects.all().order_by("first_name")
        context['users'] = users
        return render(request, "home.html", context)


class EmpUpdateView(UpdateView):
    model = User
    template_name = 'update.html'
    context_object_name = 'user'
    fields = ('first_name', 'last_name', 'mobile_number',)
    success_url = reverse_lazy('emp-list')


class Login(TemplateView):
    template_name = 'login.html'
    context_object_name = 'users'

    def post(self, request):
        username = request.POST.get('login_email')
        password = request.POST.get('login_password')
        context = {}
        user = authenticate(username=username, password=password)
        if user:
            try:
                self.users = User.objects.get(username=username)
            except Exception as e:
                print(e)
                pass
            payload = {"username": self.users.username,
                       "user_id": self.users.id,
                       "iat": str(datetime.utcnow())}
            self.encode_token = jwt.encode({"data": payload, "exp": datetime.utcnow() + timedelta(minutes=30)}).decode()
            cache.set("jwt_token", self.encode_token)
            return redirect("/mb_demoapp/home")
        else:
            context["message"] = "Invalid credentials"
            return render(request, 'login.html', context)


class Logout(TemplateView):

    def post(self, request):
        cache.delete("jwt_token")

        return redirect("/mb_demoapp/login ")
