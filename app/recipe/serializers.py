"""
serializers for recipe
"""

from rest_framework import serializers
from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """
        Model serializers
    """
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'link', 'price', 'time_minutes']
        read_only = ['id']

class RecipeDetailSerializer(serializers.ModelSerializer):
    """details serializer"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']