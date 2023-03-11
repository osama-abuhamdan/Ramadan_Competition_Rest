from rest_framework import serializers

import core.serializers
from core import models_helper, util
from core.models import Group, ContestPerson
from core.serializers import ContextFilteredPrimaryKeyRelatedField
from .models import *


class AutoSetContestSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        contest = util.get_current_contest_object(self.context["request"])
        validated_data["contest"] = contest
        return super().create(validated_data)


class SectionSerializer(AutoSetContestSerializer):
    class Meta:
        model = Section
        exclude = ('contest',)


class PointTemplateSerializer(AutoSetContestSerializer):
    section = ContextFilteredPrimaryKeyRelatedField(queryset=Section.objects)

    class Meta:
        model = PointTemplate
        depth = 2
        exclude = ('contest',)


class ListCreateGroupSerializer(AutoSetContestSerializer):
    members_count = serializers.ReadOnlyField()

    class Meta:
        model = Group
        exclude = ('contest', "announcements")
        read_only_fields = ('members_count',)


class RetrieveUpdateGroupSerializer(AutoSetContestSerializer):
    members_count = serializers.ReadOnlyField()
    admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('name', "admins", "members", "members_count")
        read_only_fields = ('members_count',)

    def get_admins(self, instance):
        objects = models_helper.get_group_admins(instance.id).values("id", "username", "first_name", "last_name")
        return core.serializers.PersonSerializer(objects, many=True, read_only=True,
                                                 fields=["id", "username", "first_name", "last_name"]).data

    def get_members(self, instance):
        objects = models_helper.get_group_members(instance.id).values("id", "username", "first_name", "last_name")
        return core.serializers.PersonSerializer(objects, many=True, read_only=True,
                                                 fields=["id", "username", "first_name", "last_name"]).data


class AddRemovePersonsToGroup(serializers.Serializer):
    persons = serializers.ListField()
    action = serializers.ChoiceField(choices=["add", "remove"], default="add")

    def create(self, validated_data):
        person_ids = validated_data["persons"]
        contest_id = util.get_current_contest_dict(self.context)["id"]
        group_id = validated_data["group_id"]
        contest_role = 1
        if validated_data["person_type"] == "admin":
            contest_role = 2
        if validated_data["action"] == "remove":
            ContestPerson.objects.filter(contest__id=contest_id, person__id__in=person_ids, group__id=group_id).delete()
        if validated_data["action"] == "add":
            defaults = dict(contest_role=contest_role, group_id=group_id)
            for person_id in person_ids:
                ContestPerson.objects.update_or_create(contest_id=contest_id, person_id=person_id,
                                                       defaults=defaults)
