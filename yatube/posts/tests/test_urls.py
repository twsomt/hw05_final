from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase
from posts.models import Comment, Group, Post, User


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
        cls.test_data_pages = [
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
        cls.test_data_actions = [
            {
                'title': 'Прокомментировать пост',
                'url_name': f'/posts/{StaticURLTests.post.id}/comment/',
            }, {
                'title': 'Подписаться на автора',
                'url_name':
                    f'/profile/{StaticURLTests.author.username}/follow/',
            }, {
                'title': 'Отписаться от автора',
                'url_name':
                    f'/profile/{StaticURLTests.author.username}/unfollow/',
            },
        ]

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.another_client = Client()
        self.another_client.force_login(self.no_author)

    def test_page_status_get_method(self):
        '''Проверка ответов основных адресов и соответствия шаблонов.'''

        for test in StaticURLTests.test_data_pages:
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
        for test in StaticURLTests.test_data_actions:
            with self.subTest(test['title']):
                response = self.another_client.get(test['url_name'])
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
