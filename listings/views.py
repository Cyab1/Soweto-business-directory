from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import filters
from .models import Business, Category, Review
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BusinessSerializer, CategorySerializer, ReviewSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "owner"]  # Filter by category or owner
    search_fields = ["name", "address"]  # Search by name or address
