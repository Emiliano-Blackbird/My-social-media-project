from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView, DetailView, ListView,
    CreateView, UpdateView
)
from django.views.generic.edit import FormView

from django.contrib.auth.models import User

from .forms import RegistrationForm, LoginForm, ProfileFollow
from profiles.forms import FollowForm
from profiles.models import UserProfile, Follow
from posts.models import Post


class HomeView(TemplateView):
    template_name = 'general/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            seguidos = Follow.objects.filter(
                follower=self.request.user.profile
            ).values_list('following__user', flat=True)
            last_posts = Post.objects.filter(user__in=seguidos)
        else:
            last_posts = Post.objects.all().order_by('-created_at')[:5]
        context['last_posts'] = last_posts
        return context


class LoginView(FormView):
    template_name = 'general/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        usuario = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=usuario, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(
                self.request, f'Bienvenido de nuevo {user.username}'
            )
            return HttpResponseRedirect(reverse('home'))
        messages.error(self.request, 'Usuario o contraseña incorrectos')
        return super().form_invalid(form)


class RegisterView(CreateView):
    template_name = 'general/register.html'
    model = User
    success_url = reverse_lazy('login')
    form_class = RegistrationForm

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente')
        return super().form_valid(form)


class LegalView(TemplateView):
    template_name = 'general/legal.html'


class ContactView(TemplateView):
    template_name = 'general/contact.html'


@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DetailView, FormView):
    model = UserProfile
    template_name = 'general/profile_detail.html'
    context_object_name = 'profile'
    form_class = FollowForm

    def get_initial(self):
        initial = super().get_initial()
        initial['profile_pk'] = self.get_object().pk
        return initial

    def form_valid(self, form):
        profile_pk = form.cleaned_data['profile_pk']
        self.object = UserProfile.objects.get(pk=profile_pk)
        follower = self.request.user.profile
        following = self.object

        follow_relation = Follow.objects.filter(
            follower=follower, following=following
        )

        if follow_relation.exists():
            follow_relation.delete()
            messages.success(
                self.request,
                f'Ya no sigues a {following.user.username}'
            )
        else:
            Follow.objects.create(follower=follower, following=following)
            messages.success(
                self.request,
                f'Ahora sigues a {following.user.username}'
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile_detail', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['posts'] = profile.user.posts.all()
        context['following'] = Follow.objects.filter(
            follower=self.request.user.profile,
            following=profile
        ).exists()
        return context


class ProfileListView(ListView):
    model = UserProfile
    template_name = 'general/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserProfile.objects.exclude(
                user=self.request.user
            ).order_by('user__username')
        return UserProfile.objects.all().order_by('user__username')


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = UserProfile
    template_name = 'general/profile_update.html'
    context_object_name = 'profile'
    fields = ['profile_picture', 'bio', 'birth_date']

    def dispatch(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if user_profile.user != request.user:
            return HttpResponseRedirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile_detail', args=[self.object.pk])


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión')
    return HttpResponseRedirect(reverse('home'))
