from os import path
import sys

from dye.tasklib import env
from dye.tasklib.django import _manage_py
from dye.tasklib.util import _create_dir_if_not_exists, _check_call_wrapper


def post_deploy(environment):
    """ This function is called by the main deploy in dye/tasklib after
    all the other tasks are done.  So this is the place where you can
    add any custom tasks that your project requires, such as creating
    directories, setting permissions etc."""
    build_webassets()
    ensure_working_directory_and_repo_exist()
    # building webassets as root can change directory ownership, so we need to
    # correct it
    ensure_static_is_writable()
    copy_legacy_files_into_place()


def build_webassets():
    _manage_py(['assets', 'clean'])
    _manage_py(['assets', 'build'])


def ensure_static_is_writable():
    if env['environment'] in ('staging', 'production'):
        owner = 'apache'
        static_path = path.join(env['django_dir'], 'static')
        _check_call_wrapper(['chown', '-R', owner, static_path])


def ensure_working_directory_and_repo_exist():
    """We need to ensure we have a working directory to use, and have a clone
    of the standards repo
    """
    if env['environment'] in ('staging', 'production'):
        owner = 'apache'
    else:
        owner = None
    working_dir = path.join(env['django_dir'], 'working')
    exports_dir = path.join(working_dir, 'exports')
    html_dir = path.join(working_dir, 'html')
    repo_dir = path.join(working_dir, 'repo')
    _create_dir_if_not_exists(working_dir, owner=owner)
    _create_dir_if_not_exists(exports_dir, owner=owner)
    _create_dir_if_not_exists(html_dir, owner=owner)

    # and now delete the old exports and html directory contents in case we
    # need to redo the html
    _check_call_wrapper('rm -rf ' + exports_dir + '/* ' + html_dir + '/*', shell=True)

    # check if repo exists - if not do git clone
    if not path.exists(repo_dir):
        sys.path.append(env['django_settings_dir'])
        from settings import STANDARD_GITHUB_REPO
        github_repo = 'https://github.com/' + STANDARD_GITHUB_REPO
        _check_call_wrapper(['git', 'clone', github_repo, repo_dir])


def copy_legacy_files_into_place():
    """We will have a directory with copies of the old index.html files
    in it that can be copied into the relevant place in the directory
    structure.
    """
    # TODO
    pass
