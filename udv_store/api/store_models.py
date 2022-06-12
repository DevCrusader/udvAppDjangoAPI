import io

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.parsers import JSONParser


class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    class StateChoice(models.TextChoices):
        archived = "Archived"
        actual = "Actual"

    state = models.CharField(max_length=50, choices=StateChoice.choices, default=StateChoice.actual, db_index=True)

    class Meta:
        ordering = ["state", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def change_state(self, new_state: str):
        self.state = new_state
        self.save()

    def change_name(self, new_name: str):
        self.name = new_name
        self.save()


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=25, null=False, blank=False)
    price = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=400)
    default_photo = models.ImageField(upload_to="defaultProductPhotos/")
    created_date = models.DateTimeField(auto_now_add=True)

    class StateChoice(models.TextChoices):
        archived = "Archived"
        actual = "Actual"

    state = models.CharField(max_length=50, choices=StateChoice.choices, default=StateChoice.actual, db_index=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        get_latest_by = "created_date"
        ordering = ["state", 'name']

    def __str__(self):
        return self.name

    def change_state(self, new_state: str):
        if self.state == new_state:
            return "Already"
        self.state = new_state
        self.save()
        return "Changed"

    def change_product_params(self, data):
        self.category_id = data["new_category"] if data.get("new_category") else self.category_id
        self.name = data["new_name"] if data.get("new_name") else self.name
        self.description = data["new_description"] if data.get("new_description") else self.description
        self.default_photo = data["new_photo"] if data.get("new_photo") else self.default_photo
        self.price = data["new_price"] if data.get("new_price") else self.price
        self.save()

    def get_info_to_store(self):
        return {
            "product_id": self.product_id,
            "product_category": self.category_id.id,
            "product_name": self.name,
            "product_price": self.price,
            "product_photo": '/'.join(self.default_photo.path.split("/")[-2:])
        }

    def get_info_to_product_list(self):
        return {
            "product_id": self.product_id,
            "product_name": self.name,
            "product_photo": '/'.join(self.default_photo.path.split("/")[-2:]),
            "product_state": self.state,
            "product_description": self.description,
            "product_price": self.price
        }

    def get_info_to_items_list(self):
        return {
            "product_items": [
                item.get_item_info_to_admin() for item in self.productitem_set.all()
            ]
        }

    def get_info_to_product_page(self, user: User):
        from django.db.models import Count
        size_order = {"No size": -1, "XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5, "XXXL": 6}

        product_items = [
            item.get_item_info_to_product_page(user)
            for item in self.productitem_set.annotate(sizes_count=Count("sizes")).filter(sizes_count__gt=0)
        ]

        size_list = sorted(list(set(
            sum(map(lambda x: list(x["sizes"].keys()), product_items), [])
        )), key=lambda x: size_order[x])

        return {
            "product_info": {
                "product_name": self.name,
                "product_price": self.price,
                "product_description": self.description
            },
            "product_items": product_items,
            "size_list": size_list
        }


class Size(models.Model):
    size = models.CharField(max_length=10, default="M", db_index=True, null=False, blank=False)

    def __str__(self):
        return self.size


class ProductItem(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=30, default="black", null=False, blank=False, db_index=True)
    photo = models.ImageField(upload_to="productItemPhotos/")
    sizes = models.ManyToManyField(Size)
    # archived_sizes = models.CharField(max_length=50, default="", null=False)

    class Meta:
        unique_together = ["product_id", "color"]
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return f"{self.product_id.name} {self.color}"

    def add_size(self, new_size):
        self.sizes.add(Size.objects.get(size=new_size))
        self.save()

    def remove_size(self, removed_size):
        self.sizes.remove(Size.objects.get(size=removed_size))
        self.save()

    # def add_archived_size(self, size: str):
    #     self.archived_sizes += size
    #     self.save()
    #
    # def remove_archived_size(self, removed_size: str, action: str):
    #     from re import findall
    #
    #     stmt = findall(r"[X]*\w", self.archived_sizes)
    #     stmt.remove(removed_size)
    #     self.archived_sizes = ''.join(stmt)
    #
    #     if action == "unarchived":
    #         self.sizes.add(Size.objects.get(size=removed_size))
    #
    #     self.save()

    def get_photo_path(self):
        return "/".join(self.photo.path.split("/")[-2:])

    def get_item_info_to_admin(self):
        sizes_unused = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
        sizes = [s.size for s in self.sizes.all()]

        if "No size" not in sizes:
            for size in sizes:
                sizes_unused.remove(size)

        return {
            "item_id": self.id,
            "color": self.color,
            "photo": self.get_photo_path(),
            "sizes": sizes,
            "sizes_unused": sizes_unused
            # "archived": findall(r"[X]*\w", self.archived_sizes)
        }

    def get_item_info_to_product_page(self, user: User):
        product_in_cart = user.cart_set.filter(product_item_id=self)

        return {
            "id": self.id,
            "color": self.color,
            "sizes": {
                s.size: product_in_cart.get(size_id=s).count if product_in_cart.filter(size_id=s).exists() else False
                for s in self.sizes.all()
            },
            "item_photo": self.get_photo_path()
        }


class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item_id = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, default=4)
    count = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def get_cart_item_info(self):
        return {
            "cart_item_id": self.id,
            "product_id": self.product_item_id.product_id.product_id,
            "name": self.product_item_id.product_id.name,
            "price": self.product_item_id.product_id.price,
            "color": self.product_item_id.color,
            "size": self.size_id.size,
            "photo": self.product_item_id.photo,
            "count": self.count
        }

    def change_count(self, action: str):
        self.count += 1 if action == "add" else -1
        self.save()


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    products_list = models.BinaryField(null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class OfficesChoice(models.TextChoices):
        Lenina = "LA", "ул. Ленина, 45а"
        Mira = "MA", "ул. Мира, 32"
        Yasnaya = "YA", "ул. Ясная, 12"

    office_address = models.CharField(max_length=2, choices=OfficesChoice.choices, default=OfficesChoice.Lenina)

    class StateChoice(models.TextChoices):
        completed = "CM", "Completed"
        in_progress = "IR", 'In progress'

    state = models.CharField(max_length=2, choices=StateChoice.choices, default=StateChoice.in_progress, db_index=True)

    class Meta:
        ordering = ["created_date"]
        get_latest_by = ["created_date"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def set_state_completed(self):
        self.state = "CM"
        self.save()

    def set_state_in_progress(self):
        self.state = "IR"
        self.save()

    def get_parsed_product_list(self):
        return JSONParser().parse(io.BytesIO(self.products_list))

    def get_detail_info(self):
        return {
            "user_id": self.user_id.id,
            "user_name": self.user_id.userinfo.get_full_name(),
            "product_list": self.get_parsed_product_list(),
            "office": self.office_address,
        }

    def get_info_to_orders_list_to_admin(self):
        return {
            "order_id": self.id,
            "user_id": self.user_id.id,
            "user_name": self.user_id.userinfo.get_full_name(),
            "created_date": self.created_date
        }

    def get_full_price(self):
        return sum([
            item["price"] * item["count"] for item in self.get_parsed_product_list()
        ])

    def get_first_three_photo_in_product_list(self):
        return [
            item["photo"] for item in self.get_parsed_product_list()[:3]
        ]

    def get_info_to_list_to_personal_page(self):
        return {
            "order_id": self.id,
            "created_date": self.created_date,
            "full_price": self.get_full_price(),
            "products_photo": self.get_first_three_photo_in_product_list(),
            "state": self.state
        }

