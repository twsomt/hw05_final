from http import HTTPStatus

from posts.tests.data import DataForTests


class StaticURLTests(DataForTests):
    '''Тестируем urls приложения posts'''

    def test_page_status_for_guest(self):
        '''Проверка доступности основных страниц и соответствия шаблонов.'''

        for test in StaticURLTests.TEST_DATA:
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
