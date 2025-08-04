# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db.models import Q
# from lino.core.model import Model
# from lino.core.fields import ForeignKey
from lino.api import dd
from lino.core.roles import SiteAdmin


class Groupwise(dd.Model):

    class Meta:
        abstract = True

    if dd.is_installed("groups"):

        group = dd.ForeignKey("groups.Group", blank=True, null=True)

        def full_clean(self):
            if not self.group_id:
                self.group = self.get_default_group()
            super().full_clean()

        def get_default_group(self):
            return None

        def on_create(self, ar):
            # if not ar.is_obvious_field('group'):
            #     self.group = ar.get_user().current_group
            super().on_create(ar)
            if not self.group_id:
                self.group = ar.get_user().current_group

        @classmethod
        def get_request_queryset(cls, ar, **filter):
            # Show only rows that belong to a group of which I am a member or which
            # is public.
            qs = super().get_request_queryset(ar, **filter)
            user = ar.get_user()
            if user.is_anonymous:
                return qs
            if user.current_group is not None:
                qs = qs.filter(group=user.current_group)
            if user.user_type.has_required_roles([SiteAdmin]):
                return qs
            q1 = Q(group__private=False)
            q2 = Q(group__members__user=user)
            qs = qs.filter(q1 | q2).distinct()
            return qs

    else:

        group = dd.DummyField()
