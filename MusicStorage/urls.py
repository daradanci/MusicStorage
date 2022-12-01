from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MusicStorage import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.start, name='start'),
    path('home/',views.home, name='home'),
    path('home/<str:name>/', views.object, name='object'),
    path('upload/', views.model_form_upload, name='model_form_upload'),
    path('edit/<str:file_name>/', views.model_form_edit, name='model_form_edit'),
    path('download/<str:file_name>/', views.download, name='download'),
    path('delete/<str:file_name>/', views.delete, name='delete'),
    path('log/', views.log, name='log'),
    path('reg/', views.reg, name='reg'),
    path('data_update/', views.global_data_update, name='data_update')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
