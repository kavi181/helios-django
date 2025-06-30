from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, include  


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
    # path('profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # path('quiz/<str:book_id>/', views.quiz, name='quiz'),
    # path('quiz/<str:book_id>/', views.quiz, name='quiz_static'),
    path('profile/', views.profile_view, name='profile'),
    # path('quiz/denutra/', views.dengue_quiz, name='quiz'),
    #path('static-quiz/<slug:slug>/', views.quiz_view, name='quiz_static'),
    path('shop/', include('shop.urls')),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('read/<slug:slug>/', views.read_book, name='read_book'),
    path('quiz/<slug:slug>/', views.quiz, name='quiz'),
    path('read-scroll/<slug:slug>/', views.read_scroll, name='read_scroll'),
    path('read-page/<slug:slug>/<int:page_number>/', views.read_page, name='read_page'),


    





] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
