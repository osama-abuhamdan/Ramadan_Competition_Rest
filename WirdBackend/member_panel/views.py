from rest_framework import viewsets

from admin_panel.models import ContestCriterion, Section
from admin_panel.serializers import ContestPolymorphicCriterionSerializer, SectionSerializer
from core import util_methods
from core.permissions import IsContestMember
from core.util_classes import CustomPermissionsMixin
from core.util_methods import get_current_contest_person
from member_panel.models import PointRecord
from member_panel.serializers import PolymorphicPointRecordSerializer


class MemberPointRecordViewSet(CustomPermissionsMixin, viewsets.ModelViewSet):
    member_allowed_methods = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
    serializer_class = PolymorphicPointRecordSerializer

    def get_queryset(self):
        person = get_current_contest_person(self.request)
        date = self.kwargs.get("date")
        return PointRecord.objects.filter(person__id=person.id, record_date=date)


class ContestCriteriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContestPolymorphicCriterionSerializer
    permission_classes = [IsContestMember]

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return ContestCriterion.objects.filter(contest=contest)


class ContestSectionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [IsContestMember]

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return Section.objects.filter(contest=contest)
