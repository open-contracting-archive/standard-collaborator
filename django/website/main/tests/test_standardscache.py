from __future__ import unicode_literals

import pytest
assert pytest is not None  # suppress warning

from pyquery import PyQuery
from main.standardscache import HTMLProducer


def create_htmlproducer():
    return HTMLProducer('fakerelease', 'fakecommit')


def create_htmlproducer_with_test_dir_structure():
    hp = create_htmlproducer()
    hp.dir_structure = {
        'en': {
            "01_intro": {
                "01_index.md": True,
            },
            "02_main": {
                "01_why.md": True,
                "02_how.md": True,
            }
        }
    }
    return hp


def test_outer_menu_data():
    hp = create_htmlproducer_with_test_dir_structure()
    menu_data = hp.outer_menu_data("en")
    assert menu_data == {
        "01_intro": {
            "link": '{% url "standard" release_name "en" "intro/index" %}',
            "title": "Intro"
        },
        "02_main": {
            "link": '{% url "standard" release_name "en" "main/why" %}',
            "title": "Main"
        },
    }


def test_outer_menu_for_section():
    hp = create_htmlproducer_with_test_dir_structure()
    menu_data = hp.outer_menu_data("en")
    menu = hp.outer_menu_for_section("en", "02_main", menu_data)
    assert menu == """<li><a href="{% url "standard" release_name "en" "intro/index" %}">Intro</a></li>
<li class="active"><a href="{% url "standard" release_name "en" "main/why" %}">Main</a></li>"""


def test_inner_menu_data():
    hp = create_htmlproducer_with_test_dir_structure()
    menu_data = hp.inner_menu_data("en", "02_main")
    assert menu_data == {
        "01_why.md": {
            "link": '{% url "standard" release_name "en" "main/why" %}',
            "title": "Why"
        },
        "02_how.md": {
            "link": '{% url "standard" release_name "en" "main/how" %}',
            "title": "How"
        },
    }


def test_inner_menu_for_content():
    hp = create_htmlproducer_with_test_dir_structure()
    menu_data = hp.inner_menu_data("en", "02_main")
    menu = hp.inner_menu_for_content("en", "02_how.md", menu_data)
    assert menu == """<li><a href="{% url "standard" release_name "en" "main/why" %}">Why</a></li>
<li class="active"><a href="{% url "standard" release_name "en" "main/how" %}">How</a></li>"""


def test_django_templatevar_conversion():
    hp = create_htmlproducer()
    pre_html = """<div class="something">
<div class="test"></div>
<a href="{{ STATIC_URL }}docson/widget.js">text</a>
</div>"""
    pq_dom = PyQuery(pre_html)
    post_pq_html = pq_dom.outerHtml()
    repaired_html = hp.repair_django_tags(post_pq_html)
    assert pre_html == repaired_html


def test_django_templatetag_url_conversion():
    hp = create_htmlproducer()
    pre_html = """<div class="something">
<div class="test"></div>
<a href="{% url 'schema' release_name 'release_package' %}">text</a>
</div>"""
    pq_dom = PyQuery(pre_html)
    post_pq_html = pq_dom.outerHtml()
    repaired_html = hp.repair_django_tags(post_pq_html)
    assert pre_html == repaired_html
