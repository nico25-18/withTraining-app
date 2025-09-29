from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, **extra_fields):
        if not username:
            raise ValueError("ユーザー名は必須です")
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)
    login_state = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []  # create_user の email などを必須にするなら指定

    class Meta:
        db_table = "User"

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # 性別
    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "男性"),
            ("female", "女性"),
            ("other", "その他"),
        ],
        blank=True,
    )

    # 合トレ希望地域
    training_area = models.CharField(
        max_length=10,
        choices=[
            ("HKD", "北海道"),
            ("AOM", "青森県"),
            ("IWT", "岩手県"),
            ("MYG", "宮城県"),
            ("AKT", "秋田県"),
            ("YMGT", "山形県"),
            ("FKSM", "福島県"),
            ("IBRK", "茨城県"),
            ("TTG", "栃木県"),
            ("GNM", "群馬県"),
            ("SITM", "埼玉県"),
            ("CB", "千葉県"),
            ("TKY", "東京都"),
            ("KNGW", "神奈川県"),
            ("NIGT", "新潟県"),
            ("TYM", "富山県"),
            ("ISKW", "石川県"),
            ("FKI", "福井県"),
            ("YMNS", "山梨県"),
            ("NGN", "長野県"),
            ("GF", "岐阜県"),
            ("SZOK", "静岡県"),
            ("AIC", "愛知県"),
            ("ME", "三重県"),
            ("SIG", "滋賀県"),
            ("KYT", "京都府"),
            ("OSK", "大阪府"),
            ("HYG", "兵庫県"),
            ("NR", "奈良県"),
            ("WKYM", "和歌山県"),
            ("TTR", "鳥取県"),
            ("SMN", "島根県"),
            ("OKYM", "岡山県"),
            ("HRSM", "広島県"),
            ("YMGT", "山口県"),
            ("TKSM", "徳島県"),
            ("KGW", "香川県"),
            ("AIC", "愛媛県"),
            ("KOC", "高知県"),
            ("FKOK", "福岡県"),
            ("SAG", "佐賀県"),
            ("NGSK", "長崎県"),
            ("KMMT", "熊本県"),
            ("OIT", "大分県"),
            ("MYZK", "宮崎県"),
            ("KGSM", "鹿児島県"),
            ("OKNW", "沖縄県"),
        ],
        blank=True,
    )

    # 合トレ希望地域詳細
    training_area_detail = models.CharField(max_length=50, blank=True)

    # トレーニング目標（例：ダイエット、筋力アップ、健康維持など）
    training_goal = models.CharField(
        max_length=100,
        choices=[
            ("bm", "ボディメイク"),
            ("bm2", "ボディメイク（大会出場レベル）"),
            ("pu", "筋力アップ"),
            ("hk", "健康維持"),
            ("ot", "その他"),
        ],
        blank=True,
    )

    # トレーニング歴（例：1年未満、1〜3年、3年以上など）
    training_experience = models.CharField(
        max_length=20,
        choices=[
            ("<1y", "1年未満"),
            ("1-3y", "1〜3年"),
            ("3-5y", "1〜5年"),
            ("5-10y", "5〜10年"),
            ("10y", "10年以上"),
        ],
        blank=True,
    )

    # 自己紹介
    introduction = models.TextField(max_length=500, blank=True)

    # プロフィール画像（任意）
    profile_image = models.ImageField(
        upload_to="profile_images/", null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username} のプロフィール"

class Like(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes_sent',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes_received',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} liked {self.to_user}"

class Match(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='matches_as_user1',
        on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='matches_as_user2',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user1', 'user2'],
                name='unique_match_between_users'
            ),
            models.CheckConstraint(
                check=~models.Q(user1=models.F('user2')),
                name='no_self_match'
            ),
        ]

    def __str__(self):
        return f"Match: {self.user1} × {self.user2}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
    ('like', 'いいねされました'),
    ('match', 'マッチしました'),
    ('message', 'メッセージが届きました'),
    ]

    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(
        max_length=10, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.to_user} へ {self.notification_type}"

class ChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chatrooms_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chatrooms_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_chatroom'),
            models.CheckConstraint(check=~models.Q(user1=models.F('user2')), name='no_self_chat'),
        ]

    def __str__(self):
        return f'ChatRoom: {self.user1.username} × {self.user2.username}'

    def get_partner(self, user):
        return self.user2 if self.user1 == user else self.user1

class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender.username}: {self.text[:30]}'

class ChatRoomViewStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    is_viewing = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'room')