from django.urls import path 
from . import views

app_name = 'ventas'

urlpatterns = [
    path('crear_venta/',
         views.CrearVentaView.as_view(), 
         name='crear_venta'),
    path('<int:pk>/detalle_venta/',
         views.VentaDetailView.as_view(), 
         name='detalle_venta'),
    path('lista_ventas/',
         views.VentaListView.as_view(),
            name='lista_ventas'),
]
