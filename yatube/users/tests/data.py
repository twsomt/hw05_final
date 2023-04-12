from django.test import Client, TestCase

from posts.models import User


class DataForTests(TestCase):
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

        cls.TEST_DATA = [
            {
                'title': 'Регистрация',
                'url_name': '/auth/signup/',
                'reverse_name': 'users:signup',
                'html_template': 'users/signup.html'
            }, {
                'title': 'Вход',
                'url_name': '/auth/login/',
                'reverse_name': 'users:login',
                'html_template': 'users/login.html'
            }, {
                'title': 'Сбросить пароль',
                'url_name': '/auth/password_reset/',
                'reverse_name': 'users:password_reset',
                'html_template': 'users/password_reset_form.html'
            }, {
                'title': 'Письмо у вас на почте',
                'url_name': '/auth/password_reset/done/',
                'reverse_name': 'users:password_reset_done',
                'html_template': 'users/password_reset_done.html'
            }, {
                'title': 'Ввод нового пароля',
                'url_name': '/auth/reset/test/12345/',
                'reverse_name': 'users:password_reset_confirm',
                'html_template': 'users/password_reset_confirm.html',
                'args': {'uidb64': 'test', 'token': '12345'}
            }, {
                'title': 'Успешное назначение нового пароля',
                'url_name': '/auth/reset/done/',
                'reverse_name': 'users:password_reset_complete',
                'html_template': 'users/password_reset_complete.html'
            }, {
                'title': 'Изменить пароль',
                'url_name': '/auth/password_change/',
                'reverse_name': 'users:password_change',
                'need_authorization': True,
                'html_template': 'users/password_change_form.html'
            }, {
                'title': 'Пароль успешно изменен',
                'url_name': '/auth/password_change/done/',
                'reverse_name': 'users:password_change_done',
                'need_authorization': True,
                'html_template': 'users/password_change_done.html'
            }, {
                'title': 'Выход',
                'url_name': '/auth/logout/',
                'reverse_name': 'users:logout',
                'need_authorization': True,
                'html_template': 'users/logged_out.html'
            },
        ]

    def setUp(self):
        self.another_client = Client()
        self.another_client.force_login(self.no_author)
