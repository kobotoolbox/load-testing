import uuid
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET

from locust import HttpUser, task

def build_form_xml(form_id):
    root = ET.Element(form_id, id=form_id)
    formhub = ET.SubElement(root, "formhub")
    ET.SubElement(formhub, "uuid").text = uuid.uuid4().hex
    return ET.ElementTree(root)

        

class HelloWorldUser(HttpUser):
    @task
    def collect_data(self):
        form_uid = "zWvTXwxF"
        
        url = f"/x/{form_uid}"
        resp = self.client.get(url)

        form = self.client.post(f"/transform/xform/{form_uid}")
        form_soup = BeautifulSoup(form.json()["form"])
        form_id = form_soup.find("form")["data-form-id"]

        answer_xml = build_form_xml(form_id)
        
        self.client.get("/connection")
        url = f"/submission/{form_uid}"

