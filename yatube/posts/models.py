from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


def user_directory_path(instance, filename):
    '''
    Функция для определения пути сохранения медиа.
    Нужно для раскладывания по папкам юзерфайлов.
    '''
    return f'user_{instance.author.id}/{filename}'


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        help_text='Введите название группы',
        max_length=200)
    slug = models.SlugField(
        verbose_name='Уникальный адрес группы',
        help_text='Введите уникальный адрес группы',
        unique=True)
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы')

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Заполняется автоматически',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Пользователь",
        help_text="Автор поста"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name="Сообщество",
        help_text="Группа, к которой будет относиться пост"
    )
    image = models.ImageField(
        # Хотел как лучше, но не пропустили тесты
        # upload_to=user_directory_path,
        upload_to='posts/',
        blank=True,
        verbose_name='Изображение',
        help_text='Выберите изображение для публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return str(self.text)[:settings.LEN_DEF__STR__POST_MODEL] + '...'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост комментария",
        help_text="Пост, к которому будет относиться комментарий"
    )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор комментария",
        help_text="Пользователь, оставивший этот комментарий"
    )
    text = models.TextField(
        verbose_name="Комментарий",
        help_text="Введите текст комментария"
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Заполняется автоматически',
        auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
        help_text="Пользователь, подписавшийся на автора"
    )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор",
        help_text="Пользователь, на которого подписались"
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
