from datetime import datetime
from braces.views import JSONResponseMixin
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, RedirectView, View

from github import Github, UnknownObjectException
from markdown import markdown

from .models import LatestVersion, CachedStandard


def get_repo():
    g = Github(client_id=settings.GITHUB_API_CLIENT_ID,
               client_secret=settings.GITHUB_API_CLIENT_SECRET)
    repo = g.get_repo(settings.STANDARD_GITHUB_REPO)
    return repo


def get_ordered_tags(repo):
    tags = repo.get_tags()
    list_tags = list(tags)
    date_format = '%a, %d %b %Y %H:%M:%S %Z'
    sorted_tags = \
        sorted(
            list_tags,
            key=lambda t: datetime.strptime(t.commit.stats.last_modified,
                                            date_format)
        )
    reversed_sorted = sorted_tags[::-1]
    latest_version = LatestVersion.objects.get()
    latest_version.tag_name = reversed_sorted[0].name
    latest_version.save()
    return reversed_sorted


def get_document_from_github(repo, path='README.md',
                             release='master', doctype='html'):
    """
    Get the standard markdown file from Github repo and decode it.
    Requires a repo and a valid release string. Does not check whether release
    string is valid to reduce calls to API.
    """
    try:
        contents = repo.get_contents(path, ref=release)
        document = contents.decoded_content
    except UnknownObjectException:
        if doctype == 'json':
            document = '{}'
        else:
            document = '<br />'
    return document


def render_markdown(document):
    return markdown(document, extensions=['footnotes', 'sane_lists', 'toc'])


def get_from_file(mdfile):
    with open(mdfile, 'r') as f:
        document = f.read()
    return document


def get_document_from_cache(repo, path, release, doctype='html'):
    try:
        cached = CachedStandard.objects.get(tag_name=release)
        if path == 'standard/standard.md':
            if cached.standard is '':
                raise CachedStandard.DoesNotExist
            else:
                document = cached.standard
        if path == 'standard/vocabulary.md':
            if cached.vocabulary == '':
                raise CachedStandard.DoesNotExist
            else:
                document = cached.vocabulary
        if path == 'standard/schema/release-schema.json':
            if cached.release_schema == '':
                raise CachedStandard.DoesNotExist
            else:
                document = cached.release_schema
    except CachedStandard.DoesNotExist:
        document = get_document_from_github_and_cache(
            repo, path, release, doctype
        )
    return document


def get_document_from_github_and_cache(repo, path, release, doctype='html'):
    document = get_document_from_github(repo, path, release, doctype)
    to_cache, created = CachedStandard.objects.get_or_create(tag_name=release)
    if path == 'standard/standard.md':
        to_cache.standard = document
    if path == 'standard/vocabulary.md':
        to_cache.vocabulary = document
    if path == 'standard/schema/release-schema.json':
        to_cache.release_schema = document
    to_cache.save()
    return document


class LatestView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            latest_release = LatestVersion.objects.get().tag_name
        except MultipleObjectsReturned:
            latest_release = 'master'
        kwargs.update({'release': latest_release})
	return reverse('standard', kwargs=kwargs)


class StandardView(TemplateView):
    template_name = 'main/standard.html'

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        cleaned_release = "master"
        self.other_releases = []

        self.repo = get_repo()
        ordered_tags = get_ordered_tags(self.repo)
        for tag in ordered_tags:
            tag.display_name = tag.name.replace('__', '.').replace('_', ' ')
            tag.is_master = False
            if tag.name == self.release:
                cleaned_release = tag.name
                self.current_release = tag
            else:
                self.other_releases.append(tag)

        if self.release == 'master':
            self.current_release = self.repo
            self.current_release.is_master = True
            self.current_release.commit = self.repo.get_commits()[0].sha
            self.current_release.display_name = 'master'

        if cleaned_release != self.release:
            # We didn't get a correct release request, so redirect
            return HttpResponseRedirect(reverse('latest'))
        else:
            return super(StandardView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(StandardView, self).get_context_data(*args, **kwargs)
        if self.current_release.is_master:
            # Always go to github
            rendered_standard = render_markdown(
                get_document_from_github(repo=self.repo,
                                         path='standard/standard.md',
                                         release=self.release)
            )
            rendered_vocabulary = render_markdown(
                get_document_from_github(repo=self.repo,
                                         path='standard/vocabulary.md',
                                         release=self.release)
            )
        else:
            # Try and get from cache
            # (goes to github and caches if not available)
            rendered_standard = render_markdown(
                get_document_from_cache(repo=self.repo,
                                        path='standard/standard.md',
                                        release=self.release)
            )
            rendered_vocabulary = render_markdown(
                get_document_from_cache(repo=self.repo,
                                        path='standard/vocabulary.md',
                                        release=self.release)
            )

        context.update({
            'standard': rendered_standard,
            'vocabulary': rendered_vocabulary,
            'current_release': self.current_release,
            'other_releases': self.other_releases,
            'site_unique_id': settings.SITE_UNIQUE_ID,
            'form': AuthenticationForm()
        })

        return context


class CommitView(TemplateView):
    template_name = 'main/standard.html'

    def get(self, request, *args, **kwargs):
        self.commit = kwargs.get('commitid')
        self.repo = get_repo()
        return super(CommitView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CommitView, self).get_context_data(*args, **kwargs)
        rendered_standard = render_markdown(
            get_document_from_cache(repo=self.repo,
                                    path='standard/standard.md',
                                    release=self.commit)
        )
        rendered_vocabulary = render_markdown(
            get_document_from_cache(repo=self.repo,
                                    path='standard/vocabulary.md',
                                    release=self.commit)
        )
        context.update({
            'commit': self.commit,
            'standard': rendered_standard,
            'vocabulary': rendered_vocabulary,
            'site_unique_id': settings.SITE_UNIQUE_ID,
            'form': AuthenticationForm()
        })

        return context


class SchemaView(JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        sn = kwargs.get('schema_name')
        release = kwargs.get('release')
        if release == 'standard':
            release = 'master'
            doc = get_document_from_github(
                repo=get_repo(),
                path='standard/schema/%s.json' % sn,
                release=release,
                doctype='json'
            )
        else:
            doc = get_document_from_cache(
                repo=get_repo(),
                path='standard/schema/%s.json' % sn,
                release=release,
                doctype='json'
            )
        return HttpResponse(doc, content_type="application/json", status=200)


class SchemaCommitView(JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        sn = kwargs.get('schema_name')
        commit = kwargs.get('commitid')
        doc = get_document_from_cache(repo=get_repo(),
                                      path='standard/schema/%s.json' % sn,
                                      release=commit,
                                      doctype='json')
        return HttpResponse(doc, content_type="application/json", status=200)
