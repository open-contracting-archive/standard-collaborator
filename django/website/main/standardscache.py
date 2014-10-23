from __future__ import unicode_literals

import os
from os import path
import re
import shutil
import subprocess

from django.conf import settings

from git import Repo
from markdown import markdown

from .models import LatestVersion

WORKING_DIR = path.abspath(path.join(path.dirname(__file__), '..', 'working'))
REPO_DIR = path.join(WORKING_DIR, 'repo')
EXPORT_ROOT = path.join(WORKING_DIR, 'exports')
HTML_ROOT = path.join(WORKING_DIR, 'html')


def get_commit_export_dir(commit):
    return path.join(EXPORT_ROOT, commit)


def get_commit_export_docs_dir(commit):
    return path.join(get_commit_export_dir(commit), settings.STANDARD_DOCS_PATH)


def get_commit_html_dir(commit):
    return path.join(HTML_ROOT, commit)


class StandardsRepo(object):

    def __init__(self):
        self.repo = Repo(REPO_DIR)

    def git_pull(self):
        subprocess.check_call(['git', 'pull'], cwd=REPO_DIR)
        # and update the latest tag
        latest_tag_name = self.get_ordered_tags()[0].name
        version_count = LatestVersion.objects.all().count()
        if version_count == 0:
            LatestVersion.objects.create(tag_name=latest_tag_name)
        else:
            latest_version = LatestVersion.objects.get()
            if latest_version.tag_name != latest_tag_name:
                latest_version.tag_name = latest_tag_name
                latest_version.save()

    def master_commit_id(self):
        """Return the hash of the last commit on master"""
        # this assumes that head is on master
        return self.repo.head.commit.hexsha

    def get_ordered_tags(self):
        tags = self.repo.tags
        sorted_tags = sorted(
            tags, key=lambda t: t.commit.committed_date, reverse=True)
        return sorted_tags

    def standardise_commit_name(self, commit):
        """ make sure we have a "standard" commit id to use elsewhere.

        For now - if the commit is "master" then we do a git pull to ensure
        we have the latest from git, and then convert it to the commit hash.
        """
        if commit == 'master':
            self.git_pull()
            return self.master_commit_id()
        else:
            # TODO: should we check commit exists?  Raise 404 if not?
            return commit

    def get_commit(self, commit):
        """Return a commit object with commit name, last modified date ..."""
        commit = self.standardise_commit_name(commit)
        # TODO: investigate when commit does not exist, decide how to handle it
        gitcommit = self.repo.commit(commit)
        # TODO: implement this
        # see template for fields required
        return gitcommit
        # return {}

    def export_commit(self, commit, force=False):
        commit = self.standardise_commit_name(commit)
        export_dir = get_commit_export_dir(commit)
        export_exists = path.exists(export_dir)
        if force and export_exists:
            shutil.rmtree(export_dir)
            export_exists = False
        if not export_exists:
            # command from http://stackoverflow.com/a/163769/3189
            subprocess.check_call(
                'git archive --prefix=%s/ %s | tar -x -C %s' %
                (commit, commit, EXPORT_ROOT),
                cwd=REPO_DIR, shell=True)
        return export_dir

    def delete_export(self, commit):
        export_dir = get_commit_export_dir(commit)
        if path.exists(export_dir):
            shutil.rmtree(export_dir)


class HTMLProducer(object):

    CONTENT_DIR_RE = re.compile(r'^\d\d_')

    def __init__(self, commit):
        self.commit = commit
        self.export_docs_dir = get_commit_export_docs_dir(commit)
        self.html_dir = get_commit_html_dir(commit)
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
        return [d for d in os.listdir(export_docs_root)
                if len(d) == 2 and path.isdir(path.join(export_docs_root, d))]

    def create_html(self):
        self.dir_structure = {}
        os.mkdir(self.html_dir)
        # TODO: do for: if: like other methods?
        for lang in self.get_exported_languages(self.export_docs_dir):
            self.dir_structure[lang] = {}
            export_lang_dir = path.join(self.export_docs_dir, lang)
            html_lang_dir = path.join(self.html_dir, lang)
            os.mkdir(html_lang_dir)
            self.create_html_lang(lang, export_lang_dir, html_lang_dir)

    def create_html_lang(self, lang, export_dir, html_dir):
        for content_dir in os.listdir(export_dir):
            # TODO: check isdir
            if self.CONTENT_DIR_RE.match(content_dir):
                self.dir_structure[lang][content_dir] = {}
                export_content_dir = path.join(export_dir, content_dir)
                # TODO: strip 01_
                html_content_dir = path.join(html_dir, content_dir)
                os.mkdir(html_content_dir)
                self.create_html_content(lang, content_dir, export_content_dir, html_content_dir)

    def create_html_content(self, lang, content_dir, export_dir, html_dir):
        for content_file in os.listdir(export_dir):
            # check for 01_ prefix and that it is a markdown file
            if self.CONTENT_DIR_RE.match(content_file) and content_file.endswith('.md'):
                self.dir_structure[lang][content_dir][content_file] = True
                export_content_file = path.join(export_dir, content_file)
                # TODO: strip 01_
                html_content_file = path.join(html_dir, content_file)[:-3] + '.html'
                self.convert_md_to_html(export_content_file, html_content_file)

    def convert_md_to_html(self, mdfile, htmlfile):
        with open(mdfile, 'r') as md:
            mdcontent = md.read()
        htmlcontent = markdown(mdcontent, extensions=['footnotes', 'sane_lists', 'toc'])
        with open(htmlfile, 'w') as html:
            html.write(htmlcontent)

    def top_level_menu(self, lang):
        """ returns a string containing the HTML for the top level menu/tabs
        for the docs in a language """
        # TODO: do something with self.dir_structure
        return ""

    def second_level_menu(self, lang, content_dir):
        """ returns a string containing the HTML for the 2nd level menu/tabs
        for the docs in a language and section """
        # TODO: do something with self.dir_structure
        return ""
