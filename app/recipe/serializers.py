"""
serializers for recipe
"""

from rest_framework import serializers
from core.models import Recipe, Tag

class TagSerializer(serializers.ModelSerializer):
    """Tag serializer data"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """
       RecipeSerializer
    """
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title','time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def create(self, validated_data):
        """create recipe with tags"""
        print(tags, 'tagg')
        tags = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user

        for t in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **t,
            )
            recipe.tags.add(tag_obj)
        return recipe

class RecipeDetailSerializer(serializers.ModelSerializer):
    """details serializer"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']