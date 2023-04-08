from django.core.paginator import Paginator

from .constants import LEN_PUBLIC_FEED


def paginator(post_list, request):
    paginator = Paginator(post_list, LEN_PUBLIC_FEED)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
