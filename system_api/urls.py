from django.urls import path
from . import views

urlpatterns = [
    path('create-job/', views.create_job, name='job-card-create'),

    path('query-job/', views.QueryJobView.as_view(), name='query-job'),


    path('database-details/', views.DatabaseDetailsView.as_view(), name='database-details'),

    path('download-job-cards/', views.export_job_cards, name='export_job_cards'),

    path('job-card-pdf/<str:job_number>/', views.JobCardPDFViewAlt.as_view(), name='job_card_pdf'),

    path('job-card/<int:id>/', views.JobCardDetailView.as_view(), name='jobcard-detail'),

    path('job-cards/update/<int:id>/', views.JobCardUpdateView.as_view(), name='jobcard-update'),

    path('job-card/images/<int:job_id>/', views.JobImagesUploadView.as_view(), name='job-images-upload'),


    path('job-card/close/<int:id>/', views.CloseJobCardView.as_view(), name='close-jobcard'),

]
