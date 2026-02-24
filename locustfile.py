"""
  X Save lots of submission entries (OpenRosa)
  X Save long submission uploads (submission with lots of attachments) (OpenRosa)
  X Export XLS with lots of submissions (> 100K) (KPI - Celery)
    Fetch data endpoint with sort field for an asset with lots of submissions (> 30 K) (KPI)
    Fetch assets endpoint for an account with lots of assets (> 100) (KPI)
"""
import os

from locust import HttpUser, run_single_user, tag, task

from mixins.enketo import EnketoMixin
from mixins.openrosa import OpenRosaMixin
from mixins.kpi import KpiMixin


class KoboUser(EnketoMixin, KpiMixin, OpenRosaMixin, HttpUser):

    @task(20)
    @tag('all', 'enketo', 'simple', 'normal')
    def collect_data_simple(self):
        self.task_collect_data_simple()

    @task(10)
    @tag('all', 'enketo', 'attachments', 'normal')
    def collect_data_with_attachments(self):
        self.task_collect_data_with_attachments()

    @task(10)
    @tag('all', 'enketo', 'attachments', 'slow')
    def collect_data_with_attachments_on_slow_connection(self):
        self.task_collect_data_with_attachments_on_slow_connection()

    @task(2)
    @tag('all', 'kpi')
    def export_submissions_xls(self):
        self.task_export_submissions_xls()

    @task(2)
    @tag('all', 'kpi', 'sync_export')
    def sync_export_submissions_xlsx(self):
        self.task_sync_export_submissions_xlsx()

    @task(1)
    @tag('all', 'kpi')
    def delete_all_submissions(self):
        self.task_delete_all_submissions()

    @task(20)
    @tag('all', 'openrosa', 'attachments')
    def submit_data(self):
        self.task_submit_data(with_attachments=True)


if __name__ == '__main__':
    run_single_user(KoboUser)
