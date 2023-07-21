from django.urls import path
from comments.views import product_view, like_comment, delete_comment

app_name = 'comments'

urlpatterns = [
    path('<int:product_id>/', product_view, name='view'),
    path('like/<int:comment_id>/<str:is_positive>/', like_comment, name='like'),
    path('delete/<int:comment_id>/', delete_comment, name='delete'),
]
