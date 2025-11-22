from django.urls import path
from . import views

urlpatterns = [
    path('', views.RootAPIView.as_view(), name='root'),
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('upload/', views.UploadAPIView.as_view(), name='upload'),
    path('datasets/<str:dataset_id>/', views.DatasetDetailAPIView.as_view(), name='dataset_detail'),
    path('history/', views.HistoryAPIView.as_view(), name='history'),
    path('report/pdf/<str:dataset_id>/', views.PDFReportAPIView.as_view(), name='pdf_report'),
]