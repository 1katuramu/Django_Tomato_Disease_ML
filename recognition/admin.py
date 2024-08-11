from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.utils.html import format_html
from .models import TomatoImage

class TomatoHealthAdminSite(admin.AdminSite):
    site_header = "TomatoHealth Detector Admin"
    site_title = "TomatoHealth Dectector Admin Portal"
    index_title = "Welcome to TomatoHealth Detector Portal"

    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = 'admin/css/custom_admin.css'
        return context

tomato_admin_site = TomatoHealthAdminSite(name='tomatoadmin')

@admin.register(TomatoImage, site=tomato_admin_site)
class TomatoImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'prediction', 'uploaded_at', 'reviewed')
    list_filter = ('prediction', 'uploaded_at', 'reviewed')
    search_fields = ('prediction',)
    readonly_fields = ('image_preview', 'uploaded_at')
    list_per_page = 20
    actions = ['mark_as_reviewed', 'mark_as_unreviewed']

    fieldsets = (
        ('Image Information', {
            'fields': ('image', 'image_preview', 'prediction')
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'reviewed')
        }),
    )

    date_hierarchy = 'uploaded_at'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(reviewed=True)
        self.message_user(request, f'{updated} images marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected images as reviewed"

    def mark_as_unreviewed(self, request, queryset):
        updated = queryset.update(reviewed=False)
        self.message_user(request, f'{updated} images marked as unreviewed.')
    mark_as_unreviewed.short_description = "Mark selected images as unreviewed"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='tomato_statistics'),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        stats = TomatoImage.objects.values('prediction').annotate(count=Count('id'))
        total_images = TomatoImage.objects.count()
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Tomato Image Statistics',
            'total_images': total_images,
            'stats': stats,
        }
        return render(request, "admin/tomato_statistics.html", context)
