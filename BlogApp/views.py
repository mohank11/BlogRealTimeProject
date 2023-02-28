from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from BlogApp.models import Post
from taggit.models import Tag

# Create your views here.
def post_list_view(request,tag_slug=None):
    post_list=Post.objects.all();
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 2)  # no.of.pages(20/2-rec=>10-pages)
    page_number = request.GET.get('page')
    try:
        post_list = paginator.page(page_number)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request,'BlogApp/post_list.html',{"post_list":post_list,'tag':tag})



def post_detail_view(request, year,month,day,post):
    post=get_object_or_404(Post,slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day);
    return render(request, "BlogApp/post_detail.html",{'post':post})



#from django.core.mail import send_mail
#send_mail('Hello', 'Very imp msg....','kunammohan2324@gmail.com',['kmohan20112000@gmail.com','pathansuhel8@gmail.com'])


#views for email
from django.core.mail import send_mail
from BlogApp.forms import EmailSendForm
def mail_send_view(request,id):
    post=get_object_or_404(Post,id=id, status='published')
    sent=False
    form=EmailSendForm()
    if request.method=='POST':
        form=EmailSendForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject='{}({}) recommends you to read "{}"'.format(cd['name'],cd['email'],	post.title)
            message="Read Post At: \n{}\n\n{} 'Comments:\n{}".format(post_url,cd['name'],cd['comments'])
            send_mail(subject, message, 'kunammohan2324@gmail.com', [cd['to']]) #use[] or ()tuple
            sent=True;
    else:
        form=EmailSendForm()
    return render(request,'BlogApp/sharebymail.html', {'post':post,'form':form,'sent':sent})

#bootstarp-sample.html-view
def bs_sample_view(request):
    return render(request,"BlogApp/Sample.html")


 #comment form-view
from BlogApp.models import Comment
from BlogApp.forms import CommentForm
from django.db.models import Count

def post_detail_view(request, year,month,day,post):
    post=get_object_or_404(Post,slug=post,
                status='published',
                publish__year=year,
                publish__month=month,
                publish__day=day)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', 'publish')[:4]

    comments=post.comments.filter(active=True)
    csubmit=False
    if request.method=='POST':
        form=CommentForm(data=request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.post=post
            new_comment.save()
            csubmit=True
    else:
        form=CommentForm()
    return render(request,'BlogApp/post_detail.html',{"post":post, 'form':form, 'comments':comments,'csubmit':csubmit,'similar_posts':similar_posts})


