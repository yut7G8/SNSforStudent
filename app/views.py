from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.contrib.auth import authenticate, login,logout, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, StudentCreateForm, CompanyCreateForm, PostAddForm, 
    StudentProfileUpdateForm, CreateEventForm, EditEventForm, SocietyProfileUpdateForm,
    AddInformationForm, InputInformationForm, CompanyProfileUpdateForm
)
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, DetailView, UpdateView

from .models import User, Student, Company, BoardModel, Connection, Event, Information, ExtraInfo
from .decorators import student_required, society_required, company_required

from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from itertools import chain

from django.urls import reverse_lazy
from .helpers import get_current_user
from django.contrib import messages

from django.utils.decorators import method_decorator

from datetime import datetime
from pytz import timezone, utc
from tzlocal import get_localzone
import pytz
from extra_views import CreateWithInlinesView, InlineFormSet

from django.template.loader import render_to_string
from django.http import JsonResponse

from django.core.mail import EmailMessage
# ログイン前のページ表示
def selectfunc(request):
    return render(request,'select.html')


# signup時、studentかsocietyか選択
class SignUpView(TemplateView):
    template_name = 'signup.html'


# login
def loginfunc(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_login = User.objects.get(email=username)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user_login)
            if user_login.is_student:
                return redirect('app:student_home', pk=user.pk)
            if user_login.is_society:
                return redirect('app:society_home', pk=user.pk)
            if user_login.is_company:
                return redirect('app:company_home',pk=user.pk)
        else:
            return render(request, 'login.html', {'error':'メールアドレスかパスワードが間違っています'})
    else:
        return render(request, 'login.html')


# StudentUserのhome画面
@login_required
@student_required
def student_home(request, pk):
    if request.user.pk == pk:
        student = User.objects.get(pk=pk)
        # ログインしたStudentユーザと結ぶついているConnection
        connections = Connection.objects.filter(follower=student)
        # 検索用に必要
        object_list = BoardModel.objects.all()
        # 表示用のリスト(Queryの扱いが不自由で統一できなかった)
        post_list = []
        for connection in connections:
            posts = BoardModel.objects.filter(user=connection.following)
            for post in posts:
                post_list.append(post)

        query = request.GET.get('q')
        if query:

            post_list = object_list.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query)
            ).distinct()

        return render(request, 'student_home.html', {'object_list':post_list,'query': query})
    else:
        return redirect('app:logout')


# SocietyUserのhome画面
@login_required
@society_required
def society_home(request, pk):
    #object = BoardModel.objects.all().order_by('-readtext') # BordModelモデルの記事（objects）を全て(all())作成された順番（order_by('-readtext')）に取得してobject変数に代入
    if request.user.pk == pk:
        posts = BoardModel.objects.filter(user=request.user)
        society = User.objects.get(pk=pk)
        return render(request, 'society_home.html', {'object':posts,'society':society})
    else:
        return redirect('app:logout')


# CompanyUserのhome画面
@login_required
@company_required
def company_home(request, pk):
    if request.user.pk == pk:
        posts = BoardModel.objects.filter(user=request.user)
        return render(request, 'company_home.html', {'object':posts})
    else:
        return redirect('app:logout')


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'select.html'


# SocietyUserのsignup
class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
    
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('app/mail_template/create/subject.txt', context)
        message = render_to_string('app/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('app:user_create_done')


#StudentUserのsignup
class StudentCreate(generic.CreateView):
    model = User
    form_class = StudentCreateForm
    template_name = 'user_create.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()

        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('app/mail_template/create/subject.txt', context)
        message = render_to_string('app/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('app:user_create_done')


#companyUserのsignup
class CompanyCreate(generic.CreateView):
    model = User
    form_class = CompanyCreateForm
    template_name = 'user_create.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'company'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()

        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('app/mail_template/create/subject.txt', context)
        message = render_to_string('app/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('app:user_create_done')



# User(Society/Student)の仮登録
class UserCreateDone(generic.TemplateView):
    template_name = 'user_create_done.html'


# User(Society/Student)の本登録処理
class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


@login_required
# 各投稿の詳細ページに飛ぶ
def detailfunc(request, pk):
    #object = BoardModel.objects.get(pk=pk)
    object = BoardModel.objects.all().order_by('-created_at') # BordModelモデルの記事（objects）を全て(all())作成された順番（order_by('-readtext')）に取得してobject変数に代入
    return render(request, 'detail.html', {'object':object})


@login_required
# 各BoardModelを参照するため用のdetail関数を用意
def everypost(request, post_id): # urls.pyから送られてくるrequestとeverypost_idを取得
    post = get_object_or_404(BoardModel, id=post_id) # idが存在しなかった場合、「404 not found」
    user = request.user
    liked = False # 初期値はFalse
    if post.like.filter(id=request.user.id).exists(): # 詳細ページにリクエストしたユーザーが既に「いいね」をした場合
        liked = True # Trueを代入
    return render(request, 'everypost.html', {'post': post, 'user':user, 'liked': liked}) # likedも渡す


@login_required
@society_required
# 投稿フォーム用のadd関数
def add(request, pk):
    if request.user.pk == pk:
        if request.method == "POST":
            form = PostAddForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.author = request.user.society_name
                post.save()
                return redirect('app:society_home', pk=request.user.pk)
        else:   
            form = PostAddForm()
        return render(request, 'add.html', {'form': form})
    else:
        return redirect('app:logout')


@login_required
@company_required
# 投稿フォーム用のadd関数
def add_company(request, pk):
    if request.user.pk == pk:
        if request.method == "POST":
            form = PostAddForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.author = request.user.company_name
                post.save()
                return redirect('app:company_home', pk=request.user.pk)
        else:   
            form = PostAddForm()
        return render(request, 'add_company.html', {'form': form})
    else:
        return redirect('app:logout')


@login_required
@society_required
# 編集フォーム用のedit関数。編集ボタンをeverypost.htmlに作成。
def edit(request, post_id):
    post = get_object_or_404(BoardModel, id=post_id)
    #print(post.user.username)
    #print(request.user.username)
    if(post.user.username==request.user.username):
        if request.method == "POST":
            form = PostAddForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect('app:everypost', post_id=post.id)
        else:
            form = PostAddForm(instance=post)
        return render(request, 'edit.html', {'form': form, 'post':post })
    return redirect('app:logout')


#companyの投稿の編集
@login_required
@company_required
# 編集フォーム用のedit関数。編集ボタンをeverypost.htmlに作成。
def edit_company(request, post_id):
    post = get_object_or_404(BoardModel, id=post_id)
    #print(post.user.username)
    #print(request.user.username)
    if(post.user.username==request.user.username):
        if request.method == "POST":
            form = PostAddForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect('app:everypost', post_id=post.id)
        else:
            form = PostAddForm(instance=post)
        return render(request, 'edit_company.html', {'form': form, 'post':post })
    return redirect('app:logout')


# 削除フォーム用のdelete関数
# 削除機能はHTMLファイルを作成する必要がない。everypost.htmlに削除ボタンを作成。
@login_required
@society_required
def delete(request, post_id):
   post = get_object_or_404(BoardModel, id=post_id)
   post.delete()
   return redirect('app:society_home', pk=request.user.pk)


#companyの投稿の削除
# 削除フォーム用のdelete関数
# 削除機能はHTMLファイルを作成する必要がない。everypost.htmlに削除ボタンを作成。
@login_required
@company_required
def delete_company(request, post_id):
   post = get_object_or_404(BoardModel, id=post_id)
   post.delete()
   return redirect('app:company_home', pk=request.user.pk)


# # 学生側は別のeveyypost(編集削除できない)ページを作る。そのための関数。
# def everypostforStuednt(request, post_id):
#     post = get_object_or_404(BoardModel, id=post_id) # idが存在しなかった場合、「404 not found」
#     return render(request, 'everypostforStudent.html', {'post': post})


# いいね機能の実装
def goodfunc(request, post_id):
    post = get_object_or_404(BoardModel, id=post_id)
    post.good = post.good + 1
    post.save()
    return render(request,'everypost.html',{'post':post})


# 制限付きいいね機能用関数
def like(request):
    post = get_object_or_404(BoardModel, id=request.POST.get('post_id')) # いいねをした記事のIDを取得しpost変数に代入
    liked = False
    if post.like.filter(id=request.user.id).exists():
        post.like.remove(request.user) # いいねを既に押していたら除外
        liked = False
    else:
        post.like.add(request.user) # いいねを押してなかったら追加
        liked = True
    # return redirect('app:everypost', post_id=post.id)
    context={
       'post': post,
       'liked': liked,
       }
    if request.is_ajax():
        html = render_to_string('like.html', context, request=request )
        return JsonResponse({'form': html})


# Studentユーザに対するSocietyアカウントの一覧表示
@login_required
@student_required
def view_societies(request, pk):
    # ユーザ制限
    if request.user.pk == pk:
        # Societyアカウントのみ取得
        user_list = User.objects.filter(is_society=True)
        society_list = []
        for society in user_list:
            # 各サークルアカウントのfollower(student)を取得
            connections = Connection.objects.filter(following=society)
            for connection in connections:
                if (connection.follower==request.user):
                    # ログインしたstudentユーザがsocietyをフォローしたらフラグを立てる(保存はしない)
                    society.connected=True
            society_list.append(society)
        #print(society_list[0][0].pk)
        return render(request, 'society_list.html', {'society_list':society_list})
    else:
        return redirect('app:logout')

# Studentユーザに対するcompanyアカウントの一覧表示
@login_required
@student_required
def view_companies(request, pk):
    # ユーザ制限
    if request.user.pk == pk:
        # Companyアカウントのみ取得
        user_list = User.objects.filter(is_company=True)
        company_list = []
        for company in user_list:
            # 各サークルアカウントのfollower(student)を取得
            connections = Connection.objects.filter(following=company)
            for connection in connections:
                if (connection.follower==request.user):
                    # ログインしたstudentユーザがcompanyをフォローしたらフラグを立てる(保存はしない)
                    company.connected=True
            company_list.append(company)
        return render(request, 'company_list.html', {'company_list':company_list})
    else:
        return redirect('app:logout')


# Studentユーザに対する各Societyアカウントの詳細表示
@login_required
@student_required
def detail_society(request, pk, id):
    if request.user.pk == pk:
        society = User.objects.get(id=id)
        #サークルの投稿取得
        posts = BoardModel.objects.filter(user=society)
        #イベントの投稿取得
        events = Event.objects.filter(society=society)
        #print(society_pk)
        #society = get_object_or_404(User, pk=society_pk)
        connections = Connection.objects.filter(following=society)
        for connection in connections:
            if(connection.follower==request.user):
                society.connected=True
        return render(request, 'detail_society.html', {'society':society, 'posts':posts,'events':events})
    else:
        return redirect('app:logout')


# Studentユーザに対する各Companyアカウントの詳細表示
@login_required
@student_required
def detail_company(request, pk, id):
    if request.user.pk == pk:
        company = User.objects.get(id=id)
        #サークルの投稿取得
        posts = BoardModel.objects.filter(user=company)
        #イベントの投稿取得
        events = Event.objects.filter(society=company)
        connections = Connection.objects.filter(following=company)
        for connection in connections:
            if(connection.follower==request.user):
                company.connected=True
        return render(request, 'detail_company.html', {'company':company, 'posts':posts, 'events':events})
    else:
        return redirect('app:logout')


# Studentのプロフィールに必要
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser



# Studentのプロフィール表示
# Studentのプロフィール表示を関数として自分で書いてみる
@login_required
@student_required
def student_profile(request, pk):
    student = User.objects.get(pk=pk)
    if request.user.pk == pk:
        connection = Connection.objects.all()
        following = []
        for i in range(len(connection)):
            if connection[i].follower.username == student.username:
                following.append(connection[i].following)
        #print(following[0].society_name)
        return render(request, 'student_profile.html', {'student':student, 'following':following})
    else:
        return redirect('app:logout')


#studentのプロフィールのアップデート
class StudentProfileUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = StudentProfileUpdateForm
    template_name = 'student_profile_update.html'

    def get_success_url(self):
        return resolve_url('app:student_profile', pk=self.kwargs['pk'])

#サークルのプロフィール表示
class SocietyProfile(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'society_profile.html'

#サークルのプロフィールのアップデート
class SocietyProfileUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = SocietyProfileUpdateForm
    template_name = 'society_profile_update.html'

    def get_success_url(self):
        return resolve_url('app:society_profile', pk=self.kwargs['pk'])

#企業のプロフィール表示-------------------------------------------------------
class CompanyProfile(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'company_profile.html'

#企業のプロフィールのアップデート-----------------------------------------------
class CompanyProfileUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = CompanyProfileUpdateForm
    template_name = 'company_profile_update.html'

    def get_success_url(self):
        return resolve_url('app:company_profile', pk=self.kwargs['pk'])


# フォロー改良版
def follow(request, *args, **kwargs):
    try:
        # Student
        follower = User.objects.get(email=request.user.email)
        # Society
        following = User.objects.get(email=kwargs['email'])
    except User.DoesNotExist:
        return redirect('app:view_societies' , pk=request.user.pk)

    if follower == following:
        messages.warning(request, '自分自身はフォローできませんよ')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        if (created):
            print("creating now")
            # Studentのフォローしている数を増やす
            follower.following_number += 1
            follower.save()
            # Societyのフォローされている数を増やす
            following.followers_number += 1
            following.save()
            # フラグを立てる
            following.connected = True
        else:
            print("removing now")
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            # Studentのフォローしている数を減らす
            follower.following_number -= 1
            follower.save()
            # Societyのフォローされている数を減らす
            following.followers_number -= 1
            following.save()
            # フラグをおろす
            following.connected = False

    context={
       'society': following,
       #'liked': liked,
        }

    print(request)
    print(request.is_ajax())
    
    if request.is_ajax():
        html = render_to_string('follow.html', context, request=request )
        return JsonResponse({'form': html})


# フォロー
@login_required
@student_required
def follow_view(request, *args, **kwargs):
    user_list = User.objects.all()
    try:
        # Student
        follower = User.objects.get(email=request.user.email)
        # Society
        following = User.objects.get(email=kwargs['email'])
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        #return render(request, 'society_list.html', {'society_list':society_list})
        return redirect('app:view_societies' , pk=request.user.pk)

    if follower == following:
        messages.warning(request, '自分自身はフォローできませんよ')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        if (created):
            # Studentのフォローしている数を増やす
            follower.following_number += 1
            follower.save()
            # Societyのフォローされている数を増やす
            following.followers_number += 1
            following.save()
            messages.success(request, '{}をフォローしました'.format(following.username))
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    return redirect('app:view_societies' , pk=request.user.pk)

@login_required
@student_required
def follow_from_detail(request, *args, **kwargs):
    user_list = User.objects.all()
    try:
        # Student
        follower = User.objects.get(email=request.user.email)
        # Society
        following = User.objects.get(email=kwargs['email'])
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        return redirect('app:detail_society' , pk=request.user.pk, id=following.id)

    if follower == following:
        messages.warning(request, '自分自身はフォローできませんよ')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        if (created):
            # Studentのフォローしている数を増やす
            follower.following_number += 1
            follower.save()
            # Societyのフォローされている数を増やす
            following.followers_number += 1
            following.save()
            messages.success(request, '{}をフォローしました'.format(following.username))
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    return redirect('app:detail_society' , pk=request.user.pk, id=following.id)

@login_required
@student_required
def follow_company(request, *args, **kwargs):
    user_list = User.objects.all()
    try:
        # Student
        follower = User.objects.get(email=request.user.email)
        # Company
        following = User.objects.get(email=kwargs['email'])
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        #return render(request, 'society_list.html', {'society_list':society_list})
        return redirect('app:view_companies' , pk=request.user.pk)

    if follower == following:
        messages.warning(request, '自分自身はフォローできませんよ')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        if (created):
            # Studentのフォローしている数を増やす
            follower.following_number += 1
            follower.save()
            # Societyのフォローされている数を増やす
            following.followers_number += 1
            following.save()
            messages.success(request, '{}をフォローしました'.format(following.username))
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    return redirect('app:view_companies' , pk=request.user.pk)


@login_required
@student_required
def follow_company_from_detail(request, *args, **kwargs):
    user_list = User.objects.all()
    try:
        # Student
        follower = User.objects.get(email=request.user.email)
        # Company
        following = User.objects.get(email=kwargs['email'])
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        #return render(request, 'society_list.html', {'society_list':society_list})
        return redirect('app:detail_company' , pk=request.user.pk, id=following.id)

    if follower == following:
        messages.warning(request, '自分自身はフォローできませんよ')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        if (created):
            # Studentのフォローしている数を増やす
            follower.following_number += 1
            follower.save()
            # Societyのフォローされている数を増やす
            following.followers_number += 1
            following.save()
            messages.success(request, '{}をフォローしました'.format(following.username))
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    return redirect('app:detail_company' , pk=request.user.pk, id=following.id)


# アンフォロー
@login_required
@student_required
def unfollow_view(request, *args, **kwargs):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    try:
        #follower = User.objects.get(username=request.user.username)
        #following = User.objects.get(username=kwargs['username'])
        follower = User.objects.get(email=request.user.email)
        following = User.objects.get(email=kwargs['email'])

        if follower == following:
            messages.warning(request, '自分自身のフォローを外せません')
        else:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            # Studentのフォローしている数を減らす
            follower.following_number -= 1
            follower.save()
            # Societyのフォローされている数を減らす
            following.followers_number -= 1
            following.save()
            messages.success(request, 'あなたは{}のフォローを外しました'.format(following.username))
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        #return render(request, 'society_list.html', {'society_list':society_list})
        return redirect('app:view_societies' , pk=request.user.pk)
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    #return render(request, 'society_list.html', {'society_list':society_list})
    return redirect('app:view_societies' , pk=request.user.pk)

# アンフォロー
@login_required
@student_required
def unfollow_from_detail(request, *args, **kwargs):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    try:
        follower = User.objects.get(email=request.user.email)
        following = User.objects.get(email=kwargs['email'])

        if follower != following:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            # Studentのフォローしている数を減らす
            follower.following_number -= 1
            follower.save()
            # Societyのフォローされている数を減らす
            following.followers_number -= 1
            following.save()
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))

        return redirect('app:detail_society' , pk=request.user.pk, id=following.id)
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    return redirect('app:detail_society' , pk=request.user.pk, id=following.id)

# アンフォロー
@login_required
@student_required
def unfollow_from_profile(request, *args, **kwargs):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    try:
        follower = User.objects.get(email=request.user.email)
        following = User.objects.get(email=kwargs['email'])

        if follower != following:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            # Studentのフォローしている数を減らす
            follower.following_number -= 1
            follower.save()
            # Societyのフォローされている数を減らす
            following.followers_number -= 1
            following.save()
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))

        return redirect('app:student_profile' , pk=request.user.pk)
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    return redirect('app:student_profile' , pk=request.user.pk)

# アンフォロー
@login_required
@student_required
def unfollow_company(request, *args, **kwargs):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    try:
        follower = User.objects.get(email=request.user.email)
        following = User.objects.get(email=kwargs['email'])

        if follower != following:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            # Studentのフォローしている数を減らす
            follower.following_number -= 1
            follower.save()
            # Societyのフォローされている数を減らす
            following.followers_number -= 1
            following.save()
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))

        return redirect('app:view_companies' , pk=request.user.pk)
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    return redirect('app:view_companies' , pk=request.user.pk)

# アンフォロー
@login_required
@student_required
def unfollow_company_from_detail(request, *args, **kwargs):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    try:
        follower = User.objects.get(email=request.user.email)
        following = User.objects.get(email=kwargs['email'])

        if follower != following:
            unfollow = Connection.objects.get(follower=follower, following=following)
            unfollow.delete()
            # Studentのフォローしている数を減らす
            follower.following_number -= 1
            follower.save()
            # Societyのフォローされている数を減らす
            following.followers_number -= 1
            following.save()
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))

        return redirect('app:detail_company' , pk=request.user.pk, id=following.id)
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    return redirect('app:detail_company' , pk=request.user.pk, id=following.id)


@login_required
#@society_required
# Societyユーザによるイベント作成
def create_event(request, pk):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:
        if request.method == "POST":
            # イベント作成フォーム
            form = CreateEventForm(request.POST, request.FILES)
            # 追加情報入力フォーム(サークル)
            form_info = AddInformationForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                # イベントの主催者にログインユーザ(サークル)を登録
                event.society = request.user
                event.save()
                info = form_info.save(commit=False)
                # 追加情報とイベントを紐付け
                info.event = event
                info.save()
                return redirect('app:view_events', pk=request.user.pk)
        else:   
            form = CreateEventForm()
            form_info = AddInformationForm()
        return render(request, 'create_event.html', {'form': form, 'form_info':form_info})
    else:
        return redirect('app:logout')


@login_required
#@student_required
# Student / Society ユーザへのイベント一覧表示
def view_events(request, pk):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:

        # Studentユーザに対する表示
        if request.user.is_student:
            # ログインしてるStudentユーザの情報取得
            student = User.objects.get(pk=pk)
            # ログインしたStudentユーザと結ぶついているConnection
            connections = Connection.objects.filter(follower=student)

            # 日本時間
            jst = pytz.timezone('Asia/Tokyo')

            # イベントリスト
            event_list = []
            for connection in connections:
                # ログインしたStudentユーザがフォローしてるサークルの作成したイベントを取得
                events = Event.objects.filter(society=connection.following)
                for event in events:
                    # 各イベントについて参加者を取得
                    participants = event.students.all()

                    # イベント開催日が現在の時刻より先ならば
                    if event.event_date > datetime.now(tz=jst):
                        for participant in participants:
                            # 参加者の中にログインしたユーザがいれば(すでに参加申し込みしていれば)フラグを立てる
                            if request.user == participant:
                                event.joined = True
                        # 申し込み期限が過ぎていたらフラグを立てる
                        if event.deadline < datetime.now(tz=jst):
                            event.expired = True
                        #print(event.images.url)
                        event_list.append(event)
            # 締め切り日時で並べ換える
            event_list = sorted(event_list, key=lambda x:x.deadline)
            # Studentユーザに対して自身がフォローしてるサークルの作成したイベントを表示する。
            return render(request, 'event_list.html', {'event_list':event_list})

        # Societyユーザに対する表示
        elif request.user.is_society or request.user.is_company:
            # ログインしてるSocietyユーザの情報取得
            society = User.objects.get(pk=pk)
            # 自身が作成したイベントを取得
            event_list = Event.objects.filter(society=society)
            # 締め切り日時で並べ換える
            event_list = sorted(event_list, key=lambda x:x.deadline)
            # Societyユーザに対して自身が作成したイベントを表示する。
            return render(request, 'event_list.html', {'event_list':event_list})

    # 不正アクセスに対するログアウト処理
    else:
        return redirect('app:logout')   


@login_required
# イベント告知の詳細ページへ
def everyevent(request, pk, id):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:

        event = get_object_or_404(Event, id=id) # idが存在しなかった場合、「404 not found」
        user = request.user
        information = get_object_or_404(Information, event=event)

        # 日本時間
        jst = pytz.timezone('Asia/Tokyo')
        
        # Studentユーザに対する表示
        if user.is_student:

            # 各イベントについて参加者を取得
            participants = event.students.all()
            for participant in participants:
                # 参加者の中にログインしたユーザがいれば(すでに参加申し込みしていれば)フラグを立てる
                if user == participant:
                    event.joined = True

            # 申し込み期限が過ぎていたらフラグを立てる
            if event.deadline < datetime.now(tz=jst):
                event.expired = True

            return render(request, 'everyevent.html', {'event': event, 'user':user})

        # Societyユーザに対する表示
        elif user.is_society or user.is_company:

            # 追加入力がある場合
            if information.info_title != '':
                # html表示のためにフラグを立てておく
                event.flag = True
                # 追加情報のタイトルをhtmlに渡す用
                event.extra = information.info_title
                # 学生に入力してもらった追加情報を取得
                extrainfos = ExtraInfo.objects.filter(source=information)
                # イベント参加者情報を取得
                students = event.students.all()
                # 参加者のうち男性の人数を記録
                students.male = 0
                # 参加者のうち女性の人数を記録
                students.female = 0
                for student in students:
                    for extrainfo in extrainfos:
                        if student == extrainfo.info_owner:
                            if student.gender==1:
                                student.gen = '女性'
                                students.female += 1
                            else:
                                student.gen = '男性'
                                students.male += 1
                            # 新しいフィールドinfoを作成し、追加情報と学生を紐付ける
                            student.info = extrainfo.info
                return render(request, 'everyevent.html', {'event': event, 'user':user, 'students':students})

            # 追加入力なしの場合
            else:
                # イベント参加者情報を取得
                students = event.students.all()
                # 参加者のうち男性の人数を記録
                students.male = 0
                # 参加者のうち女性の人数を記録
                students.female = 0
                for student in students:
                    if student.gender==1:
                        student.gen = '女性'
                        students.female += 1
                    else:
                        student.gen = '男性'
                        students.male += 1
                    print(student.gen)
                return render(request, 'everyevent.html', {'event': event, 'user':user, 'students':students})
            
            return render(request, 'everyevent.html', {'event': event, 'user':user})

    return redirect('app:logout') 
        

# 流れ
# 追加情報あり: join_event_comfirm → join_event_comfirm.html → join_event_comfirm(追加情報の保存) → join_event(参加者登録)
# 追加情報なし: join_event_comfirm → join_event_comfirm.html → join_event(参加者登録)
@login_required
@student_required
# Studentユーザへのイベント参加確認画面の表示
def join_event_confirm(request, pk, id):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:
        # イベント情報取得
        event = get_object_or_404(Event, id=id) # idが存在しなかった場合、「404 not found」
        user = request.user

        # 追加情報モデル取得
        information = get_object_or_404(Information, event=event)

        # 追加で入力すべき情報がある場合
        if information.info_title != '':
            # html表示のためにフラグを立てる
            event.flag = True
            if request.method == "POST":
                # 追加情報入力フォーム取得
                form = InputInformationForm(request.POST, request.FILES)
                if form.is_valid():
                    info = form.save(commit=False)
                    # 追加情報のタイトル情報(サークルが決めたものとの紐付け)
                    info.source = information
                    # 入力した学生ユーザとの紐付け
                    info.info_owner = request.user
                    # 保存
                    info.save()
                    return redirect('app:join_event', pk=user.pk, id=id)
            else:
                # 追加情報入力フォーム取得
                form = InputInformationForm()
            return render(request, 'join_event_confirm.html', {'event': event, 'user':user, 'information':information, 'form':form})

        return render(request, 'join_event_confirm.html', {'event': event, 'user':user})

    else:
        return redirect('app:logout') 


@login_required
@student_required
# Studentユーザによるイベント参加
def join_event(request, pk, id):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:
        # ログインしたStudentユーザ情報取得
        student = User.objects.get(pk=pk)
        # 参加するイベント取得
        event = Event.objects.get(id=id)
        # イベント参加者にStudentユーザ追加
        event.students.add(student)
        # 変更内容保存
        event.save()
        # 確認
        #print(event.students.all())

        return redirect('app:view_events', pk=request.user.pk)
    else:
        return redirect('app:logout') 


@login_required
@student_required
# Studentユーザによるイベント参加キャンセル
def cancel_event(request, pk, id):
    if request.user.pk == pk:
        # 該当イベント取得
        event = get_object_or_404(Event, id=id)
        students = event.students.all()
        information = get_object_or_404(Information, event=event)

        # イベント参加者からログインユーザを探し削除
        for student in students:
            if student == request.user:
                event.students.remove(student)

        if information.info_title != '':
            extrainfos = ExtraInfo.objects.filter(source=information)
            for info in extrainfos:
                if info.info_owner == request.user:
                    info.delete()

        #return redirect('app:everyevent', pk=request.user.pk, id=id)
        return redirect('app:view_events', pk=request.user.pk)

    else:
        return redirect('app:logout')


# Societyユーザによるイベントの編集
# このやり方だと途中から403forbitten
'''class EditEvent(OnlyYouMixin, generic.UpdateView):
    model = Event
    form_class = EditEventForm
    template_name = 'edit_event.html'

    def get_success_url(self):
        return resolve_url('app:view_events', pk=self.kwargs['pk'])'''

# クラスじゃなくて関数の使用で逃げる
@login_required
#@society_required
# 編集フォーム用のedit関数。編集ボタンをeverypost.htmlに作成。
def edit_event(request, pk, id):
    event = get_object_or_404(Event, id=id)
    information = get_object_or_404(Information, event=event)
    if(event.society.username==request.user.username):
        if request.method == "POST":
            form = CreateEventForm(request.POST, request.FILES, instance=event)
            form_info = AddInformationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                #form_info.save()

                #メールを送る
                shusaisha = event.society
                eventnonamae = event.event_name
                eventdate = event.event_date

                connections = Connection.objects.filter(following=request.user)
                followshiteruhito_email = []
                for c in connections:
                    followshiteruhito_email.append(c.follower.email)
                # print('主催者',shusaisha)
                # print('日付',eventdate)
                # print('イベントの名前',eventnonamae)
                
                subject = "{}が主催者の{}開催の{}は変更になりました".format(shusaisha,eventdate,eventnonamae)
                message = "イベントは主催者によって変更になったことをお知らせします"
                from_email = request.user.email # 送信者
                recipient_list = [request.user.email] # 宛先リスト
                bcc =  followshiteruhito_email # BCCリスト
                email = EmailMessage(subject, message, from_email, recipient_list, bcc)
                email.send()


                return redirect('app:everyevent', pk=pk, id=id)
        else:
            form = CreateEventForm(instance=event)
            form_info = AddInformationForm(instance=information)
        return render(request, 'edit_event.html', {'form': form, 'event':event})
    return redirect('app:logout')


# Societyユーザによるイベントの削除
# @login_required
# @society_required
# def delete_event(request, pk, id):
#     if request.user.pk == pk:
#         event = get_object_or_404(Event, id=id)
#         event.delete()
#         return redirect('app:view_events', pk=request.user.pk)

#     else:
#         return redirect('app:logout')

# Societyユーザによるイベントの削除
@login_required
#@society_required
def delete_event(request, pk, id):                                                  
    if request.user.pk == pk:
        event = get_object_or_404(Event, id=id)
        shusaisha = event.society
        eventnonamae = event.event_name
        eventdate = event.event_date
        event.delete()

        connections = Connection.objects.filter(following=request.user)
        followshiteruhito_email = []
        for c in connections:
            followshiteruhito_email.append(c.follower.email)
        # print('主催者',shusaisha)
        # print('日付',eventdate)
        # print('イベントの名前',eventnonamae)
        
        subject = "{}が主催者の{}開催の{}は中止になりました".format(shusaisha,eventdate,eventnonamae)
        message = "イベントは主催者によって中止になったことをお知らせします"
        from_email = request.user.email # 送信者
        recipient_list = [request.user.email] # 宛先リスト
        bcc =  followshiteruhito_email # BCCリスト
        email = EmailMessage(subject, message, from_email, recipient_list, bcc)
        email.send()

        return redirect('app:view_events', pk=request.user.pk)

    else:
        return redirect('app:logout')


#検索部分の新しいコード
def searchfunc(request,pk,*args, **kwargs):
    query = request.GET.get('q')
    if query:
        object_list = BoardModel.objects.all()

        #サークル名-------------------------------
        user_list = User.objects.all().filter(
            Q(society_name__icontains=query,
            is_society=True)
        ).distinct()
        society_list = []
        for society in user_list:
            connections = Connection.objects.filter(following=society)
            for connection in connections:
                if (connection.follower==request.user):
                    society.created=True
            society_list.append(society)
        
        number_society = len(society_list)

        object_list_author = society_list

        #企業名----------------------------------------
        user_list_company = User.objects.all().filter(
            Q(company_name__icontains=query,
            is_company=True)
        ).distinct()
        company_list = []
        for company in user_list_company:
            connections = Connection.objects.filter(following=company)
            for connection in connections:
                if (connection.follower==request.user):
                    company.created=True
            company_list.append(company)
        
        number_company = len(company_list)

        object_list_author_company = company_list

        #タグ----------------------------------------------
        tag = '#'+query

        object_list_title = object_list.filter(
                Q(content__icontains=tag)
            ).distinct()

        return render(request,'search.html',{'object_list_title':object_list_title,'object_list_author':society_list,'object_list_author_company':object_list_author_company,'query': query,'number_society':number_society,'number_company':number_company})

    else:
        object_list = BoardModel.objects.all()

        object_list_author = object_list.filter(
            Q(author__icontains=query)
        ).distinct()


        object_list_title = object_list.filter(
                Q(title__icontains=query)
            ).distinct()
        return render(request,'search.html',{'object_list_title':object_list_title,'object_list_author':object_list_author,'object_list_author_company':object_list_author,'query': query})
