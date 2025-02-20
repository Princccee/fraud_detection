from django.db import models
import datetime as dt

class InsuranceData(models.Model):
    policy_no = models.IntegerField()
    assured_age = models.IntegerField()
    nominee_relation = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    policy_sum_assured = models.IntegerField()
    premium = models.FloatField()
    premium_payment_mode = models.CharField(max_length=50)
    annual_income = models.IntegerField()
    holder_marital_status = models.CharField(max_length=50)
    indiv_requirement_flag = models.CharField(max_length=10)
    policy_term = models.IntegerField()
    policy_payment_term = models.IntegerField()
    # correspondence_city = models.CharField(max_length=100)
    # correspondence_state = models.CharField(max_length=100)
    # correspondence_postcode = models.CharField(max_length=20)
    product_type = models.CharField(max_length=100)
    channel = models.CharField(max_length=100)
    bank_code = models.FloatField(null=True, blank=True)

    policy_risk_commencement_date = models.DateTimeField(auto_now_add=False)
    date_of_death = models.DateTimeField(auto_now_add=False)
    intimation_date =  models.DateTimeField(auto_now_add=False)
    
    status = models.CharField(max_length=100)
    sub_status = models.CharField(max_length=100)
    # fraud_category = models.CharField(max_length=100)

    def __str__(self):
        return f"Policy No: {self.dummy_policy_no}"
