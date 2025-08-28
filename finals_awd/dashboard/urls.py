from django.urls import path

from dashboard import views
from .views import dashboard_view, view_notifications, all_notifications_view

from .api import current_user_api, user_notifications_api

urlpatterns=[
    path('', dashboard_view, name='dashboard'),
    path('notifications/', view_notifications, name = 'view_notifications'),

    path('notifications/all/', all_notifications_view, name='all_notifications'),

    #Show more(partial) status updates
    path('status/load_more/', views.load_more_statuses, name='load_more_statuses'),

    #REST Api
    path('api/user/', current_user_api, name='user_api'),

    #API for notifications
    path('api/notifications/', user_notifications_api, name='user_notifications_api'),
]