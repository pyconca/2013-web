from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView

from symposion.sponsorship.views import sponsors_json

urlpatterns = patterns("symposion.sponsorship.views",
    url(r"^$", TemplateView.as_view(template_name="sponsorship/list.html"), name="sponsor_list"),
    url(r"^apply/$", "sponsor_apply", name="sponsor_apply"),
    url(r"^add/$", "sponsor_add", name="sponsor_add"),
    url(r"^(?P<pk>\d+)/$", "sponsor_detail", name="sponsor_detail"),
    url(r"^featured/(?P<sponsor>\w+)$", "sponsor_featured", name="sponsor_featured"),
    url(r"^sponsors.json$", cache_page(300)(sponsors_json), name="sponsors_json"),
)
