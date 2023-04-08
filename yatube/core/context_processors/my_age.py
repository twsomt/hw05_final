from datetime import date


def add_prefix(age):
    if age % 10 == 1 and age != 11:
        return f'{age} год'
    elif 2 <= age % 10 <= 4 and age not in [12, 13, 14]:
        return f'{age} года'
    else:
        return f'{age} лет'


def my_age(request):
    """Возвращает мой возраст в годах."""
    birthday = date(1992, 12, 13)
    today = date.today()
    difference = (today - birthday).days // 365
    return {
        'age': add_prefix(difference),
    }
