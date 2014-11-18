from __future__ import unicode_literals

from django_assets import Bundle, register

# JAVASCRIPT
main_js = Bundle('js/ocds_inline.js',
                 output='js/main.js')

js = Bundle('bower_components/jquery/dist/jquery.js',
            'bower_components/bootstrap/js/modal.js',
            'bower_components/bootstrap/js/tab.js',
            'bower_components/bootstrap/js/scrollspy.js',
            'bower_components/bootstrap/js/affix.js',
            'bower_components/prism/prism.js',
            main_js,
            filters='rjsmin',
            output='js/site.js')
register('js_all', js)


# CSS
main_scss = Bundle('scss/standard.scss',
                   depends=('scss/*.scss'),
                   filters='pyscss',
                   output='css/main.css')

css = Bundle('bower_components/bootstrap/dist/css/bootstrap.min.css',
             'bower_components/prism/prism.css',
             'css/open-iconic-bootstrap.css',
             main_scss,
             output='css/site.css')
register('css_all', css)
