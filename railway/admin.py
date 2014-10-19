# -*- coding: utf-8 -*-
from django.contrib import admin
from railway.models import Railway, StationOrder, TravelTime, WomenOnlyCar


class StationOrderInline(admin.TabularInline):
    model = StationOrder
    fk_name = 'railway'


class RailwayAdmin(admin.ModelAdmin):
    inlines = [
            StationOrderInline,
            ]
    
admin.site.register(TravelTime)
admin.site.register(WomenOnlyCar)
admin.site.register(Railway, RailwayAdmin)

