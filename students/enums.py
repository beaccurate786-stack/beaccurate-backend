from django.db import models


class Department(models.TextChoices):
    COMPUTER = 'computer', 'Computer'
    EC = 'ec', 'EC'


class Semester(models.IntegerChoices):
    ONE = 1, '1'
    TWO = 2, '2'
    THREE = 3, '3'
    FOUR = 4, '4'
    FIVE = 5, '5'
    SIX = 6, '6'


class Division(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'


class StudentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
