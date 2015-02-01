from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url

js_info_dict = {
    'packages': ('ittc.cache',),
}

urlpatterns = patterns('ittc.cache.views',
    url(r'^flush$', 'flush', name='flush'),
    url(r'^stats/json$', 'stats_json', name='stats_json'),
    url(r'^stats/tms/(?P<t>[^/]+)/(?P<stat>[^/]+)/(?P<z>[^/]+)/(?P<x>[^/]+)/(?P<y>[^/]+)\.(?P<ext>(png|gif|jpg|jpeg))$', 'stats_tms', name='stats_tms'),
    url(r'^stats/geojson/(?P<z>[^/]+)/(?P<stat>[^/]+)\.geojson$', 'stats_geojson', name='stats_geojson'),
    url(r'^tms/$', 'capabilities_all_xml', name='capabilities_all_xml'),
    url(r'^tms/(?P<slug>[^/]+)/$', 'capabilities_service', name='capabilities_service'),
    url(r'^tms/(?P<slug>[^/]+)/(?P<z>[^/]+)/(?P<x>[^/]+)/(?P<y>[^/]+)\.(?P<ext>(png|gif|jpg|jpeg))$', 'tile_tms', name='tile_tms'),
    url(r'^bing/(?P<slug>[^/]+)/(?P<u>[^/]+)\.(?P<ext>(png|gif|jpg|jpeg))$', 'tile_tms', name='tile_bing')
)
