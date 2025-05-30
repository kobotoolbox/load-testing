from constants import ENKETO_FORM_UID

from utils.urls import get_enketo_url


class EnketoMixin:

    form_detail_url = f'/x/{ENKETO_FORM_UID}'
    form_transform_url = f'/transform/xform/hash/{ENKETO_FORM_UID}'
    check_connection_url = '/connection'
    form_submit_url = f'/submission/{ENKETO_FORM_UID}'

    def task_collect_data_simple(self):
        """Simulate a slow connection with a larger file"""
        self._simulate_unnecessary_interactions()
        self.task_submit_data(with_attachments=False, with_digest=True)

    def task_collect_data_with_attachments(self):
        """Simulate a slow connection with a larger file"""
        self._simulate_unnecessary_interactions()
        self.task_submit_data(with_attachments=True, with_digest=True)

    def task_collect_data_with_attachments_on_slow_connection(self):
        """Simulate a slow connection with a larger file"""
        self._simulate_unnecessary_interactions()
        self.task_submit_data(
            with_attachments=True, with_digest=True, slowness_factor=0.01
        )

    def _simulate_unnecessary_interactions(self):
        """
        Real users do this, so we should too to simulate users' load.
        They don't affect anything other than putting on minor server load.
        """
        self.client.get(get_enketo_url(self.form_detail_url))
        self.client.get(get_enketo_url(self.check_connection_url))
        self.client.post(get_enketo_url(self.form_transform_url))
