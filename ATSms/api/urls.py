from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    MenteeLanguageSelectView,
    MenteeSetupView,
    MentorSetupView,
    MatchMentorView,
    TechPathwayView,
    MentorResourceView,
    MenteeResourceView,
    MenteeQuickSetupView,
)
from .ussd import ussd_callback
from .auth_views import RegisterView

router = DefaultRouter()
router.register(r'mentor/upload-resource', MentorResourceView, basename='mentor-resource')

urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Mentee endpoints
    path('mentee/language-select/', MenteeLanguageSelectView.as_view(), name='mentee-language-select'),
    path('mentee/setup/', MenteeSetupView.as_view(), name='mentee-setup'),
    path('mentee/tech-pathway/', TechPathwayView.as_view(), name='tech-pathway'),
    path('mentee/resources/', MenteeResourceView.as_view(), name='mentee-resources'),
    path('mentee/quicksetup/', MenteeQuickSetupView.as_view(), name='mentor-quicksetup'),
    
    
    # Mentor endpoints
    path('mentor/setup/', MentorSetupView.as_view(), name='mentor-setup'),
    # path('mentee/quicksetup/', MenteeQuickSetupView.as_view(), name='mentor-quicksetup'),
    
    # Matching endpoint
    path('match-mentor/', MatchMentorView.as_view(), name='match-mentor'),
    
    # USSD endpoint
    path('ussd/callback/', ussd_callback, name='ussd-callback'),
]