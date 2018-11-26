# 个人模块开发（一）

> **Organization**: 千锋教育 Python 教学部<br>
> **Date**: 2018-11-18<br>
> **Author**: [张旭](mailto:zhangxu@1000phone.com)


## 一、功能概览

- 用户数据模型设计
- 手机注册
- 短信验证登录
- 获取个人资料
- 修改个人资料
- 头像上传


## 二、用户数据模型设计

1. User (用户自身数据)

    Field       | Description
    ------------|------------
    phonenum    | 手机号
    nickname    | 昵称
    sex         | 性别
    birth_year  | 出生年
    birth_month | 出生月
    birth_day   | 出生日
    avatar      | 个人形象
    location    | 常居地

2. Profile (个人配置数据)

    Field          | Description
    ---------------|------------
    location       | 目标城市
    min_distance   | 最小查找范围
    max_distance   | 最大查找范围
    min_dating_age | 最小交友年龄
    max_dating_age | 最大交友年龄
    dating_sex     | 匹配的性别
    vibration      | 开启震动
    only_matche    | 不让为匹配的人看我的相册
    auto_play      | 自动播放视频


## 三、关系构建

1. 关系分类
    - 一对一关系
    - 一对多关系
    - 多对多关系

2. 外键的优缺点
    - 优点:
        - 由数据库自身保证数据一致性和完整性, 数据更可靠
        - 可以增加 ER 图的可读性
        - 外键可节省开发量
    - 缺点:
        - 性能缺陷, 有额外开销
        - 主键表被锁定时, 会引发外键表也被锁
        - 删除主键表的数据时, 需先删除外键表的数据
        - 修改外键表字段时, 需重建外键约束
        - 不能用于分布式环境
        - 不容易做到数据解耦

3. 应用场景
    - 适用场景: 内部系统、传统企业级应用可以使用 (需要数据量可控, 数据库服务器数量可控)
    - 不适用场景: 互联网行业不建议使用

4. 手动构建关联
    1. 一对多: 主表 id 与 子表 id 完全一一对应
    2. 一对多: 在"多"的表内添加"唯一"表 id 字段
    3. 多对多: 创建关系表, 关系表中一般只存放两个相关联的条目的 id
    4. 博客案例思考
        1. 用户和文字的关系
        2. 用户和收藏关系
        3. 用户-角色-权限关系

5. 方法属性化

    - property

        ```python
        class Box:
            def __init__(self):
                self.l = 123
                self.w = 10
                self.h = 80

            @property
            def V(self):
                return self.l * self.w * self.h
        ```

    - cached_property

        ```python
        from django.utils.functional import cached_property

        class User(models.Model):
            year = 1990
            month = 10
            day = 29

            @cached_property
            def age(self):
                today = datetime.date.today()
                birth_date = datetime.date(self.year, self.month, self.day)
                times = today - birth_date
                return times.days // 365
        ```

## 四、第三方短信平台的接入

1. 注册账号后, 将平台分配的 APP_ID 和 APP_SECRET
    - APP_ID: 平台分配的 ID
    - APP_SECRET: 与平台交互时, 用来做安全验证的一段加密用的文本, **不能泄漏给其他人**
2. 注册平台的短信模版
3. 按照平台接口文档开发接口
    - 此类平台的接口通常是 HTTP 或 HTTPS 协议, 接入的时候只需按照接口格式发送 HTTP 请求即可


## 五、Celery 及异步任务的处理

1. 模块组成

    ![celery](./img/celery.png)

    * 任务模块 Task

        包含异步任务和定时任务. 其中, 异步任务通常在业务逻辑中被触发并发往任务队列, 而定时任务由 Celery Beat 进程周期性地将任务发往任务队列.

    * 消息中间件 Broker

        Broker, 即为任务调度队列, 接收任务生产者发来的消息（即任务）, 将任务存入队列. Celery 本身不提供队列服务, 官方推荐使用 RabbitMQ 和 Redis 等.

    * 任务执行单元 Worker

        Worker 是执行任务的处理单元, 它实时监控消息队列, 获取队列中调度的任务, 并执行它.

    * 任务结果存储 Backend

        Backend 用于存储任务的执行结果, 以供查询. 同消息中间件一样, 存储也可使用 RabbitMQ, Redis 和 MongoDB 等.

2. 安装

    ```
    pip install 'celery[redis]'
    ```

3. 创建实例

    ```python
    import time
    from celery import Celery

    broker = 'redis://127.0.0.1:6379'
    backend = 'redis://127.0.0.1:6379/0'
    app = Celery('my_task', broker=broker, backend=backend)

    @app.task
    def add(x, y):
        time.sleep(5)     # 模拟耗时操作
        return x + y
    ```

4. 启动 Worker

    ```
    celery worker -A tasks --loglevel=info
    ```

5. 调用任务

    ```python
    from tasks import add

    add.delay(2, 8)
    ```

6. 常规配置

    ```python
    broker_url = 'redis://127.0.0.1:6379/0'
    broker_pool_limit = 1000  # Borker 连接池, 默认是10

    timezone = 'Asia/Shanghai'
    accept_content = ['pickle', 'json']

    task_serializer = 'pickle'
    result_expires = 3600  # 任务过期时间

    result_backend = 'redis://127.0.0.1:6379/0'
    result_serializer = 'pickle'
    result_cache_max = 10000  # 任务结果最大缓存数量

    worker_redirect_stdouts_level = 'INFO'
    ```


## 六、Django 默认缓存

1. 接口及用法

    ```python
    from django.core.cache import cache

    # 在缓存中设置 age = 123, 10秒过期
    cache.set('age', 123, 10)

    # 获取 age
    a = cache.get('age')
    print(a)

    # 自增
    x = cache.incr('age')
    print(x)
    ```

2. 使用 Redis 做缓存后端
    - 安装 `pip install django-redis`
    - settings 配置

        ```python
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/0",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "PICKLE_VERSION": -1,
                }
            }
        }
        ```

3. 利用过期时间可以处理一些定时失效的临时数据, 比如手机验证码
