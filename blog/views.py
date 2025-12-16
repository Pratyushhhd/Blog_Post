from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from .models import Post

# Create your views here.


def post_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, published=True)
    return render(request, 'blog/post_detail.html', {'post': post})

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

