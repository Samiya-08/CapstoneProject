from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'apps'

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('tags', views.TagViewSet, basename='tag')
router.register('articles', views.ArticleViewSet, basename='article')
router.register('comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),

    path('', include(router.urls)),
]