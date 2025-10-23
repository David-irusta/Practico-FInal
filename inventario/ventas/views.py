from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaFormSet
from django.db import transaction
from productos.models import Product
from django.db.models import F
from django.contrib import messages
from django.urls import reverse
from django.views.generic import DetailView, ListView

class CrearVentaView(View):
    template_name = 'ventas/crear_venta.html'

    def get(self, request, *args, **kwargs):
        venta_form = VentaForm()
        formset = ItemVentaFormSet()
        return render(request, self.template_name, {
            'venta_form': venta_form,
            'formset': formset
        })
    def post(self, request, *args, **kwargs):
        venta_form = VentaForm(request.POST)
        formset = ItemVentaFormSet(request.POST)
        if not venta_form.is_valid() or not formset.is_valid():
            return render(request, self.template_name, {
                'venta_form': venta_form,
                'formset': formset
            })
        with transaction.atomic():
            venta = venta_form.save()
            venta.total = 0
            venta.save()
            total = 0
            productos_ids = [int(f.cleaned_data['producto'].id)for f in formset.cleaned_data if f and not f.get('DELETE', False)]
            productos = Product.objects.select_for_update().filter(id__in=productos_ids).in_bulk()

            for form in formset:
                if not form.cleaned_data or form.cleaned_data.get('Delete', False):
                    continue
                producto = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                precio_unitario = form.cleaned_data['precio_unitario']
                prod_obj = productos.get(producto.id)
                if prod_obj.stock < cantidad:
                    transaction.set_rollback(True)
                    messages.error(request, f'Stock insuficiente para el producto {producto.nombre}. Disponible: {prod_obj.stock}')
                    return render(request, self.template_name, {
                        'venta_form': venta_form,
                        'formset': formset
                    })
                subtotal = cantidad * precio_unitario
                ItemVenta.objects.create(
                    venta=venta,
                    producto=prod_obj,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )

                Product.objects.filter(id=prod_obj.id).update(stock=F('stock') - cantidad)
                total += subtotal
            
            venta.total = total
            venta.save()
        messages.success(request, f"Venta {venta.codigo} creada exitosamente.")
        return redirect('ventas:detalle_venta', pk=venta.pk)
    
class VentaDetailView(View):
    template_name = 'ventas/detalle_venta.html'
    model = Venta

class VentaListView(ListView):
    model = Venta
    template_name = 'ventas/detalle_venta.html'
    paginate_by = 20