from django.contrib import admin
from .models import Conta

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario', 'tipo', 'saldo_atual', 'ativa']
    list_filter = ['tipo', 'ativa', 'created_at']
    search_fields = ['nome', 'usuario__username']