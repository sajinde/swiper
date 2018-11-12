from lib.cache import rds
from lib import sms
from lib.qiniu import qiniu_upload_data
from common import keys
from common import errors
from swiper import platform_config
from worker import call_by_worker

def send_login_code(phone_num):
    '''发送登陆验证短信'''
    key = keys.LOGIN_SMS_KEY % phone_num
    if not rds.exists(key):
        random_code = sms.gen_verify_code(4)
        sms.async_send_sms(phone_num, random_code)
        rds.setex(key, random_code, 180)  # 状态码有效期 180s
    else:
        raise errors.NotYetTime


@call_by_worker
def upload_avatar_to_cloud(avatar, files):
    '''将图片上传至七牛云 (TODO: 未测试)'''
    for field_name, file_obj in files.items():
        # 上传
        filename = 'avatar-%s-%s' % (avatar.id, field_name)
        qiniu_upload_data(platform_config.QN_BUCKET, file_obj, filename)
        # 设置属性
        url = '%s/%s' % (platform_config.QN_BASE_URL, filename)
        setattr(avatar, field_name, url)
    avatar.save()
