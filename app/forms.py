from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import User, Student, Company, BoardModel

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.forms import ModelForm

#User = get_user_model()

User = User
Student = Student


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

    class Meta: #(UserCreationForm.Meta):
        # Userでokそう
        model = User
        #model = Student
        fields = ('first_name', 'last_name', 'school_name', 'grade', 'email', )

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
        fields = ('email', )

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
        fields =['first_name', 'last_name', 'about_me', 'school_name', 'grade'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SocietyProfileUpdateForm(forms.ModelForm):
    """societyのプロフィール更新用のフォーム定義"""
    class Meta:
        model = User
        fields =['society_name', 'school_name', 'about_me'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
# 投稿用のフォームを作成
class PostAddForm(forms.ModelForm):
    class Meta:
        model = BoardModel # model変数にBoardModelを代入
        #fields = ['title', 'content', 'author', 'images', 'good', 'read', 'readtext'] # fields変数にフォームで使用するラベルと代入
        fields = ['title', 'content', 'images']