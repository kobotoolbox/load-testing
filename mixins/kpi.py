import json
import time

from constants import PROJECT_UID
from utils.connection import add_auth_headers
from utils.urls import get_kpi_url


class KpiMixin:

    def task_export_submissions_xls(self):
        """
        Request an export, wait for its completion.
        Waiting for celery will make this task run a long time.
        """

        url = get_kpi_url(f'/api/v2/assets/{PROJECT_UID}/exports/')
        data = {
            'fields_from_all_versions': True,
            'fields': [],
            'group_sep': '/',
            'hierarchy_in_labels': False,
            'lang': '_default',
            'multiple_select': 'both',
            'type': 'xls',
            'xls_types_as_text': False,
            'include_media_url': True,
        }
        headers = add_auth_headers({'Accept': 'application/json'})
        resp = self.client.post(url, json=data, headers=headers)
        export_uid = resp.json().get('uid')

        # Wait for completion
        export_url = f'{url}{export_uid}/'
        status = 'processing'
        i = 0
        while status == 'processing':
            time.sleep(2)
            with self.client.get(
                export_url,
                headers=headers,
                name=f'{url}[export_id]/',
                catch_response=True,
            ) as resp:
                status = resp.json().get('status')
                i += 1
                if i > 15:
                    resp.failure('took too long to generate xls file')
                if status not in ['complete', 'processing']:
                    raise resp.failure('xls export failed')

    def task_sync_export_submissions_xlsx(self):
        """
        Request a synchronous CSV export.
        """

        headers = add_auth_headers({'Accept': 'application/json'})
        url = get_kpi_url(f'/api/v2/assets/{PROJECT_UID}/export-settings/')
        resp = self.client.get(url, headers=headers)
        json_ = resp.json()
        if not json_.get('results', []):
            data = {
                'name': 'sync-export',
                'export_settings': {
                    'fields_from_all_versions': True,
                    'fields': [],
                    'group_sep': '/',
                    'hierarchy_in_labels': False,
                    'lang': '_default',
                    'multiple_select': 'both',
                    'type': 'xls',
                    'query': {},
                    'xls_types_as_text': False,
                    'include_media_url': True,
                },
            }

            resp = self.client.post(url, json=data, headers=headers)
            print(resp.content)
            sync_export = resp.json()
        else:
            sync_export = json_['results'][0]

        sync_export_url = sync_export['data_url_xlsx']
        self.client.get(sync_export_url, headers=headers)

    def task_delete_all_submissions(self):
        """Important to keep the test consistent by preventing data building up"""
        url = get_kpi_url(f'/api/v2/assets/{PROJECT_UID}/data/bulk/')
        data = {'payload': json.dumps({'confirm': True})}
        headers = add_auth_headers({'Accept': 'application/json'})
        self.client.delete(url, data=data, headers=headers)
