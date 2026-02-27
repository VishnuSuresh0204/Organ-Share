from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Basic pages
    path('', views.index),
    path('about/', views.about),
    path('login/', views.login_view),
    path('logout/', views.logout_view),

    # Registrations
    path('reci_reg/', views.recipient_register),
    path('doct_reg/', views.doctor_register),
    path('dono_reg/', views.donor_register),

    # User Dashboards
    path('admin_home/', views.admin_home),
    path('recipient_home/', views.recipient_home),
    path('donor_home/', views.donor_home),
    path('doctor_home/', views.doctor_home),

    # Admin List Views
    path('view_recipients/', views.view_recipients),
    path('viw_donors/', views.view_donors),
    path('view_doctors/', views.view_doctors),

    # Admin Approve/Reject
    path('approve_recipient/', views.approve_recipient),
    path('approve_donor/', views.approve_donor),

    # Doctor Approve/Reject (correct)
    path('approve_doctor/', views.approve_doctor),

    path('doctor_profile/', views.doctor_profile),
    path('doctor_view_donors/', views.doctor_view_donors),

    path('doctor_edit_profile', views.doctor_edit_profile),
    path('doctor_add_slot/', views.doctor_add_slot),
    path('doc_view_appoint/',views.doctor_view_appointments),

    path('create_appointment/',views.book_appointment),

    path('res_view_slot/',views.view_available_slots),
    path('doc_view_user/',views.doctor_view_recipient),
    
    path('book_slot/', views.book_appointment),
    path('view_booking/', views.recipient_view_appointments),

    path('add_feedback/', views.add_feedback ),
    path('edit_feedback/', views.edit_feedback),
    path('delete_feedback/', views.delete_feedback),
    path('view_feedback/', views.view_feedback),

    path('admin_view_feedbacks/', views.view_feedbacks_admin),

    path('doc_view_donors', views.doctor_view_donors),

    path('doc_view_donor_details', views.doctor_view_donor_detail),

    # Profile Paths
    path('recipient_profile/', views.recipient_profile),
    path('edit_recipient_profile/', views.edit_recipient_profile),
    path('donor_profile/', views.donor_profile),
    path('edit_donor_profile/', views.edit_donor_profile),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
