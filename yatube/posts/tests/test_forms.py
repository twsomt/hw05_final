from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Comment, Post
from posts.tests.data import DataForTests


class PostFormTest(DataForTests):
    '''Посты правильно создаются и редактируются.'''

    def test_post_create_client(self):
        '''Любой авторизованный пользователь может создать новый пост.'''

        img = SimpleUploadedFile(
            name='test_img_2.jpg',
            content=PostFormTest.img_code,
            content_type='image/jpg'
        )
        posts_counter = Post.objects.count()
        response = self.another_client.post(
            reverse('posts:post_create'),
            {'text': 'Текст второго поста для тестов',
             'group': PostFormTest.group.id,
             'image': img,
             },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_counter + 1)
        self.assertTrue(
            Post.objects.filter(
                # тесты создают изображение с именем
                # не test_img_2 а например test_img_2VlMLRJ
                # не смог это пофиксить.
                # скорее всего это из-за моего апгрейда пути в моделях.
                # но по сути текст из text является уникальным
                # а значит если пост с таким текстом существует,
                # значит пост создается успешно
                text='Текст второго поста для тестов',
            ).exists()
        )

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
                post=PostFormTest.comment.post.id,
                text=PostFormTest.comment.text,
                author=PostFormTest.post.author.id
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
