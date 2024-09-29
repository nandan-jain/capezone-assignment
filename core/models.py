from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    name = models.CharField(max_length=100)
    fmv = models.DecimalField(max_digits=10, decimal_places=2)  # Fair Market Value


class Deal(models.Model):
    name = models.CharField(max_length=100, unique=True)
    projects = models.ManyToManyField(Project, through="DealProject")


class DealProject(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tax_credit_transfer_rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(1))],
    )
