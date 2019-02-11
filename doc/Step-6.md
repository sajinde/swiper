# 服务器性能，及上线部署

> **Organization**: 千锋教育 Python 教学部<br>
> **Date**: 2018-11-26<br>
> **Author**: [张旭](mailto:zhangxu@1000phone.com)

## 一、并发与性能

* 概念
    * 理解 I/O 的概念
    * 理解 “同步/异步”、“阻塞/非阻塞”
    * 了解 “事件驱动” 和 “多路复用”
    * 异步模型并不会消灭阻塞，而是在发生 I/O 阻塞时切换到其他任务，从而达到异步非阻塞

* 计算密集型
    * CPU 长时间满负荷运行, 如图像处理、大数据运算、科学运算等
    * 计算密集型: 用 C 语言或 Cython 补充

* I/O 密集型
    * 网络 IO, 文件 IO, 设备 IO 等
    * Unix: 一切皆文件

* 多任务处理
    * 进程、线程、协程调度的过程叫做上下文切换
    * 进程、线程、协程对比

     名称 | 资源占用 |           数据通信            | 上下文切换 (Context)
    -----|---------|------------------------------|------------------
     进程 |    大   | 不方便 (网络、共享内存、管道等) | 操作系统按时间片切换, 不够灵活, 慢
     线程 |    小   |           非常方便            | 按时间片切换, 不够灵活, 快
     协程 |  非常小 |           非常方便            | 根据I/O事件切换, 更加有效的利用 CPU

* 全局解释器锁 ( GIL )

    ![GIL](./img/GIL.png)

    * 它确保任何时候一个进程中都只有一个 Python 线程能进入 CPU 执行。
    * 全局解释器锁造成单个进程无法使用多个 CPU 核心
    * 通过多进程来利用多个 CPU 核心，一般进程数与CPU核心数相等，或者CPU核心数两倍

* 协程

    - Python 下协程的发展:
        - stackless / greenlet / gevent
        - tornado 通过纯 Python 代码实现了协程处理 (底层使用 yield)
        - asyncio: Python 官方实现的协程

    - asyncio 实现协程

        ```python
        import asyncio

        async def foo(n):
            for i in range(10):
                print('wait %s s' % n)
                await asyncio.sleep(n)
            return i

        task1 = foo(1)
        task2 = foo(1.5)
        tasks = [asyncio.ensure_future(task1),
                asyncio.ensure_future(task2)]

        loop = asyncio.get_event_loop()  # 事件循环，协程调度器
        loop.run_until_complete( asyncio.wait(tasks) )
        ```

* 结论：通常使用多进程 + 多协程达到最大并发性能
    * 因为 GIL 的原因, Python 需要通过多进程来利用多个核心
    * 线程切换效率低, 而且应对 I/O 不够灵活
    * 协程更轻量级，完全没有协程切换的消耗，而且可以由程序自身统一调度和切换
    * HTTP Server 中，每一个请求都由独立的协程来处理

* 单台服务器最大连接数
    * 文件描述符: 限制文件打开数量 (一切皆文件)
    * 内核限制: `net.core.somaxconn`
    * 内存限制
    * 修改文件描述符: `ulimit -n 65535`

* 使用 Gunicorn 驱动 Django
    * <http://docs.gunicorn.org/en/latest/install.html>
    * Gunicorn 扮演 HTTPServer 的角色
    * HTTPServer: 只负责网络连接 (TCP握手、数据收/发)

* 分清几个概念
    * WSGI:
        全称是 WebServerGatewayInterface, 它是 Python 官方定义的一种描述 HTTP 服务器 (如nginx)与 Web 应用程序 (如 Django、Flask) 通信的规范。全文定义在 [PEP333](https://www.python.org/dev/peps/pep-0333/)

    * uwsgi:
        与 WSGI 类似, 是 uWSGI 服务器自定义的通信协议, 用于定义传输信息的类型(type of information)。每一个 uwsgi packet 前 4byte 为传输信息类型的描述, 与 WSGI 协议是两种东西, 该协议性能远好于早期的 Fast-CGI 协议。

    * uWSGI:
        uWSGI 是一个全功能的 HTTP 服务器, 实现了WSGI协议、uwsgi 协议、http 协议等。它要做的就是把 HTTP协议转化成语言支持的网络协议。比如把 HTTP 协议转化成 WSGI 协议, 让 Python 可以直接使用。

    ```
    HTTP Server  => 负责 1. 接受、断开客户端请求; 2. 接收、发送网络数据
        ^
        |
        v
      WSGI       => 负责 在 HTTPServer 和 WebApp 之间进行数据转换
        ^
        |
        v
    Web App      => 负责 Web 应用的业务逻辑
    ```

## 二、压力测试

* 常用工具
    - [ab (apache benchmark)](https://httpd.apache.org/docs/2.4/programs/ab.html)
    - [siege](https://github.com/JoeDog/siege)
    - webbench
    - [wrk](https://github.com/wg/wrk)

* Web 系统性能关键指标: **RPS** (Requests per second)
* 其他:
    * QPS (每秒查询数)
    * TPS (每秒事务数, 数据库指标)

* Ubuntu 下安装 ab: `apt-get install apache2-utils`
* 压测: `ab -k -n 1000 -c 300 http://127.0.0.1:9000/`

## 三、服务器的登陆与维护

1. SSH 登陆服务器: ssh root@xxx.xxx.xxx.xxx
2. 密钥
    1. 产生: ssh-keygen
    2. 公钥: ~/.ssh/id_rsa.pub
    3. 私钥: ~/.ssh/id_rsa
    4. 免密登陆服务器
        1. 复制公钥内容
        2. 将公钥内容粘贴到服务器的 ~/.ssh/authorized_keys
3. 代码上传
    1. `rsync -crvP --exclude={.venv,.git,__pycache__,logs}  ./ root@35.194.171.19:/opt/swiper/`

## 五、脚本开发

* 系统部署脚本
* 代码发布脚本
* 程序启动脚本
* 程序停止脚本
* 程序重启脚本
    * 不间断重启: `kill -HUP [进程 ID]`

## 六、Nginx

* 反向代理
* 负载均衡
    - 轮询: rr (默认)
    - 权重: weight
    - IP哈希: ip_hash
    - 最小连接数: least_conn

* 其他负载均衡
    * LVS
    * HAProxy
    * F5

* 可以不使用 Nginx, 直接用 gunicorn 吗？
    * Nginx 相对于 Gunicorn 来说更安全
    * Nginx 可以用作负载均衡

* 处理静态文件相关配置

    ```nginx
    location /statics/ {
        root   /project/bbs/;
        expires 30d;
        access_log off;
    }

    location /medias/ {
        root   /project/bbs/;
        expires 30d;
        access_log off;
    }
    ```

## 七、服务器架构

```
               User Request    cli_ip(12.23.34.45) -> ip_hash: 3
             |    |    |    |
             V    V    V    V
             www.example.com                ---> 第一层负载均衡
                 DNS 轮询
                /       \
               V         V
           Nginx         Nginx
        115.2.3.11     115.2.3.12           ---> Nginx 绑定公网 IP
       /    |     \   /     |    \
      /     |       X       |     \
     V      V     V   V     V      V
AppServer  AppServer  AppServer  AppServer  ---> Gunicorn + Django
10.0.0.1   10.0.0.2   10.0.0.3   10.0.0.4   ---> AppServer 绑定内网 IP
weight:10  weight:20  weight:20  weight:20  ---> 权重
    |         |          |           |
    V         V          V           V
+------------------------------------------+
|           缓存层   主机 <--> 从机          |
+------------------------------------------+
    |         |          |           |
    V         V          V           V
+------------------------------------------+
|           数据库  主机 <--> 从机           |
+------------------------------------------+
```

### 服务器架构的发展

### 服务器性能的预估
