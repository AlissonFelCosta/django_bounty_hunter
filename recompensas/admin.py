from django.contrib import admin

from .models import Bando, Cacador, Cartaz, Procurado


@admin.register(Bando)
class BandoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'area_atuacao')
    search_fields = ('nome', 'area_atuacao')


@admin.register(Cacador)
class CacadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'reputacao')
    search_fields = ('nome',)


@admin.register(Procurado)
class ProcuradoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'apelido', 'nivel_periculosidade', 'bando')
    list_filter = ('nivel_periculosidade', 'bando')
    search_fields = ('nome', 'apelido')


@admin.register(Cartaz)
class CartazAdmin(admin.ModelAdmin):
    list_display = ('procurado', 'status', 'valor_recompensa', 'cacador', 'data_emissao')
    list_filter = ('status',)
    search_fields = ('procurado__nome',)
