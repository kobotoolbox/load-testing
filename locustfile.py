"""
  X Save lots of submission entries (KoBoCAT)
    Save long submission uploads (submission with lots of attachments) (KoBoCAT)
    Export XLS with lots of submissions (> 100K) (KPI - Celery)
    Fetch data endpoint with sort field for an asset with lots of submissions (> 30 K) (KPI)
    Fetch assets endpoint for an account with lots of assets (> 100) (KPI)
"""
import uuid
import os
from datetime import datetime
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET

from locust import HttpUser, task


FORM_UID = "ufCT4fdO"
SMALL_FILE = open("assets/small.txt", "r")
IMAGE_FILE = open("assets/image.png", "r")


class KoboUser(HttpUser):
    form_detail_url = f"/x/{FORM_UID}"
    form_transform_url = f"/transform/xform/{FORM_UID}"
    check_connection_url = "/connection"
    form_submit_url = f"/submission/{FORM_UID}"

    @task
    def collect_data_simple(self):        
        self._simulate_unnecessary_interactions()

        # Extract form enkeno ID and first input info
        form = self.client.post(self.form_transform_url)
        form_soup = BeautifulSoup(form.json()["form"])
        form_id = self._get_form_id(form_soup)
        first_input = form_soup.find("form").find("fieldset").find("fieldset").find("input")
        first_input_name = first_input["name"].split("/")[-1]
        first_input_value = first_input["value"]

        answer_xml = self._build_form_xml(form_id, first_input_name, first_input_value)
        
        resp = self.client.post(self.form_submit_url, files=dict(xml_submission_file=answer_xml))
    
    @task
    def collect_file_upload(self):
        self._simulate_unnecessary_interactions()

        form = self.client.post(self.form_transform_url)

        form_soup = BeautifulSoup(form.json()["form"])
        form_id = self._get_form_id(form_soup)
        file_input = form_soup.find("form").find("input", {"type": "file"})
        file_input_name = file_input["name"].split("/")[-1]

        file = SMALL_FILE
        file_name = os.path.basename(file.name)
        answer_xml = self._build_form_xml(form_id, file_input_name, file_name)

        resp = self.client.post(self.form_submit_url, files={"xml_submission_file": answer_xml, file_name: file})
    
    def _get_form_id(self, form_soup):
        return form_soup.find("form")["data-form-id"]

    def _simulate_unnecessary_interactions(self):
        """
        Real users do this, so we should too to simulate user load.
        They don't effect anything other than putting on minor server load.
        """
        self.client.get(self.form_detail_url)
        self.client.get(self.check_connection_url)

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