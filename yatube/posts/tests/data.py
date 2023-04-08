from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from posts.constants import CACHE_TIMER
from posts.models import Comment, Group, Post, User


class DataForTests(TestCase):
    '''Статикданные для тестов.'''
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
        cls.another_user = User.objects.create_user(
            username='test_user_for_edit_test',
            password='test_password'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Описание тестовой группы.'
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа #2',
            slug='test_group_slug_2',
            description='Описание второй тестовой группы.'
        )
        cls.img_code = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.img = SimpleUploadedFile(
            name='test_img_1.jpg',
            content=cls.img_code,
            content_type='image/jpg'
        )
        cls.post = Post.objects.create(
            text='Текст первого поста для тестов.',
            author=cls.author,
            group=cls.group,
            image=cls.img,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.author,
        )

        cls.TEST_DATA = [
            {
                'title': 'Главная страница',
                'url_name': '/',
                'reverse_name': 'posts:index',
                'html_template': 'posts/index.html',
                'cache': CACHE_TIMER,
            }, {
                'title': 'Страница с постами группы',
                'url_name': f'/group/{cls.group.slug}/',
                'reverse_name': 'posts:group_list',
                'html_template': 'posts/group_list.html',
                'args': [cls.group.slug],
            }, {
                'title': 'Страница пользователя',
                'url_name': f'/profile/{cls.author.username}/',
                'reverse_name': 'posts:profile',
                'html_template': 'posts/profile.html',
                'args': [cls.author.username],
            }, {
                'title': 'Страница с деталями поста',
                'url_name': f'/posts/{cls.post.id}/',
                'reverse_name': 'posts:post_detail',
                'html_template': 'posts/post_detail.html',
                'args': [cls.post.id],
            }, {
                'title': 'Страница создания поста',
                'url_name': '/create/',
                'reverse_name': 'posts:post_create',
                'need_authorization': True,
                'html_template': 'posts/create_post.html',
            }, {
                'title': 'Страница редактирования поста автором',
                'url_name': f'/posts/{cls.post.id}/edit/',
                'reverse_name': 'posts:edit',
                'need_authorization': True,
                'html_template': 'posts/create_post.html',
                'args': [cls.post.id],
            },
        ]

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.another_client = Client()
        self.another_client.force_login(self.no_author)
