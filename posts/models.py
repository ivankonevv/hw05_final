from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Часть URL адреса группы',
    )
    description = models.TextField(
        verbose_name='Описание группы',
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст вашего поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор поста',
        null=False,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа для поста',
        help_text='Выберите группу или оставьте пустым',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение для поста',
        help_text='Только файлы изображений',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f'Автор: {self.author} от {self.pub_date:%d.%m.%Y}.'


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост с комментарием',
                             )
    author = models.ForeignKey(User,
                               null=True,
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(fields=['user', 'author'],
                                name='following_unique',)
