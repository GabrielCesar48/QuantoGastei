from django.contrib import admin
from .models import Categoria, Transacao

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'usuario', 'padrao']
    list_filter = ['tipo', 'padrao']
    search_fields = ['nome']

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'tipo', 'valor', 'data', 'usuario', 'conta_origem']
    list_filter = ['tipo', 'data', 'created_at']
    search_fields = ['descricao', 'usuario__username']
    date_hierarchy = 'data'