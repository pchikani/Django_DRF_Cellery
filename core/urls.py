from django.urls import path, re_path
from rest_framework.authtoken import views
from .views import IndexView, AboutView, AccountView, HomeView, AddPortfolioView, PortfolioList, get_currprice, get_intradayprice , SearchView , ContactView , RemovePortfolioView, PortfolioDetails , GetTokenView, ChartView , ScripeDetailsView, holdings_report, trade_report


app_name = 'core'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('', IndexView.as_view(), name='index'),
    path('addportfolio/', AddPortfolioView.as_view(), name='addportfolio'),
    path('removeportfolio/', RemovePortfolioView.as_view(), name='removeportfolio'),
    path('search-list/', SearchView.as_view(), name='search-list'),
    path('contact-us/', ContactView.as_view(), name='contact-us'),
    path('about/', AboutView.as_view(), name='about'),
    path('refreshdata/', get_intradayprice , name='refreshdata'),
    path('latestprice/', get_currprice, name='latestprice' ),
    re_path('api/portfoliolist/(?P<token>\w+)/$', PortfolioList.as_view(), name='portfoliolist'),
    re_path('api/portfoliodetails/(?P<id>\w+)/(?P<token>\w+)/$', PortfolioDetails.as_view(), name='portfoliodetails'),
    path('gettoken/', GetTokenView.as_view(), name='gettoken'),
    path('chart/', ChartView.as_view(), name='chart'),
    path('scripedetails/<int:id>/', ScripeDetailsView.as_view(), name='scripedetails'),
    path('holdings-report/', holdings_report, name='holdings-report'),
    path('trade-report/', trade_report, name='trade-report'),
    path('account-details/', AccountView.as_view(), name='accountDetails')
]