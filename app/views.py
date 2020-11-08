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
    StudentProfileUpdateForm, CreateEventForm, EditEventForm
)
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, DetailView, UpdateView

from .models import User, Student, Company, BoardModel, Connection, Event
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
                return redirect('app:student_home', pk=user.pk)
            if user_login.is_society:
                return redirect('app:society_home', pk=user.pk)
            if user_login.is_company:
                return redirect('app:company_home')
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
        return render(request, 'society_home.html', {'object':posts})
    else:
        return redirect('app:logout')


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


@login_required
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


# 削除フォーム用のdelete関数
# 削除機能はHTMLファイルを作成する必要がない。everypost.htmlに削除ボタンを作成。
@login_required
@society_required
def delete(request, post_id):
   post = get_object_or_404(BoardModel, id=post_id)
   post.delete()
   return redirect('app:society_home', pk=request.user.pk)


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


# Studentユーザに対する各Societyアカウントの詳細表示
@login_required
@student_required
def detail_society(request, pk, id):
    if request.user.pk == pk:
        society = User.objects.get(id=id)
        #print(society_pk)
        #society = get_object_or_404(User, pk=society_pk)
        connections = Connection.objects.filter(following=society)
        for connection in connections:
            if(connection.follower==request.user):
                society.created=True
        return render(request, 'detail_society.html', {'society':society})
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


class StudentProfileUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = StudentProfileUpdateForm
    template_name = 'student_profile_update.html'

    def get_success_url(self):
        return resolve_url('app:student_profile', pk=self.kwargs['pk'])



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
    return redirect('app:detail_society' , pk=request.user.pk, email=following.email)


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
        return redirect('app:student_profile', pk=request.user.pk)
        
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    #return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'email': following.username}))
    #return render(request, 'society_list.html', {'society_list':society_list})
    return redirect('app:student_profile', pk=request.user.pk)



@login_required
@society_required
# Societyユーザによるイベント作成
def create_event(request, pk):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:
        if request.method == "POST":
            form = CreateEventForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                # イベントの主催者にログインユーザ(サークル)を登録
                event.society = request.user
                event.save()
                return redirect('app:view_events', pk=request.user.pk)
        else:   
            form = CreateEventForm()
        return render(request, 'create_event.html', {'form': form})
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

            # イベントリスト
            event_list = []
            for connection in connections:
                # ログインしたStudentユーザがフォローしてるサークルの作成したイベントを取得
                events = Event.objects.filter(society=connection.following)
                for event in events:
                    # 各イベントについて参加者を取得
                    participants = event.students.all()
                    for participant in participants:
                        # 参加者の中にログインしたユーザがいれば(すでに参加申し込みしていれば)フラグを立てる
                        if request.user == participant:
                            event.joined = True
                    event_list.append(event)

            # Studentユーザに対して自身がフォローしてるサークルの作成したイベントを表示する。
            return render(request, 'event_list.html', {'event_list':event_list})

        # Societyユーザに対する表示
        elif request.user.is_society:
            # ログインしてるSocietyユーザの情報取得
            society = User.objects.get(pk=pk)
            # 自身が作成したイベントを取得
            event_list = Event.objects.filter(society=society)
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
        
        # Studentユーザに対する表示
        if user.is_student:

            # 各イベントについて参加者を取得
            participants = event.students.all()
            for participant in participants:
                # 参加者の中にログインしたユーザがいれば(すでに参加申し込みしていれば)フラグを立てる
                if user == participant:
                    event.joined = True

            return render(request, 'everyevent.html', {'event': event, 'user':user})

        # Societyユーザに対する表示
        elif user.is_society:
            return render(request, 'everyevent.html', {'event': event, 'user':user})

    return redirect('app:logout') 
        

# Studentユーザへのイベント参加確認画面の表示
def join_event_confirm(request, pk, id):
    # ユーザ認証(url書き換えによるログイン偽装防止)
    if request.user.pk == pk:
        # イベント情報取得
        event = get_object_or_404(Event, id=id) # idが存在しなかった場合、「404 not found」
        user = request.user
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
        print(event.students.all())
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
        # イベント参加者からログインユーザを探し削除
        for student in students:
            if student == request.user:
                event.students.remove(student)

        #return redirect('app:everyevent', pk=request.user.pk, id=id)
        return redirect('app:view_events', pk=request.user.pk)

    else:
        return redirect('app:logout')


# Societyユーザによるイベントの編集
class EditEvent(OnlyYouMixin, generic.UpdateView):
    model = Event
    form_class = EditEventForm
    template_name = 'edit_event.html'

    def get_success_url(self):
        return resolve_url('app:view_events', pk=self.kwargs['pk'])


# Societyユーザによるイベントの削除
@login_required
@society_required
def delete_event(request, pk, id):
    if request.user.pk == pk:
        event = get_object_or_404(Event, id=id)
        event.delete()
        return redirect('app:view_events', pk=request.user.pk)

    else:
        return redirect('app:logout')


