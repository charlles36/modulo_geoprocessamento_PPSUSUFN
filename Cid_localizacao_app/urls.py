"""
URL configuration for Cid_localizacao_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload_relatorio, name='upload_relatorio'),
    path('vincular_bairros', views.vincular_bairros, name='vincular_bairros'),
    path('relatorios/', views.lista_relatorios, name='lista_relatorios'),
    path('', views.index, name='index'),
    path('get_bairros', views.get_bairros, name='get_bairros'),
    path('get_cids/', views.get_cids, name='get_cids'),
    path('get_datas/', views.get_datas, name='get_datas'),
    path('get_relatorio_datas/', views.get_relatorio_datas, name='get_relatorio_datas'),
    path('delete_relatorio/<int:relatorio_id>/', views.delete_relatorio, name='delete_relatorio'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
