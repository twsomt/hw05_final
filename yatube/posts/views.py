from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .paginator import paginator

# from django.views.decorators.cache import cache_page


# @cache_page(CACHE_TIMER, key_prefix='index_page')
# По поводу отключенного кеширования написал в ЛС
def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginator(posts, request)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator(group.posts.select_related('author',), request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    posts = user_obj.posts.select_related('author', 'group')
    page_obj = paginator(posts, request)
    qty_posts = posts.count()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author__following__user=request.user
        ).exists()
    )
    context = {
        'user_obj': user_obj,
        'page_obj': page_obj,
        'qty_posts': qty_posts,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects
        .select_related('author', 'group'),
        pk=post_id
    )
    qty_posts = post.author.posts.count()
    short_text_title = post.text[:settings.LEN_TITLE_POST_DETAIL]
    form = CommentForm()
    comments = post.comments.select_related('author',)
    context = {
        'post': post,
        'short_text_title': short_text_title,
        'qty_posts': qty_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html',
                      {'form': form}
                      )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden(
            "Вы не можете редактировать этот пост, "
            "поскольку не являетесь его автором"
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': True}
                      )
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(posts, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    subscribe_obj = get_object_or_404(Follow, author=author, user=request.user)
    subscribe_obj.delete()
    return redirect('posts:follow_index')
