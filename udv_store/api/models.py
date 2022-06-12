from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    class RolesChoices(models.TextChoices):
        Employee = "EE", "Employee"
        Moderator = "MR", 'Moderator'
        Administrator = "AR", "Administrator"

    role = models.CharField(max_length=2, choices=RolesChoices.choices, default=RolesChoices.Employee, db_index=True)
    balance = models.PositiveIntegerField(default=0)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    patronymic = models.CharField(max_length=50, null=False, blank=True, default="")
    position = models.CharField(max_length=70, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    ava_back_color = models.CharField(max_length=7, null=False, blank=False, default="#000000")
    ava_main_color = models.CharField(max_length=7, null=False, blank=False, default="#FDB4FF")

    def get_full_name(self):
        return ' '.join([str(self.first_name), str(self.last_name)])

    def set_role_moderator(self):
        self.role = "MR"
        self.save()

    def set_role_employee(self):
        self.role = "EE"
        self.save()

    def set_role_administrator(self):
        self.role = "AR"
        self.save()

    def change_balance(self, count: int, action: str):
        if action == "add":
            self.balance += count
        if action == "remove":
            self.balance -= count
        self.save()

    class Meta:
        verbose_name = "Информация о пользователе"
        verbose_name_plural = "Информация о пользователях"


class Activity(models.Model):
    activity_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    ucoins_count = models.PositiveSmallIntegerField()
    description = models.TextField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    last_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"
        ordering = ["created_date"]
        get_latest_by = "created_date"

    def __str__(self):
        return self.name


class UcoinRequest(models.Model):
    request_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class StateChoice(models.TextChoices):
        accepted = "AC", "Accepted"
        rejected = "RJ", "Rejected"
        in_progress = "IR", 'In progress'

    state = models.CharField(max_length=2, choices=StateChoice.choices, default=StateChoice.in_progress, db_index=True)
    rejected_comment = models.CharField(max_length=250, default="", null=False, blank=True)

    class Meta:
        ordering = ["-created_date"]
        get_latest_by = ["created_date"]
        verbose_name = "Запрос"
        verbose_name_plural = "Запросы"

    def set_state_accepted(self):
        self.state = "AC"
        self.save()

    def set_state_rejected(self, comment: str):
        self.state = "RJ"
        self.rejected_comment = comment
        self.save()

    def set_state_in_progress(self):
        self.state = "IR"
        self.save()

    def get_info_to_list(self):
        return {
            "request_id": self.request_id,
            "ucoin_count": self.activity_id.ucoins_count,
            "date": self.created_date.date(),
            "state": self.state
        }

    def get_full_data(self):
        return {
            "request_id": self.request_id,
            "user_id": self.user_id.id,
            "user_name": ' '.join([self.user_id.userinfo.first_name, self.user_id.userinfo.last_name]),
            "comment": self.comment,
            "activity_id": self.activity_id.activity_id,
            "activity_name": self.activity_id.name,
            "created_date": self.created_date
        }


class Present(models.Model):
    user_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user_from = models.IntegerField(null=False, blank=False)
    text = models.TextField(max_length=500, null=False, blank=False)
    sign = models.CharField(max_length=100, null=False, blank=False, default="Admin")
    ucoin_count = models.IntegerField(null=False, blank=False)
    background = models.CharField(max_length=100, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class StateChoice(models.TextChoices):
        sent = "SN", "Sent"
        read = "RD", "Read"

    state = models.CharField(max_length=2, choices=StateChoice.choices, default=StateChoice.sent, db_index=True)

    def set_state_read(self):
        self.state = "RD"
        self.save()

    class Meta:
        verbose_name = "Подарок"
        verbose_name_plural = "Подарки"
        ordering = ["-created_date"]

    def get_present_info(self):
        return {
            "id": self.id,
            "user_from_id": self.user_from,
            "user_from_name": User.objects.get(id=self.user_from).userinfo.get_full_name(),
            "text": self.text,
            "sign": self.sign,
            "ucoin_count": self.ucoin_count,
            "background": self.background,
            "state": self.state,
        }

    # def get_unread_count(self, user):
    #     return user.present_set.filter(state="SN").count()


class BalanceHistory(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class ActionChoice(models.TextChoices):
        add = "AD", "Add"
        expenses = "EX", "Expenses"

    action = models.CharField(max_length=2, choices=ActionChoice.choices, default=ActionChoice.add, db_index=True)

    class CategoryChoice(models.TextChoices):
        requests = "RQ", "Requests"
        orders = "OR", "Orders"
        presents = "PR", "Presents"

    category = models.CharField(max_length=2, choices=CategoryChoice.choices,
                                default=CategoryChoice.presents, db_index=True)
    category_id = models.IntegerField(null=False, blank=False)
    ucoin_count = models.IntegerField(default=0, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "История баланса"
        verbose_name_plural = "История баланса"
        ordering = ["-created_date"]



# class UserHistory(models.Model):
#     class CategoryChoice(models.TextChoices):
#         requests = "RQ", "Requests"
#         orders = "OR", "Orders"
#         balance = "BL", "Balance"
#         presents = "PR", "Presents"
#
#     category = models.CharField(max_length=2, choices=CategoryChoice.choices,
#                                 default=CategoryChoice.balance, db_index=True)
#     category_id = models.PositiveBigIntegerField(null=False, blank=False)


# class UserHistoryUtil:
#     def __init__(self, user_id):
#         self.user_id = user_id
#         self.table_name = f"api_{user_id}_history"
#
#     def create_table(self):
#         with connection.cursor() as cursor:
#             cursor.execute(f"CREATE TABLE {self.table_name} AS SELECT * FROM api_userhistory;")
#
#         return "Successfully!"
#
#     def delete_table(self):
#         with connection.cursor() as cursor:
#             cursor.execute(f"DROP TABLE {self.table_name};")
#
#         return "Successfully!"
#
#     def get_category(self, category_name):
#         with connection.cursor() as cursor:
#             category = "RQ" if category_name == "Requests" else "OR" if category_name == "Orders" \
#                 else "BL" if category_name == "Balance" else "PR" if category_name == "Presents" else ValueError()
#
#             cursor.execute(f"SELECT category_id FROM {self.table_name} WHERE category = {category};")
#
#             return cursor.fetchall()
#
#     def set_category(self, category_name, category_id):
#         with connection.cursor() as cursor:
#             category = "RQ" if category_name == "Requests" else "OR" if category_name == "Orders" \
#                 else "BL" if category_name == "Balance" else "PR" if category_name == "Presents" else ValueError()
#
#             cursor.execute(f"INSERT INTO {self.table_name} (category, category_id) VALUES ({category}, {category_id});")
#
#         return "Successfully!"
