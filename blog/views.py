from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from .models import Post
from .forms import CommentForm

# Delete Post
# =====================
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only author or staff/admin can delete
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
        # else: form will contain errors
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
# Post List
# =====================
def post_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

# =====================
# Post Detail
# =====================
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, published=True)
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

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

# =====================
# Create Post
# =====================
@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title and content:
            Post.objects.create(
                author=request.user,
                title=title,
                content=content,
                published=True
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
        post.save()
        return redirect('post_detail', pk=post.pk)

    return render(request, 'blog/edit_post.html', {'post': post})
