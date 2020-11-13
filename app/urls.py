from django.urls import path
from . import views
from .views import (
    selectfunc, loginfunc, student_home, society_home, company_home, SignUpView, detailfunc, goodfunc,
    view_societies, follow_view, unfollow_view, detail_society,
    student_profile
)


app_name = 'app'

urlpatterns = [
    path('',selectfunc,name='select'),
    path('login/', loginfunc, name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('student_create/', views.StudentCreate.as_view(), name='student_create'),
    path('company_create/', views.CompanyCreate.as_view(), name='company_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    
    path('student_home/<int:pk>',student_home,name='student_home'),
    path('society_home/<int:pk>',society_home,name='society_home'),
    path('company_home',company_home,name='company_home'),

    path('view_societies/<int:pk>',view_societies,name='view_societies'),
    path('detail_society/<int:pk>/<email>',detail_society,name='detail_society'),

    #path('detail/<int:pk>', detailfunc, name='detail'),
    path('good/<int:pk>', goodfunc, name='good'),

    path('student_profile/<int:pk>', student_profile, name='student_profile'),
    path('student_profile_update/<int:pk>',views.StudentProfileUpdate.as_view(),name='student_profile_update'),
    #path('<slug:username>', views.StudentProfileDetailView.as_view(), name='profile'),
    #path('profile/<email>', views.StudentProfileDetailView.as_view(), name='profile'),
    #path('<slug:username>/edit', views.StudentProfileUpdateView.as_view(), name='edit'),
    #path('student_profile/<int:pk>', views.StudentProfile.as_view(), name='student_profile'),

    path('society_profile/<int:pk>/', views.SocietyProfile.as_view(), name='society_profile'),
    path('society_profile_update/<int:pk>/', views.SocietyProfileUpdate.as_view(), name='society_profile_update'),

    path('follow/<email>', views.follow_view, name='follow'),
    path('follow2/<email>', views.follow_from_detail, name='follow_from_detail'),
    path('unfollow/<email>', views.unfollow_view, name='unfollow'),
    #path('<slug:username>/follow', views.follow_view, name='follow'),
    #path('<slug:username>/unfollow', views.unfollow_view, name='unfollow'),

    #path('detail/', detailfunc, name='detailfunc'), # views.pyのdetailfuncを参照
    path('detail/<int:post_id>/', views.everypost, name='everypost'), # views.pyのeverypost関数を参照
    # path('detail/<int:post_id>/', views.everypostforStuednt, name='everypostforStudent'), # 学生側の閲覧用everypage
    path('add/<int:pk>', views.add, name='add'), # 投稿フォーム用のpath(仮)設定
    path('edit/<int:post_id>/', views.edit, name='edit'), # 編集機能の追加
    path('delete/<int:post_id>/', views.delete, name='delete'), # 削除機能の追加
]