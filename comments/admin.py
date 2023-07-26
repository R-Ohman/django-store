from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from comments.models import ProductComment, Attachment, UserReport


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ['file_preview']

    def file_preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" width="150">', obj.file.url)
        return ''
    file_preview.short_description = 'Image Preview'

class CommentInline(admin.StackedInline):
    model = ProductComment
    extra = 0
    readonly_fields = ('user', 'updated_at', 'created_at', 'get_attachments', 'text', 'assessment', 'rating')
    ordering = ('-created_at',)
    inlines = (AttachmentInline, )

    def get_attachments(self, obj):
        attachments = obj.attachments.all()
        url = reverse('admin:comments_productcomment_change', args=[obj.pk])
        images = ''.join(f'<img src="{attachment.file.url}" width="100" style="margin:10px;"/>' for attachment in attachments)
        return format_html(f'<a href="{url}">{images}</a>')

    get_attachments.short_description = 'Attachments'

    fieldsets = (
        ('Comment Details', {
            'fields': (('user', 'rating'), 'assessment', 'updated_at', 'created_at', ),
        }),
        ('Comment Content', {
            'fields': ('text', 'get_attachments',),
            'classes': ('collapse',),
        }),
    )
    classes = ('collapse',)


@admin.register(ProductComment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'product', 'created_at', 'get_attachments_number')
    readonly_fields = ('user', 'updated_at', 'created_at', 'product')
    inlines = (AttachmentInline, )
    fields = ('user', 'rating', 'assessment', 'text', 'product', 'updated_at', 'created_at',)

    def get_attachments_number(self, obj):
        return obj.attachments.count()
    get_attachments_number.short_description = 'Attachments'


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('email', 'topic', 'created_at', 'is_resolved')
    readonly_fields = ('user', 'name', 'email', 'topic', 'text', 'created_at')
    fields = ('user', 'name', 'email', 'topic', 'text', 'created_at', 'is_resolved')
    search_fields = ('email', 'topic', )

    def run_set_resolved(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_resolved = True
            obj.save()

    run_set_resolved.short_description = "Set status to resolved"
    actions = (run_set_resolved,)

