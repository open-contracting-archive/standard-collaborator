from django_assets import Bundle, register
js = Bundle('bower_components/jquery/dist/jquery.js',
            filters='rjsmin',
            output='js/site.js')
css = Bundle('bower_components/bootstrap/dist/css/bootstrap.css',
             filters='cssmin',
             output='css/site.css')
register('css_all', css)
register('js_all', js)
