from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import exploredata.views

urlpatterns = [
    url(r'^$', exploredata.views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
]
