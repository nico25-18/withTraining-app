from datetime import timedelta
import json
from cloudinary.uploader import destroy
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import send_mail
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm, CustomPasswordResetForm, CustomSetPasswordForm, ProfileForm, SearchForm
from .models import Profile, CustomUser, Like, Match, Notification, ChatRoom, Message, ChatRoomViewStatus
import os

# TOPページ
def home(request):
    return render(request, 'users/home.html')
# 新規登録
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.login_state = True
            user.last_login_date = timezone.now()
            user.save()
            login(request, user)
            return redirect('mypage')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})
# ログイン
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.login_state = True
            user.last_login_date = timezone.now()
            user.save()
            login(request, user)
            return redirect('mypage')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
# ログアウト
@login_required
def custom_logout_view(request):
    request.user.login_state = 0
    request.user.save()
    logout(request)
    return redirect('home')
# マイページ
@login_required
def mypage(request):
    request.session.pop('search_conditions', None)
    return render(request, 'users/mypage.html', {'user': request.user})
# マイページ_通知数
@login_required
def unread_notification_count(request):
    count = Notification.objects.filter(to_user=request.user, is_read=False).count()
    return JsonResponse({'unread_notification_count': count})
# プロフィール編集
from decouple import config
from django.conf import settings
@login_required
def edit_profile(request):
    profile = request.user.profile
    old_image = profile.profile_image
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            
            if request.POST.get('delete_profile_image') and old_image:
                if settings.DEBUG:
                    old_image_path = old_image.path
                    # DB上のイメージパス削除
                    if profile.profile_image.path == old_image_path:
                        profile.profile_image.delete(save=True)
                
                    # 物理ファイルも削除（存在していれば）
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                else:
                    if profile.profile_image.name == old_image.name:
                        old_image_name = old_image.name
                        profile.profile_image.delete(save=True)
                        public_id = old_image_name.rsplit('.', 1)[0]
                        destroy(public_id)
                    
            if profile.profile_image:
                if settings.DEBUG:
                    if old_image and profile.profile_image.path != old_image.path:
                        if os.path.exists(old_image.path):
                            os.remove(old_image.path)
                else:
                    if old_image and profile.profile_image.name != old_image.name:
                        public_id = old_image.name.rsplit('.', 1)[0]
                        destroy(public_id)
                    
            return redirect('mypage')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {'form': form})
# ユーザー検索
@login_required
def user_search(request):
    searched = False
    liked_user_ids = list(request.user.likes_sent.all().values_list("to_user__id", flat=True))

    # 検索条件がGETで来ている（＝検索ボタンが押された）
    if request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            request.session['search_conditions'] = request.GET.dict()
            searched = True
    else:
        # セッションに条件が保存されていればそれを復元
        search_conditions = request.session.get('search_conditions')
        if search_conditions:
            form = SearchForm(search_conditions)
            searched = True
        else:
            form = SearchForm()

    profiles = Profile.objects.exclude(user=request.user)

    # マッチングしている相手も省く
    matches = Match.objects.filter(models.Q(user1=request.user) | models.Q(user2=request.user))
    for match in matches:
        if match.user1 == request.user:
            profiles = profiles.exclude(user=match.user2)
        else:
            profiles = profiles.exclude(user=match.user1)

    if form.is_valid() and searched:
        cd = form.cleaned_data
        if cd.get('gender'):
            profiles = profiles.filter(gender=cd['gender'])
        if cd.get('training_area'):
            profiles = profiles.filter(training_area=cd['training_area'])
        if cd.get('training_area_detail'):
            profiles = profiles.filter(training_area_detail__icontains=cd['training_area_detail'])
        if cd.get('training_goal'):
            profiles = profiles.filter(training_goal=cd['training_goal'])
        if cd.get('training_experience'):
            profiles = profiles.filter(training_experience=cd['training_experience'])

    return render(request, 'users/user_search.html', {
        'form': form,
        'searched': searched,
        'profiles': profiles if searched else [],
        'liked_user_ids': liked_user_ids,
    })
# おすすめユーザー一覧
@login_required
def recommended_users(request):
    current_user = request.user
    current_profile = current_user.profile

    # 既にいいねしているユーザーID一覧
    like_ids = Like.objects.filter(
        models.Q(from_user=current_user)
    ).values_list('to_user_id')
    
    # 既にマッチしているユーザーID一覧
    matched_ids = Match.objects.filter(
        models.Q(user1=current_user) | models.Q(user2=current_user)
    ).values_list('user1_id', 'user2_id')

    exclude_ids_flat = set()
    exclude_ids_flat.add(request.user.id) # 自分自身
    for i in like_ids:
        exclude_ids_flat.add(i)
    for s, r in matched_ids:
        exclude_ids_flat.add(s)
        exclude_ids_flat.add(r)

    # 除外ユーザー（自分＋マッチ済）
    exclude_ids = list(exclude_ids_flat)

    # 候補リスト
    recommendations = []

    # おすすめ優先度1 地域・目標・経験一致
    candidates_1 = Profile.objects.filter(
        training_area=current_profile.training_area,
        training_goal=current_profile.training_goal,
        training_experience=current_profile.training_experience
    ).exclude(user_id__in=exclude_ids
    ).order_by('id')[:10]

    recommendations.extend(candidates_1)

    # ユーザーを一意に保つためのIDリスト
    collected_ids = set(p.user.id for p in recommendations)

    if len(recommendations) < 10:
        # おすすめ優先度2 地域一致
        candidates_2 = Profile.objects.filter(
            training_area=current_profile.training_area
        ).exclude(user_id__in=exclude_ids + list(collected_ids)
        ).order_by('id')

        for p in candidates_2:
            if len(recommendations) >= 10:
                break
            recommendations.append(p)
            collected_ids.add(p.user.id)

    if len(recommendations) < 10:
        # おすすめ優先度3 目標一致
        candidates_3 = Profile.objects.filter(
            training_goal=current_profile.training_goal
        ).exclude(user_id__in=exclude_ids + list(collected_ids)
        ).order_by('id')

        for p in candidates_3:
            if len(recommendations) >= 10:
                break
            recommendations.append(p)
            collected_ids.add(p.user.id)

    if len(recommendations) < 10:
        # おすすめ優先度4 その他すべて（登録日新しい順）
        candidates_4 = Profile.objects.exclude(
            user_id__in=exclude_ids + list(collected_ids)
        ).order_by('id')

        for p in candidates_4:
            if len(recommendations) >= 10:
                break
            recommendations.append(p)

    return render(request, 'users/recommended_users.html', {
        'recommendations': recommendations
    })
# ユーザープロフィール閲覧
@login_required
def user_profile(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)

    # 自分自身のプロフィールならマイページへリダイレクトしてもOK
    if target_user == request.user:
        return redirect('mypage')

    profile = get_object_or_404(Profile, user=target_user)

    # 既にいいねしているかを判定
    liked = Like.objects.filter(from_user=request.user, to_user=target_user).exists()
    
    # 既にマッチングしているかを判定
    room = ChatRoom.objects.filter((models.Q(user1=request.user) & models.Q(user2=target_user)) | (models.Q(user1=target_user) & models.Q(user2=request.user))).first()
    
    room_id = ""
    if room:
        room_id = room.id
            
    return render(request, 'users/user_profile.html', {
        'target_user': target_user,
        'profile': profile,
        'liked': liked,
        'room_id': room_id,
    })
# 通知一覧
@login_required
def notification_list(request):
    target = Notification.objects.filter(to_user=request.user).order_by('-created_at')
    
    notifications = []
    
    for noti in target:
        room_id = None
        if (noti.notification_type == 'match' or noti.notification_type == 'message'):
            partner = noti.from_user
            chatroom = ChatRoom.objects.filter((models.Q(user1=request.user) & models.Q(user2=partner)) 
                                               | (models.Q(user1=partner) & models.Q(user2=request.user))).first()
            room_id = chatroom.id
        
        notifications.append({
            'room_id': room_id,
            'notification': noti,
        })
    return render(request, 'users/notification_list.html', {
        'notifications': notifications
    })
# 通知一覧_既読
@csrf_exempt
@login_required
def mark_notification_as_read_ajax(request, notification_id):
    if request.method == "POST":
        try:
            notification = Notification.objects.get(id=notification_id, to_user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)
# 通知一覧_一括既読
@csrf_exempt
@require_POST
@login_required
def mark_notifications_as_target_read_ajax(request):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    Notification.objects.filter(id__in=ids, to_user=request.user).update(is_read=True)
    return JsonResponse({'status': 'success'})
# 通知一覧_一括削除
@csrf_exempt
@require_POST
@login_required
def mark_notifications_as_target_delete_ajax(request):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    Notification.objects.filter(id__in=ids, to_user=request.user).delete()
    return JsonResponse({'status': 'success'})
# いいね
@login_required
@require_POST
def toggle_like_ajax(request):
    to_user_id = request.POST.get('to_user_id')
    if not to_user_id:
        return JsonResponse({'success': False, 'error': 'No user ID provided'}, status=400)

    try:
        to_user = CustomUser.objects.get(id=to_user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    if to_user == request.user:
        return JsonResponse({'success': False, 'error': 'Cannot like yourself'}, status=400)

    like, created = Like.objects.get_or_create(from_user=request.user, to_user=to_user)

    if not created:
        # すでにいいね済み → 削除
        like.delete()
        
        # マッチ解除（あれば）
        Match.objects.filter(
            models.Q(user1=request.user, user2=to_user) |
            models.Q(user1=to_user, user2=request.user)
        ).delete()
        
        return JsonResponse({'success': True, 'liked': False})
    else:
        # 通知（いいね）
        Notification.objects.create(
            to_user=to_user,
            from_user=request.user,
            notification_type='like',
            message=f"{request.user.username} さんがあなたにいいねしました"
        )
        
        # 新規いいね → 相手からも来ていたらマッチ成立
        reciprocal = Like.objects.filter(from_user=to_user, to_user=request.user).exists()

        if reciprocal:
            # user1 < user2 の順に統一
            u1, u2 = sorted([request.user, to_user], key=lambda x: x.id)
            Match.objects.get_or_create(user1=u1, user2=u2)
            ChatRoom.objects.get_or_create(user1=u1, user2=u2)
            
            # 通知（マッチ）
            Notification.objects.create(
                to_user=request.user,
                from_user=to_user,
                notification_type='match',
                message=f"{to_user.username} さんとマッチしました！"
            )
            Notification.objects.create(
                to_user=to_user,
                from_user=request.user,
                notification_type='match',
                message=f"{request.user.username} さんとマッチしました！"
            )

        return JsonResponse({'success': True, 'liked': True})
# マッチング一覧
@login_required
def match_list(request):
    user = request.user
    matches = Match.objects.filter(models.Q(user1=user) | models.Q(user2=user))
    
    match_users = []
    for match in matches:
        if match.user1 == user:
            match_users.append(match.user2)
        else:
            match_users.append(match.user1)

    return render(request, 'users/match_list.html', {
        'match_users': match_users
    })
# チャットルーム一覧
@login_required
def chatroom_list(request):
    user = request.user
    chatrooms = ChatRoom.objects.filter(models.Q(user1=user) | models.Q(user2=user))

    chatroom_data = []
    
    for room in chatrooms:
        partner = room.get_partner(request.user)
        latest_message = Message.objects.filter(chatroom=room).order_by('-timestamp').first()
        # まだ読んでいないメッセージ数をカウント
        unread_count = Message.objects.filter(
            chatroom=room,
            is_read=False,
            sender=partner  # 相手が送ったメッセージ
        ).count()
        
        chatroom_data.append({
            'room': room,
            'partner': partner,
            'latest_message': latest_message,
            'unread_count': unread_count,
        })
    return render(request, 'users/chatroom_list.html', {
        'chatrooms': chatroom_data
    })
# チャットルーム一覧_未読メッセージ数
@login_required
def get_unread_counts_per_room(request):
    user = request.user
    chatrooms = ChatRoom.objects.filter(models.Q(user1=user) | models.Q(user2=user))

    chatroom_data = []
    
    for room in chatrooms:
        partner = room.get_partner(request.user)
        latest_message = Message.objects.filter(chatroom=room).order_by('-timestamp').first()
        # まだ読んでいないメッセージ数をカウント
        unread_count = Message.objects.filter(
            chatroom=room,
            is_read=False,
            sender=partner  # 相手が送ったメッセージ
        ).count()
        
        chatroom_data.append({
            'room_id': room.id,
            'latest_message': latest_message.text if latest_message else 'メッセージはまだありません',
            'unread_count': unread_count,
        })
    return JsonResponse({'chatrooms': chatroom_data})
# 各チャットルーム
@login_required
def chatroom_detail(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # アクセス権チェック
    if request.user != room.user1 and request.user != room.user2:
        return redirect('chatroom_list')
    
    partner = room.get_partner(request.user)
    partner_status, _ = ChatRoomViewStatus.objects.get_or_create(user=partner, room=room)
    
    messages = room.messages.order_by('timestamp')  
    
    if not partner_status.is_viewing or timezone.now() - partner_status.last_updated >= timedelta(seconds=10):
        partner_status.is_viewing = False
        partner_status.save()
        
        room.messages.filter(sender=partner, is_read=False).update(is_read=True)
        
        
    return render(request, 'users/chatroom_detail.html', {
        'room': room,
        'partner': partner,
        'messages': messages,
    })
# 各チャットルーム_メッセージ送信
@login_required
@require_POST
def send_message_ajax(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    partner = room.get_partner(request.user)
    partner_status, _ = ChatRoomViewStatus.objects.get_or_create(user=partner, room=room)
    
    if request.user != room.user1 and request.user != room.user2:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    text = request.POST.get('text')
    if text:
        msg = Message.objects.create(
            chatroom=room,
            sender=request.user,
            text=text,
        )

        if partner_status.is_viewing and timezone.now() - partner_status.last_updated < timedelta(seconds=10):
            msg.is_read = partner_status.is_viewing
        else:
            partner_status.is_viewing = False
            partner_status.save()
        
        # 通知
        Notification.objects.create(
            to_user=room.get_partner(request.user),
            from_user=request.user,
            notification_type='message',
            message=f'{request.user.username} さんからメッセージが届きました'
        )

        return JsonResponse({
            'id': msg.id,
            'message': msg.text,
            'sender': msg.sender.username,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
            'is_read': msg.is_read,
        })
    else:
        return JsonResponse({'error': 'Empty message'}, status=400)
# 各チャットルーム_メッセージ受信
@csrf_exempt
@login_required
def get_new_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user != room.user1 and request.user != room.user2:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    since = request.GET.get('since')
    if not since:
        return JsonResponse({'error': 'No timestamp provided'}, status=400)

    since_dt = parse_datetime(since)
    partner = room.get_partner(request.user)

    new_messages = Message.objects.filter(
        chatroom=room,
        sender=partner,
        timestamp__gt=since_dt
    ).order_by('timestamp')
    
    if new_messages and len(new_messages):
        # 受信メッセージあり
        new_messages.update(is_read=True)
    
    messages_data = [
        {
        'id': m.id,
        'message': m.text,
        'sender': m.sender.username,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M'),
        'is_read': m.is_read,
        } for m in new_messages
    ]
    
    # 自分のチャットルームをオンライン(ポーリングされているかで判定)
    status, _ = ChatRoomViewStatus.objects.get_or_create(user=request.user, room=room)
    status.is_viewing = True
    status.save()
    
    # 相手のチャットルーム状態の取得
    partner_status, _ = ChatRoomViewStatus.objects.get_or_create(user=partner, room=room)
    read_message_ids = []
    if partner_status.is_viewing and timezone.now() - partner_status.last_updated < timedelta(seconds=10):
        my_unread = Message.objects.filter(
        chatroom=room,
        sender=request.user,
        is_read=False
        )
        read_message_ids = list(my_unread.values_list('id', flat=True))
        my_unread.update(is_read=True)
    else:
        partner_status.is_viewing = False
        partner_status.save()
    
    return JsonResponse({'messages': messages_data, 'read_ids': read_message_ids})
# パスワードリセット
def custom_password_reset(request):
    User = get_user_model()
    error_message = ''
    success_message = ''

    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            try:
                user = User.objects.get(username=username)
                if not user.email:
                    error_message = 'メールアドレスが未設定のユーザーのため、パスワードリセットができません。'
                elif user.email != email:
                    error_message = '登録されているメールアドレスが異なります。再度入力してください。'
                else:
                    # パスワードリセットメール送信
                    subject = "【WithTraining】パスワードリセットのご案内"
                    context = {
                        'user': user,
                        'domain': request.get_host(),
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                    }
                    message = render_to_string('users/password_reset_email.html', context)
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                    success_message = 'パスワードリセット用のメールを送信しました。'
                    return render(request, 'users/password_reset_done.html')
            except User.DoesNotExist:
                error_message = '該当するユーザーが存在しません。'

    else:
        form = CustomPasswordResetForm()

    return render(request, 'users/password_reset.html', {
        'form': form,
        'error_message': error_message,
        'success_message': success_message
    })
# パスワードリセット用
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')