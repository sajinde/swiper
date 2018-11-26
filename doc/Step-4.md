# 社交、VIP模块开发

> **Organization**: 千锋教育 Python 教学部<br>
> **Date**: 2018-11-22<br>
> **Author**: [张旭](mailto:zhangxu@1000phone.com)


## 一、功能概述

1. 交友模块
    - 表结构设计
    - 获取推荐列表
    - 匹配检查
    - 喜欢
    - 超级喜欢
    - 不喜欢
    - 反悔
    - 查看喜欢过我的人

2. 好友模块
    - 好友表结构设计
    - 查看好友列表
    - 查看好友信息

3. VIP 模块
    - VIP表设计
    - 权限表设计
    - 权限检查逻辑处理
    - 权限详情接口
    - 权限: 超级喜欢 / 反悔 / 查看被喜欢


## 二、模型设计

1. Swiped (划过的记录)

    Field | Description
    ------|-------------
    uid   | 用户自身 id
    sid   | 被滑的陌生人 id
    mark  | 滑动类型
    time  | 滑动的时间

2. Friend (匹配到的好友)

    Field | Description
    ------|------------
    uid1  | 好友 ID
    uid2  | 好友 ID

3. VIP (会员)

    Field | Description
    ------|------------
    name  | 会员名称
    level | 登记
    price | 价格

4. Permission (权限)
    Field       | Description
    ------------|------------
    name        | 权限名称
    description | 权限说明


## 三、关系分析

1. 滑动者与被滑动者
    - 一个人可以滑动很多人
    - 一个人可以被多人滑动
    - 结论: 同表之内构建起来的逻辑上的多对多关系

2. 用户与好友
    - 一个用户由多个好友
    - 一个用户也可以被多人加为好友
    - 结论: 同表之内构建起来的逻辑上的多对多关系, Friend 表实际上就是一个关系表

3. User 与 VIP
    - 一种 VIP 对应多个 User
    - 一个 User 只会有一种 VIP
    - 结论: 一对多关系

4. VIP 与权限
    - 一种 VIP 级别对应多种权限
    - 一个权限会属于在多种级别的 VIP
    - 结论: 多对多关系


## 四、类方法与静态方法

- `method`

    - 通过实例调用
    - 可以引用类内部的**任何属性和方法**

- `classmethod`

    - 无需实例化
    - 可以调用类属性和类方法
    - 无法取到普通的成员属性和方法

- `staticmethod`

    - 无需实例化
    - **无法**取到类内部的任何属性和方法, 完全独立的一个方法


## 五、利用 Q 对象进行复杂查询

```python
from django.db.models import Q

# AND
Model.objects.filter(Q(x=1) & Q(y=2))

# OR
Model.objects.filter(Q(x=1) | Q(y=2))

# NOT
Model.objects.filter(~Q(name='kitty'))
```
