from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .forms import PassengerInfoForm, UserForm
from .models import Flight, UserInfo
from .classes import IncomeMetric, Order
from django.contrib.auth.models import Permission, User
import datetime, pytz
from operator import attrgetter

ADMIN_ID = 1


# 管理员后台财务管理 统计航空公司每周、每月，每年营业收入情况。
def admin_finance(request):
    all_flights = Flight.objects.all()
    all_flights = sorted(all_flights, key=attrgetter('leave_time'))  # 将所有航班按照起飞时间排序

    # 将航班每天的输入打上不同的时间标签 [周，月，日]
    week_day_incomes = []
    month_day_incomes = []
    year_day_incomes = []

    # 用set存储所有的 周，月，年
    week_set = set()
    month_set = set()
    year_set = set()
    for flight in all_flights:
        if flight.income > 0:  # 只统计有收入的航班
            # 打上周标签
            this_week = flight.leave_time.strftime('%W')  # datetime获取周
            week_day_incomes.append((this_week, flight.income))  # 添加元组(week, income)
            week_set.add(this_week)
            # 打上月标签
            this_month = flight.leave_time.strftime('%m')  # datetime获取月
            month_day_incomes.append((this_month, flight.income))  # 添加元组(month, income)
            month_set.add(this_month)
            # 打上年标签
            this_year = flight.leave_time.strftime('%Y')  # datetime获取年
            year_day_incomes.append((this_year, flight.income))  # 添加元组(year, income)
            year_set.add(this_year)

    # 存储每周收入
    # 将每周的收入用 IncomeMetric 类型存储在 week_incomes List中
    week_incomes = []
    for week in week_set:
        income = sum(x[1] for x in week_day_incomes if x[0] == week)  # 同周次的income求和
        flight_sum = sum(1 for x in week_day_incomes if x[0] == week)  # 同周次的航班总数目
        week_income = IncomeMetric(week, flight_sum, income)  # 将数据存储到IncomeMetric类中，方便jinja语法
        week_incomes.append(week_income)
    week_incomes = sorted(week_incomes, key=attrgetter('metric'))  # 将List类型的 week_incomes 按周次升序排列

    # 存储每月收入
    # 将每月的收入用 IncomeMetric 类型存储在 month_incomes List中
    month_incomes = []
    for month in month_set:
        income = sum(x[1] for x in month_day_incomes if x[0] == month)
        flight_sum = sum(1 for x in month_day_incomes if x[0] == month)
        month_income = IncomeMetric(month, flight_sum, income)
        month_incomes.append(month_income)
    month_incomes = sorted(month_incomes, key=attrgetter('metric'))  # 将List类型的 month_incomes 按月份升序排列

    # 存储每年收入
    # 将每年的收入用 IncomeMetric 类型存储在 year_incomes List中
    year_incomes = []
    for year in year_set:
        income = sum(x[1] for x in year_day_incomes if x[0] == year)
        flight_sum = sum(1 for x in year_day_incomes if x[0] == year)
        year_income = IncomeMetric(year, flight_sum, income)
        year_incomes.append(year_income)
    year_incomes = sorted(year_incomes, key=attrgetter('metric'))  # 将List类型的 year_incomes 按年份升序排列

    # 存储order信息
    passengers = User.objects.exclude(pk=1)  # 去掉管理员
    order_set = set()
    for p in passengers:
        flights = Flight.objects.filter(user=p)
        for f in flights:
            route = f.leave_city + ' → ' + f.arrive_city
            order = Order(p.username, f.name, route, f.leave_time, f.price)
            order_set.add(order)

    # 信息传给前端
    context = {
        'week_incomes': week_incomes,
        'month_incomes': month_incomes,
        'year_incomes': year_incomes,
        'order_set': order_set
    }
    return context


# 主页 欢迎页面性质的订票页面
def index(request):
    return render(request, 'booksystem/index.html')


# 免除csrf
@csrf_exempt
def book_ticket(request, flight_id):
    if not request.user.is_authenticated():  # 如果没登录就render登录页面
        return render(request, 'booksystem/login.html')
    else:
        flight = Flight.objects.get(pk=flight_id)
        # 查看乘客已经订购的flights
        booked_flights = Flight.objects.filter(user=request.user)  # 返回 QuerySet

        if flight in booked_flights:
            return render(request, 'booksystem/book_conflict.html', locals())

        # book_flight.html 点确认之后，request为 POST 方法，虽然没有传递什么值，但是传递了 POST 信号
        # 确认订票，flight数据库改变

        # 验证一下，同样的机票只能订一次
        if request.method == 'POST':
            if flight.capacity > 0:
                flight.book_sum += 1
                flight.capacity -= 1
                flight.income += flight.price
                flight.user.add(request.user)
                flight.save()  # 一定要记着save
        # 传递更改之后的票务信息
        context = {
            'flight': flight,
            'username': request.user.username
        }
        return render(request, 'booksystem/book_flight.html', context)


# 退票
def refund_ticket(request, flight_id):
    flight = Flight.objects.get(pk=flight_id)
    flight.book_sum -= 1
    flight.capacity += 1
    flight.income -= flight.price
    flight.user.remove(request.user)
    flight.save()
    return redirect('booksystem:order_info')


# 退出登录
def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'booksystem/login.html', context)


# 登录
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user is not None:  # 登录成功
            if user.is_active:  # 加载订票页面
                login(request, user)
                context = {
                    'username': request.user.username
                }
                if user.id == ADMIN_ID:
                    context = admin_finance(request)  # 获取要传入前端的数据
                    return render(request, 'booksystem/admin_finance.html', context)
                else:
                    # 旅客分类
                    user_id = request.user.id
                    user_obj = UserInfo.objects.get(user_id=user_id)
                    # 查看乘客已经订购的票flights
                    booked_flights = Flight.objects.filter(user=request.user)  # 返回 QuerySet
                    totle_price = 0
                    n = booked_flights.count()
                    print("n------------", n)
                    for flight in booked_flights:
                        totle_price += flight.price
                    print("totle_price------------", totle_price)
                    if n==0:
                        avg_price = 0
                    else:
                        avg_price = int(totle_price // n)
                    print("avg_price------------", avg_price)
                    if 0 <= avg_price <= 1000:
                        user_obj.kind = "低价值用户"
                    elif 1001 <= avg_price <= 2000:
                        user_obj.kind = "普通价值用户"
                    else:
                        user_obj.kind = "高价值用户"
                    user_obj.save()
                    # 旅客分类结束
                    return render(request, 'booksystem/result.html', context)
            else:
                return render(request, 'booksystem/login.html', {'error_message': 'Your account has been disabled'})
        else:  # 登录失败
            return render(request, 'booksystem/login.html', {'error_message': 'Invalid login'})
    return render(request, 'booksystem/login.html')


# 注册
def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        UserInfo.objects.create(user_id=user.id)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                context = {
                    'username': request.user.username
                }
                return render(request, 'booksystem/result.html', context)  # 注册成功直接render result页面
    context = {
        "form": form,
    }
    return render(request, 'booksystem/register.html', context)


# 搜索结果页面
def result(request):
    if request.method == 'POST':
        form = PassengerInfoForm(request.POST)  # 绑定数据至表单
        if form.is_valid():
            passenger_lcity = form.cleaned_data.get('leave_city')
            passenger_acity = form.cleaned_data.get('arrive_city')
            passenger_ldate = form.cleaned_data.get('leave_date')

            # 全设为aware比较
            passenger_ltime = datetime.datetime.combine(passenger_ldate, datetime.time())
            print(passenger_ltime)

            # filter 可用航班
            all_flights = Flight.objects.filter(leave_city=passenger_lcity, arrive_city=passenger_acity)
            usable_flights = []
            for flight in all_flights:  # off-set aware
                flight.leave_time = flight.leave_time.replace(tzinfo=None)  # replace方法必须要赋值。。笑哭
                if flight.leave_time.date() == passenger_ltime.date():  # 只查找当天的航班
                    usable_flights.append(flight)

            # 按不同的key排序
            usable_flights_by_ltime = sorted(usable_flights, key=attrgetter('leave_time'))  # 起飞时间从早到晚
            usable_flights_by_atime = sorted(usable_flights, key=attrgetter('arrive_time'))
            usable_flights_by_price = sorted(usable_flights, key=attrgetter('price'))  # 价格从低到高

            # 转换时间格式
            time_format = '%H:%M'

            # 虽然只转换了一个list，其实所有的都转换了
            for flight in usable_flights_by_price:
                flight.leave_time = flight.leave_time.strftime(time_format)  # 转成了str
                flight.arrive_time = flight.arrive_time.strftime(time_format)

            # 决定 search_head , search_failure 是否显示
            dis_search_head = 'block'
            dis_search_failure = 'none'
            if len(usable_flights_by_price) == 0:
                dis_search_head = 'none'
                dis_search_failure = 'block'
            context = {
                # 搜多框数据
                'leave_city': passenger_lcity,
                'arrive_city': passenger_acity,
                'leave_date': str(passenger_ldate),
                # 搜索结果
                'usable_flights_by_ltime': usable_flights_by_ltime,
                'usable_flights_by_atime': usable_flights_by_atime,
                'usable_flights_by_price': usable_flights_by_price,
                # 标记
                'dis_search_head': dis_search_head,
                'dis_search_failure': dis_search_failure
            }
            if request.user.is_authenticated():
                context['username'] = request.user.username
            return render(request, 'booksystem/result.html', context)  # 最前面如果加了/就变成根目录了，url错误
        else:
            return render(request, 'booksystem/index.html')  # 在index界面提交的表单无效，就保持在index界面
    else:
        username = request.user.username
        context = {
            'dis_search_head': 'none',
            'dis_search_failure': 'none',
            'username': username
        }
    return render(request, 'booksystem/result.html', context)


# 显示用户个人信息
def user_info(request):
    print("request.user------------", request.user)
    if request.user.is_authenticated():
        # 如果用户是管理员，render公司航班收入统计信息页面 admin_finance
        if request.user.id == ADMIN_ID:
            context = admin_finance(request)  # 获取要传入前端的数据
            return render(request, 'booksystem/admin_finance.html', context)
        # 如果用户是普通用户，render用户的机票信息 user_info
        else:
            try:
                user_info = UserInfo.objects.get(user=request.user)
                context = {
                    'user_info': user_info,
                    'email': request.user.email,
                    'username': request.user.username,  # 导航栏信息更新
                }
                return render(request, 'booksystem/user_info.html', context)
            except Exception as e:
                print("e------------", e)
    return render(request, 'booksystem/login.html')  # 用户如果没登录，render登录页面


# 修改用户信息
def user_change(request):
    if request.method == 'GET':
        user_info = UserInfo.objects.filter(user=request.user)[0]
        if request.user.is_authenticated():
            username = request.user.username
        GENDER_CHOICES = user_info.GENDER_CHOICES
        gender_list = []
        for i in GENDER_CHOICES:
            gender_list.append(i)
        print("gender_list------------", gender_list)

        return render(request, 'booksystem/change_user_info.html', locals())
    elif request.method == 'POST':
        # 添加用户信息
        if request.user.is_authenticated():
            user_id = request.user.id
            print("user_id------------", user_id)
            # 获取提交的数据
            name = request.POST.get('name')
            nickname = request.POST.get('nickname')
            sex = request.POST.get('sex')
            age = request.POST.get('age')
            phone = request.POST.get('phone')
            sfz = request.POST.get('sfz')
            print("sfz------------", sfz)
            # 查找用户
            user = UserInfo.objects.filter(user_id=user_id)[0]
            if user:
                # 更新修改数据
                user.name = name
                user.nickname = nickname
                user.sex = sex
                user.age = age
                user.phone = phone
                user.sfz = sfz
                user.save()
            else:
                # 保存数据
                UserInfo.objects.create(name=name, nickname=nickname, sex=sex, age=age, phone=phone, sfz=sfz,
                                        user_id=user_id)
            return redirect(reverse('booksystem:user_info'))


# 查询用户订单信息 航班信息，退票管理
def order_info(request):
    if request.user.is_authenticated():
        # 如果用户是管理员，render公司航班收入统计信息页面 admin_finance
        if request.user.id == ADMIN_ID:
            context = admin_finance(request)  # 获取要传入前端的数据
            return render(request, 'booksystem/admin_finance.html', context)
        # 如果用户是普通用户，render用户的机票信息 user_info
        else:
            booked_flights = Flight.objects.filter(user=request.user)  # 从 booksystem_flight_user 表过滤出该用户订的航班
            context = {
                'booked_flights': booked_flights,
                'username': request.user.username,  # 导航栏信息更新
            }
            return render(request, 'booksystem/order_info.html', context)
    return render(request, 'booksystem/login.html')  # 用户如果没登录，render登录页面


# 积分查询
def score(request):
    user_id = request.user.id
    print("user_id------------", user_id)
    try:
        score_obj = UserInfo.objects.get(user_id=user_id)
        # 查看乘客已经订购的票flights
        booked_flights = Flight.objects.filter(user=request.user)  # 返回 QuerySet
        totle_price = 0
        for flight in booked_flights:
            totle_price += flight.price
        print("totle_price------------", totle_price)
        score_int = int(totle_price // 2)
        score = str(score_int)
        score_obj.score = score
        score_obj.save()

        # # 旅客分类
        # user_obj = UserInfo.objects.get(user_id=user_id)
        # # 查看乘客已经订购的票flights
        # booked_flights = Flight.objects.filter(user=request.user)  # 返回 QuerySet
        # totle_price = 0
        # n = booked_flights.count()
        # print("n------------", n)
        # for flight in booked_flights:
        #     totle_price += flight.price
        # print("totle_price------------", totle_price)
        # avg_price = int(totle_price // n)
        # print("avg_price------------", avg_price)
        # if 0 <= avg_price <= 1000:
        #     user_obj.kind = "低价值用户"
        # elif 1001 <= avg_price <= 2000:
        #     user_obj.kind = "普通价值用户"
        # else:
        #     user_obj.kind = "高价值用户"
        # user_obj.save()
        # # 旅客分类结束
        if request.user.is_authenticated():
            username = request.user.username
        return render(request, 'booksystem/score.html', locals())
    except Exception as e:
        print("e------------", e)
        return HttpResponse("您还没有过订单信息, 暂无积分 ")