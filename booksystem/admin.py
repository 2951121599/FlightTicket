from django.contrib import admin
from .models import Flight, UserInfo
from .forms import FlightForm

admin.site.site_header = "后台管理界面"
admin.site.site_title = "后台管理界面"
# 自定义表单管理
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'leave_city', 'arrive_city', 'leave_airport', 'arrive_airport', 'leave_time', 'arrive_time', 'capacity',
        'price', 'book_sum', 'income')
    form = FlightForm  # 在FlightForm中自定义需要在后台中输入哪些信息


admin.site.register(Flight, FlightAdmin)


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('name','score','kind')
    list_filter = ['kind', ]
    search_fields = ['kind', ]


admin.site.register(UserInfo, UserInfoAdmin)
