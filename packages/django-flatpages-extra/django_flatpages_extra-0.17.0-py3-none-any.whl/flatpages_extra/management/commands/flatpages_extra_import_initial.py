import functools

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage as OriginalFlatPage
from django.core.management.base import BaseCommand
from django.utils.translation import ngettext

from flatpages_extra.models import FlatPage, Revision

UserPermission = User.user_permissions.through
GroupPermission = Group.permissions.through


class Command(BaseCommand):
    help = "Import data from contrib.flatpages (log entries, permissions, and initial revisions)"

    @staticmethod
    @functools.cache
    def get_new_permission(old_permission):
        ct = ContentType.objects.get_for_model(FlatPage, for_concrete_model=False)
        return Permission.objects.get(
            content_type=ct,
            codename=old_permission.codename,
            name=old_permission.name,
        )

    @staticmethod
    def get_original_publication_timestamps():
        """
        Return a dictionary of page id-> publication datetime based on the
        admin log entries, looking for ADDITION records.
        """
        addition_entries = LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(OriginalFlatPage),
            action_flag=ADDITION,
        )
        return {
            int(pk): timestamp  # LogEntry stores object_id as a string
            for pk, timestamp in addition_entries.values_list(
                "object_id", "action_time"
            )
        }

    def handle(self, **options):
        revisions = self.create_initial_revisions()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully imported {} revision",
                        "Successfully imported {} revisions",
                        len(revisions),
                    ).format(len(revisions))
                )
            )

        logentries = self.copy_logentries()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully copied {} log entry",
                        "Successfully copied {} log entries",
                        len(logentries),
                    ).format(len(logentries))
                )
            )

        custom_permissions = self.copy_custom_permissions()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully copied {} custom permission",
                        "Successfully copied {} custom permissions",
                        len(custom_permissions),
                    ).format(len(custom_permissions))
                )
            )

        user_permissions = self.copy_user_permissions()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully copied {} user permission",
                        "Successfully copied {} user permissions",
                        len(user_permissions),
                    ).format(len(user_permissions))
                )
            )

        group_permissions = self.copy_group_permissions()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully copied {} group permission",
                        "Successfully copied {} group permissions",
                        len(group_permissions),
                    ).format(len(group_permissions))
                )
            )

    def create_initial_revisions(self):
        known_publications = self.get_original_publication_timestamps()
        revisions = [
            page.make_initial_revision(
                published_on=known_publications.get(page.pk),
                save=False,
            )
            for page in FlatPage.objects.all()
        ]
        return Revision.objects.bulk_create(revisions)

    def copy_logentries(self):
        ct_original = ContentType.objects.get_for_model(OriginalFlatPage)
        ct_new = ContentType.objects.get_for_model(FlatPage, for_concrete_model=False)

        entries = LogEntry.objects.filter(content_type=ct_original)
        for e in entries:
            e.pk = None
            e._state.adding = True
            e.content_type = ct_new

        return LogEntry.objects.bulk_create(entries)

    def copy_custom_permissions(self):
        ct_original = ContentType.objects.get_for_model(OriginalFlatPage)
        ct_new = ContentType.objects.get_for_model(FlatPage, for_concrete_model=False)

        permissions = []
        for p in Permission.objects.filter(content_type=ct_original):
            _, created = Permission.objects.get_or_create(
                content_type=ct_new,
                name=p.name,
                codename=p.codename,
            )
            if created:
                permissions.append(p)

        return permissions

    def copy_user_permissions(self):
        ct_original = ContentType.objects.get_for_model(OriginalFlatPage)
        user_permissions = UserPermission.objects.filter(
            permission__content_type=ct_original
        ).select_related("permission")
        for p in user_permissions:
            p.pk = None
            p._state.adding = True
            p.permission = self.get_new_permission(p.permission)

        return UserPermission.objects.bulk_create(user_permissions)

    def copy_group_permissions(self):
        ct_original = ContentType.objects.get_for_model(OriginalFlatPage)
        group_permissions = GroupPermission.objects.filter(
            permission__content_type=ct_original
        ).select_related("permission")
        for p in group_permissions:
            p.pk = None
            p._state.adding = True
            p.permission = self.get_new_permission(p.permission)

        return GroupPermission.objects.bulk_create(group_permissions)
