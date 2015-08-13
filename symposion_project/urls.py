from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView

admin.autodiscover()

import symposion.views

# from pinax.apps.account.openid_consumer import PinaxConsumer

WIKI_SLUG = r"(([\w-]{2,})(/[\w-]{2,})*)"

urlpatterns = patterns("",
    (r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),

    url(r"^sponsors/prospectus/$", TemplateView.as_view(template_name='sponsor_prospectus.html'), name="sponsor_prospectus"),

    url(r"^about/", TemplateView.as_view(template_name="about.html"), name="about"),

    url(r"^venue/", TemplateView.as_view(template_name="venue.html"), name="venue"),

    url(r"^speak/", TemplateView.as_view(template_name="speak.html"), name="speak"),

    url(r"^sprints/", TemplateView.as_view(template_name="sprints.html"), name="sprints"),

    url(r"^learn/", TemplateView.as_view(template_name="learn.html"), name="learn"),

    url(r"^contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),

    url(r"^conduct/", TemplateView.as_view(template_name="conduct.html"), name="conduct"),

    url(r"^admin/", include(admin.site.urls)),

    url(r"^account/signup/$", symposion.views.SignupView.as_view(), name="account_signup"),
    url(r"^account/login/$", symposion.views.LoginView.as_view(), name="account_login"),
    url(r"^account/", include("account.urls")),

    url(r"^dashboard/", symposion.views.dashboard, name="dashboard"),
    url(r"^speaker/", include("symposion.speakers.urls")),
    url(r"^proposals/", include("symposion.proposals.urls")),
    url(r"^sponsors/", include("symposion.sponsorship.urls")),
    url(r"^boxes/", include("symposion.boxes.urls")),
    url(r"^teams/", include("symposion.teams.urls")),
    url(r"^reviews/", include("symposion.reviews.urls")),
    url(r"^schedule/", include("symposion.schedule.urls")),
    url(r"^markitup/", include("markitup.urls")),

    url(r"^su/", include("django_switchuser.urls")),

    url(r"^map/?", RedirectView.as_view(url='http://goo.gl/maps/0RQcD')),
    url(r"^m/?", RedirectView.as_view(url='http://eventmobi.com/PyConCa-2013/')),
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
