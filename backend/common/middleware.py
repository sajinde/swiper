from logging import getLogger
from traceback import format_exc

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from common import errors
from lib.http import render_json
from lib.mail import async_mail_admins
from user.models import User

err_log = getLogger('err')


class LogicErrorMiddleware(MiddlewareMixin):
    '''通用逻辑异常处理中间件'''
    def process_exception(self, request, exception):
        if isinstance(exception, errors.LogicError):
            response = render_json(error=exception)
        else:
            error_info = '\n%s' % format_exc()
            err_log.error(error_info)  # 输出错误日志
            async_mail_admins('异常告警', error_info, fail_silently=False)
            response = render_json(error=errors.InternalError)

        return response


class AuthMiddleware(MiddlewareMixin):
    '''登陆认证检查中间件'''
    # 不需要检查的路径
    IGNORED_PATH_LIST = [
        '/api/user/verify',
        '/api/user/login',
        '/weibo/'
    ]

    def is_ignored_path(self, path):
        '''是否是需要忽略的路径'''
        for ignored_path in self.IGNORED_PATH_LIST:
            if path.startswith(ignored_path):
                return True
        return False

    def process_request(self, request):
        # 排除白名单里的路径
        if self.is_ignored_path(request.path):
            return

        # 检查 uid 是否存在于 session 中
        if 'uid' not in request.session:
            return render_json(error=errors.LoginRequired)

        # 为 request 动态添加 user 属性
        uid = request.session['uid']
        try:
            user = User.get(pk=uid)
            request.user = user
        except User.DoesNotExist:
            return render_json(error=errors.UserNotExist)
