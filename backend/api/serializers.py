from rest_framework import serializers
from .models import AppUser, Dataset


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'email', 'created_at']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        if AppUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already taken"})

        if AppUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already registered"})

        return attrs

    def create(self, validated_data):
        user = AppUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class DatasetSerializer(serializers.ModelSerializer):
    uploaded_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')

    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'summary']


class DatasetDetailSerializer(serializers.ModelSerializer):
    uploaded_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')

    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'summary', 'data']