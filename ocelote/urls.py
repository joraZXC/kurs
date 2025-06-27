from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from core.views_auth import CustomLoginView
from django.contrib.auth.views import LogoutView
from core.views import event_create, admin_event_create
from core.views import register, home, zone_list, zone_detail, zone_create, event_list, event_create, event_edit, ticket_purchase, review_list, review_create, analytics_dashboard, profile
app_name = 'core'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    path('zones/', zone_list, name='zone_list'),
    path('zones/<int:pk>/', zone_detail, name='zone_detail'),
    path('zones/create/', zone_create, name='zone_create'),
    path('events/', event_list, name='event_list'),
    path('events/<int:pk>/edit/', event_edit, name='event_edit'),
    path('tickets/purchase/', ticket_purchase, name='ticket_purchase'),
    path('reviews/', review_list, name='review_list'),
    path('reviews/create/', review_create, name='review_create'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('profile/', profile, name='profile'),
    
]