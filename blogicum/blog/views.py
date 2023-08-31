from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blogicum.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post, User


class ProfileSuccessUrlMixin:
    """Миксин переадресации на профиль."""
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class DetailSuccessUrlMixin:
    """Миксин переадресации на отдельный пост."""
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']},
        )


class CommentInfoMixin:
    """
    Миксин для повторяющейся информации
    CBV редактирования и удаления комментария.
    """
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment.objects.filter(author=self.request.user),
            pk=self.kwargs['comment_id'],
        )


class PostListView(ListView):
    """Абстрактный CBV для списка публикаций."""
    model = Post
    template_name = None
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        posts = Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))
        return posts


class IndexListView(PostListView):
    """CBV главной страницы."""
    template_name = 'blog/index.html'


class CategoryListView(PostListView):
    """CBV для страниц категорий."""
    template_name = 'blog/category.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category,
            is_published=True,
            slug=category_slug,
        )
        queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        context['category'] = get_object_or_404(Category, slug=category_slug)
        return context


class PostCreateView(
    LoginRequiredMixin,
    ProfileSuccessUrlMixin,
    CreateView,
):
    """CBV формы создания публикации."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context


class PostUpdateView(
    LoginRequiredMixin,
    DetailSuccessUrlMixin,
    UpdateView,
):
    """CBV редактирования публикации."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['id'])

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        id = self.kwargs['id']
        if instance.author != request.user:
            return redirect(
                'blog:post_detail',
                id=id,
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(
    LoginRequiredMixin,
    ProfileSuccessUrlMixin,
    DeleteView,
):
    """CBV удаления публикации."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.filter(author=self.request.user),
            pk=self.kwargs['id'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class CommentCreateView(
    LoginRequiredMixin,
    DetailSuccessUrlMixin,
    CreateView,
):
    """CBV создания комментария."""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(
            Post,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
            pk=self.kwargs['id']
        )
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin,
    DetailSuccessUrlMixin,
    CommentInfoMixin,
    UpdateView,
):
    """CBV редактирования комментария."""
    pass


class CommentDeleteView(
    LoginRequiredMixin,
    DetailSuccessUrlMixin,
    CommentInfoMixin,
    DeleteView,
):
    """CBV удаления комментария."""
    pass


class ProfileListView(ListView):
    """CBV страницы профиля."""
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        queryset = Post.objects.select_related(
            'location',
            'category',
            'author',
        ).filter(
            author=self.author,
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))
        if self.author != self.request.user:
            queryset = queryset.filter(
                pub_date__lte=timezone.now(),
                category__is_published=True,
                is_published=True,
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(
    LoginRequiredMixin,
    ProfileSuccessUrlMixin,
    UpdateView,
):
    """CBV редактирования профиля."""
    model = Post
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)


class PostDetailView(DetailView):
    """CBV для отдельных публикаций."""
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = ['id']

    def get_object(self, queryset=None):
        queryset = Post.objects.select_related(
            'category',
            'location',
            'author',
        )
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            ) | queryset.filter(
                author=self.request.user,
            )
        else:
            queryset = queryset.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
        return get_object_or_404(queryset, pk=self.kwargs.get('id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        comments = Comment.objects.select_related(
            'author',
        ).filter(
            post=self.object,
        ).order_by('created_at')
        context['comments'] = comments
        return context
