import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    '''Посты правильно создаются и редактируются.'''
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
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Описание тестовой группы.'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.another_client = Client()
        self.another_client.force_login(self.no_author)

    def test_post_create_client(self):
        '''Любой авторизованный пользователь может создать новый пост.'''
        posts_counter = Post.objects.count()
        form_data = {
            'text': 'Текст второго поста для тестов',
            'author': PostFormTest.no_author,
            'group': PostFormTest.group.id,
            'image': PostFormTest.uploaded,
        }
        response = self.another_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_counter + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст второго поста для тестов',
                author=PostFormTest.no_author,
                group=PostFormTest.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit_author(self):
        '''Автор может редактировать пост.'''
        post = Post.objects.create(
            text='Текст первого поста для тестов.',
            author=PostFormTest.author,
            group=PostFormTest.group,
        )
        uploaded = SimpleUploadedFile(
            name='small_new.gif',
            content=PostFormTest.small_gif,
            content_type='image/gif'
        )
        response = self.author_client.post(
            reverse('posts:edit', args=[post.id]),
            {'text': 'Обновленный текст №1',
             'author': PostFormTest.no_author,
             'group': PostFormTest.group.id,
             'image': uploaded,
             }
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        post.refresh_from_db()
        self.assertTrue(
            Post.objects.filter(
                text='Обновленный текст №1',
                author=PostFormTest.author,
                group=PostFormTest.group,
                image='posts/small_new.gif'
            ).exists()
        )

    def test_post_edit_no_author(self):
        '''НЕ автор НЕ может редактировать пост.'''
        post = Post.objects.create(
            text='Текст первого поста для тестов.',
            author=PostFormTest.author,
            group=PostFormTest.group,
        )
        posts_counter = Post.objects.count()
        response = self.another_client.post(
            reverse('posts:edit', args=[post.id]),
            {'text': 'Обновленный текст №2, который мы не увидим'}
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.text, 'Текст первого поста для тестов.')
        self.assertEqual(Post.objects.count(), posts_counter)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentFormTest(TestCase):
    '''Комментарии правильно создаются.'''
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.another_client = Client()
        self.another_client.force_login(self.no_author)

    def test_comment_create_author(self):
        '''Авторизованный пользователь может создать комментарий.'''
        comment_counter = Comment.objects.count()
        response = self.author_client.post(
            reverse('posts:add_comment', args=[self.post.id],),
            {'post': self.post.id,
             'text': 'Комментарий №2',
             'author': self.author.pk}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Comment.objects.count(), comment_counter + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post.id,
                text='Комментарий №2',
                author=self.author.pk
            ).exists()
        )

    def test_comment_create_no_author(self):
        '''НЕ авторизованный пользователь НЕ может создать комментарий.'''
        comment_counter = Comment.objects.count()
        response = self.client.post(
            reverse('posts:add_comment', args=[self.post.id],),
            {'post': self.post.id,
             'text': 'Комментарий №2',
             'author': self.author.pk}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Comment.objects.count(), comment_counter)
