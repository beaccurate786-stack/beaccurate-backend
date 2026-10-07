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


class Batch(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'
    C = 'C', 'C'
    D = 'D', 'D'


class StudentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class Role(models.TextChoices):
    SUPER_ADMIN = 'Super Admin', 'Super Admin'
    HOD = 'HOD', 'HOD'
    MENTOR = 'Mentor', 'Mentor'
    STUDENT = 'Student', 'Student'


class Weekday(models.IntegerChoices):
    MONDAY = 0, 'Monday'
    TUESDAY = 1, 'Tuesday'
    WEDNESDAY = 2, 'Wednesday'
    THURSDAY = 3, 'Thursday'
    FRIDAY = 4, 'Friday'
    SATURDAY = 5, 'Saturday'
    SUNDAY = 6, 'Sunday'
