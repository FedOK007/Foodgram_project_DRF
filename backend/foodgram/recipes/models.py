from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    color = ColorField(
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
        return self.name[:settings.CROP_LEN_TEXT]


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
        return self.name[:settings.CROP_LEN_TEXT]


class Recipe(models.Model):
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
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False,
        null=False,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeToIngredient',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeToTag',
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:settings.CROP_LEN_TEXT]


class RecipeToIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingridients'
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
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}_'
            f'{self.ingredient.name}'[:settings.CROP_LEN_TEXT]
        )


class RecipeToTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
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
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            ),
        ]
    
    def __str__(self):
        return (
            f'{self.recipe.name}_'
            f'{self.tag.name}'[:settings.CROP_LEN_TEXT]
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shoppingcarts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shoppingcarts_recipe'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        return f'{self.user}_{self.recipe} cart'[:settings.CROP_LEN_TEXT]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.name[:settings.CROP_LEN_TEXT]} favorites'
