# IdleHunter URL configuration
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path, re_path
from django.contrib import admin
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from config.views import home

# Admin branding
admin.site.site_header = "IdleHunter Yönetim"
admin.site.site_title = "IdleHunter Yönetim"
admin.site.index_title = "IdleHunter Yönetim"

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="IdleHunter API",
        default_version="v1",
        description="IdleHunter REST API: VMs, data sources, health.",
        contact=openapi.Contact(name="IdleHunter"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

# Unlocalized URLs (admin, auth, set_language, dashboard, api, swagger)
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", include("apps.web.urls")),
    path("api/", include("config.api_urls")),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
if getattr(settings, "ENABLE_MFA", False):
    try:
        urlpatterns.append(path("mfa/", include("mfa.urls")))
    except Exception:
        pass

# Localized URLs: home requires login and role; anonymous users are redirected to login
urlpatterns += i18n_patterns(
    path("", home, name="home"),
    prefix_default_language=False,
)
