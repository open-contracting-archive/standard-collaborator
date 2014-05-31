from os import path, pardir
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, RedirectView

from github import Github
from markdown import markdown


def get_repo():
    g = Github(client_id=settings.GITHUB_API_CLIENT_ID,
               client_secret=settings.GITHUB_API_CLIENT_SECRET)
    repo = g.get_repo(settings.STANDARD_GITHUB_REPO)
    return repo


def get_standard_from_github(repo, release="master"):
    """
    Get the standard markdown file from Github repo and decode it.
    Requires a repo and a valid release string. Does not check whether release
    string is valid to reduce calls to API.
    """
    contents = repo.get_contents(settings.STANDARD_FILE_PATH, ref=release)
    return contents.decoded_content


def render_markdown(repo=None, release=None, mdfile=None):
    rendered = ""
    if mdfile:
        with open(mdfile, 'r') as f:
            rendered = markdown(f.read())
    if repo:
        rendered = markdown(get_standard_from_github(repo, release=release))
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
    doc_path = path.abspath(
        path.join(settings.BASE_DIR, pardir, pardir, 'STANDARD.md')
    )

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        cleaned_release = "master"
        self.repo = get_repo()
        self.current_release = self.repo
        self.current_release.is_master = True
        self.other_releases = []
        for tag in self.repo.get_tags():
            if tag.name == self.release:
                cleaned_release = tag.name
                self.current_release = tag
                self.current_release.is_master = False
            else:
                self.other_releases.append(tag)

        if cleaned_release != self.release:
            # We didn't get a correct release request, so redirect
            print 'redirecting'
            return HttpResponseRedirect(reverse('latest'))
        else:
            return super(StandardView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(StandardView, self).get_context_data(*args, **kwargs)
        rendered_standard = render_markdown(repo=self.repo,
                                            release=self.release)
        context.update({
            'standard': rendered_standard,
            'current_release': self.current_release,
            'other_releases': self.other_releases,
        })
        return context
