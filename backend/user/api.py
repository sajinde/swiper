from django.shortcuts import render

from lib.cache import rds
from lib.http import require_post
from common import errors
from user.models import User
from user.forms import ProfileForm
from user.logic import send_login_code
from user.logic import upload_avatar_to_cloud


@require_post
def verify_phone(request):
    '''提交手机号，向用户发送验证码'''
    phone_num = request.POST.get('phone')
    send_login_code(phone_num)


@require_post
def login(request):
    '''提交验证码并登录'''
    phone_num = request.POST.get('phone')
    code = request.POST.get('code')
    key = keys.LOGIN_SMS_KEY % phone_num
    if rds.get(key) != code:
        raise errors.InvalidPIN

    # 获取用户，并执行登陆操作
    user, created = User.get_or_create(phone_num=phone_num)
    if created:
        user.init()
    request.session['uid'] = user.id
    request.session['nickname'] = user.nickname
    return {'user': user.to_dict()}


def show_profile(request):
    '''查看配置'''
    return request.user.profile.to_dict()


@require_post
def update_profile(request):
    '''修改用户配置'''
    profile = request.user.profile
    form = ProfileForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
    else:
        raise errors.ParamsError


@require_post
def upload_avatar(request):
    '''上传头像'''
    avatar = request.user.avatar
    upload_avatar_to_cloud(avatar, request.POST)
