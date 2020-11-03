from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.contrib.auth import authenticate, login,logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect,render
from django.template.loader import render_to_string
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, StudentCreateForm, CompanyCreateForm
)
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .models import User, Student, Company, BoardModel
from .decorators import student_required, society_required, company_required

from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from itertools import chain

# ログイン前のページ表示
def selectfunc(request):
    return render(request,'select.html')


# signup時、studentかsocietyか選択
class SignUpView(TemplateView):
    template_name = 'signup.html'


# login
def loginfunc(request):
    if request.method == 'POST':
        unko = User.objects.get(email=request.POST.get('username'))
        print(unko.is_society)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_login = User.objects.get(email=username)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user_login)
            if user_login.is_student:
                #return render(request, 'list.html')
                #return redirect('app:list')
                return redirect('app:student_home')
            if user_login.is_society:
                #return render(request, 'society_home.html')
                return redirect('app:society_home')
            if user_login.is_company:
                #return render(request, 'company_home.html')
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
        #object_list = User.objects.all()

        object_list = object_list.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        ).distinct()
        #b_count = b_object_list.count()

        # u_object_list = u_object_list.filter(
        #     Q(society_name__icontains=query)
        # ).distinct()
        # u_count = u_object_list.count()

        #object_list = list(chain(b_object_list,u_object_list))
        # print(b_count)
        # print(u_count)
        # count_sum = b_count + u_count


        if object_list:
        
            print('入ってますよ')

        else:
            print('ふざけんなこのやろうしね')
        
        #return render(request,'student_home.html',{'b_object_list':b_object_list,'u_object_list':u_object_list,'query':query,'count':count_sum})

    else:
        #print(BoardModel.objects.all().get(author='soccer'))
        #count_sum = 0
        object_list = BoardModel.objects.all()
    return render(request, 'student_home.html', {'object_list':object_list,'query': query})
    #return render(request,'student_home.html')


# def index(request):
#    query = request.GET.get('q')
#    if query:
#        posts = Post.objects.all().order_by('-created_at')
#        posts = posts.filter(
#        Q(title__icontains=query)|
#        Q(user__username__icontains=query)
#        ).distinct()
#    else:
#        posts = Post.objects.all().order_by('-created_at')  
#    return render(request, 'blog_app/index.html', {'posts': posts, 'query': query,}) #省略


# SocietyUserのhome画面
@login_required
@society_required
def society_home(request):
    return render(request,'society_home.html')


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
        #login(self.request, user)
        #return redirect('app:list')。
    
        #user = form.save(commit=False)
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
        #login(self.request, user)
        #return redirect('app:list')。
    
        #user = form.save(commit=False)
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


# 各投稿の詳細ページに飛ぶ
def detailfunc(request, pk):
    object = BoardModel.objects.get(pk=pk)
    return render(request, 'detail.html', {'object':object})


# いいね機能の実装
def goodfunc(request, pk):
    post = BoardModel.objects.get(pk=pk)
    post.good = post.good + 1
    post.save()
    return redirect('app:student_home')




# 以下使わないが、念のため残しておく。
'''
def loginfunc(request):
    if request.method == 'POST':
        print(request.POST)
        username2 = request.POST['username']
        password2 = request.POST['password']
        user = authenticate(request, email=username2, password=password2)

        if user is not None:
            login(request, user)
            return render(request,'list.html')
        
        else:
            return redirect('login')

    return render(request, 'login.html')

def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('app:list')
        else:
            return redirect('app:list')
    return render(request, 'select.html')

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'login.html'

def create_user(request):
    if request.method == 'POST':
        #username = request.POST['username']
        #password = request.POST['password']
        user_form = UserCreateForm(request.POST)
        student_form = StudentCreateForm(request.POST)
        print('1')

        print(user_form.is_valid())
        print(student_form.is_valid())
        if  user_form.is_valid() and student_form.is_valid():
            user = user_form.save()
            #student = student_form.save()
            #student.user = user
            #student.save()
            print('3')
            return redirect('app:list')
    else:
        user_form = UserCreateForm()
        student_form = StudentCreateForm()
        print('4')
    print('5')
    return render(
        request,
        'signup2.html',
        {'user_form': user_form, 'student_form': student_form}
    )

def signupfunc(request):
  if request.method =='POST':
    username2 = request.POST['username']
    password2 = request.POST['password']
    try:
      User.objects.get(username=username2)
      return render(request, 'signup.html', {'error':'このユーザーは登録されています'})
    except:
      user = User.objects.create_user(username, '', password2)
      return render(request, 'signup.html', {'some':100})
  return render(request, 'signup.html', {'some':100})

@login_required
def listfunc(request):
    object_list = BoardModel.objects.all()
    return render(request, 'list.html', {'object_list':object_list})
   #return render(request, 'list.html')

'''