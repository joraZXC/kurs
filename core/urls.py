from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('zones/', views.zone_list, name='zone_list'),
    path('zones/<int:zone_id>/', views.zone_detail, name='zone_detail'),
    path('zones/create/', views.zone_create, name='zone_create'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('tickets/purchase/', views.ticket_purchase, name='ticket_purchase'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('zones/staff/', views.staff_management, name='staff_management'),
    path('zones/<int:zone_id>/remove/employer/', views.remove_employer_from_zone, name='remove_employer_from_zone'),
    path('admin/event/create/', views.admin_event_create, name='admin_event_create'),
    path('register/organizer/', views.register_organizer, name='register_organizer'),
    path('zones/staff/', views.staff_management, name='staff_management'),
    
]