from rest_framework import routers
from .api import PostViewSet, CommentViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
