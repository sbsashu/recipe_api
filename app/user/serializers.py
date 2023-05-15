"""serializers for models"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    """serialier for user model"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, "min_length": 5 }}

    def create(self, validate_data):
        """create user and return with encrypted pass code"""
        return get_user_model().objects.create_user(**validate_data)

    def update(self, instance, validated_data):
        """update the date"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user

class UserTokenSerializer(serializers.Serializer):
    """sreializer for token serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """validate insput field"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate the user')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs