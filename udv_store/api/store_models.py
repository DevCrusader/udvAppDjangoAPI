import io

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.parsers import JSONParser


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=25, null=False, blank=False)
    price = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=400)
    have_size = models.BooleanField(default=True, null=False, blank=False)
    # default_photo = models.ImageField(upload_to="images/defaultProductPhotos/")
    created_date = models.DateTimeField(auto_now_add=True)

    class StateChoice(models.TextChoices):
        archived = "Archived"
        actual = "Actual"

    state = models.CharField(max_length=50, choices=StateChoice.choices, default=StateChoice.archived, db_index=True)

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
        # self.category_id = data["new_category"] if data.get("new_category") else self.category_id
        self.name = data["new_name"] if data.get("new_name") else self.name
        self.description = data["new_description"] if data.get("new_description") else self.description
        # self.default_photo = data["new_photo"] if data.get("new_photo") else self.default_photo
        self.price = data["new_price"] if data.get("new_price") else self.price
        self.save()

    # def photo_path(self):
    #     return '/'.join(self.default_photo.path.split("/")[-2:])

    def item_count(self):
        return sum([pi.sizes.count() for pi in self.productitem_set.all()])

    def items_list_1(self):
        # return [
        #     item.get_item_info_to_admin() for item in self.productitem_set.all()
        # ]
        pass

    def product_items_and_sizes(self):
        # from django.db.models import Count

        product_items = [
            item.get_item_info_to_product_page()
            # for item in self.productitem_set.annotate(sizes_count=Count("sizes")).filter(sizes_count__gt=0)
            for item in self.productitem_set.all()

        ]

        # unique sizes in list
        # size_list = sorted(list(set(
        #     sum(map(lambda x: x["sizes"], product_items), [])
        # )), key=lambda x: size_order[x])

        return {
            "product_items": product_items,
        }

    def items_list(self):
        return [
            {
                'id': item.id,
                'color': item.color,
                'photo': item.photo_main()
            }
            for item in self.productitem_set.all()]


class Size(models.Model):
    size = models.CharField(max_length=10, default="M", db_index=True, null=False, blank=False)

    def __str__(self):
        return self.size


class ProductItem(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=30, default="чёрн", null=False, blank=False, db_index=True)
    # photo = models.ImageField(upload_to="images/productItemPhotos/")
    sizes = models.ManyToManyField(Size, blank=True)

    class Meta:
        unique_together = ["product_id", "color"]
        verbose_name = "Цвет товара"
        verbose_name_plural = "Цвета товаров"

    def __str__(self):
        return f"{self.product_id.name} {self.color}"

    def add_size(self, new_size):
        self.sizes.add(Size.objects.get(size=new_size))
        self.save()

    def remove_size(self, removed_size):
        self.sizes.remove(Size.objects.get(size=removed_size))
        self.save()

    # def photo_path(self):
    #     return "/".join(self.photo.path.split("/")[-2:])

    def get_item_info_to_admin(self):
        sizes_unused = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
        sizes = [s.size for s in self.sizes.all()]

        if "No size" not in sizes:
            for size in sizes:
                sizes_unused.remove(size)

        return {
            "item_id": self.id,
            "color": self.color,
            "photo": self.photo_list(),
            "sizes": sizes,
            "sizes_unused": sizes_unused
        }

    def get_item_info_to_product_page(self):
        return {
            "id": self.id,
            "color": self.color,
            "sizes": [s.size for s in self.sizes.all()],
            "photo": self.photo_list(),
        }

    def photo_main(self):
        return self.productphoto_set.first().photo_path()

    def photo_list(self):
        return [photo.photo_path() for photo in self.productphoto_set.all()]


class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item_id = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, default=4, null=True)
    count = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def item_info(self):
        return {
            "product_id": self.product_item_id.product_id.product_id,
            "product_item_id": self.product_item_id.id,
            "color": self.product_item_id.color,
            "size": self.get_size(),
            "count": self.count
        }

    def get_size(self):
        return self.size_id.size if self.size_id else None

    def item_params(self):
        return {
            "product_item": self.product_item_id,
            "product": self.product_item_id.product_id
        }

    def get_order_info(self):
        return {
            "name": self.product_item_id.product_id.name,
            "color": self.product_item_id.color,
            "size": self.get_size(),
            "photo": self.product_item_id.photo_main(),
            "count": self.count
        }

    def change_count(self, action: str):
        self.count += 1 if action == "add" else -1
        self.save()


class ProductPhoto(models.Model):
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="images/productItemPhotos/")
    main_photo = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_created=True, null=False, blank=False)

    def photo_path(self):
        return "/".join(self.photo.path.split("/")[-2:])

    def __str__(self):
        return self.photo_path()

    class Meta:
        ordering = ['-main_photo']
        verbose_name = "Фотография товара"
        verbose_name_plural = "Фотографии товаров"


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
        completed = "Completed"
        in_progress = "In progress"
        accepted = "Accepted"

    state = models.CharField(max_length=12, choices=StateChoice.choices, default=StateChoice.accepted, db_index=True)

    class Meta:
        ordering = ["created_date"]
        get_latest_by = ["created_date"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def set_state_completed(self):
        self.state = "Completed"
        self.save()

    def set_state_in_progress(self):
        self.state = "In progress"
        self.save()

    def get_parsed_product_list(self):
        return JSONParser().parse(io.BytesIO(self.products_list))

    def get_detail_info(self):
        return {
            "id": self.id,
            "user_id": self.user_id.id,
            "user_name": self.user_id.userinfo.get_full_name(),
            "product_list": self.get_parsed_product_list(),
            "office": self.office_address,
            "date": self.created_date,
            "state": self.state
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
        # return [
        #     item["photo"] for item in self.get_parsed_product_list()[:3]
        # ]
        pass

    def get_info_to_list_to_personal_page(self):
        return {
            "order_id": self.id,
            "created_date": self.created_date,
            "full_price": self.get_full_price(),
            "products_photo": self.get_first_three_photo_in_product_list(),
            "state": self.state
        }

