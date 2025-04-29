from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse

from posts.models import Post
from posts.forms import PostCreateForm
from .forms import CommentCreateForm


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    template_name = 'posts/post_create.html'
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Post creado con éxito.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView, CreateView):
    template_name = 'posts/post_detail.html'
    model = Post
    context_object_name = 'post'
    form_class = CommentCreateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(
            self.request, 'Comentario añadido correctamente.'
        )
        return reverse('post_detail', args=[self.get_object().pk])


@login_required
def like_post(request, pk):
    post = Post.objects.get(pk=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.info(request, 'Ya no te gusta este post.')
    else:
        post.likes.add(request.user)
        messages.info(request, 'Te gusta este post.')

    return HttpResponseRedirect(reverse('post_detail', args=[pk]))


@login_required
def like_post_ajax(request, pk):
    post = Post.objects.get(pk=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        response = {
            'message': 'Ya no te gusta este post.',
            'liked': False,
            'nLikes': post.likes.count()
        }
    else:
        post.likes.add(request.user)
        response = {
            'message': 'Te gusta este post.',
            'liked': True,
            'nLikes': post.likes.count()
        }

    return JsonResponse(response)
