from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User, Student, Company, BoardModel


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'society_name','school_name','grade','is_student','is_society','is_company')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'society_name')
    ordering = ('email',)


class MyStudentChangeForm(UserChangeForm):
    class Meta:
        model = Student
        fields = '__all__'


# 'email'fieldはStudentUser特有ではないため以下のコードでエラーが出てしまう。
'''
class MyStudentCreationForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ('email',)
'''

class MyCompanyChangeForm(UserChangeForm):
    class Meta:
        model = Company
        fields = '__all__'

admin.site.register(User, MyUserAdmin)
admin.site.register(Student)
admin.site.register(Company)
admin.site.register(BoardModel)