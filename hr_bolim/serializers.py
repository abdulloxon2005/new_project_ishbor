from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    consent_given = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'role', 'consent_given')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Parollar mos kelmadi.")
        if not data.get('consent_given'):
            raise serializers.ValidationError("Siz maxfiylik siyosatiga rozilik berishingiz kerak (GDPR).")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['email'], # Use email as username
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'candidate'),
            password=validated_data['password'],
            consent_given=validated_data['consent_given'],
            consent_date=timezone.now()
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
