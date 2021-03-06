from __future__ import unicode_literals

import codecs
from datetime import datetime
import os
from os import path
import re
import shutil
import subprocess
import urllib
from django.conf import settings
from django.http import Http404
from django.template.loader import render_to_string

from git import Repo, BadObject
from markdown import markdown
from pyquery import PyQuery
import unicodecsv as csv

WORKING_DIR = path.abspath(path.join(path.dirname(__file__), '..', 'working'))
REPO_DIR = path.join(WORKING_DIR, 'repo')
EXPORT_ROOT = path.join(WORKING_DIR, 'exports')
HTML_ROOT = path.join(WORKING_DIR, 'html')

# 2 digit and underscore prefix
NUMERIC_PREFIX_RE = re.compile(r'^\d\d_')
# it could be "en" or "en-gb" or "en_gb"
LANG_CODE_RE = re.compile(r'^[a-z]{2}([-_][a-z]{2,5})?$')
# check for full length SHA
GIT_SHA_RE = re.compile(r'^[0-9a-fA-F]{40}$')
# look for url encoded {%...%}
TEMPLATETAG_RE = re.compile(r'%7B%%20.*?%20%%7D')  # .*? is non-greedy


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
    repo = StandardsRepo()
    commit = repo.standardise_commit_name(release)
    repo.export_commit(commit)
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


def get_exported_languages(release):
    """ find all 2 letter language codes in directory """
    # TODO: should we support en_gb etc? -> drop len == 2 check
    # but we might want the exported languages elsewhere ...
    repo = StandardsRepo()
    commit = repo.standardise_commit_name(release)
    repo.export_commit(commit)
    export_docs_root = get_commit_export_docs_dir(commit)
    return [d for d in os.listdir(export_docs_root)
            if LANG_CODE_RE.match(d) and path.isdir(path.join(export_docs_root, d))]


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

        # now convert to a commit ID
        try:
            return self.repo.commit(commit).hexsha
        except BadObject:
            raise Http404

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
        return self.get_contents(json_path)

    def get_file_contents(self, commit, file_name):
        export_dir = self.export_commit(commit)
        file_path = path.join(export_dir, file_name)
        return self.get_contents(file_path)

    def get_contents(self, file_path):
        try:
            with open(file_path, 'r') as f:
                file_contents = f.read()
            return file_contents
        except IOError:
            return ""

    def delete_export(self, commit):
        export_dir = get_commit_export_dir(commit)
        if path.exists(export_dir):
            shutil.rmtree(export_dir)


class HTMLProducer(object):

    def __init__(self, release, std_commit):
        self.release = release
        self.std_commit = std_commit
        self.export_dir = get_commit_export_dir(std_commit)
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

    def make_dir_structure(self):
        self.dir_structure = {}
        for lang in get_exported_languages(self.std_commit):
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
            html_content_stub = path.join(
                html_dir, export_md_file_to_name(content_file)
            )
            self.convert_mdfile_to_htmlfile(export_content_file, html_content_stub, outer_menu_html, inner_menu_html)

    def convert_django_template_var(self, htmlstring):
        return htmlstring

    def extract_toc_to_html(self, pq_dom):
        toc = pq_dom(".toc")
        if not toc:
            return ''
        toc.find('ul').addClass('nav')
        toc_html = toc.outerHtml()
        pq_dom.remove(".toc")
        rendered_menu = render_to_string('main/sidemenu.html', {
            'toc': toc_html
        })
        return rendered_menu

    def insert_included_json(self, pq_dom):
        include_nodes = pq_dom.find(".include-json")
        for node in include_nodes.items():
            json_file = node.attr['data-src']
            if not json_file:
                continue
            json_path = path.join(self.export_dir, json_file)
            if not path.isfile(json_path):
                continue
            with open(json_path, 'r') as f:
                json_contents = f.read()
            node.html('<pre><code class="language-javascript">' + json_contents + '</code></pre>')

    def csv_to_html_table(self, csvreader, table_class):
        html = []
        if table_class:
            table_class += " side-scroll-table"
        else:
            table_class = "side-scroll-table"
        html.append('<table class="%s">' % table_class)
        for rownum, row in enumerate(csvreader):
            if rownum == 0:
                html.append('<thead><tr>')
                html.extend(['<th>' + column + '</th>' for column in row])
                html.append('</tr></thead><tbody>')
            else:
                html.append('<tr>')
                html.extend(['<td>' + column + '</td>' for column in row])
                html.append('</tr>')
        html.append('</tbody></table>')
        return ''.join(html)

    def insert_included_csv(self, pq_dom):
        include_nodes = pq_dom.find(".include-csv")
        for node in include_nodes.items():
            csv_file = node.attr['data-src']
            table_class = node.attr['data-table-class']
            if not csv_file:
                continue
            csv_path = path.join(self.export_dir, csv_file)
            if not path.isfile(csv_path):
                continue
            with open(csv_path, 'r') as f:
                csvreader = csv.reader(f)
                csv_contents = self.csv_to_html_table(csvreader, table_class)
            node.html(csv_contents)

    def repair_django_tags(self, htmlcontent):
        # URL encoded "{{ " and " }}"
        htmlcontent = htmlcontent.replace('%7B%7B%20', '{{ ')
        htmlcontent = htmlcontent.replace('%20%7D%7D', ' }}')
        # URL encoded {% ... %} is %7B%%20 ... %20%%7D
        last_match_end = 0
        newhtml = []
        for match in TEMPLATETAG_RE.finditer(htmlcontent):
            # add string up to last match and update last_match_end
            newhtml.append(htmlcontent[last_match_end:match.start()])
            last_match_end = match.end()
            # then url decode the matched text and add the string
            newhtml.append(urllib.unquote(match.group()))
        newhtml.append(htmlcontent[last_match_end:])
        htmlcontent = ''.join(newhtml)
        return htmlcontent

    def convert_md_to_html(self, mdcontent, outer_menu_html, inner_menu_html):
        htmlcontent = markdown(mdcontent, extensions=['footnotes', 'sane_lists', 'toc'])
        pq_dom = PyQuery(htmlcontent)
        rendered_menu = self.extract_toc_to_html(pq_dom)
        self.insert_included_json(pq_dom)
        self.insert_included_csv(pq_dom)
        htmlcontent = pq_dom.outerHtml()
        htmlcontent = self.repair_django_tags(htmlcontent)
        rendered_html = render_to_string('main/menu_content.html', {
            'outer_menu': outer_menu_html,
            'inner_menu': inner_menu_html,
            'html_content': htmlcontent,
        })
        return rendered_html, rendered_menu

    def convert_mdfile_to_htmlfile(self, mdfile, htmlfile_stub,
                                   outer_menu_html, inner_menu_html):
        with codecs.open(mdfile, encoding="utf8", mode='r') as md:
            mdcontent = md.read()

        rendered_html, rendered_menu = self.convert_md_to_html(
            mdcontent, outer_menu_html, inner_menu_html)

        with open(htmlfile_stub + '.html', mode='w') as html:
            html.write(rendered_html.encode('utf8'))
        with open(htmlfile_stub + '_menu.html', mode='w') as menu:
            menu.write(rendered_menu.encode('utf8'))

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
                # we do the template bit here, so the release name will change
                # when eg master and <commit_id> refer to the same commit, and
                # we only have one exported html file on disk.  This way the
                # release_name from the view context data will be used.
                "link": """{{% url "standard" release_name "{0}" "{1}" %}}""".format(lang, url_path),
                "title": humanise(remove_numeric_prefix(section_dir)),
            }
        return menu_data

    def outer_menu_for_section(self, lang, active_section, menu_data):
        """ returns a string containing the HTML for the top level menu/tabs
        for the docs in a language.  Maybe use template render?

        Something like:

            <li class="active"><a href="/r/.../standard/main">Main</a></li>
            <li><a href="/r/.../section2/part1">Definitions</a></li>
            <li><a href="/r/.../section3/part1">Schemas</a></li>
            <li><a href="/r/.../section4/part1">Merging</a></li>
        """
        menu = []
        for section in sorted(self.dir_structure[lang].keys()):
            link_info = menu_data[section]
            if section == active_section:
                li = '<li class="active">'
            else:
                li = '<li>'
            menu.append(li + '<a href="%(link)s">%(title)s</a></li>' % link_info)
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
                # see comment in outer_menu_data as to why
                "link": """{{% url "standard" release_name "{0}" "{1}" %}}""".format(lang, url_path),
                "title": humanise(export_md_file_to_name(content_file)),
            }
        return menu_data

    def inner_menu_for_content(self, lang, active_content_file, menu_data):
        """ returns a string containing the HTML for the 2nd level menu/tabs
        for the docs in a language and section """
        menu = []
        for content_file in sorted(menu_data.keys()):
            link_info = menu_data[content_file]
            if content_file == active_content_file:
                li = '<li class="active">'
            else:
                li = '<li>'
            menu.append(li + '<a href="%(link)s">%(title)s</a></li>' % link_info)
        return '\n'.join(menu)
