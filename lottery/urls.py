from django.urls import path
from . import views

app_name = 'lottery'

urlpatterns = [
    path('', views.lottery_results, name='results'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add/', views.add_result, name='add_result'),
    path('admin-panel/edit/<int:pk>/', views.edit_result, name='edit_result'),
    path('admin-panel/delete/<int:pk>/', views.delete_result, name='delete_result'),
    path('admin-panel/bulk-delete/', views.bulk_delete_results, name='bulk_delete_results'),
    path('admin-panel/export-csv/', views.export_results_csv, name='export_results_csv'),
    path('admin-panel/ads/add/', views.add_advertisement, name='add_advertisement'),
    path('admin-panel/ads/edit/<int:pk>/', views.edit_advertisement, name='edit_advertisement'),
    path('admin-panel/ads/delete/<int:pk>/', views.delete_advertisement, name='delete_advertisement'),
    path('admin-panel/fetch-results/', views.fetch_results, name='fetch_results'),
    path('monthly-table/', views.monthly_table, name='monthly_table'),
]
