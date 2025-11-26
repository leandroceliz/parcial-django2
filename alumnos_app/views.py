import io
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .forms import RegistroForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Alumno
from .forms import RegistroForm
from django.core.mail import send_mail
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.views import View # Para nuestra vista de PDF
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.contrib import messages



# Usamos CreateView para el registro, es la forma mas limpia
class RegistroUsuario(CreateView):
    model = User
    form_class = RegistroForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('login') # Redirigir al login despues del registro

    # Sobreescribir form_valid para enviar el email y/o loguear si es necesario
    def form_valid(self, form):
        response = super().form_valid(form)
       # 2. Enviar el correo de bienvenida
        try:
            asunto = '¡Bienvenido a nuestro proyecto Parcial Django!'
            mensaje = (
                f'Hola {self.object.username},\n\n'
                'Gracias por registrarte. Ya puedes iniciar sesión y comenzar '
                'a gestionar tus alumnos.\n\n'
                '¡Éxito en tu parcial!'
            )
            
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL, # O 'tu_email_de_envio@ejemplo.com'
                recipient_list=[self.object.email], # El email del nuevo usuario
                fail_silently=False,
            )
            print(f"Correo de bienvenida enviado a: {self.object.email}")
            
        except Exception as e:
            # Es importante no fallar la creación de usuario si el email falla
            print(f"Error al enviar correo de bienvenida: {e}")

        return response
       


# 1. Vista de Dashboard (Listado de Alumnos)
class DashboardListView(LoginRequiredMixin, ListView):
    model = Alumno
    context_object_name = 'alumnos'
    template_name = 'alumnos_app/dashboard.html'
    
    # REQUISITO: Solo mostrar los alumnos creados por el usuario logueado
    def get_queryset(self):
        # Filtra los alumnos donde el campo 'usuario' es igual al usuario actual (self.request.user)
        return Alumno.objects.filter(usuario=self.request.user).order_by('apellido')

# 2. Vista de Creacion de Alumnos
class AlumnoCreateView(LoginRequiredMixin, CreateView):
    model = Alumno
    # Estos son los campos que se mostraran en el formulario
    fields = ['nombre', 'apellido', 'legajo'] 
    template_name = 'alumnos_app/alumno_form.html'
    success_url = reverse_lazy('dashboard') # Redirigir al dashboard al terminar

    # REQUISITO: Asignar automáticamente el usuario actual antes de guardar
    def form_valid(self, form):
        # Antes de guardar, asignamos el objeto User actual al campo 'usuario' del modelo Alumno
        form.instance.usuario = self.request.user 
        return super().form_valid(form)

# Actualizamos la vista de inicio para redirigir al dashboard si ya está logueado
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirige al dashboard
    return render(request, 'index.html')

class GenerarPDFView(LoginRequiredMixin, View):
    # Puedes definir el correo del docente aquí o usar una variable de settings.
    EMAIL_DOCENTE = 'docente.parcial@universidad.edu' 

    def get(self, request, pk, *args, **kwargs):
        # 1. Obtener el alumno (se asegura que el alumno pertenece al usuario logueado)
        alumno = get_object_or_404(
            Alumno, 
            pk=pk, 
            usuario=self.request.user
        )

        # 2. Generar el PDF en memoria (buffer)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter # Dimensiones de la página (carta)

        # 3. Dibujar Contenido (Reportlab)
        p.setFont("Helvetica-Bold", 18)
        p.drawString(inch, height - inch, "Reporte Oficial de Alumno")
        
        # Llenar los datos
        p.setFont("Helvetica", 12)
        y_pos = height - 1.8 * inch
        
        p.drawString(inch, y_pos, f"Nombre Completo: {alumno.nombre} {alumno.apellido}")
        y_pos -= 0.3 * inch
        p.drawString(inch, y_pos, f"Legajo/DNI: {alumno.legajo}")
        y_pos -= 0.3 * inch
        p.drawString(inch, y_pos, f"Generado por: {self.request.user.username} ({self.request.user.email})")

        p.showPage() # Finaliza la página
        p.save()     # Guarda el PDF al buffer

        # 4. Mover el puntero del buffer al inicio para que el correo pueda leerlo
        buffer.seek(0)
        
        # Nombre del archivo adjunto
        filename = f"reporte_alumno_{alumno.legajo}.pdf"
        
        # 5. Enviar el PDF adjunto por Email
        try:
            asunto = f"Reporte de {alumno.nombre} {alumno.apellido}"
            cuerpo = f"Adjunto se encuentra el reporte en PDF del alumno {alumno.nombre} {alumno.apellido}."
            
            email = EmailMessage(
                subject=asunto,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                # Enviar al docente y al mismo usuario que lo solicitó (o solo al usuario)
                to=[self.EMAIL_DOCENTE, self.request.user.email] 
            )
            # Adjuntar el archivo desde el buffer
            email.attach(filename, buffer.read(), 'application/pdf')
            email.send()
            
            # 6. Éxito: Notificar y redirigir
            messages.success(request, f"¡El reporte PDF de {alumno.nombre} ha sido enviado por correo!")
            
        except Exception as e:
            # 7. Error: Notificar y redirigir
            print(f"Error de Correo al enviar PDF: {e}")
            messages.error(request, f"Error al enviar el PDF. Revisa la configuración de correo. ({e})")
            
        return redirect('dashboard')