from django.contrib.auth import get_user_model
from django.db import models


class Group(models.Model):
    """ Модель группы. """
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Идентификатор', unique=True)
    description = models.TextField('Описание')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        """ Мета-класс группы,
        описывающий 'нормальное' название и сортировку. """
        verbose_name = 'Group'


class Post(models.Model):
    """ Модель поста. """
    text = models.TextField(
        verbose_name='Содержание поста',
        help_text='Напишите что-нибудь!')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу!')
    # поле для картинки
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        """ Мета-класс поста,
        описывающий 'нормальное' название и сортировку. """
        verbose_name = 'Post'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост')
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор')
    text = models.TextField(
        max_length=250,
        verbose_name='Содержание комментария',
        help_text='Напишите что-нибудь!')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        """ Мета-класс поста,
        описывающий 'нормальное' название и сортировку. """
        verbose_name = 'Comment'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = 'user', 'author'
