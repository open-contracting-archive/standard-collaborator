from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, RedirectView

from github import Github, UnknownObjectException
from markdown import markdown


def get_repo():
    g = Github(client_id=settings.GITHUB_API_CLIENT_ID,
               client_secret=settings.GITHUB_API_CLIENT_SECRET)
    repo = g.get_repo(settings.STANDARD_GITHUB_REPO)
    return repo


def get_standard_from_github(repo, path='README.md', release="master"):
    """
    Get the standard markdown file from Github repo and decode it.
    Requires a repo and a valid release string. Does not check whether release
    string is valid to reduce calls to API.
    """
    try:
        contents = repo.get_contents(path, ref=release)
        document = contents.decoded_content
    except UnknownObjectException:
        document = '<br />'
    return document


def render_markdown(repo=None, path=None, release=None, mdfile=None):
    rendered = ""
    if mdfile:
        with open(mdfile, 'r') as f:
            rendered = markdown(f.read(),
                                extensions=['footnotes',
                                            'sane_lists',
                                            'toc',
                                            'extra'])
    if repo:
        rendered = markdown(
            get_standard_from_github(repo, path=path, release=release),
            extensions=['footnotes', 'sane_lists', 'toc']
        )
    return rendered


class LatestView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        repo = get_repo()
        latest_release_name = repo.get_tags()[0].name
        kwargs.update({'release': latest_release_name})
        return reverse('standard', kwargs=kwargs)


class StandardView(TemplateView):
    template_name = 'main/standard.html'

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        if not self.release:
            self.commit = kwargs.get('commit')
            self.release = 'master'
        cleaned_release = "master"
        self.repo = get_repo()
        self.current_release = self.repo
        self.current_release.is_master = True
        self.current_release.commit = self.repo.get_commits()[0].sha
        self.current_release.display_name = 'master'
        self.other_releases = []
        for tag in self.repo.get_tags():
            tag.display_name = tag.name.replace('__', '.').replace('_', ' ')
            tag.is_master = False
            if tag.name == self.release:
                cleaned_release = tag.name
                self.current_release = tag
            else:
                self.other_releases.append(tag)

        if not self.commit and cleaned_release != self.release:
            # We didn't get a correct release request, so redirect
            return HttpResponseRedirect(reverse('latest'))
        else:
            return super(StandardView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(StandardView, self).get_context_data(*args, **kwargs)
        rendered_standard = render_markdown(repo=self.repo,
                                            path='standard/standard.md',
                                            release=self.release)
        rendered_vocabulary = render_markdown(repo=self.repo,
                                              path='standard/vocabulary.md',
                                              release=self.release)
        context.update({
            'standard': rendered_standard,
            'vocabulary': rendered_vocabulary,
            'current_release': self.current_release,
            'other_releases': self.other_releases,
            'site_unique_id': settings.SITE_UNIQUE_ID,
            'form': AuthenticationForm()
        })

        if self.commit:
        context.update({
            'version': self.commit
        })
        return context
