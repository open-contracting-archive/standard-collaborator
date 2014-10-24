from __future__ import unicode_literals

import pytest
from os import path, pardir
from django.conf import settings
from main.views import StandardView, LatestView

sample_markdown = """
Paragraph. *Italic*, **bold**, `monospace`. Itemized lists
look like:

* this one
* that one
* the other one
"""
import factory


#def test_template_name_is_standard():
#    view = StandardView()
#    assert view.template_name == 'main/standard.html'


#def test_doc_path_is_base_dir_plus_STANDARD():
#    view = StandardView()
#    # STANDARD.md is in root folder which is two up from django/website
#    base_dir = path.abspath(path.join(settings.BASE_DIR, pardir, pardir))
#    assert view.doc_path == path.join(base_dir, 'STANDARD.md')


#@pytest.fixture
#def returned_html(tmpdir):
#    mdfile = tmpdir.join('testmarkdown.md')
#    mdfile.write(sample_markdown)
#    filepath = mdfile.strpath
#    return (StandardView().render_markdown(filepath), filepath)


#def test_render_file_returns_html_of_md_file(returned_html):
#    assert '<li>this one</li>' in returned_html[0]
#    assert '<strong>bold</strong>' in returned_html[0]


#def test_get_context_data_adds_rendered_html_from_doc_path(returned_html):
#    view = StandardView()
#    view.doc_path = returned_html[1]
#    context = view.get_context_data()
#    assert context.get('standard') == returned_html[0]
