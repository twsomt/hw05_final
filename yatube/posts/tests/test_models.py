from django.contrib.auth import get_user_model

from posts.constants import LEN_DEF__STR__POST_MODEL
from posts.tests.data import DataForTests

User = get_user_model()


class PostModelTest(DataForTests):
    """Тестируем модель Post."""

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_post_str = (PostModelTest.post
                             .text[:LEN_DEF__STR__POST_MODEL] + '...')
        assert str(PostModelTest.post) == expected_post_str, (
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


class GroupModelTest(DataForTests):
    """Тестируем модель Group."""

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_group_str = GroupModelTest.group.title
        assert str(GroupModelTest.group) == expected_group_str, (
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


class CommentModelTest(DataForTests):
    """Тестируем модель Comment."""

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
