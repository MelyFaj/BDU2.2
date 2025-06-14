from django.shortcuts import render
from .forms import TextForm, AddBlogForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_profile.models import User

# Create your views here.

from .models import (
    Blog,
    Category,
    Reply,
    # Tag,
    Comment
)

from transformers import pipeline

# Initialize the sentiment analysis pipeline
#sentiment_analyzer variable that holds the sentiment analysis pipeline.
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def home(request):
    blogs = Blog.objects.order_by('-created_date')
    context = {
        "blogs": blogs,
    }
    return render(request, 'home.html', context)

def blogs(request):
    queryset = Blog.objects.order_by('-created_date')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 4)
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')
    
    context = {
        "blogs": blogs,
        "paginator": paginator
    }
    return render(request, 'blogs.html', context)


def analyze_sentiment(comment_text):
    try:
        result = sentiment_analyzer(comment_text)[0]  # Analyze sentiment
        return result['label']  # 'LABEL' contains sentiment like "POSITIVE" or "NEGATIVE"
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "None"  # Return "None" in case of failure

def blog_details(request, slug):
    form = TextForm()
    blog = get_object_or_404(Blog, slug=slug)
    category = Category.objects.get(id=blog.category.id)
    related_blogs = category.category_blogs.all()
    comments_with_sentiment = []

    if request.method == "POST" and request.user.is_authenticated:
        form = TextForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('text')
            

            Comment.objects.create(
                user=request.user,
                blog=blog,
                text=form.cleaned_data.get('text')
            )
            # return redirect('blog_details', slug=slug)
    for comment in blog.blog_comments.all():
        sentiment = analyze_sentiment(comment.text)
        comments_with_sentiment.append({
            'comment': comment,
            'sentiment': sentiment
        })

    context = {
        "blog": blog,
        "related_blogs": related_blogs,
        "comments_with_sentiment": comments_with_sentiment,
        "form": form,
    }
    return render(request, 'blog_details.html', context)

def category_blogs(request, slug):
    category = get_object_or_404(Category, slug=slug)
    queryset = category.category_blogs.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    all_blogs = Blog.objects.order_by('-created_date')[:5]
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        "blogs": blogs,
        "all_blogs": all_blogs
    }
    return render(request, 'category_blogs.html', context)

@login_required(login_url='login')
def add_reply(request, blog_id, comment_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == "POST":
        form = TextForm(request.POST)
        if form.is_valid():
            comment = get_object_or_404(Comment, id=comment_id)
            Reply.objects.create(
                user=request.user,
                comment=comment,
                text=form.cleaned_data.get('text')
            )
    return redirect('blog_details', slug=blog.slug)


@login_required(login_url='login')
def my_blogs(request):
    queryset = request.user.user_blogs.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 6)
    delete = request.GET.get('delete', None)

    if delete:
        blog = get_object_or_404(Blog, pk=delete)
        
        if request.user.pk != blog.user.pk:
            return redirect('home')

        blog.delete()
        messages.success(request, "Your blog has been deleted!")
        return redirect('my_blogs')

    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        "blogs": blogs,
        "paginator": paginator
    }
    
    return render(request, 'my_blogs.html', context)
    

@login_required(login_url='login')
def add_blog(request):
    form = AddBlogForm()

    if request.method == "POST":
        form = AddBlogForm(request.POST, request.FILES)
        if form.is_valid():
            # tags = request.POST['tags'].split(',')
            user = get_object_or_404(User, pk=request.user.pk)
            category = get_object_or_404(Category, pk=request.POST['category'])
            blog = form.save(commit=False)
            blog.user = user
            blog.category = category
            blog.save()

            messages.success(request, "Blog added successfully")
            return redirect('blog_details', slug=blog.slug)
        else:
            print(form.errors)

    context = {
        "form": form
    }
    return render(request, 'add_blog.html', context)


@login_required(login_url='login')
def update_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    form = AddBlogForm(instance=blog)

    if request.method == "POST":
        form = AddBlogForm(request.POST, request.FILES, instance=blog)
        
        if form.is_valid():
            
            if request.user.pk != blog.user.pk:
                return redirect('home')

            user = get_object_or_404(User, pk=request.user.pk)
            category = get_object_or_404(Category, pk=request.POST['category'])
            blog = form.save(commit=False)
            blog.user = user
            blog.category = category
            blog.save()

            
            messages.success(request, "Blog updated successfully")
            return redirect('blog_details', slug=blog.slug)
        else:
            print(form.errors)


    context = {
        "form": form,
        "blog": blog
    }
    return render(request, 'update_blog.html', context)


@login_required(login_url='login')
def user_dashboard(request):
    # Get all blogs written by the logged-in user
    user_blogs = request.user.user_blogs.all()

    # Prepare a list to hold blogs, comments, and sentiments
    blogs_with_comments = []

    for blog in user_blogs:
        comments_with_sentiment = []
        
        # Fetch all comments for the blog
        for comment in blog.blog_comments.all():
            sentiment = analyze_sentiment(comment.text)  # Analyze sentiment for the comment text
            comments_with_sentiment.append({
                'comment': comment,
                'sentiment': sentiment
            })
        
        # Append blog details with comments and sentiments
        blogs_with_comments.append({
            'blog': blog,
            'comments': comments_with_sentiment
        })

    context = {
        "blogs_with_comments": blogs_with_comments
    }
    
    return render(request, 'user_dashboard.html', context)

