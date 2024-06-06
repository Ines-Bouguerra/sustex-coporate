from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from esganalyse import consumers
from django.conf import settings
from django.conf.urls.static import static
from chatbot import consumers_chat
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="My API description",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="Awesome License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('',include('sustexcoporateapp.urls')),
    path('admin/', admin.site.urls),
    path('user/',include('usermanagement.urls')),
    path('esg/',include('esganalyse.urls')),
    path('benchmarking/',include('benchmarking.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ws/wss url patterns
websocket_urlpatterns = [
    # consumer for a particular user
      path('ws/data/', consumers.DashboardConsumer.as_asgi()),
      path('ws/chatbot/',consumers_chat.ChatConsumer.as_asgi()), 
]