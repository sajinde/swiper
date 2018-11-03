from logging import getLogger
from sys import exc_info
from traceback import format_exception

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from common import errors
from lib.http import render_json
from user.models import User

err_log = getLogger('err')


class JsonMiddleware(MiddlewareMixin):
    '''将结果渲染成 json 数据'''
    def process_response(self, request, response):
        '''对结果进行封装'''
        if isinstance(response, HttpResponse):
            return response
        elif isinstance(response, dict):
            return render_json(response)
        else:
            err_log.error('Unknow type of the result: %s' % response)
            return response

    def process_exception(self, request, exception):
        '''异常处理'''
        if isinstance(exception, errors.LogicError):
            return render_json(error=exception)
        else:
            # TODO: 向开发者发送异常告警邮件
            error_info = format_exception(*exc_info())
            err_log.error(''.join(error_info))  # 输出错误日志
            return render_json(error=errors.InternalError)


class AuthMiddleware(MiddlewareMixin):
    '''登陆认证检查中间件'''
    # 不需要检查的路径
    IGNORED_PATH_LIST = [
        '/user/verify/phone',
        '/user/verify/code',
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
