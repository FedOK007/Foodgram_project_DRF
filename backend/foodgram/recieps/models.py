from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

User = get_user_model()
CROP_LEN_TEXT = settings.CROP_LEN_TEXT


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    color = models.CharField(
        'Цвет HEX',
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:CROP_LEN_TEXT]


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        blank=False,
        null=False
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name[:CROP_LEN_TEXT]


class Reciep(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        blank=False,
        null=False
    )
    image = models.ImageField(
        'Картинка',
        blank=False,
        null=False,
        upload_to='ingridients/'
    )
    text = models.TextField(
        'Рецепт',
        blank=False,
        null=False
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipes',
        blank=True,
        null=True,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='ReciepToIngredient',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='ReciepToTag',
        verbose_name='Теги'
    )
    favorites = models.ManyToManyField(
        User,
        through='Favorite',
        verbose_name='Списки избранного',
        related_name='reciepsinfavorites'
    )
    shoppingcarts = models.ManyToManyField(
        User,
        through='ShoppingCart',
        verbose_name='Списки покупок',
        related_name='reciepsinshoppingcart'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:CROP_LEN_TEXT]


class ReciepToIngredient(models.Model):
    reciep = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='reciep_ingridients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        verbose_name='Ингридиент'
    )
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Связь ингридиентов с рецептами'
        verbose_name_plural = 'Связь ингридиентов с рецептами'

    def __str__(self):
        return f'{self.reciep}_{self.ingredient}_{self.amount}'[:CROP_LEN_TEXT]


class ReciepToTag(models.Model):
    reciep = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Связь рецептов с тегами'
        verbose_name_plural = 'Связь рецептов с тегами'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shoppingcarts'
    )
    reciep = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shoppingcarts_reciep'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        return f'{self.user}_{self.reciep} cart'[:CROP_LEN_TEXT]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    reciep = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite_reciep'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'reciep'],
                name='unique_user_reciep'
            )
        ]

    def __str__(self):
        return f'{self.name[:CROP_LEN_TEXT]} favorites'
