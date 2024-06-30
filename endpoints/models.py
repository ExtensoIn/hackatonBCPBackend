from django.db import models
from django.utils.timezone import now


class Empresa(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    sector_code = models.IntegerField()
    co2_revenues = models.FloatField()
    water_revenues = models.FloatField()
    energy_revenues = models.FloatField()
    health_policy = models.BooleanField()
    supply_chain_policy = models.BooleanField()
    diversity_policy = models.BooleanField()
    salary_gap = models.FloatField()
    net_employment_creation = models.FloatField()
    board_independency_policy = models.BooleanField()
    board_diversity_policy = models.BooleanField()
    board_experience_policy = models.BooleanField()
    renewable_energy = models.FloatField()
    market_gap = models.FloatField()
    green_capex = models.BooleanField()
    date = models.DateField(default=now)
    esg_score = models.FloatField(null=True)
