from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('about/', views.about, name='about'),
    path('signup/', views.signup_choice, name='signup'),

    path('signup_choice/', views.signup_choice, name='signup_choice'),
    path('signup_form/', views.signup_form, name='signup_form'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('participant/', views.participant, name='participant'),
    path('contactus/', views.contactus, name='contactus'),
    path('profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('quiz/<str:book_id>/', views.quiz, name='quiz'),



] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
