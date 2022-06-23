from applications.reports.models.monthly import MonthlyReport


def get_reports_queryset(user):
    return MonthlyReport.objects.filter(tenant=user.tenant)
