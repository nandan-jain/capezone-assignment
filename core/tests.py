from decimal import Decimal, ROUND_HALF_UP
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Project, Deal, DealProject


class ProjectAPITest(APITestCase):
    def test_create_project(self):
        url = reverse("project-list")
        data = {"name": "Project A", "fmv": "100000.00"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, "Project A")

    def test_list_projects(self):
        Project.objects.create(name="Project A", fmv="100000.00")
        url = reverse("project-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class DealAPITest(APITestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="Project A", fmv="100000.00")
        self.project2 = Project.objects.create(name="Project B", fmv="200000.00")

    def test_create_deal_with_projects(self):
        url = reverse("deal-list")
        data = {
            "name": "Deal 1",
            "projects": [
                {"project": self.project1.id, "tax_credit_transfer_rate": "0.85"},
                {"project": self.project2.id, "tax_credit_transfer_rate": "0.90"},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Deal.objects.count(), 1)
        self.assertEqual(DealProject.objects.count(), 2)

    def test_edit_deal_add_project(self):
        deal = Deal.objects.create(name="Deal 1")
        DealProject.objects.create(
            deal=deal, project=self.project1, tax_credit_transfer_rate="0.85"
        )

        url = reverse("deal-detail", kwargs={"pk": deal.id})
        data = {
            "name": "Deal 1 Updated",
            "projects": [
                {"project": self.project1.id, "tax_credit_transfer_rate": "0.85"},
                {"project": self.project2.id, "tax_credit_transfer_rate": "0.90"},
            ],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DealProject.objects.count(), 2)

    def test_remove_project_from_deal(self):
        deal = Deal.objects.create(name="Deal 1")
        DealProject.objects.create(
            deal=deal, project=self.project1, tax_credit_transfer_rate="0.85"
        )
        DealProject.objects.create(
            deal=deal, project=self.project2, tax_credit_transfer_rate="0.90"
        )

        url = reverse("deal-detail", kwargs={"pk": deal.id})
        data = {
            "name": "Deal 1 Updated",
            "projects": [
                {"project": self.project1.id, "tax_credit_transfer_rate": "0.85"}
            ],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DealProject.objects.count(), 1)

    def test_tax_credit_calculation(self):
        deal = Deal.objects.create(name="Deal 1")
        DealProject.objects.create(
            deal=deal, project=self.project1, tax_credit_transfer_rate=Decimal("0.85")
        )
        DealProject.objects.create(
            deal=deal, project=self.project2, tax_credit_transfer_rate=Decimal("0.90")
        )

        url = reverse("deal-tax-credits", kwargs={"pk": deal.id})
        response = self.client.get(url, format="json")

        # Expected total tax credit calculation using Decimal
        expected_total_tax_credit = (Decimal(100000) * Decimal(0.85) * Decimal(0.3)) + (
            Decimal(200000) * Decimal(0.90) * Decimal(0.3)
        )

        # Rounding both values to two decimal places
        rounded_response_total = Decimal(
            response.data["total_tax_credit_transfer_amount"]
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        rounded_expected_total = expected_total_tax_credit.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Compare the rounded values
        self.assertEqual(rounded_response_total, rounded_expected_total)

        # Ensure the number of projects is correct
        self.assertEqual(len(response.data["projects"]), 2)
