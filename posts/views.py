from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(1 * 20, key_prefix="index_page")
def index(request):
    """
    Главная страница(index).
    """
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    """
    Страница всех постов группы.
    """
    group = get_object_or_404(
        Group,
        slug=slug,
    )
    posts = group.posts.all()
    post_list = Post.objects.all()[:12]
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    """
    Страница создания нового поста.
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')
    
    
def profile(request, username):
    """
    Страница просмотра профиля пользователя.
    """
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = author.following.exists()
    context = {
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    """
    Отдельная страница просмотра поста.
    """
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'author': post.author,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    """
    Редактирование поста.
    """
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if post.author != request.user:
        return redirect('post',
                        username=username,
                        post_id=post.pk,
                        )
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        context = {
            'form': form,
            'post': post,
        }
        return render(request, 'new.html', context)
    form.save()
    return redirect('post',
                    username=username,
                    post_id=post.pk,
                    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    """
    Создание комментария к посту.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post',
                    username=username,
                    post_id=post.pk,
                    )


@login_required
def follow_index(request):
    """
    Страница с постами избранных авторов.
    """
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    """
    Подписка на профиль пользователя.
    """
    author = get_object_or_404(User, username=username)
    following = author.following.exists()
    if request.user != author and not following:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """
    Отписка от профиля пользователя.
    """
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect('profile', username=username)
