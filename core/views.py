from decimal import Decimal
from django.db.models import F, DecimalField, ExpressionWrapper
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Deal, Project
from .serializers import DealSerializer, ProjectSerializer, DealListSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.order_by("id")
    serializer_class = ProjectSerializer


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.prefetch_related("dealproject_set__project")
    serializer_class = DealSerializer

    @action(detail=True, methods=["get"])
    def tax_credits(self, request, pk=None):
        """Retrieve total tax credit transfer amounts for a deal's projects."""
        deal = self.get_object()
        projects = deal.dealproject_set.annotate(
            tax_credit_transfer_amount=ExpressionWrapper(
                F("project__fmv") * Decimal(0.3) * F("tax_credit_transfer_rate"),
                output_field=DecimalField(),
            )
        )
        project_details = DealListSerializer(projects, many=True).data
        total_tax_credit = sum(
            Decimal(project["tax_credit_transfer_amount"])
            for project in project_details
        )

        return Response(
            {
                "total_tax_credit_transfer_amount": total_tax_credit,
                "projects": project_details,
            }
        )
