import functools
from collections.abc import Iterable

from django.core.cache import cache

from admin_panel.models import Group
from core.models import ContestPerson, Contest, Person


def cache_returned_values(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = hash(args) + hash(kwargs.values())
        results = cache.get(key)
        if results is None:
            results = func(*args, **kwargs)
            cache.set(key, results)
        return results

    return wrapper


@cache_returned_values
def get_contest_people(contest_id, contest_role=(1, 2, 3)):
    person_ids = ContestPerson.objects.filter(contest__id=contest_id, contest_role__in=contest_role) \
        .values_list('person__id', flat=True)
    return Person.objects.filter(id__in=person_ids)


@cache_returned_values
def get_person_contests_ids_and_roles(username, contest_role=(1, 2, 3)):
    if not isinstance(contest_role, Iterable):
        contest_role = tuple(contest_role)

    queryset = ContestPerson.objects.filter(person__username=username, contest_role__in=contest_role) \
        .values_list("contest__id", "contest_role")

    return queryset


@cache_returned_values
def get_person_contests_queryset(username, contest_role=(1, 2, 3)):
    contest_ids = get_person_contests_ids_and_roles(username, contest_role)
    contest_ids = [c[0] for c in contest_ids]
    return Contest.objects.filter(id__in=contest_ids)


def get_person_contests_managed(username):
    return get_person_contests_queryset(username, [2, 3])


@cache_returned_values
def get_person_managed_groups(username, contest_id):
    is_super_admin = ContestPerson.objects.filter(person__username=username, contest_id=contest_id,
                                                  contest_role=3).exists()
    if is_super_admin:
        return Group.objects.filter(contest__id=contest_id)
    else:
        group_ids = ContestPerson.objects.filter(person__username=username, contest_id=contest_id, contest_role=2,
                                                 group_role=2).values_list("group__id", flat=True)
        return Group.objects.filter(id__in=group_ids)


@cache_returned_values
def get_group_admins(group_id):
    person_ids = ContestPerson.objects.filter(group__id=group_id, contest_role__in=[2, 3], group_role=2) \
        .values('person__id')
    return Person.objects.filter(id__in=person_ids)


@cache_returned_values
def get_group_members(group_id):
    person_ids = ContestPerson.objects.filter(group__id=group_id, contest_role__in=[1, 2, 3], group_role=1) \
        .values('person_id')
    return Person.objects.filter(id__in=person_ids)