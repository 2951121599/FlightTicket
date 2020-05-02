from django.contrib.auth.models import Permission, User
from django.db import models


# 航班表
class Flight(models.Model):
    user = models.ManyToManyField(User, default=1)
    name = models.CharField(max_length=100, verbose_name="班次")
    leave_city = models.CharField(max_length=100, null=True, verbose_name="离开城市")
    arrive_city = models.CharField(max_length=100, null=True, verbose_name="到达城市")
    leave_airport = models.CharField(max_length=100, null=True, verbose_name="离开的机场")
    arrive_airport = models.CharField(max_length=100, null=True, verbose_name="到达的机场")
    leave_time = models.DateTimeField(null=True, verbose_name="离开时间")
    arrive_time = models.DateTimeField(null=True, verbose_name="到达时间")
    capacity = models.IntegerField(default=0, null=True, verbose_name="座位总数")
    price = models.FloatField(default=0, null=True, verbose_name="价格")
    book_sum = models.IntegerField(default=0, null=True, verbose_name="订票总人数")
    income = models.FloatField(default=0, null=True, verbose_name="收入")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Flight"
        verbose_name = '航班信息表'
        verbose_name_plural = verbose_name


# 用户信息表
class UserInfo(models.Model):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    user = models.OneToOneField(User)
    name = models.CharField(max_length=50, null=True, verbose_name="姓名")
    nickname = models.CharField(max_length=50, null=True, verbose_name="英文名")
    sex = models.CharField(max_length=50, choices=GENDER_CHOICES, default='男', verbose_name="性别")
    age = models.CharField(max_length=50, null=True, verbose_name="年龄")
    phone = models.CharField(max_length=50, null=True, verbose_name="手机号码")
    sfz = models.CharField(max_length=50, null=True, verbose_name="身份证号")
    score = models.CharField(max_length=50, default=0, verbose_name="积分")
    kind = models.CharField(max_length=50, default="低价值用户", verbose_name="分类")

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = "user_info"
        verbose_name = '用户信息表'
        verbose_name_plural = verbose_name
