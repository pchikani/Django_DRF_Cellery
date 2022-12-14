from rest_framework import serializers
from .models import Portfolio , Scripe

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'

