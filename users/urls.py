from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'), # トップページ
    # 新規登録、ログイン、ログアウト
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.custom_logout_view, name='logout'),
    # マイページ関連（プロフィール編集、通知、ユーザー検索、マッチ一覧、チャット一覧）
    path('mypage/', views.mypage, name='mypage'), 
    path('mypage/unread_counts/', views.unread_notification_count, name='unread_notification_count'), 
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_as_read_ajax, name='mark_notification_as_read_ajax'), # 通知既読
    path('notifications/mark_target_read/', views.mark_notifications_as_target_read_ajax, name='mark_notification_as_target_read_ajax'), # 通知一括既読
    path('notifications/mark_target_delete/', views.mark_notifications_as_target_delete_ajax, name='mark_notification_as_target_delete_ajax'), # 通知一括削除
    path('search/', views.user_search, name='user_search'),
    path('users/recommend/', views.recommended_users, name='recommended_users'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('ajax/toggle_like/', views.toggle_like_ajax, name='toggle_like_ajax'), # いいね機能    
    path('matches/', views.match_list, name='match_list'),
    path('chatrooms/', views.chatroom_list, name='chatroom_list'),
    path('chatrooms/unread_counts/', views.get_unread_counts_per_room, name='get_unread_counts_per_room'), # 各チャット未読
    path('chatrooms/<int:room_id>/', views.chatroom_detail, name='chatroom_detail'),
    path('chatrooms/<int:room_id>/send/', views.send_message_ajax, name='send_message_ajax'), # メッセージ送信
    path('chatrooms/<int:room_id>/messages/', views.get_new_messages, name='get_new_messages'), # メッセージ受信
    # パスワード操作関連
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)