from decimal import Decimal, ROUND_DOWN
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import serializers
from .models import Project, Deal, DealProject


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "fmv"]


class DealProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealProject
        fields = ["project", "tax_credit_transfer_rate"]


class DealSerializer(serializers.ModelSerializer):
    projects = DealProjectSerializer(many=True, write_only=True)

    class Meta:
        model = Deal
        fields = ["id", "name", "projects"]

    def create(self, validated_data):
        projects_data = validated_data.pop("projects")
        with transaction.atomic():
            deal = Deal.objects.create(**validated_data)

            # Using a list to gather all DealProject instances to be created
            deal_projects = []
            for project_data in projects_data:
                deal_projects.append(
                    DealProject(
                        deal=deal,
                        project=project_data["project"],
                        tax_credit_transfer_rate=project_data[
                            "tax_credit_transfer_rate"
                        ],
                    )
                )
            DealProject.objects.bulk_create(deal_projects)
        return deal

    def update(self, instance, validated_data):
        # Update the Deal fields
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        # Get existing DealProject relationships
        existing_projects = {dp.project.id: dp for dp in instance.dealproject_set.all()}

        # Update or create DealProject relationships
        projects_data = validated_data.get("projects", [])
        for project_data in projects_data:
            project_id = project_data["project"].id

            tax_credit_transfer_rate = project_data["tax_credit_transfer_rate"]

            if project_id in existing_projects:
                # Update existing DealProject
                deal_project = existing_projects[project_id]
                deal_project.tax_credit_transfer_rate = tax_credit_transfer_rate
                deal_project.save()
            else:
                # Create new DealProject relationship
                project = get_object_or_404(Project, id=project_id)
                DealProject.objects.create(
                    deal=instance,
                    project=project,
                    tax_credit_transfer_rate=tax_credit_transfer_rate,
                )

        # Handle removal of projects not included in the update
        for existing_project_id in existing_projects:
            if not any(
                project["project"].id == existing_project_id
                for project in projects_data
            ):
                existing_projects[existing_project_id].delete()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        projects = instance.dealproject_set.all()
        data["projects"] = [
            {
                "project": project.project.name,
                "tax_credit_transfer_rate": project.tax_credit_transfer_rate,
                "tax_credit_transfer_amount": (
                    project.project.fmv
                    * Decimal(0.3)
                    * project.tax_credit_transfer_rate
                ).quantize(Decimal("0.01"), rounding=ROUND_DOWN),
            }
            for project in projects
        ]
        return data


class DealListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="project.name")
    fmv = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="project.fmv"
    )
    tax_credit_transfer_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2
    )

    class Meta:
        model = DealProject
        fields = [
            "id",
            "name",
            "fmv",
            "tax_credit_transfer_rate",
            "tax_credit_transfer_amount",
        ]
