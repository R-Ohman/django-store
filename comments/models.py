from django.db import models
from django.template.defaultfilters import slugify


class ProductComment(models.Model):
    ASSESSMENT_CHOICES = (
        (2.0, '2.0'),
        (2.5, '2.5'),
        (3.0, '3.0'),
        (3.5, '3.5'),
        (4.0, '4.0'),
        (4.5, '4.5'),
        (5.0, '5.0'),
    )

    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=2048, blank=True, null=True)
    assessment = models.DecimalField(max_digits=2, decimal_places=1, choices=ASSESSMENT_CHOICES)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def attachments(self):
        return Attachment.objects.filter(comment=self)

    def __str__(self):
        return f'{self.product.name} | {self.user.username} | {self.assessment}'

    class Meta:
        verbose_name = 'product comment'
        verbose_name_plural = 'product comments'


def get_image_filename(instance, filename):
    title = instance.comment.user.username + instance.comment.product.name
    slug = slugify(title)
    return "post_images/%s-%s" % (slug, filename)


class Attachment(models.Model):
    comment = models.ForeignKey('comments.ProductComment', on_delete=models.CASCADE, related_name='attachments')
    file = models.ImageField(upload_to=get_image_filename, verbose_name='Image', null=False, blank=False)


class Like(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='likes')
    comment = models.ForeignKey('comments.ProductComment', on_delete=models.CASCADE, related_name='likes')
    is_positive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} | {self.comment}'

    class Meta:
        verbose_name = 'like'
        verbose_name_plural = 'likes'
        unique_together = ('user', 'comment')

    def set_is_positive(self, value):
        self.is_positive = value > 0

    def get_is_positive(self):
        return 1 if self.is_positive else -1

    is_positive_value = property(get_is_positive, set_is_positive)


class UserReport(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comment_reports', null=True, blank=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    topic = models.CharField(max_length=255, null=False, blank=False)
    text = models.TextField(max_length=2048, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} | {self.topic}'

    class Meta:
        verbose_name = 'user report'
        verbose_name_plural = 'user reports'


