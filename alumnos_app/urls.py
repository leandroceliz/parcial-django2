from django.urls import path
from .views import index, RegistroUsuario, DashboardListView, AlumnoCreateView, GenerarPDFView 
urlpatterns = [
    path('', index, name='index'), # Pagina de inicio
    path('registro/', RegistroUsuario.as_view(), name='registro'), # Nuestra vista de registro
    path('dashboard/', DashboardListView.as_view(), name='dashboard'), 
    path('alumno/crear/', AlumnoCreateView.as_view(), name='alumno_crear'),
    path('alumno/<int:pk>/generar_pdf/', GenerarPDFView.as_view(), name='generar_pdf'),
]