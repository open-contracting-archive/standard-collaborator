from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from main.standardscache import StandardsRepo, HTMLProducer


class Command(BaseCommand):
    args = '<tag>'
    help = 'test the standards cache thing'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('args must be %s' % self.args)

        release = args[0]

        repo = StandardsRepo()
        repo.export_commit(release, force=True)
        std_commit = repo.standardise_commit_name(release)

        html_prod = HTMLProducer(release, std_commit)
        html_prod.delete_html_dir()
        html_prod.get_html_dir()
