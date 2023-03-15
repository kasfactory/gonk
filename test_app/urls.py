from django.urls import path, include

urlpatterns = [
    path('tasks/', include('gonk.contrib.rest_framework.urls')),
]
