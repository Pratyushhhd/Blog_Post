from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post
from .forms import CommentForm

# =====================
# Delete Post
# =====================
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'blog/delete_post.html', {'post': post})


# =====================
# Signup View
# =====================
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# =====================
# Custom Login View
# =====================
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('post_list')


# =====================
# Post List with Search & Pagination
# =====================
def post_list(request):
    search_query = request.GET.get('q', '')
    posts = Post.objects.filter(status='published').order_by('-created_at')

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination (5 posts per page)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {
        'posts': page_obj,
        'search_query': search_query,
        'page_obj': page_obj
    })


# =====================
# Post Detail
# =====================

def post_detail(request, pk):
    # Fetch the post regardless of status
    post = get_object_or_404(Post, pk=pk)

    if post.status == 'draft' and not (request.user == post.author or request.user.is_staff):
        raise Http404("This post is not published.")

    comments = post.comments.all()

    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('post_detail', pk=post.pk)
        else:
            return redirect('login')
    else:
        form = CommentForm()

    liked = False
    if request.user.is_authenticated:
        liked = post.likes.filter(id=request.user.id).exists()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'liked': liked,
        'total_likes': post.total_likes()
    })


# =====================
# Create Post
# =====================
@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        status = request.POST.get('status', 'draft')  

        if title and content:
            Post.objects.create(
                author=request.user,
                title=title,
                content=content,
                status=status
            )
            return redirect('post_list')

    return render(request, 'blog/create_post.html')


# =====================
# Edit Post
# =====================
@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.status = request.POST.get('status', post.status)
        post.save()
        return redirect('post_detail', pk=post.pk)

    return render(request, 'blog/edit_post.html', {'post': post})


# =====================
# Like / Unlike Post (AJAX or redirect)
# =====================
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', pk=pk)

# =====================
# User Dashboard
# =====================
@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'blog/dashboard.html', {
        'posts': posts
    })
