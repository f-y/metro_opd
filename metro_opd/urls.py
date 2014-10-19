from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^station/list', "station.views.get_station_list"),
    url(r'^station/arrivedtrain', "trainplace.views.get_trains_by_time_and_station"),
)
