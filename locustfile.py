"""
  X Save lots of submission entries (KoBoCAT)
  X Save long submission uploads (submission with lots of attachments) (KoBoCAT)
  X Export XLS with lots of submissions (> 100K) (KPI - Celery)
    Fetch data endpoint with sort field for an asset with lots of submissions (> 30 K) (KPI)
    Fetch assets endpoint for an account with lots of assets (> 100) (KPI)
"""
import uuid
import os
import time
import json
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from requests_toolbelt.multipart import encoder
from locust import HttpUser, task


FORM_UID = os.getenv("FORM_UID", "")
API_TOKEN = os.getenv("API_TOKEN", "")
KPI_SUBDOMAIN = os.getenv("KPI_SUBDOMAIN", "kf")
ENKETO_SUBDOMAIN = os.getenv("ENKETO_SUBDOMAIN", "ee")

SMALL_FILE = "assets/small.txt"
IMAGE_FILE = "assets/image.png"


class KoboUser(HttpUser):
    form_detail_url = f"/x/{FORM_UID}"
    form_transform_url = f"/transform/xform/{FORM_UID}"
    check_connection_url = "/connection"
    form_submit_url = f"/submission/{FORM_UID}"

    @task(20)
    def collect_data_simple(self):        
        self._simulate_unnecessary_interactions()

        # Extract form enkeno ID and first input info
        form = self.client.post(self.form_transform_url)
        form_soup = self._form_response_to_soup(form)
        form_id = self._get_form_id(form_soup)
        first_input = form_soup.find("form").find("fieldset").find("fieldset").find("input")
        first_input_name = first_input["name"].split("/")[-1]
        first_input_value = first_input["value"]

        answer_xml = self._build_form_xml(form_id, first_input_name, first_input_value)
        
        resp = self.client.post(self.form_submit_url, files=dict(xml_submission_file=answer_xml))
    
    @task(10)
    def collect_file_upload(self):
        self._simulate_unnecessary_interactions()

        form = self.client.post(self.form_transform_url)

        form_soup = self._form_response_to_soup(form)
        form_id = self._get_form_id(form_soup)
        file_input = form_soup.find("form").find("input", {"type": "file"})
        file_input_name = file_input["name"].split("/")[-1]

        with open(SMALL_FILE, "rb") as file:
            file_name = os.path.basename(file.name)
            answer_xml = self._build_form_xml(form_id, file_input_name, file_name)

            resp = self.client.post(self.form_submit_url, files={"xml_submission_file": answer_xml, file_name: file})

    @task(10)
    def collect_many_file_uploads(self):
        """ Simulate a slow connection with larger file """
        self._simulate_unnecessary_interactions()

        form = self.client.post(self.form_transform_url)

        form_soup = self._form_response_to_soup(form)
        form_id = self._get_form_id(form_soup)
        file_input = form_soup.find("form").find("input", {"type": "file"})
        file_input_name = file_input["name"].split("/")[-1]

        with open(IMAGE_FILE, "rb") as file:
            file_name = os.path.basename(file.name)
            answer_xml = self._build_form_xml(form_id, file_input_name, file_name)

            def my_callback(monitor):
                time.sleep(0.1)

            e = encoder.MultipartEncoder(
                fields={
                    'xml_submission_file': ('xml_submission_file', answer_xml, 'text/xml'),
                    file_name: (file_name, file, 'image/png')}
                )
            m = encoder.MultipartEncoderMonitor(e, my_callback)

            resp = self.client.post(self.form_submit_url, data=m, headers={'Content-Type': m.content_type})

    @task(2)
    def export_submissions_xls(self):
        """
        Request an export, wait for it's completion.
        Waiting for celery will make this task run a long time.
        """
        form = self.client.post(self.form_transform_url)
        form_soup = self._form_response_to_soup(form)
        form_id = self._get_form_id(form_soup)
        
        url = f"/api/v2/assets/{form_id}/exports/"
        data = {
            "fields_from_all_versions": True,
            "fields": [],
            "group_sep": "/",
            "hierarchy_in_labels": False,
            "lang": "_default",
            "multiple_select": "both",
            "type": "xls",
            "xls_types_as_text": False,
            "include_media_url": True
        }
        headers = {
            'Authorization': 'Token ' + API_TOKEN,
            "Accept": "application/json",
            "Host": self._get_kpi_url(),
        }
        resp = self.client.post(url, json=data, headers=headers)
        export_uid = resp.json().get("uid")

        # Wait for completion
        export_url = f"{url}{export_uid}/"
        status = "processing"
        i = 0
        while status == "processing":
            time.sleep(2)
            with self.client.get(export_url, headers=headers, name=f"{url}[export_id]/", catch_response=True) as resp:
                status = resp.json().get("status")
                i += 1
                if i > 15:
                    resp.failure("took too long to generate xls file")
                if status not in ["complete", "processing"]:
                    raise resp.failure("xls export failed")
    
    @task(1)
    def delete_all_submissions(self):
        """ Important to keep the test consistent by preventing data building up """
        form = self.client.post(self.form_transform_url)
        form_soup = self._form_response_to_soup(form)
        form_id = self._get_form_id(form_soup)
        url = f"/api/v2/assets/{form_id}/data/bulk/"
        data = {"payload": json.dumps({"confirm": True})}
        headers = {
            'Authorization': 'Token ' + API_TOKEN,
            "Accept": "application/json",
            "Host": self._get_kpi_url(),
        }
        resp = self.client.delete(url, data=data, headers=headers)
    
    def _get_kpi_url(self):
        return urlparse(self.client.base_url).netloc.replace(ENKETO_SUBDOMAIN, KPI_SUBDOMAIN)

    def _get_form_id(self, form_soup):
        return form_soup.find("form")["data-form-id"]

    def _simulate_unnecessary_interactions(self):
        """
        Real users do this, so we should too to simulate user load.
        They don't effect anything other than putting on minor server load.
        """
        self.client.get(self.form_detail_url)
        self.client.get(self.check_connection_url)

    def _form_response_to_soup(self, response):
        """Parse response json using BeautifulSoup"""
        return BeautifulSoup(response.json()["form"], features="html.parser")

    def _build_form_xml(self, form_id, name, value) -> bytes:
        """ Build submission xml file with specified name/value """
        root = ET.Element(form_id, id=form_id)
        formhub = ET.SubElement(root, "formhub")
        ET.SubElement(formhub, "uuid").text = uuid.uuid4().hex

        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        ET.SubElement(root, "start").text = now
        ET.SubElement(root, "end").text = now

        ET.SubElement(root, name).text = value

        return ET.tostring(ET.ElementTree(root).getroot())
