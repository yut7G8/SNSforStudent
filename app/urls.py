from django.urls import path
from . import views
from .views import (
    selectfunc, loginfunc, student_home, society_home, company_home, SignUpView, detailfunc, goodfunc,
    view_societies, follow_view, unfollow_view, detail_society,
    student_profile, view_companies, searchfunc, 
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
    #path('company_home',company_home,name='company_home'),

    path('view_societies/<int:pk>',view_societies,name='view_societies'),
    path('detail_society/<int:pk>/<int:id>/',detail_society,name='detail_society'),

    # いいね機能用のURL++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    path('detail/<int:post_id>/', goodfunc, name='good'),

    path('like/', views.like, name='like'),

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    path('student_profile/<int:pk>', student_profile, name='student_profile'),
    path('student_profile_update/<int:pk>',views.StudentProfileUpdate.as_view(),name='student_profile_update'),

    path('society_profile/<int:pk>/', views.SocietyProfile.as_view(), name='society_profile'),
    path('society_profile_update/<int:pk>/', views.SocietyProfileUpdate.as_view(), name='society_profile_update'),

    # 改良版
    path('follow_button/<email>', views.follow, name='follow'),
    # 現状のフォロー
    path('follow/<email>', views.follow_view, name='follow_view'),
    path('follow2/<email>', views.follow_from_detail, name='follow_from_detail'),
    path('unfollow/<email>', views.unfollow_view, name='unfollow'),

    path('follow_company/<email>', views.follow_company, name='follow_company'),
    path('follow_company2/<email>', views.follow_company_from_detail, name='follow_company_from_detail'),

    path('detail/<int:post_id>/', views.everypost, name='everypost'), # views.pyのeverypost関数を参照
    # path('detail/<int:post_id>/', views.everypostforStuednt, name='everypostforStudent'), # 学生側の閲覧用everypage
    path('add/<int:pk>', views.add, name='add'), # 投稿フォーム用のpath(仮)設定
    path('edit/<int:post_id>/', views.edit, name='edit'), # 編集機能の追加
    path('delete/<int:post_id>/', views.delete, name='delete'), # 削除機能の追加

    path('create_cvent/<int:pk>', views.create_event, name='create_event'), # サークルユーザによるイベント作成
    #path('create_cvent/<int:pk>', views.CreateEventFormSet.as_view(), name='create_event'),
    path('view_events/<int:pk>', views.view_events, name='view_events'), # 学生ユーザに対するイベント表示
    path('everyevent/<int:pk>/<int:id>/', views.everyevent, name='everyevent'), # 各イベントの詳細表示
    path('join_event_confirm/<int:pk>/<int:id>/', views.join_event_confirm, name='join_event_confirm'), # イベントの参加フォーム(確認画面へ)
    path('join_event/<int:pk>/<int:id>/', views.join_event, name='join_event'), # 学生ユーザによるイベント参加
    path('cancel_event/<int:pk>/<int:id>/', views.cancel_event, name='cancel_event'), #学生ユーザによるイベント参加キャンセル
    #path('edit_event/<int:pk>',views.EditEvent.as_view(),name='edit_event'), #サークルユーザによるイベント編集
    path('edit_event/<int:pk>/<int:id>/',views.edit_event,name='edit_event'),
    path('delete_event/<int:pk>/<int:id>/', views.delete_event, name='delete_event'), # サークルユーザによるイベント削除

    #橘川が加えた(11/24)--------------------------
    #companyの初期画面
    path('company_home/<int:pk>',company_home,name='company_home'),
    #companyのprofile
    path('company_profile/<int:pk>/', views.CompanyProfile.as_view(), name='company_profile'),
    path('company_profile_update/<int:pk>/', views.CompanyProfileUpdate.as_view(), name='company_profile_update'),
    #企業の投稿
    path('add_company/<int:pk>', views.add_company, name='add_company'), 
    path('edit_company/<int:post_id>/', views.edit_company, name='edit_company'), # 編集機能の追加
    path('delete_company/<int:post_id>/', views.delete_company, name='delete_company'), # 削除機能の追加
    #企業一覧
    path('view_companies/<int:pk>',view_companies,name='view_companies'),
    path('detail_company/<int:pk>/<int:id>/',views.detail_company,name='detail_company'),
    #検索機能
    path('search/<int:pk>',searchfunc,name='search')
    
]