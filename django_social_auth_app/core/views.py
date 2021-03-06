from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from social_django.models import UserSocialAuth
from django_social_auth_app.repository.models import Repository, Tag
from django_social_auth_app.repository.tables import RepositoryTable
from django_tables2 import RequestConfig
from django.db.models import Q
from functools import reduce
import operator


@login_required
def home(request):
    user = request.user
    repositories_list = None
    on_filter = False

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None

    tags_filter_param = request.POST.dict().get('tags') or ''

    if tags_filter_param:
        filtered_tags = Tag.objects.filter(reduce(operator.or_, (Q(title__contains=search.strip()) for search in tags_filter_param.split(','))))
        repositories_list = Repository.objects.filter(owner_id=user.id).filter(tags__in=filtered_tags).distinct()
        on_filter = True
    else:
        repositories_list = Repository.objects.filter(owner_id=user.id).all()

    repositories_table = RepositoryTable(repositories_list)
    RequestConfig(request).configure(repositories_table)

    return render(request, 'core/home.html', {'github_login': github_login,
                                              'repositories_table': repositories_table,
                                              'tags_filter_param': tags_filter_param,
                                              'repositories_list': repositories_list,
                                              'on_filter': on_filter})
