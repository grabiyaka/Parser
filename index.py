from settings import requests, datetime, etree

from parsers.formdekor import *
from parsers.hitbeton import *
from parsers.technoOdis import *

def save_to_xml(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def send_xml_to_server(xml_data, filename):
    url = 'https://parser-for-grabiyaka.000webhostapp.com'  

    headers = {
        'Content-Type': 'application/xml',  
    }

    xml_str = xml_data

    files = {filename: (filename + '.xml', xml_str.encode('utf-8'))}
    response = requests.post(url, files=files, timeout=30)

    if response.status_code == 200:
        print("XML успешно отправлен на сервер!")

        print("Ответ сервера на " + filename + ":")
        print(response.text)
    else:
        print("Ошибка при отправке XML на сервер.")
        

def build_done_xml(array):
    output = '<?xml version="1.0" encoding="UTF-8"?>\n' \
             '<yml_catalog date="' + datetime.now().strftime('%Y-%m-%d %H:%M') + '">\n' \
             '    <shop>\n' \
             '        <name>Products</name>\n' \
             '        <company></company>\n' \
             '        <url></url>\n' \
             '        <platform>Opencart</platform>\n' \
             '        <version></version>\n' \
             '        <currencies>\n' \
             '            <currency id="USD" rate="1"/>\n' \
             '        </currencies>\n' \
             '        <categories>\n' \
             '            <category id="59"> Поліуретанові штампи</category>\n' \
             '            <category id="60"> Форми для 3d панелей</category>\n' \
             '        </categories>\n' \
             '        <offers>'
    for el in array: 
        output += str(el).replace('&', '&quot;')
    output += '\n' \
              '                </offers>\n' \
              '            </shop>\n' \
              '        </yml_catalog>'
    return output

def getProductsXML(url):
    print('Import products from '+ url + '...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
    }
    response = requests.get(url, headers=headers)
    encoding = response.encoding if response.encoding else 'utf-8'
    xml_data_bytes = response.content

    root = etree.fromstring(xml_data_bytes)

    offers = root.xpath('//offers/offer')
    offer_strings = [etree.tostring(offer, encoding='unicode') for offer in offers]
    result = ''.join(offer_strings)
    
    return result

print('program launch...')

FormdekorData = generate_xml_f(getFormdekorData()).replace('&', '&amp;')
TechnoOdisData = generate_xml_t(getTechnoOdisData()).replace('&', '&amp;')
HitbetonData = generate_xml_h(getHitbetonData()).replace('&', '&amp;')
SejmData = getProductsXML('https://cs3852032.prom.ua/products_feed.xml?hash_tag=873abdb034aaeb2b57a36797818f1e6a&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=121186603%2C121186630&nested_group_ids=121186603%2C121186630&extra_fields=keywords').replace('&', '&amp;')
MolliData = getProductsXML('https://molli.com.ua/price/prom.xml').replace('&', '&amp;')

send_xml_to_server(FormdekorData, 'formdekor_data')
send_xml_to_server(TechnoOdisData, 'techno_odis_data')
send_xml_to_server(HitbetonData, 'hitbeton_data')
send_xml_to_server(SejmData, 'semj_data')
send_xml_to_server(MolliData, 'molli_data')

response = requests.post('https://parser-for-grabiyaka.000webhostapp.com', data={"success": "true"})
if response.status_code == 200:
    if response.text == 'success':
        print('Все файлы успешно выгружены и объединены! Программу можно закрывать.')
else:
    print("Произошла ошибка при получении ответа")

input("Press any key to exit...")






