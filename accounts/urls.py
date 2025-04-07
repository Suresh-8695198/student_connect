from django.urls import path
from . import views
from .views import login_view


urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile_view/<str:email>/', views.profile_view, name='profile_view'),
    path('profile_form/<str:email>/', views.profile_form, name='profile_form'),
    path('edit_form/<str:email>/', views.edit_form, name='edit_form'),
    path('add_social_url/<str:social_media>/<str:email>/', views.add_social_url, name='add_social_url'),
    path('signup/', views.signup_view, name='signup_view'),
    path('waiting/<str:email>/', views.waiting_view, name='waiting_view'),
    path('approve/<str:email>/', views.approve_request, name='approve_request'),

    path('profile/<str:email>/add_experience/', views.add_experience, name='add_experience'),
    path('edit_experience/<str:email>/<str:experience_id>/', views.edit_experience, name='edit_experience'),

    path('profile/<str:email>/add_education/', views.add_education, name='add_education'),
    path('edit_education/<str:email>/<str:education_id>/', views.edit_education, name='edit_education'),

    path('alumni-directory/', views.alumni_directory, name='alumni_directory'),
    path('student-profile/<str:student_id>/', views.student_profile, name='student_profile'),
    
    path("chat/<str:current_user_email>/<str:recipient_email>/", views.chat_view, name="chat_view"),
    path("send_message/", views.send_message, name="send_message"),
    path("edit_message/", views.edit_message, name="edit_message"),
    path("delete_message/", views.delete_message, name="delete_message"),

    
    path('get-connect-status/<str:student_id>/', views.get_connect_status, name='get_connect_status'),
    path('send-connect-request/<str:student_id>/', views.send_connect_request, name='send_connect_request'),
    path('handle-connect-request/<str:connect_request_id>/<str:action>/', views.handle_connect_request, name='handle_connect_request'),

    path('alumni-map/', views.alumni_map, name='alumni_map'),
    path("post-job/<str:email>/", views.post_job, name="post_job"),
    path("browse-job/", views.browse_job, name="browse_job"),
    path('success-stories/', views.success_stories, name='success_stories'),
    path('newsletter/', views.newsletter, name='newsletter'),
   
    path('surveys/', views.survey_list, name='survey_list'),
    path('submit-response/', views.submit_survey_response, name='submit_survey_response'),
    path('get_surveys/', views.get_surveys, name='get_surveys'),

    path("submit_feedback/", views.submit_feedback, name="submit_feedback"),
    path("feedback/", views.feedback_page, name="feedback"),
    
]
