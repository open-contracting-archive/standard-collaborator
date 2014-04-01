from os import path, pardir
from django.conf import settings
from django.views.generic import TemplateView

from markdown import markdown


class StandardView(TemplateView):
    template_name = 'main/standard.html'
    doc_path = path.abspath(
        path.join(settings.BASE_DIR, pardir, pardir, 'STANDARD.md')
   )

    def render_markdown(self, mdfile):
        with open(mdfile, 'r') as f:
            return markdown(f.read())

    def get_context_data(self):
        context = super(StandardView, self).get_context_data()
        context.update({
            'standard': self.render_markdown(self.doc_path)
        })
        return context
