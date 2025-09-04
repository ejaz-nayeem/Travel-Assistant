from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password') 
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # extra claims if you want
        token['username'] = user.username
        return token

    def validate(self, attrs):
        # replace "username" with "email"
        login_data = {
            'email': attrs.get('username'),
            'password': attrs.get('password')
        }
        # map email into "username" so JWT auth works
        attrs['username'] = login_data['email']
        return super().validate(attrs)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']
        
class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for the final step of password reset.
    """
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the password.
    Requires the user to provide their current password.
    """
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return data

# accounts/serializers.py

# ... (your other serializers) ...

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    Allows changing username, first_name, and last_name.
    Email is read-only as changing it often requires a re-verification process.
    """
    email = serializers.EmailField(read_only=True) # Prevent users from changing their email via this endpoint
    
    class Meta:
        model = CustomUser
        # The "Full Name" in your Figma is typically handled by first_name and last_name
        fields = ['username', 'email', 'first_name', 'last_name']
    
class EmailChangeRequestSerializer(serializers.Serializer):
    """
    Serializer for the first step of changing a user's email.
    """
    current_password = serializers.CharField(write_only=True, required=True)
    new_email = serializers.EmailField(required=True)

    def validate_new_email(self, value):
        """
        Check if the new email is already in use by another account.
        """
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value
