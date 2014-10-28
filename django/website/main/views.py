from __future__ import unicode_literals

from os import path
import re

from braces.views import JSONResponseMixin
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import translation
from django.views.generic import TemplateView, RedirectView, View

from .standardscache import (HTML_ROOT, StandardsRepo, HTMLProducer,
                             get_path_for_release, get_exported_languages)


class StandardRedirectView(RedirectView):
    permanent = False

    # TODO: what about legacy tags where this URL is valid?
    def get_redirect_url(self, *args, **kwargs):
        kwargs.update({
            'release': self.release,
            'lang': self.lang,
            'path': get_path_for_release(self.release, self.lang)
        })
        return reverse('standard', kwargs=kwargs)


class LatestView(StandardRedirectView):

    def get(self, request, *args, **kwargs):
        self.release = StandardsRepo().get_latest_tag_name()
        self.lang = settings.STANDARD_DEFAULT_LANG
        return super(LatestView, self).get(request, *args, **kwargs)


class StandardRootView(StandardRedirectView):

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        self.lang = settings.STANDARD_DEFAULT_LANG
        return super(StandardRootView, self).get(request, *args, **kwargs)


class StandardLangView(StandardRedirectView):

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        self.lang = kwargs.get('lang')
        return super(StandardLangView, self).get(request, *args, **kwargs)


class CommitRedirectView(RedirectView):

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        self.old_url_path = kwargs.get('old_url_path')
        return super(CommitRedirectView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        kwargs = {'release': self.release}
        return reverse('standard-root', kwargs=kwargs) + self.old_url_path


class StandardView(TemplateView):
    template_name = 'main/standard.html'
    git_sha_re = re.compile(r'^[0-9a-fA-F]{40}$')

    def get(self, request, *args, **kwargs):
        self.release = kwargs.get('release')
        # allow for child class to set this
        self.is_commit_id = (self.git_sha_re.match(self.release) is not None)
        self.lang = kwargs.get('lang')
        translation.activate(self.lang)
        self.path = kwargs.get('path')
        self.other_releases = []

        self.repo = StandardsRepo()
        self.repo.export_commit(self.release)
        self.std_commit = self.repo.standardise_commit_name(self.release)

        self.html_prod = HTMLProducer(self.release, self.std_commit)
        self.html_dir = self.html_prod.get_html_dir()

        cleaned_release = "master"

        ordered_tags = self.repo.get_ordered_tag_dicts()
        for tag in ordered_tags:
            if tag['name'] == self.release:
                cleaned_release = tag['name']
                self.current_release = tag
            else:
                self.other_releases.append(tag)

        if self.release == 'master':
            self.current_release = self.repo.get_master_tag_dict()

        if not self.is_commit_id and cleaned_release != self.release:
            # We didn't get a correct release request, so redirect
            return HttpResponseRedirect(reverse('latest'))
        else:
            return super(StandardView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(StandardView, self).get_context_data(*args, **kwargs)
        # get file path corresponding to self.path and put in context
        # it will be included using SSI (Server Side Include)
        content_path = path.join(self.std_commit, self.lang, self.path) + '.html'
        if not path.exists(path.join(HTML_ROOT, content_path)):
            raise Http404
        lang_codes = get_exported_languages(self.release)
        lang_list = [{'code': lang, 'name': settings.LANG_CODE_NAME.get(lang, lang)}
                     for lang in lang_codes]
        lang_list.sort(key=lambda l: l['name'])

        context_dict = {
            'content_path': content_path,
            'release_name': self.release,
            'latest_release_name': StandardsRepo().get_latest_tag_name(),
            'other_releases': self.other_releases,
            'site_unique_id': settings.SITE_UNIQUE_ID,
            'lang': self.lang,
            'lang_list': lang_list,
            'file_path': self.path,
            'form': AuthenticationForm()
        }
        if self.is_commit_id:
            context_dict['commit'] = self.release
        else:
            context_dict['current_release'] = self.current_release

        context.update(context_dict)
        return context


class SchemaView(JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        repo = StandardsRepo()
        schema_name = kwargs.get('schema_name')

        release = kwargs.get('release')
        if release == 'standard':
            release = 'master'

        doc = repo.get_json_contents(release, schema_name)
        if doc is None:
            # Set to blank json if no doc so docson has something to render
            doc = "{}"
        return HttpResponse(doc, content_type="application/json", status=200)
