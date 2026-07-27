from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Root URL ke liye simple view
def home_view(request):
    return HttpResponse("<h1>Welcome to Nexus Technologies Backend</h1><p>Go to <a href='/api/'>/api/</a> for endpoints.</p>")

urlpatterns = [
    path('', home_view), # <-- Yeh line add kar dein root URL ke liye
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]