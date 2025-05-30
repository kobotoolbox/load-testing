import mimetypes
import os
import random
import string
import time
import uuid

from requests.exceptions import RequestException
from requests_toolbelt.multipart.encoder import (
    MultipartEncoder,
    MultipartEncoderMonitor,
)

from constants import PROJECT_UID, VERSION_UID, FORM_UUID, ASSETS_DIR
from utils.connection import authenticate_request, add_auth_headers
from utils.urls import get_kc_url

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


class OpenRosaMixin:

    def task_submit_data(
        self,
        with_attachments: bool = False,
        with_digest: bool = False,
        slowness_factor: float = None,
    ):

        submission_uuid = uuid.uuid4().hex
        # Load and populate the XML template
        with open(os.path.join(ASSETS_DIR, 'submission.xml'), 'r') as f:
            xml_template = f.read()

        xml_content = (
            xml_template
            .replace('{{submission_uuid}}', submission_uuid)
            .replace('{{PROJECT_UID}}', PROJECT_UID)
            .replace('{{version_uid}}', VERSION_UID)
            .replace('{{form_uuid}}', FORM_UUID)
            .replace('{{text}}', self._get_random_text())
        )

        if not with_attachments:
            xml_content = xml_content.replace('{{images}}', '')
            fields = {
                'xml_submission_file': ('submission.xml', xml_content, 'text/xml')
            }
            self._post_with_retry(
                get_kc_url('/submission'), fields, with_digest, slowness_factor
            )
        else:
            files = self._get_attachment_files()
            groups = self._group_files_from_upload(files)
            xml_content = self._inject_images_in_xml(files, xml_content)
            print(xml_content)

            # Submit each group with retry logic
            for i, group in enumerate(groups, start=1):
                print(f'[Chunk {i}/{len(groups)}] Uploading {len(group)} files...')
                fields = {
                    'xml_submission_file': ('submission.xml', xml_content, 'text/xml')
                }
                if with_attachments:
                    for j, file in enumerate(group):
                        fields[f'image{j}'] = (
                            file['name'], file['content'], file['mimetype']
                        )

                self._post_with_retry(
                    get_kc_url('/submission'), fields, with_digest, slowness_factor
                )

    @staticmethod
    def _get_attachment_files():
        files = []
        for filename in sorted(os.listdir(ASSETS_DIR)):
            path = os.path.join(ASSETS_DIR, filename)
            if filename in ['submission.xml', 'form.xlsx']:
                continue
            mimetype, _ = mimetypes.guess_type(path)
            if not mimetype:
                continue

            with open(path, 'rb') as f:
                content = f.read()
                files.append({
                    'name': filename,
                    'content': content,
                    'size': len(content),
                    'mimetype': mimetype,
                })

        random.shuffle(files)
        return files

    @staticmethod
    def _get_random_text():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=20))

    @staticmethod
    def _group_files_from_upload(files: list[dict]) -> list[list[dict]]:
        # Split files into groups not exceeding MAX_UPLOAD_SIZE
        current_group = []
        current_size = 0
        groups = []

        for file in files:
            if current_size + file['size'] > MAX_UPLOAD_SIZE:
                groups.append(current_group)
                current_group = []
                current_size = 0
            current_group.append(file)
            current_size += file['size']

        if current_group:
            groups.append(current_group)

        return groups

    @staticmethod
    def _inject_images_in_xml(files, xml_content):
        file_xml_nodes = []
        for idx, file in enumerate(files):
            file_xml_nodes.append(f"<image{idx + 1}>{file['name']}</image{idx + 1}>")
        return xml_content.replace('{{images}}', ''.join(file_xml_nodes))

    def _post_with_retry(
        self,
        url: str,
        fields: dict,
        with_digest: bool,
        slowness_factor: float = None,
    ):
        intervals = [5] * 3 + [15] * 3 + [60] * 10  # Retry intervals in seconds
        for attempt, delay in enumerate(intervals, start=1):
            try:
                response = authenticate_request(
                    self.client.post,
                    url=url,
                    data=fields,
                    with_digest=with_digest,
                    slowness_factor=slowness_factor,
                )
                # response = requests.post(url, headers=add_auth_headers(headers), data=m)
                if response.status_code in (200, 201, 202):
                    print(f'[OK] Submission succeeded on attempt {attempt}.')
                    return
                else:
                    print(
                        f'[WARN] Attempt {attempt} failed: '
                        f'{response.status_code} - {response.text}'
                    )
            except RequestException as e:
                print(f'[ERROR] Attempt {attempt} raised exception: {str(e)}')

            print(f'Retrying in {delay} seconds...')
            time.sleep(delay)

        print('[FAIL] All retries failed. Submission permanently failed.')
