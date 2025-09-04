from django.urls import path
from .views import (signup, MyTokenObtainPairView, social_signup_signin, 
send_password_reset_otp, verify_password_reset_otp,
set_new_password, change_password,user_profile, logout,request_email_change, # <-- Import new view
verify_email_change)
    
   
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #path('send-otp/', send_otp, name='send_otp'),
    #path('verify-otp/', verify_otp_and_signup, name='verify_otp_and_signup'),
    path('signup/', signup, name='signup'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('social-login/', social_signup_signin, name='social_signup_signin'),
    path('password-reset/send-otp/', send_password_reset_otp, name='send_password_reset_otp'),
    path('password-reset/verify-otp/', verify_password_reset_otp, name='verify_password_reset_otp'),
    path('password-reset/set-new/', set_new_password, name='set_new_password'),
    path('change-password/', change_password, name='change_password'),
    
    path('profile/', user_profile, name='user-profile'),
    path('profile/request-email-change/', request_email_change, name='request-email-change'),
    path('profile/verify-email-change/', verify_email_change, name='verify-email-change'),
    path('logout/', logout, name='logout'),
]