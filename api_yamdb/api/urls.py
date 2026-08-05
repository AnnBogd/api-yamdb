from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

api_v1_router_3_dev = DefaultRouter()
api_v1_router_3_dev.register(
    r'titles/(?P<title_id>\d+)/reviews/',
    ReviewViewSet,
    basename='reviews'
)
api_v1_router_3_dev.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
    CommentViewSet,
    basename='comments'
)
urlpatterns = [
    path('v1/', include(api_v1_router_3_dev.urls)),
]
