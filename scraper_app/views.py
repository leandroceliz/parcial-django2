import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.views import View # <-- Importar View o DetailView, si no lo hiciste
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import BusquedaForm

class ScraperView(LoginRequiredMixin, View):
    template_name = 'scraper_app/scraper_form.html'

    def get(self, request):
        form = BusquedaForm()
        return render(request, self.template_name, {'form': form, 'resultados': None})

    def post(self, request):
        form = BusquedaForm(request.POST)
        resultados = []

        if form.is_valid():
            keyword = form.cleaned_data['palabra_clave']

            # REEMPLAZA ESTA URL por una página web educativa real si lo deseas.
            url = 'http://example.com' 
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Lógica de scraping básica (busca párrafos que contengan la palabra clave)
                for p in soup.find_all('p'):
                    if keyword.lower() in p.text.lower():
                        extracto = p.text[:200] + ('...' if len(p.text) > 200 else '')
                        resultados.append({
                            'titulo': f"Resultado para '{keyword}'",
                            'extracto': extracto,
                            'url': url 
                        })
                        if len(resultados) >= 5: 
                            break

                # Envío por Correo (Punto 5 - Se dispara con el botón "Enviar Resultados por Email")
                if 'enviar_correo' in request.POST and resultados:
                    self.enviar_resultados_correo(request.user, resultados, keyword)
                    messages.success(request, f"Resultados de '{keyword}' enviados a tu correo ({request.user.email}).")

            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error al acceder a la URL para scraping: {e}")

        return render(request, self.template_name, {'form': form, 'resultados': resultados})


    def enviar_resultados_correo(self, user, resultados, keyword):
        cuerpo = f"Resultados del scraping para '{keyword}':\n\n"
        for i, res in enumerate(resultados, 1):
            cuerpo += f"{i}. Título: {res['titulo']}\n   Extracto: {res['extracto']}\n   URL: {res['url']}\n\n"

        send_mail(
            subject=f"Resultados de Scraping: {keyword}",
            message=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email], 
            fail_silently=True,
        )