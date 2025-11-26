from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluye las URLs de autenticación (Login/Logout, etc.)
    path('cuentas/', include('django.contrib.auth.urls')),
    # Incluye las URLs de tu app principal (Dashboard, CRUD de Alumnos)
    path('', include('alumnos_app.urls')),
    path('herramientas/', include('scraper_app.urls')),
]