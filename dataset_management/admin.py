from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Dataset, DatasetSample


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'total_samples', 'file_size_display', 
        'file_extension', 'is_validated', 'uploaded_at'
    ]
    list_filter = [
        'is_validated', 'uploaded_at', 'file_path'
    ]
    search_fields = ['name', 'description']
    readonly_fields = [
        'uploaded_at', 'updated_at', 'total_samples', 
        'file_size_display', 'file_extension'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'file_path')
        }),
        ('Dataset Statistics', {
            'fields': (
                'total_samples', 'medical_domains', 'domain_distribution',
                'avg_title_length', 'avg_abstract_length'
            ),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('is_validated', 'validation_errors'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'updated_at', 'file_size_display', 'file_extension'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in a human-readable format"""
        if obj.file_size_mb:
            return f"{obj.file_size_mb} MB"
        return "N/A"
    file_size_display.short_description = "File Size"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['file_path']
        return self.readonly_fields


class DatasetSampleInline(admin.TabularInline):
    model = DatasetSample
    extra = 0
    fields = ['title', 'medical_domains', 'is_preprocessed']
    readonly_fields = ['title', 'medical_domains', 'is_preprocessed']
    can_delete = False
    
    def has_add_permission(self, request, obj):
        return False


@admin.register(DatasetSample)
class DatasetSampleAdmin(admin.ModelAdmin):
    list_display = [
        'title_truncated', 'dataset', 'domain_count', 
        'is_preprocessed', 'created_at'
    ]
    list_filter = [
        'dataset', 'is_preprocessed', 'created_at', 'medical_domains'
    ]
    search_fields = ['title', 'abstract', 'authors', 'journal']
    readonly_fields = ['created_at', 'domain_count']
    
    fieldsets = (
        ('Article Information', {
            'fields': ('dataset', 'title', 'abstract')
        }),
        ('Classification', {
            'fields': ('medical_domains',)
        }),
        ('Metadata', {
            'fields': ('authors', 'journal', 'publication_year', 'doi'),
            'classes': ('collapse',)
        }),
        ('Preprocessing', {
            'fields': (
                'is_preprocessed', 'preprocessed_title', 'preprocessed_abstract'
            ),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('created_at', 'domain_count'),
            'classes': ('collapse',)
        }),
    )
    
    def title_truncated(self, obj):
        """Display truncated title"""
        return obj.title[:75] + "..." if len(obj.title) > 75 else obj.title
    title_truncated.short_description = "Title"
    
    def domain_count(self, obj):
        """Display number of domains"""
        return obj.domain_count
    domain_count.short_description = "# Domains"


# Add custom admin site configuration
admin.site.site_header = "MedLitBot Administration"
admin.site.site_title = "MedLitBot Admin"
admin.site.index_title = "Medical Literature Classification System"
