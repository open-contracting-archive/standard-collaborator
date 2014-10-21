from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from main.standardscache import StandardsRepo, HTMLProducer


class Command(BaseCommand):
    args = '<tag>'
    help = 'test the standards cache thing'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('args must be %s' % self.args)

        tag = args[0]

        repo = StandardsRepo()
        repo.git_pull()
        repo.export_commit(tag, force=True)
        tag = repo.convert_commit(tag)

        html_prod = HTMLProducer(tag)
        html_prod.create_html()
