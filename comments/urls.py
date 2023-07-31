from django.urls import path
from comments.views import like_comment, delete_comment, translate_comment

app_name = 'comments'

urlpatterns = [
    path('like/<int:comment_id>/<str:is_positive>/', like_comment, name='like'),
    path('delete/<int:comment_id>/', delete_comment, name='delete'),
    path('translate/<int:comment_id>/', translate_comment, name='translate'),
]
