from django.contrib import admin
from .models import LotteryResult, Advertisement

@admin.register(LotteryResult)
class LotteryResultAdmin(admin.ModelAdmin):
    list_display = ['date', 'state', 'winning_number', 'created_at']
    list_filter = ['state', 'date']
    search_fields = ['state', 'winning_number']
    date_hierarchy = 'date'
    ordering = ['-date', 'state']

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'text']
    ordering = ['-created_at']
