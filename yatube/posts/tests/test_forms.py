from http import HTTPStatus
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from posts.models import Comment, Post
from django.test import Client, TestCase, override_settings

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
            content=PostFormTest.small_gif,
            content_type='image/gif'
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
        response = self.author_client.post(
            reverse('posts:edit', args=[self.post.id]),
            {'text': 'Обновленный текст №1'}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Обновленный текст №1')

    def test_post_edit_no_author(self):
        '''НЕ автор НЕ может редактировать пост.'''
        response = self.another_client.post(
            reverse('posts:edit', args=[self.post.id]),
            {'text': 'Обновленный текст №1'}
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Текст первого поста для тестов.')


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
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Комментарий №1',
            author=cls.author,
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
                post=CommentFormTest.comment.post.id,
                text=CommentFormTest.comment.text,
                author=CommentFormTest.post.author.id
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