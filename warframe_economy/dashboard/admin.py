import typing
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import PrimeItem
import typing


@admin.register(PrimeItem)
class PrimeItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_name', 'primeset_name',)

