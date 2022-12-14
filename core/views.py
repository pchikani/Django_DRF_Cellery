from http.client import responses
import imp, random
from time import timezone
from django.contrib.auth.models import User
from django import views
from django.views.generic import ListView , View ,TemplateView , DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from decimal import *
from datetime import datetime
import requests
from django.http import HttpResponse

from .serializers import PortfolioSerializer
from rest_framework.parsers import JSONParser
from rest_framework import mixins , status
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from .models import Portfolio, Scripe , ContactUS, Trade

def get_currprice(request):
    api_key = 'P9PL2RAXE6WZXR7L'
    scripes = Scripe.objects.all()
    for scripe in scripes:
        #url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + scripe.scripename + '&apikey=' + api_key
        url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=' + scripe.scripename + '&to_currency=INR&apikey=' + api_key
        r = requests.get(url)
        datac = r.json()
        if 'Realtime Currency Exchange Rate' in datac:
                curr_price = datac['Realtime Currency Exchange Rate']['5. Exchange Rate']
                volume = 14578
                scripe.currprice = Decimal(curr_price)
                scripe.highprice = Decimal(curr_price)
                scripe.lowprice = Decimal(curr_price)
                scripe.closeprice = Decimal(curr_price)
                scripe.volume = volume
                scripe.save()
    return redirect("core:home")

def get_intradayprice(request):
    portfolioUpdate = Portfolio.objects.filter(user=request.user).select_related('scripename')
    for scripe in portfolioUpdate:
        if scripe.scripename.currprice:
            scripe.curprice = Decimal(scripe.scripename.currprice)
            scripe.save() 

    userPortfolio = Portfolio.objects.filter(user=request.user).select_related('scripename')
    totalInvestmentAmount = Portfolio.objects.filter(user=request.user).aggregate(totalInvestmentAmount=Sum('investmentvalue'))['totalInvestmentAmount'] or 0
    totalCurrentAmount = Portfolio.objects.filter(user=request.user).aggregate(totalCurrentAmount=Sum('curvalue'))['totalCurrentAmount'] or 0
    totalProfitLoss = Portfolio.objects.filter(user=request.user).aggregate(totalProfitLoss=Sum('profitloss'))['totalProfitLoss'] or 0
    totalPercentage = 0
    if totalProfitLoss != 0 and totalInvestmentAmount != 0 : 
        totalPercentage = round(totalProfitLoss * 100 / totalInvestmentAmount,2)

    randomVal = float(random.randrange(101,989))/100

    context = {
        'object': userPortfolio,
        'totalInvestmentAmount': round(totalInvestmentAmount,2),
        'totalCurrentAmount': round(totalCurrentAmount,2),
        'totalProfitLoss': round(totalProfitLoss,2),
        'totalPercentage': totalPercentage,
        'randomVal': Decimal(round(randomVal,2))
    }
    return render(request, 'home_sub.html', context)
        


class ChartView(LoginRequiredMixin, View):
    def get(self, *args , **kwargs):
        try:
            portfolioChart = Portfolio.objects.filter(user=self.request.user).select_related('scripename')
            context = {
                'object': portfolioChart  
            }
            return render(self.request, 'chart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have any scrips in your portfolio")
            return redirect("/")

class IndexView(View):
    def get(self, *args, **kwargs):
        scripes = Scripe.objects.all()
        context = {
            'object': scripes
        } 
        return render(self.request, 'index.html', context)

class HomeView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            #get_currprice(self.request)
            portfolioUpdate = Portfolio.objects.filter(user=self.request.user).select_related('scripename')
            for scripe in portfolioUpdate:
                if scripe.scripename.currprice:
                    scripe.curprice = Decimal(scripe.scripename.currprice)
                    scripe.save() 

            userPortfolio = Portfolio.objects.filter(user=self.request.user).select_related('scripename')
            totalInvestmentAmount = Portfolio.objects.filter(user=self.request.user).aggregate(totalInvestmentAmount=Sum('investmentvalue'))['totalInvestmentAmount'] or 0
            totalCurrentAmount = Portfolio.objects.filter(user=self.request.user).aggregate(totalCurrentAmount=Sum('curvalue'))['totalCurrentAmount'] or 0
            totalProfitLoss = Portfolio.objects.filter(user=self.request.user).aggregate(totalProfitLoss=Sum('profitloss'))['totalProfitLoss'] or 0
            totalPercentage = 0
            if totalProfitLoss != 0 and totalInvestmentAmount != 0 : 
                totalPercentage = round(totalProfitLoss * 100 / totalInvestmentAmount,2)
            
            randomVal = float(random.randrange(101,989))/100

            context = {
                'object': userPortfolio,
                'totalInvestmentAmount': round(totalInvestmentAmount,2),
                'totalCurrentAmount': round(totalCurrentAmount,2),
                'totalProfitLoss': round(totalProfitLoss,2),
                'totalPercentage': totalPercentage,
                'randomVal': Decimal(round(randomVal,2))
            }
            return render(self.request, 'home.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have any scrips in your portfolio")
            return redirect("home/")

class AddPortfolioView(LoginRequiredMixin, View):
    model = Portfolio
    template_name = "add_portfolio.html"

    def get(self, *args, **kwargs):
        scripes = Scripe.objects.all()

        context = {
            'addobject': scripes
        } 
        return render(self.request, 'add_portfolio.html', context)

    def post(self, request, *args, **kwargs):
        scripe = Portfolio()
        scripe.user = self.request.user
        scripe_name = request.POST["name"]
        scripename = Scripe.objects.get(scripename=scripe_name)

        portfolio_details = Portfolio.objects.filter(user=self.request.user,scripename=scripename.id).first()
        if portfolio_details:
            scripe_total_quantity = Decimal(request.POST["quantity"]) + Decimal(portfolio_details.quantity)
            scripe_added_amount = Decimal(request.POST["quantity"]) * Decimal(request.POST["price"])
            scripe_total_amount = Decimal(scripe_added_amount) + Decimal(portfolio_details.investmentvalue)
            scripe_buy_price = Decimal(scripe_total_amount) / Decimal(scripe_total_quantity)
            scripe.buyprice = Decimal(scripe_buy_price)
            scripe.quantity = Decimal(scripe_total_quantity)
            scripe.id = portfolio_details.id
            scripe.timestamp = datetime.now()
        else:
            scripe.buyprice = Decimal(request.POST["price"])
            scripe.quantity = Decimal(request.POST["quantity"])


        scripe.scripename = scripename
        scripe.save()

        #Saving the into trade table
        trade = Trade()
        trade.user = self.request.user
        trade.scripename = scripename
        trade.buyprice = Decimal(request.POST["price"])
        trade.quantity = Decimal(request.POST["quantity"])
        trade.timestamp = datetime.now()
        trade.buysell = 'buy'
        trade.save()

        messages.info(self.request, "Scripe was added to your portfolio.")
        return redirect("/home/")

class RemovePortfolioView(LoginRequiredMixin, View):
    model = Portfolio
    template_name = "remove_portfolio.html"

    def get(self, *args, **kwargs):
        scripes = Portfolio.objects.filter(user=self.request.user).select_related('scripename')

        context = {
            'removeobject': scripes
        } 
        return render(self.request, 'remove_portfolio.html', context)

    def post(self, request, *args, **kwargs):
        scripe = Portfolio()
        scripe.user = self.request.user
        scripe_name = request.POST["name"]
        scripe_qty = request.POST["quantity"]
        scripe_price = request.POST["price"]
        scripename = Scripe.objects.get(scripename=scripe_name)

        portfolio_details = Portfolio.objects.filter(user=self.request.user,scripename=scripename.id).first()
        if portfolio_details:
            #portfolio_details.delete()
            if Decimal(portfolio_details.quantity) == Decimal(request.POST["quantity"]):
                portfolio_details.delete()

                #Saving the into trade table
                trade = Trade()
                trade.user = self.request.user
                trade.scripename = scripename
                trade.buyprice = Decimal(request.POST["price"])
                trade.quantity = Decimal(request.POST["quantity"])
                trade.timestamp = datetime.now()
                trade.buysell = 'sell'
                trade.save()

                messages.info(self.request, "Scripe was removed from your portfolio.")
                return redirect("/home/")
            
            if Decimal(request.POST["quantity"]) > Decimal(portfolio_details.quantity):
                messages.warning(self.request, "Specified quantity is greater than available quantity in Portfolio")
                return redirect('core:removeportfolio')

            if Decimal(request.POST["quantity"]) < Decimal(portfolio_details.quantity):
                scripe_total_quantity = Decimal(portfolio_details.quantity) - Decimal(request.POST["quantity"]) 
                scripe_removed_amount = Decimal(request.POST["quantity"]) * Decimal(request.POST["price"])
                scripe_total_amount = Decimal(portfolio_details.investmentvalue) - Decimal(scripe_removed_amount)
                scripe_sell_price = Decimal(scripe_total_amount) / Decimal(scripe_total_quantity)
                scripe.buyprice = Decimal(scripe_sell_price)
                scripe.quantity = Decimal(scripe_total_quantity)
                scripe.id = portfolio_details.id
                scripe.timestamp = datetime.now()
                scripe.scripename = scripename
                scripe.save()

                #Saving the into trade table
                trade = Trade()
                trade.user = self.request.user
                trade.scripename = scripename
                trade.buyprice = Decimal(request.POST["price"])
                trade.quantity = Decimal(request.POST["quantity"])
                trade.timestamp = datetime.now()
                trade.buysell = 'sell'
                trade.save()

                messages.info(self.request, "Scripe was removed from your portfolio.")
                return redirect("/home/")

class SearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_text = request.GET.get("search_box", None)
        if search_text:
            print(search_text)
            try:
                SearchItems = Portfolio.objects.filter(scripename__scripename__contains=search_text)
                randomVal = float(random.randrange(101,989))/100
                if SearchItems:
                    context = {
                        'object': SearchItems,
                        'randomVal': Decimal(round(randomVal,2))
                    }
                    return render(self.request, 'search.html', context)
                else:
                    messages.warning(
                        self.request, "No crypto available for this Search category")
                    return redirect("/home/")
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "No crypto available for this Search category")
                return redirect("/home/")
        else:
            messages.warning(
                self.request, "Please input item to Search")
            return redirect("/home/")


class ScripeDetailsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        scripeid = self.kwargs['id']
        try:
            order = Trade.objects.filter(user=self.request.user,scripename=scripeid)
            context = {
                'object': order
            }
            return render(self.request, 'scripe_details.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have any trade orders")
            return redirect("/home/")



class ContactView(View):
    model = ContactUS
    template_name = "contactUS.html"

    def get(self, *args, **kwargs):
        return render(self.request, 'contactUS.html')

    def post(self, request, *args, **kwargs):
        contact = ContactUS()
        contact.name = request.POST["name"]
        contact.email = request.POST["email"]
        contact.phone = request.POST["phone"]
        contact.subject = request.POST["subject"]
        contact.message = request.POST["message"]

        contact.save()
        messages.info(self.request, "Your request was received.")
        return redirect("/home/")

class AboutView(View):
    template_name = "about.html"
    def get(self, *args, **kwargs):
        return render(self.request, 'about.html')


class GetTokenView(LoginRequiredMixin, TemplateView):
    template_name = "get_token.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['username'] = self.request.user.username
        context['token'] = Token.objects.get(user=self.request.user)
        return self.render_to_response(context)

class AccountView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        userDetails = User.objects.get(username=self.request.user)
        context = {
            'object': userDetails
        } 
        return render(self.request, 'account_details.html', context)
    
    def post(self, request, *args, **kwargs):
        userDetails = User.objects.get(username=self.request.user)
        password = request.POST["NewPassword"]
        repassword = request.POST["RePassword"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email = request.POST["Email"]

        if not password:
            messages.warning(self.request, "Input Password is empty")
            return redirect('core:accountDetails')

        if password != repassword:
            messages.warning(self.request, "New Password & Re-Type Password does not match")
            return redirect('core:accountDetails')

        userDetails.set_password(password)
        userDetails.first_name = firstname
        userDetails.last_name = lastname
        userDetails.email = email
        userDetails.save()
        
        messages.info(self.request, "Your Account details have been updated.")
        return redirect("/home/")        


def holdings_report(request, *args, **kwargs):
    template_path = 'holdings_report.html'
    portfolioDetials = Portfolio.objects.filter(user=request.user.id).select_related('scripename')
    totalInvestmentAmount = Portfolio.objects.filter(user=request.user.id).aggregate(totalInvestmentAmount=Sum('investmentvalue'))['totalInvestmentAmount'] or 0
    totalCurrentAmount = Portfolio.objects.filter(user=request.user.id).aggregate(totalCurrentAmount=Sum('curvalue'))['totalCurrentAmount'] or 0
    totalProfitLoss = Portfolio.objects.filter(user=request.user.id).aggregate(totalProfitLoss=Sum('profitloss'))['totalProfitLoss'] or 0
    totalPercentage = round(totalProfitLoss * 100 / totalInvestmentAmount,2)
    
    userDetails = User.objects.get(username=request.user)


    context = {
        'object': portfolioDetials,
        'totalInvestmentAmount': round(totalInvestmentAmount,2),
        'totalCurrentAmount': round(totalCurrentAmount,2),
        'totalProfitLoss': round(totalProfitLoss,2),
        'totalPercentage': Decimal(totalPercentage),
        'firstName': userDetails.first_name,
        'lastName': userDetails.last_name,
        'email': userDetails.email
    }
       
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Holdings_report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
    #return render(request, 'holdings_report.html', context)


def trade_report(request, *args, **kwargs):
    template_path = 'trade_report.html'
    tradeDetails = Trade.objects.filter(user=request.user.id)
    userDetails = User.objects.get(username=request.user)

    context = {
        'object': tradeDetails,
        'firstName': userDetails.first_name,
        'lastName': userDetails.last_name,
        'email': userDetails.email
    }
       
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="trade_report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

class PortfolioList(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

    def get(self, request, token):
        tokendata = Token.objects.all()
        for tokenval in tokendata:
            if str(tokenval) == token:
                print("token matches")
                return self.list(request)
            else:
                print("token does not match")
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, token):
        tokendata = Token.objects.all()
        for tokenval in tokendata:
            if str(tokenval) == token:
                print("token matches")
                return self.create(request)
            else:
                print("token does not match")
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class PortfolioDetails(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    lookup_field = 'id'
    #permission_classes = [IsAuthenticated]
    #authentication_classes = (TokenAuthentication,)

    def get(self, request, id, token):
        tokendata = Token.objects.all()
        for tokenval in tokendata:
            if str(tokenval) == token:
                print("token matches")
                return self.retrieve(request, id=id)
            else:
                print("token does not match")
        return Response(status=status.HTTP_401_UNAUTHORIZED)
            
    def put(self, request , id, token):
        tokendata = Token.objects.all()
        for tokenval in tokendata:
            if str(tokenval) == token:
                print("token matches")
                return self.update(request, id=id)
            else:
                print("token does not match")
        return Response(status=status.HTTP_401_UNAUTHORIZED)
        

    def delete(self, request, id, token):
        tokendata = Token.objects.all()
        for tokenval in tokendata:
            if str(tokenval) == token:
                print("token matches")
                return self.destroy(request, id=id)
            else:
                print("token does not match")
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    


        

