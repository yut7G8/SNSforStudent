from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from datetime import datetime

from django.urls import reverse

#create_userとcreate_superuserメソッドを定義しているUserManagerというクラスも修正する必要がある
#create_user:ユーザーの新規作成時に呼び出されるメソッド
#create_superuser:管理者用のユーザーを作成するときに使われるメソッド

class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password,grade,**extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        #メールアドレスの正規化
        email = self.normalize_email(email)
        user = self.model(email=email,grade=grade,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None,grade=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password,grade, **extra_fields)

    def create_superuser(self, email, password, grade=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password,grade,**extra_fields)


GENDER_CHOICES = [
    ('1', '女性'),
    ('2', '男性'),
]

# SocietyUser
# StudentUserもこのUser(for society)を引き継ぐ
class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""
    grade = models.IntegerField(_('grade'),null=True,blank=True,default=0)
    school_name = models.CharField(_('school name'),max_length=100,null=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    gender = models.CharField('性別', max_length=1, choices=GENDER_CHOICES)
    society_name = models.CharField(_('society name'), max_length=150, blank=True)
    company_name = models.CharField(_('company name'), max_length=150, blank=True)
    about_me = models.TextField(blank=True)
    image = models.ImageField(upload_to='',blank=True,null=True)

    followers_number = models.IntegerField(_('followers_number'),null=True,blank=True,default=0)
    following_number = models.IntegerField(_('following_number'),null=True,blank=True,default=0)

    #url情報を入れることができるように改良
    url_info = models.URLField(default=None,null=True)


    is_student = models.BooleanField(default=False)
    is_society = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

    is_connected = models.BooleanField(default=False)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email


    def get_absolute_url(self):
        print("model")
        return reverse('profile', kwargs={'username': self.username})


# StudentUser
class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True, related_name='student')

    def __str__(self):
        return self.user.username
    


# CompanyUser
class Company(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True, related_name='company')

    def __str__(self):
        return self.user.username


# 投稿用モデル
class BoardModel(models.Model):

    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.CharField(max_length=100)
    images = models.ImageField(upload_to='', blank=True)
    good = models.IntegerField(default=0)
    read = models.IntegerField(default=0)
    readtext = models.CharField(max_length=200)
    # いいね機能. ManytoMabyFieldを使用.
    like = models.ManyToManyField(User, related_name='like', blank=True)
    created_at = models.DateTimeField('投稿日', default=timezone.now)

    #橘川追加
    url = models.URLField(default=None)


    def __str__(self):
        return self.title


# フォロー
class Connection(models.Model):
    # student
    follower = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    # society
    following = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} : {}".format(self.follower.username, self.following.username)



# イベントクラス
class Event(models.Model):
    # 主催者(society)
    society = models.ForeignKey(User, related_name='society', on_delete=models.CASCADE)
    # 参加者(student)
    students = models.ManyToManyField(User, related_name='joined_student')
    # イベント名
    event_name = models.CharField(_('event name'), max_length=30, blank=True)
    # イベント内容
    content = models.TextField()
    # 宣伝用画像
    images = models.ImageField(upload_to='',blank=True,null=True)
    # イベント開催日
    event_date = models.DateTimeField(verbose_name="開催日時", default=datetime.now)
    # 申し込み締め切り日時
    deadline = models.DateTimeField(verbose_name="締め切り日時", default=datetime.now)

    #橘川追加
    url = models.URLField(default=None)

    def __str__(self):
        return self.event_name

# イベント参加時にサークルユーザが決定する追加情報
class Information(models.Model):
    # 結びついているイベント
    event = models.ForeignKey(Event, related_name='event', on_delete=models.CASCADE)
    # 追加情報のタイトル(サークルが任意で決定)
    info_title = models.CharField(max_length=200, default=None)

    def __str__(self):
        return self.info_title



# イベント参加時に学生が入力する追加情報
class ExtraInfo(models.Model):
    source = models.ForeignKey(Information, related_name='source', on_delete=models.CASCADE)
    # 情報主(学生)
    info_owner = models.ForeignKey(User, related_name='info_owner', on_delete=models.CASCADE, default=None)
    # 追加情報(学生が入力するもの)
    info = models.CharField(max_length=200, default=None)

    def __str__(self):
        return self.info
