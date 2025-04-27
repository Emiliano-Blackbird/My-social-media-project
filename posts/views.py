from django.views.generic.edit import CreateView
from posts.models import Post
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import CommentCreateForm
from posts.forms import PostCreateForm
from django.http import JsonResponse


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    template_name = 'posts/post_create.html'
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Post creado con éxito.')
        return super(PostCreateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView, CreateView):
    template_name = 'posts/post_detail.html'
    model = Post
    context_object_name = 'post'
    form_class = CommentCreateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = self.get_object()
        return super(PostDetailView, self).form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Comentario añadido correctamente.')
        return reverse('post_detail', args=[self.get_object().pk])


@login_required
def like_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user in post.likes.all():
        messages.add_message(request, messages.INFO, 'Ya no te gusta este post.')
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        messages.add_message(request, messages.INFO, 'Te gusta este post.')

    return HttpResponseRedirect(reverse('post_detail', args=[pk]))


@login_required
def like_post_ajax(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        return JsonResponse({'message': 'Ya no te gusta este post.', 'liked': False, 'nLikes': post.likes.all().count()})
    else:
        post.likes.add(request.user)
        return JsonResponse({'message': 'Te gusta este post.', 'liked': True, 'nLikes': post.likes.all().count()})
