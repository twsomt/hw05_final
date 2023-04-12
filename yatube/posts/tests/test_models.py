from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.conf import settings

from posts.models import Comment, Follow, Group, Post, User

User = get_user_model()


class PostModelTest(TestCase):
    """Тестируем модель Post."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Описание тестовой группы.'
        )
        cls.post = Post.objects.create(
            text='Текст первого поста для тестов.',
            author=cls.author,
            group=cls.group,
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_post_str = (PostModelTest.post
                             .text[:settings.LEN_DEF__STR__POST_MODEL] + '...')
        self.assertEqual(
            str(PostModelTest.post),
            expected_post_str,
            "Метод __str__ в модели Post работает неверно. "
            f"Ожидалось '{expected_post_str}', "
            f"получено '{str(PostModelTest.post)}'"
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Пользователь',
            'group': 'Сообщество',
            'image': 'Изображение',
        }
        expected_fields = {field: post._meta.get_field(
            field).verbose_name for field in field_verboses}
        self.assertDictEqual(field_verboses, expected_fields)

    def test_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Текст нового поста',
            'pub_date': 'Заполняется автоматически',
            'author': 'Автор поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Выберите изображение для публикации',
        }
        expected_fields = {field: post._meta.get_field(
            field).help_text for field in field_help_text}
        self.assertDictEqual(field_help_text, expected_fields)


class GroupModelTest(TestCase):
    """Тестируем модель Group."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        cls.no_author = User.objects.create_user(
            username='test_user_no_author',
            password='test_password'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Описание тестовой группы.'
        )

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_group_str = GroupModelTest.group.title
        self.assertEqual(
            str(GroupModelTest.group),
            expected_group_str,
            "Метод __str__ в модели Group работает неверно. "
            f"Ожидалось '{expected_group_str}', "
            f"получено '{str(GroupModelTest.group)}'"
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный адрес группы',
            'description': 'Описание группы',
        }
        expected_fields = {field: group._meta.get_field(
            field).verbose_name for field in field_verboses}
        self.assertDictEqual(field_verboses, expected_fields)

    def test_help_text(self):
        """help_text в полях модели Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Введите название группы',
            'slug': 'Введите уникальный адрес группы',
            'description': 'Введите описание группы',
        }
        expected_fields = {field: group._meta.get_field(
            field).help_text for field in field_help_text}
        self.assertDictEqual(field_help_text, expected_fields)


class CommentModelTest(TestCase):
    """Тестируем модель Comment."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Описание тестовой группы.'
        )
        cls.post = Post.objects.create(
            text='Текст первого поста для тестов.',
            author=cls.author,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        expected_post_str = (CommentModelTest.post
                             .text[:settings.LEN_DEF__STR__POST_MODEL] + '...')
        self.assertEqual(
            str(CommentModelTest.post),
            expected_post_str,
            "Метод __str__ в модели Post работает неверно. "
            f"Ожидалось '{expected_post_str}', "
            f"получено '{str(CommentModelTest.post)}'"
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост комментария',
            'text': 'Комментарий',
        }
        expected_fields = {field: comment._meta.get_field(
            field).verbose_name for field in field_verboses}
        self.assertDictEqual(field_verboses, expected_fields)

    def test_help_text(self):
        """help_text в полях модели Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_text = {
            'post': 'Пост, к которому будет относиться комментарий',
            'text': 'Введите текст комментария',
        }
        expected_fields = {field: comment._meta.get_field(
            field).help_text for field in field_help_text}
        self.assertDictEqual(field_help_text, expected_fields)


class FollowModelTest(TestCase):
    """Тестируем модель Follow."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        cls.no_author = User.objects.create_user(
            username='test_user_no_author',
            password='test_password'
        )
        cls.follow = Follow.objects.create(
            user=cls.no_author,
            author=cls.author,
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Follow совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        expected_fields = {field: follow._meta.get_field(
            field).verbose_name for field in field_verboses}
        self.assertDictEqual(field_verboses, expected_fields)

    def test_help_text(self):
        """help_text в полях модели Follow совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_help_text = {
            'user': 'Пользователь, подписавшийся на автора',
            'author': 'Пользователь, на которого подписались',
        }
        expected_fields = {field: follow._meta.get_field(
            field).help_text for field in field_help_text}
        self.assertDictEqual(field_help_text, expected_fields)
