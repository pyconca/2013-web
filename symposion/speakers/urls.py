from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from symposion.speakers.views import speakers_json


urlpatterns = patterns("symposion.speakers.views",
    url(r"^create/$", "speaker_create", name="speaker_create"),
    url(r"^create/(\w+)/$", "speaker_create_token", name="speaker_create_token"),
    url(r"^edit/(?:(?P<pk>\d+)/)?$", "speaker_edit", name="speaker_edit"),
    url(r"^profile/(?P<pk>\d+)/$", "speaker_profile", name="speaker_profile"),
    url(r"^staff/create/(\d+)/$", "speaker_create_staff", name="speaker_create_staff"),
    url(r"^speakers.json$", cache_page(300)(speakers_json), name="speakers_json"),
)
