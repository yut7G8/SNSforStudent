from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

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


# SocietyUser
# StudentUserもこのUser(for society)を引き継ぐ
class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""
    grade = models.IntegerField(_('grade'),null=True,blank=True,default=0)
    school_name = models.CharField(_('school name'),max_length=100,null=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    society_name = models.CharField(_('society name'), max_length=150, blank=True)


    is_student = models.BooleanField(default=False)
    is_society = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)


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


    # ここいらない
    '''
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.society_name)
        return full_name.strip()

    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    '''
    

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


# StudentUser
class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True, related_name='student')

    def __str__(self):
        return self.user.username
    

    #念のため残してるけどStudentUserのこの部分は恐らくいらない。
    '''
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    grade = models.IntegerField(_('grade'),null=True,blank=True,default=0)
    school_name = models.CharField(_('school name'),max_length=100,null=True)
    email = models.EmailField(_('email address'), unique=True, default=None)

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
    '''
    


# CompanyUser
class Company(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True, related_name='company')

    def __str__(self):
        return self.user.username


# 投稿用モデル
class BoardModel(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.CharField(max_length=100)
    images = models.ImageField(upload_to='')
    good = models.IntegerField()
    read = models.IntegerField()
    readtext = models.CharField(max_length=200)
    #author2 = models.ForeignKey(User,varbose_name = '作者',on_delete=models.PROTECT)