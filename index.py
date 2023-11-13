from settings import requests, datetime, etree, ET, re, score

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
    global score
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
    }
    response = requests.get(url, headers=headers)
    encoding = response.encoding if response.encoding else 'utf-8'
    xml_data_bytes = response.content

    root = etree.fromstring(xml_data_bytes)

    offers_to_remove = root.xpath('//offers/offer[@in_stock="false"]')

    for offer in offers_to_remove:
        offer.getparent().remove(offer)

    result = ''.join(etree.tostring(child, encoding='unicode') for child in root.xpath('//offers/*'))
    
    score = score + len(root.xpath('//offers/offer'))

    return result

print('program launch...')

xmlData = {
    'FormdekorData': generate_xml_f(getFormdekorData()).replace('&', '&amp;'),
    'TechnoOdisData': generate_xml_t(getTechnoOdisData()).replace('&', '&amp;'),
    'HitbetonData': generate_xml_h(getHitbetonData()).replace('&', '&amp;'),
    'SejmData': getProductsXML('https://cs3852032.prom.ua/products_feed.xml?hash_tag=873abdb034aaeb2b57a36797818f1e6a&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=121186603%2C121186630&nested_group_ids=121186603%2C121186630&extra_fields=keywords').replace('&', '&amp;'),
    'MolliData': getProductsXML('https://molli.com.ua/price/prom.xml').replace('&', '&amp;'),
    'FortechneData': getProductsXML('https://cs3218374.prom.ua/products_feed.xml?hash_tag=7dccd0184ad811ba59f127366e3525d2&sales_notes=&product_ids=1932135796%2C1932135795%2C1927190939%2C1927190940%2C1927190941%2C1927190938%2C1927190937%2C1927190934%2C1927190933%2C1927190932%2C1927190930%2C1927190931%2C1927190929%2C1927190927%2C1927190928%2C1927190924%2C1927190926%2C1927190925%2C1927190923%2C1927190922%2C1927190921%2C1927190920%2C1927190919%2C1927190918%2C1927190915%2C1927190917%2C1927190916%2C1927190913%2C1927190914%2C1927190909%2C1927190910%2C1927190911%2C1927190912%2C1867919325%2C1867919326%2C1867919323%2C1867919324%2C1867919321%2C1867919322%2C1867919320%2C1867919319%2C1867919318%2C1867919317%2C1867919316%2C1867919315%2C1867919314%2C1867919312%2C1867919313%2C1867919309%2C1867919311%2C1867919310%2C1867919307%2C1867919308%2C1867919306%2C1867919305%2C1867919303%2C1867919304%2C1867919301%2C1867919302%2C1867919300%2C1867919299%2C1867919297%2C1867919298%2C1867919296%2C1867919295%2C1867919293%2C1867919294%2C1867919292%2C1867919290%2C1867919291%2C1867919289%2C1867919287%2C1867919288%2C1867919286%2C1867919285%2C1867919284%2C1867919282%2C1867919283%2C1867919280%2C1867919281%2C1867919279%2C1867919276%2C1867919278%2C1867919277%2C1867919274%2C1867919273%2C1867919275%2C1867919272%2C1867919271%2C1867919270%2C1867919269%2C1867919268%2C1867919267%2C1867919266%2C1867919265&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=').replace('&', '&amp;')
}

send_xml_to_server(xmlData['FormdekorData'], 'formdekor_data')
send_xml_to_server(xmlData['TechnoOdisData'], 'techno_odis_data')
send_xml_to_server(xmlData['HitbetonData'], 'hitbeton_data')
send_xml_to_server(xmlData['SejmData'], 'semj_data')
send_xml_to_server(xmlData['MolliData'], 'molli_data')
send_xml_to_server(xmlData['FortechneData'], 'fortechne_data')

response = requests.post('https://parser-for-grabiyaka.000webhostapp.com', data={"success": "true"})
if response.status_code == 200:
    if response.text == 'success':
        print('Все файлы успешно выгружены и объединены! Программу можно закрывать.')
else:
    print("Произошла ошибка при получении ответа")

input("Press any key to exit...")






