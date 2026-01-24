from . import views
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('tweet/', views.index,name='index'),

] 