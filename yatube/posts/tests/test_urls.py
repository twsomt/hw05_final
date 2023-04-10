from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

# from posts.constants import CACHE_TIMER
from posts.models import Comment, Group, Post, User

from django.conf import settings


class StaticURLTests(TestCase):
    '''Тестируем urls приложения posts'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='test_user_author',
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
        cls.TEST_DATA_PAGES = [
            {
                'title': 'Главная страница',
                'url_name': '/',
                'html_template': 'posts/index.html',
                'cache': settings.CACHE_TIMER,
            }, {
                'title': 'Страница с постами группы',
                'url_name': f'/group/{cls.group.slug}/',
                'html_template': 'posts/group_list.html',
            }, {
                'title': 'Страница пользователя',
                'url_name': f'/profile/{cls.author.username}/',
                'html_template': 'posts/profile.html',
            }, {
                'title': 'Страница с деталями поста',
                'url_name': f'/posts/{cls.post.id}/',
                'html_template': 'posts/post_detail.html',
            }, {
                'title': 'Страница создания поста',
                'url_name': '/create/',
                'need_authorization': True,
                'html_template': 'posts/create_post.html',
            }, {
                'title': 'Страница редактирования поста автором',
                'url_name': f'/posts/{cls.post.id}/edit/',
                'need_authorization': True,
                'html_template': 'posts/create_post.html',
            }, {
                'title': 'Страница с моими подписками',
                'url_name': '/follow/',
                'need_authorization': True,
                'html_template': 'posts/follow.html',
            },
        ]
        cls.TEST_DATA_ACTIONS = [
            {
                'title': 'Прокомментировать пост',
                'url_name': f'/posts/{StaticURLTests.post.id}/comment/',
            }, {
                'title': 'Подписаться на автора',
                'url_name': f'/posts/{StaticURLTests.post.id}/comment/',
            }, {
                'title': 'Отписаться от автора',
                'url_name': f'/posts/{StaticURLTests.post.id}/comment/',
            },
        ]
      
    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.another_client = Client()
        self.another_client.force_login(self.no_author)

    def test_page_status_get_method(self):
        '''Проверка ответов основных адресов и соответствия шаблонов (GET).'''

        for test in StaticURLTests.TEST_DATA_PAGES:
            with self.subTest(test['title']):

                if test.get('need_authorization'):
                    current_client = self.author_client
                else:
                    current_client = self.client

                response = current_client.get(test['url_name'])
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, test['html_template'])

    def test_non_existent_page(self):
        '''Тест ответа 404 для несуществующей страницы.'''
        response = self.client.get('/non_existent_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_not_author_can_not_edit_post(self):
        '''Редактирование поста доступно только автору.'''
        response = self.another_client.get(
            f'/posts/{StaticURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_actions_pathes(self):
        '''Адреса действий доступны и возвращат редиректы.'''
        for test in StaticURLTests.TEST_DATA_ACTIONS:
            with self.subTest(test['title']):
                response = self.another_client.get(test['url_name'])
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
