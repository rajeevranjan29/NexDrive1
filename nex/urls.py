from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('ride/', include('ride.urls', namespace='ride')),
    path('driver/', include('driver.urls', namespace='driver')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 