from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import User, Student, Company, BoardModel, Event, Information, ExtraInfo, GENDER_CHOICES

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.forms import ModelForm

import bootstrap_datepicker_plus as datetimepicker

#User = get_user_model()

User = User
Student = Student

GENDER_CHOICES = GENDER_CHOICES + [('', '---------')]


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


# SocietyUserのsignup
class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        fields = ( 'school_name', 'society_name', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

    @transaction.atomic
    def save(self,commit=True):
        user = super().save(commit=False)
        user.is_society = True
        user.save()
        return user


# StudentUserのsignup
class StudentCreateForm(UserCreationForm):

    gender = forms.ChoiceField(label='性別', choices=GENDER_CHOICES, required=False)

    class Meta: #(UserCreationForm.Meta):
        # Userでokそう
        model = User
        #model = Student
        fields = ('first_name', 'last_name', 'gender', 'school_name', 'grade', 'email', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        student = Student.objects.create(user=user)
        return user


# CompanyUserのsignup
class CompanyCreateForm(UserCreationForm):

    class Meta: #(UserCreationForm.Meta):
        # Userでokそう
        model = User
        #model = Student
        fields = ('email','company_name' )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_company = True
        user.save()
        company = Company.objects.create(user=user)
        return user


class StudentProfileUpdateForm(forms.ModelForm):
    """studentのプロフィール更新用のフォーム定義"""
    class Meta:
        model = User
        fields =['image','first_name', 'last_name', 'about_me', 'school_name', 'grade'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SocietyProfileUpdateForm(forms.ModelForm):
    """societyのプロフィール更新用のフォーム定義"""
    class Meta:
        model = User
        fields =['image','society_name', 'school_name', 'about_me'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CompanyProfileUpdateForm(forms.ModelForm):
    """societyのプロフィール更新用のフォーム定義"""
    class Meta:
        model = User
        fields =['image','company_name','about_me','url_info'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
# 投稿用のフォームを作成
class PostAddForm(forms.ModelForm):

    url = forms.URLField(required=False)
    
    class Meta:
        model = BoardModel # model変数にBoardModelを代入
        #fields = ['title', 'content', 'author', 'images', 'good', 'read', 'readtext'] # fields変数にフォームで使用するラベルと代入
        fields = ['title', 'content', 'images','url']


# サークルユーザ用イベント作成フォーム
class CreateEventForm(forms.ModelForm):

    #event_date = forms.SplitDateTimeField(label='作成日')
    #extra_info = forms.CharField(required=False)
    url = forms.URLField(required=False)

    class Meta:
        model = Event
        fields = ['event_name', 'content', 'event_date', 'deadline','images', 'url']


# サークルが作成する追加情報欄
class AddInformationForm(forms.ModelForm):

    info_title = forms.CharField(required=False)

    class Meta:
        model = Information
        fields = ['info_title',]


# 学生が入力する追加情報
class InputInformationForm(forms.ModelForm):

    class Meta:
        model = ExtraInfo
        fields = ['info', ]



# サークルユーザ用イベント編集フォーム
# 使わない
class EditEventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['event_name', 'content', 'event_date', 'deadline', ]

        #widgets = {
            #'event_date': forms.SelectDateWidget
        #}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

