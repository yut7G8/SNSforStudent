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
from django.shortcuts import redirect,render, get_object_or_404
from django.template.loader import render_to_string
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, StudentCreateForm, CompanyCreateForm, PostAddForm
)
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, DetailView, UpdateView

from .models import User, Student, Company, BoardModel, Connection
from .decorators import student_required, society_required, company_required

from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from itertools import chain

from django.urls import reverse_lazy
from .helpers import get_current_user
from django.contrib import messages

from django.utils.decorators import method_decorator

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
                return redirect('app:student_home')
            if user_login.is_society:
                return redirect('app:society_home')
            if user_login.is_company:
                return redirect('app:company_home')
        else:
            return render(request, 'login.html', {'error':'メールアドレスかパスワードが間違っています'})
    else:
        return render(request, 'login.html')


# StudentUserのhome画面
@login_required
@student_required
def student_home(request):
    query = request.GET.get('q')
    if query:
        object_list = BoardModel.objects.all()

        object_list = object_list.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        ).distinct()

    else:
        object_list = BoardModel.objects.all()
    return render(request, 'student_home.html', {'object_list':object_list,'query': query})


# SocietyUserのhome画面
@login_required
@society_required
def society_home(request):
    #return render(request,'society_home.html')
    #return render(request,'detail.html')
    object = BoardModel.objects.all().order_by('-readtext') # BordModelモデルの記事（objects）を全て(all())作成された順番（order_by('-readtext')）に取得してobject変数に代入
    # if (request.user == BoardModel.objects.order_by('user')):
    return render(request, 'society_home.html', {'object':object})
    # else:
    #     return redirect('app:add')

# CompanyUserのhome画面
@login_required
@company_required
def company_home(request):
    return render(request,'company_home.html')


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
    object = BoardModel.objects.all().order_by('-readtext') # BordModelモデルの記事（objects）を全て(all())作成された順番（order_by('-readtext')）に取得してobject変数に代入
    return render(request, 'detail.html', {'object':object})


# 各BoardModelを参照するため用のdetail関数を用意
def everypost(request, post_id): # urls.pyから送られてくるrequestとeverypost_idを取得
    post = get_object_or_404(BoardModel, id=post_id) # idが存在しなかった場合、「404 not found」
    user = request.user
    #print(request.user.is_society)
    #print(post.author)
    return render(request, 'everypost.html', {'post': post, 'user':user})


@login_required
@society_required
# 投稿フォーム用のadd関数
def add(request):
   if request.method == "POST":
      form = PostAddForm(request.POST, request.FILES)
      print(1)
      if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.author = request.user.society_name
        #print(post.author)
        post.save()
        print(2)
        return redirect('app:society_home')
   else:   
       form = PostAddForm()
       print(3)
   return render(request, 'add.html', {'form': form})


@login_required
@society_required
# 編集フォーム用のedit関数。編集ボタンをeverypost.htmlに作成。
def edit(request, post_id):
    post = get_object_or_404(BoardModel, id=post_id)
    #print(post.user.username)
    #print(request.user.username)
    if(post.user.username==request.user.username): # 投稿者のみが編集できるように設定
        if request.method == "POST":
            form = PostAddForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect('app:everypost', post_id=post.id)
        else:
            form = PostAddForm(instance=post)
        return render(request, 'edit.html', {'form': form, 'post':post })
    else:
        return redirect('app:select')


# 削除フォーム用のdelete関数
# 削除機能はHTMLファイルを作成する必要がない。everypost.htmlに削除ボタンを作成。
@login_required
@society_required
def delete(request, post_id):
   post = get_object_or_404(BoardModel, id=post_id)
   if(post.user.username==request.user.username): # 投稿者のみが削除できるように設定
       post.delete()
       return redirect('app:society_home')
   else:
       return redirect('app:select') 


# # 学生側は別のeveyypost(編集削除できない)ページを作る。そのための関数。
# def everypostforStuednt(request, post_id):
#     post = get_object_or_404(BoardModel, id=post_id) # idが存在しなかった場合、「404 not found」
#     return render(request, 'everypostforStudent.html', {'post': post})


# いいね機能の実装
def goodfunc(request, pk):
    post = BoardModel.objects.get(pk=pk)
    post.good = post.good + 1
    post.save()
    return redirect('app:student_home')


# Studentユーザに対するSocietyアカウントの一覧表示
@login_required
@student_required
def view_societies(request):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    return render(request, 'society_list.html', {'society_list':society_list})


# Studentユーザに対する各Societyアカウントの詳細表示
@login_required
@student_required
def detail_society(request, pk):
    society = User.objects.get(pk=pk)
    return render(request, 'detail_society.html', {'society':society})


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
    connection = Connection.objects.all()
    following = []
    for i in range(len(connection)):
        if connection[i].follower.username == student.username:
            following.append(connection[i].following)
    #print(following[0].society_name)
    return render(request, 'student_profile.html', {'student':student, 'following':following})



# フォロー
@login_required
@student_required
def follow_view(request, *args, **kwargs):
    user_list = User.objects.all()
    society_list = []
    for user in user_list:
        if user.is_society:
            society_list.append(user)
    try:
        #follower = User.objects.get(username=request.user.username)
        follower = User.objects.get(email=request.user.email)
        #print(request.user.email)
        #print(kwargs)
        #print("hello")
        #following = User.objects.get(username=kwargs['username'])
        following = User.objects.get(email=kwargs['email'])
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        return render(request, 'society_list.html', {'society_list':society_list})

    if follower == following:
        messages.warning(request, '自分自身はフォローできませんよ')
    else:
        _, created = Connection.objects.get_or_create(follower=follower, following=following)

        if (created):
            #print("hello")
            #print(follower.following_number)
            follower.following_number += 1
            #print(follower.following_number)
            following.followers_number += 1
            messages.success(request, '{}をフォローしました'.format(following.username))
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    return render(request, 'society_list.html', {'society_list':society_list})


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
            follower.following_number -= 1
            following.followers_number -= 1
            messages.success(request, 'あなたは{}のフォローを外しました'.format(following.username))
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['email']))
        #return HttpResponseRedirect(reverse_lazy('users:index'))
        return render(request, 'society_list.html', {'society_list':society_list})
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    return render(request, 'society_list.html', {'society_list':society_list})