from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page})


def group_posts(request, slug):
    NeededGroup = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=NeededGroup)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': NeededGroup, 'page': page})


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    paginator = Paginator(
        Post.objects.filter(author=get_object_or_404(
            User,
            username=username)),
        10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author__username=username).exists())
    return render(request, 'profile.html', {
        'page': page,
        'user_profile': get_object_or_404(User, username=username),
        'count_posts': Post.objects.filter(
            author=get_object_or_404(
                User,
                username=username)).count(),
        'current_user': request.user,
        'following': following,
        'subscribers':
            Follow.objects.filter(author__username=username).count(),
        'subscribes': Follow.objects.filter(user__username=username).count()})


def post_view(request, username, post_id):
    form = PostForm(
        request.POST or None)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = Comment.objects.filter(post=post)
    comForm = CommentForm()
    return render(request, 'post.html', {
        'form': form,
        'post': post,
        'post_id': post_id,
        'author': get_object_or_404(User, username=username),
        'current_user': request.user,
        'comments': comments,
        'CommentForm': comForm,
        'subscribers':
            Follow.objects.filter(author__username=username).count(),
        'subscribes': Follow.objects.filter(user__username=username).count()})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect(
            reverse('post', kwargs={'username': username, 'post_id': post_id}))
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        post.save()
        return redirect(
            reverse('post', kwargs={'username': username, 'post_id': post_id}))
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(
        request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {'page': page,
         'paginator': paginator,
         'follow': True})


@login_required
def profile_follow(request, username):
    if request.user != get_object_or_404(User, username=username):
        try:
            Follow.objects.create(
                user=request.user,
                author=get_object_or_404(User, username=username)
            )
        except IntegrityError:
            return redirect('profile', username=username)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
