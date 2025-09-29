from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import CustomUser, Profile
import re

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='名前（ニックネーム可）',
        help_text='50文字以内。ひらがな・カタカナ・英字・数字・@ が使えます。',
        max_length=50,
        error_messages={
            'required': '必須入力です。',
            'max_length': '50文字以内で入力してください。',
        }
    )

    email = forms.EmailField(
        required=False,
        label='メールアドレス',
        help_text='パスワードを忘れた際の再設定に使用されます。',
        error_messages={
            'invalid': 'メールアドレスの形式が正しくありません。',
        }
    )

    password1 = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput,
        min_length=8,
        help_text='8文字以上。英字・数字・記号を組み合わせてください。',
        error_messages={
            'required': '必須入力です。',
            'min_length': 'パスワードは8文字以上で入力してください。',
        }
    )

    password2 = forms.CharField(
        label='パスワード（確認）',
        strip=False,
        widget=forms.PasswordInput,
        min_length=8,
        help_text='確認のため、もう一度同じパスワードを入力してください。',
        error_messages={
            'required': '必須入力です。',
            'min_length': 'パスワードは8文字以上で入力してください。',
        }
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.fullmatch(r'[ぁ-んァ-ヶa-zA-Z0-9@]+', username):
            raise forms.ValidationError('ユーザー名は、ひらがな・カタカナ・英数字・@ のみ使用できます。')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('既に登録されているユーザー名です。')
        return username    
    
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if not re.fullmatch(r'[!-~]+', password):  # 半角の英数記号のみ
            raise forms.ValidationError('パスワードは半角英字・数字・記号のみ使用できます。')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'パスワードが一致していません。')
            
class CustomPasswordResetForm(forms.Form):
    username = forms.CharField(label='ユーザー名', max_length=50)
    email = forms.EmailField(label='メールアドレス')
    
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='新しいパスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        min_length=8,
        help_text='8文字以上。英字・数字・記号を組み合わせてください。',
        error_messages={
            'required': '必須入力です。',
            'min_length': 'パスワードは8文字以上で入力してください。',
        }
    )
    new_password2 = forms.CharField(
        label='新しいパスワード（確認）',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        min_length=8,
        help_text='確認のため、もう一度同じパスワードを入力してください。',
        error_messages={
            'required': '必須入力です。',
            'min_length': 'パスワードは8文字以上で入力してください。',
        }
    )
    
    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        if not re.fullmatch(r'[!-~]+', password):  # 半角の英数記号のみ
            raise forms.ValidationError('パスワードは半角英字・数字・記号のみ使用できます。')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'パスワードが一致していません。')
            
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'gender',
            'training_area',
            'training_area_detail',
            'training_goal',
            'training_experience',
            'introduction',
            'profile_image',
        ]

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'training_area': forms.Select(attrs={'class': 'form-control'}),
            'training_area_detail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：新宿区、仙台市近辺'}),
            'training_goal': forms.Select(attrs={'class': 'form-control'}),
            'training_experience': forms.Select(attrs={'class': 'form-control'}),
            'introduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '自己紹介を入力してください'}),
        }

        labels = {
            'gender': '性別',
            'training_area': '合トレ希望地域',
            'training_area_detail': '合トレ希望地域（詳細）',
            'training_goal': 'トレーニング目標',
            'training_experience': 'トレーニング歴',
            'introduction': '自己紹介',
            'profile_image': 'プロフィール画像',
        }

class SearchForm(forms.Form):
    gender = forms.ChoiceField(
        choices=[
            ('', '指定しない'), 
            ('male', '男性'), 
            ('female', '女性'), 
            ('other', 'その他')
        ],
        required=False,
        label='性別'
    )
    training_area = forms.ChoiceField(
        choices=[
            ('', '指定しない'), 
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
        required=False,
        label='合トレ希望地域'
    )
    training_area_detail = forms.CharField(
        max_length=50,
        required=False,
        label='希望地域詳細（キーワード）'
    )
    training_goal = forms.ChoiceField(
        choices=[
            ('', '指定しない'), 
            ("bm", "ボディメイク"),
            ("bm2", "ボディメイク（大会出場レベル）"),
            ("pu", "筋力アップ"),
            ("hk", "健康維持"),
            ("ot", "その他"),
        ],
        required=False,
        label='トレーニング目標'
    )
    training_experience = forms.ChoiceField(
        choices=[
            ('', '指定しない'), 
            ("<1y", "1年未満"),
            ("1-3y", "1〜3年"),
            ("3-5y", "1〜5年"),
            ("5-10y", "5〜10年"),
            ("10y", "10年以上"),
        ],
        required=False,
        label='トレーニング歴'
    )
    