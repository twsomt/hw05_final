import time

from django import forms
from django.core.paginator import Page
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from posts.constants import CACHE_TIMER, LEN_PUBLIC_FEED, LEN_TITLE_POST_DETAIL
from posts.forms import CommentForm
from posts.models import Follow, Group, Post, User
from posts.tests.data import DataForTests


class ViewsTests(DataForTests):
    '''Проверка основных адресов и соответствия шаблонов.'''

    def test_response_view_func(self):
        '''Функции используют ожидаемые шаблоны.'''
        for test in self.TEST_DATA:
            with self.subTest(test['title']):

                if test.get('need_authorization'):
                    current_client = self.author_client
                else:
                    current_client = self.client

                if test.get('cache'):
                    time.sleep(test['cache'])  # Косвенно тестируем кеш

                response = current_client.get(
                    reverse(test['reverse_name'], args=test.get('args'))
                )
                self.assertTemplateUsed(response, test['html_template'])

    def post_fields_check(self, post):
        '''Вспомогательная функция для проверки полей объекта класса Post.'''
        self.assertEqual(post.id, ViewsTests.post.id)
        self.assertEqual(post.text, ViewsTests.post.text)
        self.assertEqual(post.author, ViewsTests.post.author)
        self.assertEqual(post.group, ViewsTests.post.group)
        self.assertEqual(post.image, ViewsTests.post.image)

    def get_qty_posts_author(self, username):
        '''Вспомогательная функция для получения кол-ва постов пользователя.'''
        user_obj = get_object_or_404(User, username=username)
        return user_obj.posts.count()

    def create_edit_fields_check(self, response):
        '''Вспомогательная функция для проверки полей в формах.'''
        context = response.context
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        form = context.get('form')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        time.sleep(CACHE_TIMER)  # Косвенно тестируем кеш
        response = self.client.get(reverse('posts:index'))

        context = response.context
        # page_obj
        post = context['page_obj'].object_list[0]
        self.assertIsInstance(post, Post)
        self.post_fields_check(post)

    def test_list_group_page_show_correct_context(self):
        '''Шаблон group_list сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse('posts:group_list', args=[ViewsTests.group.slug])
        )

        context = response.context
        # page_obj
        post = context['page_obj'].object_list[0]
        self.post_fields_check(post)

        # group
        group = context['group']
        self.assertIsInstance(group, Group)
        self.assertEqual(group.id, ViewsTests.group.id)
        self.assertEqual(group.title, ViewsTests.group.title)
        self.assertEqual(group.slug, ViewsTests.group.slug)
        self.assertEqual(group.description, ViewsTests.group.description)

    def test_profile_page_show_correct_context(self):
        '''Шаблон profile сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse('posts:profile', args=[ViewsTests.author.username])
        )

        context = response.context
        # user_obj
        author = context['user_obj']
        self.assertIsInstance(author, User)
        self.assertEqual(author.username, ViewsTests.author.username)

        # page_obj
        post = context['page_obj'].object_list[0]
        self.assertIsInstance(post, Post)
        self.post_fields_check(post)

        # qty_posts
        qty_posts = context['qty_posts']
        expected_qty_posts = self.get_qty_posts_author(
            ViewsTests.author.username)
        self.assertEqual(qty_posts, expected_qty_posts)

    def test_post_detail_page_show_correct_context(self):
        '''Шаблон post_detail сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse('posts:post_detail', args=[ViewsTests.post.id])
        )

        context = response.context
        # post
        post = context['post']
        self.post_fields_check(post)

        # short_text_title
        short_text_title = context['short_text_title']
        expected_short_text_title = (
            ViewsTests.post.text[:LEN_TITLE_POST_DETAIL])
        self.assertEqual(short_text_title, expected_short_text_title)

        # qty_posts
        qty_posts = context['qty_posts']
        expected_qty_posts = self.get_qty_posts_author(
            ViewsTests.author.username)
        self.assertEqual(qty_posts, expected_qty_posts)

        # form
        form = context['form']
        self.assertIsInstance(form, CommentForm)

        # comments
        comments = context['comments'][0]
        self.assertEqual(comments, ViewsTests.comment)

    def test_post_create_page_show_correct_context(self):
        '''Шаблон post_create сформирован с правильным контекстом.'''
        response = self.author_client.get(reverse('posts:post_create'))
        self.create_edit_fields_check(response)

    def test_post_edit_correct_form_redirect(self):
        '''Шаблон post_edit сформирован с правильным контекстом.
        В instance попадает пост, переданный аргументом в редактирование.
        '''
        response = self.author_client.get(
            reverse('posts:edit', args=[ViewsTests.post.id]))
        self.create_edit_fields_check(response)

        # form instance
        form = response.context.get('form')
        form_fields_values = form.instance.__dict__
        self.assertEqual(form_fields_values['id'], ViewsTests.post.id)
        self.assertEqual(form_fields_values['text'], ViewsTests.post.text)
        self.assertEqual(form_fields_values['author_id'], ViewsTests.author.id)
        self.assertEqual(form_fields_values['group_id'], ViewsTests.group.id)

    def text_group_adress(self):
        '''Пост не попадает в группу, для которой не был предназначен.'''
        group = get_object_or_404(
            Group, slug=ViewsTests.another_group.slug)
        posts_count = group.posts.count()
        self.assertEqual(posts_count, 0)


class PaginatorViewsTest(TestCase):
    '''Тестирование пагинатора.'''
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        cls.post_creater_and_get_qty_posts()

    @classmethod
    def post_creater_and_get_qty_posts(cls):
        '''Добавляем в БД 15 постов и запоминаем их число'''
        cls.qty_posts = 15  # количество постов
        Post.objects.bulk_create(
            Post(author=cls.author,
                 text=f'Текст поста #{i} для тест пагинатора.',
                 ) for i in range(cls.qty_posts)
        )

    def test_first_page_contains_ten_records(self):
        '''Количество постов на первой странице равно 10.'''
        time.sleep(CACHE_TIMER)  # Косвенно тестируем кеш
        response = self.client.get(reverse('posts:index'))
        page_obj = response.context['page_obj']
        self.assertIsInstance(page_obj, Page)
        self.assertEqual(
            len(page_obj), LEN_PUBLIC_FEED
        )

    def test_second_page_contains_three_records(self):
        '''Количество постов на второй странице 1 >= x >= 10.'''
        response = self.client.get(reverse('posts:index') + '?page=2')
        page_obj = response.context['page_obj']
        self.assertIsInstance(page_obj, Page)
        self.assertEqual(
            len(page_obj), self.qty_posts - LEN_PUBLIC_FEED
        )


class CasheTest(DataForTests):
    '''Страница index кешируется с интервалом CACHE_TIMER сек.'''

    def test_cache(self):
        '''Сразу после публикации новый пост не виден.'''
        response = self.client.get(reverse('posts:index'))
        context = response.context
        self.assertIsNone(context)

        # то, что пост виден после публикации + паузы, проверяется выше
        # в тестах контекста


class FollowViewsTest(DataForTests):
    '''Подписки функционируют нормально.'''

    def creater(self):
        '''Вспомогательная функция для создания подписки.'''
        Follow.objects.create(
            user=self.no_author,
            author=self.author
        )

    def test_authorized_user_follow(self):
        '''Авторизованный юзер может подписаться на автора поста.'''
        self.another_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username},
            )
        )
        follow_obj = Follow.objects.latest('id')
        self.assertEqual(follow_obj.user_id, self.no_author.id)
        self.assertEqual(follow_obj.author_id, self.post.author.id)

    def test_authorized_user_unfollow(self):
        '''Авторизованный юзер может отписаться от автора поста.'''
        self.another_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username},
            )
        )
        followers_cnt_subscribing = Follow.objects.count()

        self.another_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post.author.username},
            )
        )
        self.assertEqual(Follow.objects.count(), followers_cnt_subscribing - 1)

    def test_follow_post_on_follow_page(self):
        '''После подписки пост попадает на страницу подписок.'''
        self.creater()

        follow_list = (
            self.another_client.get(reverse('posts:follow_index'))
            .context['page_obj']
            .object_list
        )

        self.assertIn(self.post, follow_list)

    def test_follow_post_not_in_wrong_page(self):
        '''После подписки пост не попадает на ненужную страницу.'''
        self.creater()

        follow_list = (
            self.author_client.get(reverse('posts:follow_index'))
            .context['page_obj']
            .object_list
        )

        self.assertNotIn(self.post, follow_list)