from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedModel, CreatedAtModel


User = get_user_model()


class Category(CreatedAtModel, PublishedModel):
    """Модель для тематической категории."""
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.',
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(CreatedAtModel, PublishedModel):
    """Модель для географической метки."""
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(CreatedAtModel, PublishedModel):
    """Модель для публикаций."""
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(
        blank=True,
        upload_to='post_img',
        verbose_name='Фото',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.',
    )

    author = models.ForeignKey(
        User,
        related_name='author',
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )

    category = models.ForeignKey(
        Category,
        related_name='category',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    location = models.ForeignKey(
        Location,
        related_name='location',
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(CreatedAtModel):
    """Модель для комментариев."""
    text = models.TextField(verbose_name='Комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
