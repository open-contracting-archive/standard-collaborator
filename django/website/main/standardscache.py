from __future__ import unicode_literals

from datetime import datetime
import os
from os import path
import re
import shutil
import subprocess

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.template.loader import render_to_string

from git import Repo
from markdown import markdown

WORKING_DIR = path.abspath(path.join(path.dirname(__file__), '..', 'working'))
REPO_DIR = path.join(WORKING_DIR, 'repo')
EXPORT_ROOT = path.join(WORKING_DIR, 'exports')
HTML_ROOT = path.join(WORKING_DIR, 'html')
NUMERIC_PREFIX_RE = re.compile(r'^\d\d_')


def get_commit_export_dir(commit):
    return path.join(EXPORT_ROOT, commit)


def get_commit_export_docs_dir(commit):
    return path.join(get_commit_export_dir(commit), settings.STANDARD_DOCS_PATH)


def get_commit_html_dir(commit):
    return path.join(HTML_ROOT, commit)


def tag_to_tag_dict(tag):
    """takes a GitPython tag object and converts to dict with fields we need"""
    return {
        'name': tag.name,
        'display_name': tag.name.replace('__', '.').replace('_', ' '),
        'is_master': False,
        'commit': tag.commit.hexsha,
        'last_modified': datetime.fromtimestamp(tag.commit.committed_date)
    }


def remove_numeric_prefix(name):
    return name[3:]


def export_md_file_to_name(filename):
    """We take in "01_intro.md" and return "intro"
    """
    return filename[3:-3]


def humanise(name):
    """ Take "further_info" and return "Further info" """
    return name.replace('_', ' ').capitalize()


def is_section_dir(export_dir, section_dir):
    return (NUMERIC_PREFIX_RE.match(section_dir) and
            path.isdir(path.join(export_dir, section_dir)))


def is_content_file(content_file):
    return NUMERIC_PREFIX_RE.match(content_file) and content_file.endswith('.md')


def export_path_to_url_path(section_dir, content_file):
    return '%s/%s' % (remove_numeric_prefix(section_dir),
                      export_md_file_to_name(content_file))


def get_path_for_release(release, lang):
    """get the path (eg 'xxx/yyy' for 01_xxx/01_yyy) for the release and
    language specified
    """
    commit = StandardsRepo().standardise_commit_name(release)
    export_docs_dir = get_commit_export_docs_dir(commit)
    lang_dir = path.join(export_docs_dir, lang)
    try:
        first_section_dir = [d for d in sorted(os.listdir(lang_dir))
                            if is_section_dir(lang_dir, d)][0]
        first_content_file = [f for f in sorted(os.listdir(path.join(lang_dir, first_section_dir)))
                            if is_content_file(f)][0]
        return export_path_to_url_path(first_section_dir, first_content_file)
    except OSError:
        raise Http404


class StandardsRepo(object):

    def __init__(self):
        self.repo = Repo(REPO_DIR)

    def git_pull(self):
        """ ensure we always actually get the latest and don't have to worry
        about merge conflicts """
        subprocess.check_call(['git', 'fetch'], cwd=REPO_DIR)
        subprocess.check_call(['git', 'fetch', '--tags'], cwd=REPO_DIR)
        subprocess.check_call(['git', 'reset', '--hard', 'origin/master'], cwd=REPO_DIR)

    def master_commit_id(self):
        """Return the hash of the last commit on master"""
        # this assumes that head is on master
        return self.repo.head.commit.hexsha

    def get_ordered_tags(self):
        tags = self.repo.tags
        sorted_tags = sorted(
            tags, key=lambda t: t.commit.committed_date, reverse=True)
        return sorted_tags

    def get_latest_tag_name(self):
        ordered_tags = self.get_ordered_tags()
        if len(ordered_tags) == 0:
            return 'master'
        else:
            return ordered_tags[0].name

    def get_ordered_tag_dicts(self):
        return [tag_to_tag_dict(tag) for tag in self.get_ordered_tags()]

    def get_master_tag_dict(self):
        tag_dict = tag_to_tag_dict(self.repo.head)
        tag_dict['name'] = tag_dict['display_name'] = 'master'
        tag_dict['is_master'] = True
        return tag_dict

    def standardise_commit_name(self, commit):
        """ make sure we have a "standard" commit id to use elsewhere.

        For now - if the commit is "master" then we do a git pull to ensure
        we have the latest from git, and then convert it to the commit hash.
        """
        if commit == 'master':
            self.git_pull()
            return self.master_commit_id()
        # TODO: if not SHA, convert to SHA - tags etc ...
        else:
            # TODO: should we check commit exists?  Raise 404 if not?
            return commit

    def get_commit(self, commit):
        # TODO: implement this
        # see template for fields required
        """Return a commit object with commit name, last modified date ..."""
        commit = self.standardise_commit_name(commit)
        # TODO: investigate when commit does not exist, decide how to handle it
        gitcommit = self.repo.commit(commit)
        return gitcommit
        # return {}

    def export_commit(self, commit, force_regenerate=False):
        commit = self.standardise_commit_name(commit)
        export_dir = get_commit_export_dir(commit)
        export_exists = path.exists(export_dir)
        if force_regenerate and export_exists:
            shutil.rmtree(export_dir)
            export_exists = False
        if not export_exists:
            # command from http://stackoverflow.com/a/163769/3189
            subprocess.check_call(
                'git archive --prefix=%s/ %s | tar -x -C %s' %
                (commit, commit, EXPORT_ROOT),
                cwd=REPO_DIR, shell=True)
        return export_dir

    def get_json_contents(self, commit, json_name):
        export_dir = self.export_commit(commit)
        json_path = path.join(
            export_dir, settings.STANDARD_SCHEMA_PATH, '%s.json' % json_name)
        try:
            with open(json_path, 'r') as json_file:
                json_contents = json_file.read()
            return json_contents
        except IOError:
            return None

    def delete_export(self, commit):
        export_dir = get_commit_export_dir(commit)
        if path.exists(export_dir):
            shutil.rmtree(export_dir)


class HTMLProducer(object):

    def __init__(self, release, std_commit):
        self.release = release
        self.std_commit = std_commit
        self.export_docs_dir = get_commit_export_docs_dir(std_commit)
        self.html_dir = get_commit_html_dir(std_commit)
        self.dir_structure = {}
        # cache for directory structure, will end up like:
        # self.dir_structure = {
        #     "en": {
        #         "01_intro": {
        #             "01_index": True,
        #         },
        #         "02_main": {
        #             "01_why": True,
        #             "02_how": True,
        #         }
        #     },
        #     "es": {
        #         ...
        #     }
        # }

    def get_html_dir(self, ensure_exists=True):
        """ get the html directory """
        if ensure_exists and not path.exists(self.html_dir):
            self.create_html()
        # TODO: should we return not found if not exists and not ensure_exists ??
        return self.html_dir

    def delete_html_dir(self):
        if path.exists(self.html_dir):
            shutil.rmtree(self.html_dir)

    def get_exported_languages(self, export_docs_root):
        """ find all 2 letter language codes in directory """
        # TODO: should we support en_gb etc? -> drop len == 2 check
        # but we might want the exported languages elsewhere ...
        return [d for d in os.listdir(export_docs_root)
                if len(d) == 2 and path.isdir(path.join(export_docs_root, d))]

    def make_dir_structure(self):
        self.dir_structure = {}
        # TODO: do for: if: like other methods?
        for lang in self.get_exported_languages(self.export_docs_dir):
            self.dir_structure[lang] = {}
            export_lang_dir = path.join(self.export_docs_dir, lang)
            self.make_dir_structure_lang(lang, export_lang_dir)

    def make_dir_structure_lang(self, lang, export_dir):
        for section_dir in os.listdir(export_dir):
            if is_section_dir(export_dir, section_dir):
                self.dir_structure[lang][section_dir] = {}
                export_section_dir = path.join(export_dir, section_dir)
                self.make_dir_structure_content(lang, section_dir, export_section_dir)

    def make_dir_structure_content(self, lang, section_dir, export_dir):
        for content_file in os.listdir(export_dir):
            # check for 01_ prefix and that it is a markdown file
            if is_content_file(content_file):
                self.dir_structure[lang][section_dir][content_file] = True

    def create_html(self):
        if len(self.dir_structure.keys()) == 0:
            self.make_dir_structure()

        os.mkdir(self.html_dir)
        for lang in self.dir_structure:
            export_lang_dir = path.join(self.export_docs_dir, lang)
            html_lang_dir = path.join(self.html_dir, lang)
            os.mkdir(html_lang_dir)
            self.create_html_lang(lang, export_lang_dir, html_lang_dir)

    def create_html_lang(self, lang, export_dir, html_dir):
        outer_menu_data = self.outer_menu_data(lang)
        for section_dir in self.dir_structure[lang]:
            export_section_dir = path.join(export_dir, section_dir)
            html_section_dir = path.join(html_dir,
                                         remove_numeric_prefix(section_dir))
            os.mkdir(html_section_dir)
            self.create_html_content(lang, section_dir, export_section_dir, html_section_dir, outer_menu_data)

    def create_html_content(self, lang, section_dir, export_dir, html_dir, outer_menu_data):
        inner_menu_data = self.inner_menu_data(lang, section_dir)
        outer_menu_html = self.outer_menu_for_section(lang, section_dir, outer_menu_data)
        for content_file in self.dir_structure[lang][section_dir]:
            inner_menu_html = self.inner_menu_for_content(lang, content_file, inner_menu_data)
            export_content_file = path.join(export_dir, content_file)
            # replace .md with .html
            html_content_file = path.join(
                html_dir, export_md_file_to_name(content_file)
            ) + '.html'
            self.convert_md_to_html(export_content_file, html_content_file, outer_menu_html, inner_menu_html)

    def convert_md_to_html(self, mdfile, htmlfile, outer_menu_html, inner_menu_html):
        with open(mdfile, 'r') as md:
            mdcontent = md.read()
        htmlcontent = markdown(mdcontent, extensions=['footnotes', 'sane_lists', 'toc'])
        with open(htmlfile, 'w') as html:
            html.write(outer_menu_html)
            html.write(inner_menu_html)
            html.write(htmlcontent)

    def outer_menu_data(self, lang):
        """ return something like
        {
            "01_standard": {"link": "/r/.../standard/main", "title": "Main"},
            "02_definitions": {"link": "/r/.../definitions/part1", "title": "Definitions"},
            "03_schemas": {"link": "/r/.../schemas/part1", "title": "Schemas"},
            "04_merging": {"link": "/r/.../merging/part1", "title": "Merging"},
        } """
        menu_data = {}
        for section_dir in sorted(self.dir_structure[lang].keys()):
            first_content_file = sorted(self.dir_structure[lang][section_dir])[0]
            url_path = export_path_to_url_path(section_dir, first_content_file)
            menu_data[section_dir] = {
                "link": reverse('standard', args=(self.release, lang, url_path)),
                "title": humanise(remove_numeric_prefix(section_dir)),
            }
        return menu_data

    def outer_menu_for_section(self, lang, active_section, menu_data):
        """ returns a string containing the HTML for the top level menu/tabs
        for the docs in a language.  Maybe use template render?

        Something like:

        <ul class="nav nav-tabs">
            <li class="active"><a href="/r/.../standard/main">Main</a></li>
            <li><a href="/r/.../section2/part1">Definitions</a></li>
            <li><a href="/r/.../section3/part1">Schemas</a></li>
            <li><a href="/r/.../section4/part1">Merging</a></li>
        </ul>
        """
        menu = ['<ul class="nav nav-tabs">']
        for section in sorted(self.dir_structure[lang].keys()):
            link_info = menu_data[section]
            if section == active_section:
                menu.append('<li class="active">')
            else:
                menu.append('<li>')
            menu.append('<a href="%(link)s">%(title)s</a></li>' % link_info)
        menu.append('</ul>')
        return '\n'.join(menu)

    def inner_menu_data(self, lang, section_dir):
        """ return something like
        {
            "01_intro.md": {"link": "/r/.../standard/intro", "title": "Intro"},
            "02_data.md": {"link": "/r/.../standard/data", "title": "Data"},
            "03_further_info.md": {"link": "/r/.../standard/further_info", "title": "Further Info"},
        } """
        menu_data = {}
        for content_file in sorted(self.dir_structure[lang][section_dir].keys()):
            url_path = export_path_to_url_path(section_dir, content_file)
            menu_data[content_file] = {
                "link": reverse('standard', args=(self.release, lang, url_path)),
                "title": humanise(export_md_file_to_name(content_file)),
            }
        return menu_data

    def inner_menu_for_content(self, lang, active_content_file, menu_data):
        """ returns a string containing the HTML for the 2nd level menu/tabs
        for the docs in a language and section """
        menu = ['<ul class="nav nav-tabs">']
        for content_file in sorted(menu_data.keys()):
            link_info = menu_data[content_file]
            if content_file == active_content_file:
                menu.append('<li class="active">')
            else:
                menu.append('<li>')
            menu.append('<a href="%(link)s">%(title)s</a></li>' % link_info)
        menu.append('</ul>')
        return '\n'.join(menu)
