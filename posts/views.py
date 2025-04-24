from django.views.generic.edit import CreateView
from posts.models import Post
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from posts.forms import PostCreateForm


@method_decorator(login_required, name='dispatch')  # Decorador (protege la vista)
class PostCreateView(CreateView):
    template_name = 'posts/post_create.html'
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Post creado con éxito.')
        return super(PostCreateView, self).form_valid(form)
