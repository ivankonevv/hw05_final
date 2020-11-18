import datetime


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    date = datetime.datetime.today().year
    return {'year': date}
