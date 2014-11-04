from __future__ import unicode_literals

from django_assets import Bundle, register

# JAVASCRIPT

js = Bundle('bower_components/jquery/dist/jquery.js',
            'bower_components/bootstrap/js/modal.js',
            'bower_components/bootstrap/js/tab.js',
            'bower_components/bootstrap/js/scrollspy.js',
            'bower_components/bootstrap/js/affix.js',
            'bower_components/prism/prism.js',
            filters='rjsmin',
            output='js/site.js')
register('js_all', js)


# CSS
standard_scss = Bundle('scss/standard.scss',
                       filters='pyscss',
                       output='css/standard.css',
                       depends='scss/*.scss')

css = Bundle('bower_components/bootstrap/dist/css/bootstrap.min.css',
             'bower_components/prism/prism.css',
             'css/open-iconic-bootstrap.css',
             standard_scss,
             output='css/site.css')
register('css_all', css)
