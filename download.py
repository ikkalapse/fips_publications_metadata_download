import re

import requests
import os
import json
from datetime import datetime
from pathlib import Path

# тип ОИС
from bs4 import BeautifulSoup

# тип ОИС
ois_type = 'PO'

# количество обрабатываемых страниц (если надо все, то посомтреть самостоеятельно)
pages_count = 5923

# инициализация каталога проекта
project_dir = os.path.join("downloads", datetime.today().strftime('%Y-%m-%d'))
# создание каталога
Path(project_dir).mkdir(parents=True, exist_ok=True)

urls = {'PO': 'https://www.fips.ru/publication-web/publications/PO?pageNumber=<PAGE_NUMBER>' + \
             '&tab=PO&inputDocNumber=&inputDocNumber_from=&inputDocNumber_to=' + \
             '&inputSelectOIS=IndustrialDesign%7C1&selectOISDocType=S%2CS2' + \
             '&_extendedFilter=on&registration_S=&registration_Po=&searchTextBox_applicationNumber=' + \
             '&searchTextBox_applicationNumber_from=&searchTextBox_applicationNumber_to=&publish_S=' + \
             '&publish_Po=&applicationFilling_S=&applicationFilling_Po=&searchTextBox_classifierMkpo=&searchSortSelect' \
             '=dtRegistration&searchSortDirection=false',
        'IZ': 'https://www.fips.ru/publication-web/publications/IZPM?pageNumber=<PAGE_NUMBER>&tab=IZPM&inputDocNumber' \
             '=&inputDocNumber_from=&inputDocNumber_to=&inputSelectOIS=Invention&selectOISDocType=C1%2CC2' \
             '&extendedFilter=true&_extendedFilter=on&registration_S=&registration_Po' \
             '=&searchTextBox_applicationNumber=&searchTextBox_applicationNumber_from' \
             '=&searchTextBox_applicationNumber_to=&publish_S=&publish_Po=&applicationFilling_S' \
             '=&applicationFilling_Po=&searchTextBox_classifierMpk=&selectFieldGroup_NoticeType=0' \
             '&selectFieldGroupValue_NoticeType=PD4A%2CPD4A%2CTC4A%2CTC4A%2CTE4A%2CTE4A%2CQZ4A-06%2CQZ4A-06%2CMZ4A' \
             '%2CMZ4A%2CMM4A%2CMM4A%2CMG4A%2CMG4A%2CMF4A-02%2CMF4A-02%2CMF4A-01%2CMF4A-01%2CMF4A%2CMF4A%2CNG4A%2CNG4A' \
             '%2CNF4A%2CNF4A%2CND4A-01%2CND4A-01%2CND4A%2CND4A%2CRH4A%2CRH4A%2CPC4A-01%2CPC4A-01%2CPC4A-02%2CPC4A-02' \
             '%2CQB4A-02%2CQB4A-02%2CQB4A-01%2CQB4A-01%2CQB4A%2CQB4A%2CQZ4A-011%2CQZ4A-011%2CQZ4A-012%2CQZ4A-012' \
             '%2CQZ4A-013%2CQZ4A-013%2CQZ4A-014%2CQZ4A-014%2CQZ4A-01%2CQZ4A-01%2CQZ4A-02%2CQZ4A-02%2CQC4A-011%2CQC4A' \
             '-011%2CQC4A-012%2CQC4A-012%2CQC4A-013%2CQC4A-013%2CQC4A-01%2CQC4A-01%2CQC4A-02%2CQC4A-02%2CQA4A%2CQA4A' \
             '%2CRL4A%2CRL4A%2CTK4A-01%2CTK4A-01%2CTK4A-02%2CTK4A-02%2CBF4A%2CBF4A%2CRZ4A%2CRZ4A%2CTH4A-02%2CTH4A-02' \
             '%2CTH4A-01%2CTH4A-01%2CTH4A%2CTH4A&searchSortSelect=dtPublish&searchSortDirection=true'}

# Сначала скачиваем все страницы
page_number = 1
while page_number <= pages_count:
    json_filename = os.path.join(project_dir, ois_type + '-page-' + str(page_number) + '.json')
    if os.path.exists(json_filename) is not True:
        print(page_number)
        patents = []
        page_url = urls[ois_type].replace("<PAGE_NUMBER>", str(page_number))
        soup = BeautifulSoup(requests.get(page_url).text, 'html.parser')
        for table in soup.select("td > table:has(tr.fline)"):
            patent = {}
            link = table.find('td', class_='nowrap').find("a")
            # Patent URL
            patent['url'] = "https://www.fips.ru" + link.get('href')
            # Patent registration number
            patent['reg_number'] = re.search(r"(\d+)", link.text).group(0)
            # etc
            spans = table.find_all('span', attrs={'class': 'mobileblock'})
            for span in spans:
                if "Регистрация" in span.text:
                    patent['reg_date'] = re.search(r"(\d{2}\.\d{2}\.\d{4})", span.text).group(0)
                if "Публикация" in span.text:
                    patent['pub_date'] = re.search(r"(\d{2}\.\d{2}\.\d{4})", span.text).group(0)
                if "Номер заявки" in span.text:
                    patent['app_number'] = re.search(r"(\d+)", span.text).group(0)
                if "Дата подачи заявки" in span.text:
                    patent['app_date'] = re.search(r"(\d{2}\.\d{2}\.\d{4})", span.text).group(0)
            patents.append(patent)
        # сохранение JSON-файла
        with open(json_filename, 'w+') as fp:
            json.dump(patents, fp)
    page_number = page_number + 1
