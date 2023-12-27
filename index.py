from settings import requests, datetime, etree, ET, re, score

from parsers.formdekor import *
from parsers.hitbeton import *
from parsers.technoOdis import *

def convert_to_offer_bona(xml_data):
    
    xml_data = ET.tostring(xml_data, encoding='utf-8').decode('utf-8')
    root = ET.fromstring(xml_data)

    offer_data = {}

    try:
        offer_data["id"] = root.find(".//{*}id").text
    except AttributeError:
        print("ID not found for an item.")
        return None

    offer_data["available"] = "true"

    offer_data["url"] = root.find(".//{*}link").text
    offer_data["price"] = root.find(".//{*}price").text.split()[0]  # Убираем валюту и оставляем только цифры
    offer_data["currencyId"] = root.find(".//{*}price").text.split()[1]  # Получаем валюту
    offer_data["categoryId"] = "2073"  # Указываем фиксированную категорию, как в примере

    offer_data["picture"] = "\n".join([f'    <picture>{img.text}</picture>' for img in root.findall(".//{*}image_link")])

    offer_data["name"] = root.find(".//{*}title").text
    offer_data["vendor"] = root.find(".//{*}brand").text
    offer_data["description"] = f'    <description>\n{root.find(".//{*}description").text}\n    </description>'

    param_elements = [f'    <param name="{detail.find("{*}attribute_name").text}">{detail.find("{*}attribute_value").text}</param>'
                      for detail in root.findall(".//{*}product_detail")]
    offer_data["params"] = "\n".join(param_elements)

    offer_xml = f'<offer id="{offer_data["id"]}" available="{offer_data["available"]}">\n'
    offer_xml += f'    <url>{offer_data["url"]}</url>\n'
    offer_xml += f'    <price>{offer_data["price"]}</price>\n'
    offer_xml += f'    <currencyId>{offer_data["currencyId"]}</currencyId>\n'
    offer_xml += f'    <categoryId>{offer_data["categoryId"]}</categoryId>\n'
    offer_xml += offer_data["picture"] + "\n"
    offer_xml += f'    <name>{offer_data["name"]}</name>\n'
    offer_xml += f'    <vendor>{offer_data["vendor"]}</vendor>\n'
    offer_xml += offer_data["description"] + "\n"
    offer_xml += offer_data["params"] + "\n"
    offer_xml += '</offer>'

    return offer_xml



def convert_xml_to_offer(xml_element):
    offer_data = {}
    offer_data['id'] = xml_element.find('.//g:id', namespaces={'g': 'http://base.google.com/ns/1.0'}).text
    offer_data['available'] = 'true' if xml_element.find('.//g:availability', namespaces={'g': 'http://base.google.com/ns/1.0'}).text == 'in stock' else 'false'
    offer_data['url'] = xml_element.find('.//g:link', namespaces={'g': 'http://base.google.com/ns/1.0'}).text
    offer_data['price'] = xml_element.find('.//g:price', namespaces={'g': 'http://base.google.com/ns/1.0'}).text.split()[0]
    offer_data['currencyId'] = 'UAH'

    # Check if the element exists before accessing its text attribute
    category_element = xml_element.find('.//g:google_product_category', namespaces={'g': 'http://base.google.com/ns/1.0'})
    offer_data['categoryId'] = category_element.text if category_element is not None else ''

    offer_data['picture'] = xml_element.find('.//g:image_link', namespaces={'g': 'http://base.google.com/ns/1.0'}).text
    offer_data['name'] = xml_element.find('.//g:title', namespaces={'g': 'http://base.google.com/ns/1.0'}).text
    offer_data['vendor'] = xml_element.find('.//g:brand', namespaces={'g': 'http://base.google.com/ns/1.0'}).text
    offer_data['description'] = xml_element.find('.//g:description', namespaces={'g': 'http://base.google.com/ns/1.0'}).text

    param_elements = xml_element.findall('.//g:applink', namespaces={'g': 'http://base.google.com/ns/1.0'})
    offer_data['params'] = {element.get('property'): element.get('content') for element in param_elements}

    offer_xml = f'<offer id="{offer_data["id"]}" available="{offer_data["available"]}">\n'
    offer_xml += f'    <url>{offer_data["url"]}</url>\n'
    offer_xml += f'    <price>{offer_data["price"]}</price>\n'
    offer_xml += f'    <currencyId>{offer_data["currencyId"]}</currencyId>\n'
    offer_xml += f'    <categoryId>{offer_data["categoryId"]}</categoryId>\n'
    offer_xml += f'    <picture>{offer_data["picture"]}</picture>\n'
    offer_xml += f'    <name>{offer_data["name"]}</name>\n'
    offer_xml += f'    <vendor>{offer_data["vendor"]}</vendor>\n'
    offer_xml += f'    <description>\n{offer_data["description"]}\n    </description>\n'

    for param_name, param_value in offer_data['params'].items():
        offer_xml += f'    <param name="{param_name}">{param_value}</param>\n'

    offer_xml += '</offer>'

    return offer_xml

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
        output += str(el)
    output += '\n' \
              '                </offers>\n' \
              '            </shop>\n' \
              '        </yml_catalog>'
    return output

def save_to_xml(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)

def send_xml_to_server(xml_data, filename):
    if xml_data:
        try: 
            url = 'https://parser-for-grabiyaka.000webhostapp.com'

            files = {filename: (filename + '.xml', xml_data.encode('utf-8'))}
            response = requests.post(url, files=files, timeout=300)

            if response.status_code == 200:
                print("XML успешно отправлен на сервер!")

                print("Ответ сервера на " + filename + ":")
                print(response.text)
            else:
                print("Ошибка при отправке XML на сервер.")
        except Exception as e:
            print("!!!! Ошибка при отправке XML на сервер:", str(e) + '   !!!!!')
            
    else: 
        print('!!!!!  ' + filename + ' error  !!!!!')


def getProductsXML(url, article='', price = 500):
    global score
    global id

    try:
        print('Import products from ' + article + '...')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        encoding = response.encoding if response.encoding else 'utf-8'
        xml_data_bytes = response.content
        
        offers = []
        
        root = etree.fromstring(xml_data_bytes)
    
        ### FORMAT ROOT IF THIS NEED
            
        if root.tag.endswith('shop'):
            items = root.xpath('//items')
            items[0].tag = 'offers'

            for item in root.xpath('//offers/item'):
                item.tag = 'offer'
                if 'in_stock' in item.attrib:
                    item.attrib['in_stock'] = 'available'

            offers = root.xpath('//offers/offer')
            
        elif root.tag.endswith('feed'): 
            entries = root.xpath('//g:entry', namespaces={'g': 'http://www.w3.org/2005/Atom'})
            for entry in entries:
                new_offer = convert_xml_to_offer(entry)
                offers.append(new_offer)
            all_offers = '<offers>'
            for el in offers:
                all_offers = all_offers + str(el)
                        
            all_offers = all_offers + '</offers>'
                        
            root = etree.fromstring(all_offers)
            
        elif  root.tag.endswith('rss'):
            items = root.xpath("//item", namespaces={'g': 'http://www.w3.org/2005/Atom'})
            for el in items:
                new_offer = convert_to_offer_bona(el)
                offers.append(new_offer)
            all_offers = '<offers>'
            for el in offers:
                all_offers = all_offers + str(el)
                    
            all_offers = all_offers + '</offers>'
            
            root = etree.fromstring(all_offers)
            
        # elif  root.tag.endswith('yml_catalog'):
            
        ###
        
        offers = root.xpath('//offers/offer')
        
        for offer in offers:
            group_id = offer.get("group_id")
            if group_id is not None:
                offer.set("group_id", f"{group_id} {article}")
        
        for offer in offers:
            pictures = offer.xpath('.//picture')
            
            for picture in pictures:
                picture.tag = 'image'
        
        offers_to_remove = root.xpath('//offers/offer[@in_stock!="true"]')
        for offer in offers_to_remove:
            offer.getparent().remove(offer)
            
        offers_to_remove = []
            
        offers_to_remove = root.xpath('//offers/offer[number(translate(price, ",", ".")) < ' + str(price) +']')
        for offer in offers_to_remove:
            offer.getparent().remove(offer)

        available_false_elements = root.xpath('//offers/offer[@available!="true"]')
        for element in available_false_elements:
            element.getparent().remove(element)

        for offer in offers:
            if article:
                vendor_element = offer.find('vendor')
                vendor_code_element = offer.find('vendorCode')

                if vendor_element is not None and vendor_element.text is not None:
                    vendor_element.text = vendor_element.text + ' ' + article
                else:
                    new_vendor_element = etree.Element('vendor')
                    new_vendor_element.text = article
                    offer.append(new_vendor_element)

                if vendor_code_element is not None:
                    if vendor_code_element.text is not None:
                        vendor_code_element.text = vendor_code_element.text + str(id) + ' ' + article
                    else:
                        vendor_code_element.text = str(id) + ' ' + article
                else:
                    new_vendor_code_element = etree.Element('vendorCode')
                    new_vendor_code_element.text = offer.get('id') + str(id) + ' ' + article
                    offer.append(new_vendor_code_element)
            id = id + 1
        
        result = ''.join(etree.tostring(child, encoding='unicode') for child in root.xpath('//offers/*'))

        score = score + len(root.xpath('//offers/offer'))

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error during HTTP request: {e}")
        return None

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML ({article}): {e}")
        return None
    
def get_and_save_data(urls_and_names, filename, price = 500):
    data = []
    for url, name in urls_and_names:
        result = getProductsXML(url, name, price)
        data.append(result)

    save_to_xml(build_done_xml(data), filename)



print('program launch...')

drp = [
    ('https://cs3852032.prom.ua/products_feed.xml?hash_tag=873abdb034aaeb2b57a36797818f1e6a&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=121186603%2C121186630&nested_group_ids=121186603%2C121186630&extra_fields=keywords',
     'Сейм'),
    ('https://molli.com.ua/price/prom.xml',
     'Молі'),
    ('https://cs3218374.prom.ua/products_feed.xml?hash_tag=7dccd0184ad811ba59f127366e3525d2&sales_notes=&product_ids=1932135796%2C1932135795%2C1927190939%2C1927190940%2C1927190941%2C1927190938%2C1927190937%2C1927190934%2C1927190933%2C1927190932%2C1927190930%2C1927190931%2C1927190929%2C1927190927%2C1927190928%2C1927190924%2C1927190926%2C1927190925%2C1927190923%2C1927190922%2C1927190921%2C1927190920%2C1927190919%2C1927190918%2C1927190915%2C1927190917%2C1927190916%2C1927190913%2C1927190914%2C1927190909%2C1927190910%2C1927190911%2C1927190912%2C1867919325%2C1867919326%2C1867919323%2C1867919324%2C1867919321%2C1867919322%2C1867919320%2C1867919319%2C1867919318%2C1867919317%2C1867919316%2C1867919315%2C1867919314%2C1867919312%2C1867919313%2C1867919309%2C1867919311%2C1867919310%2C1867919307%2C1867919308%2C1867919306%2C1867919305&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=',
     'Фонет'),
    ('https://ranger.ua/public/zalivkaukr.xml',
     'Палати'),
    ('https://vitergear.com.ua/content/export/079b9966a7d87a1f38054780026dc271.xml',
     'Подорож'),
    ('https://orthofreedom.com.ua/products_feed.xml?hash_tag=2816faa525c8332b233a18470758b632&sales_notes=&product_ids=&label_ids=14183265&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=&extra_fields=keywords',
     'Ерс'),
    ('https://terrasport.ua/xml/sveltus.xml',
     'Терас'),
    ('https://www.websklad.biz.ua/wp-content/uploads/randomize_prom_40282.xml',
     'Складвеб'),
    ('https://bona-store.prom.ua/google_merchant_center.xml?hash_tag=bd35f3ed6dd506edb27edbc0be2345a5&product_ids=&label_ids=&export_lang=ru&group_ids=73357627%2C73420209%2C73420212%2C73420213%2C82869744&nested_group_ids=73357627%2C73420209%2C73420212%2C73420213%2C82869744',
     'Бонагиль'),
    ('https://kaloriferu.com.ua/products_feed.xml?hash_tag=d993b7f2c54cae4e758c4f7e4cab6874&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=2445141%2C4623178&nested_group_ids=2445141%2C4623178',
     'Дід'),
    ('https://my.foks.biz/s/pb/f?key=69d0d2a7-70c9-41ff-b7ce-c545f41368aa&type=prom&ext=xml',
     'Ян'),
    ('http://drop.co.ua/feed/dropprom.xml',
     'Інстор'),
    ('https://himate.com.ua/index.php?route=feed/unixml/prom',
     'Gro'),
    ('https://uadron.com/products_feed.xml?hash_tag=281dd6d99f9dd4625d3c5e6ffe15f88d&sales_notes=&product_ids=&label_ids=11323491&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=',
     'Дрон'),
    ('https://elektreka.com.ua/system/storage/download/v_nayavnost_yml.xml',
     'Електр'),
    ('http://itsellopt.com.ua/price_lists/general_price_cC9Ulx.xml',
     'Ітсел'),
    ('https://gastrorag.ua/feed.xml',
     'Гастро'),
    ('https://airon.ua/xml-prices/airon_partner.xml',
     'Айрон'),
    ('https://blanknote.ua/index.php?route=feed/yandex_marketnew_ua',
     'Блокнот'),
    ('https://spok.ua/content/export/5b0fa426f203508f146837a161303a3a.xml',
     'Кіндер'),
    ('https://hanert.com.ua/my-account-2/',
     'Хане'),
    ('https://sanpid.in.ua/products_feed.xml?hash_tag=975ae322d8fca4749aefe37020928260&sales_notes=&product_ids=&label_ids=9722762&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=',
     'Санп'),
    ('http://ol.partners/api/ApiXml_v2/e4fd23e3-cbf8-44b2-ad72-690d7c6da701',
     'Ол'),
    ('https://newtea.ua/facebook.xml',
     'Чай'),
    ('https://gofin.biz/index.php?route=extension/feed/neoseo_product_feed&name=prom_ru',
     'Гофі'),
    ('https://nosisvoe.com.ua/rozetka_feed.xml',
     'Носи'),
    ('https://baby-comfrt.prom.ua/yandex_market.xml?hash_tag=06bbd7ee5bcaac2dab84f1337a54434f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=86546354%2C86546356%2C86546358%2C86546359%2C91593455%2C94597402%2C95833412%2C97079049&nested_group_ids=',
     'Бебі'),
    ('https://kukuruzabox.com.ua/products_feed.xml?hash_tag=58ee6724781917b0cf6d043572013925&sales_notes=&product_ids=&label_ids=&exclude_fields=description&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk&group_ids=2323313%2C2509099%2C22798006%2C85080759%2C98570328&nested_group_ids=2323313%2C2509099%2C22798006%2C85080759%2C98570328&extra_fields=',
     'Ку'),
    ('https://loveyouhome.ua/index.php?route=extension/feed/unixml/prom',
     'Лав'),
    ('https://lekos.com.ua/partner/',
     'Еко'),
    ('https://support.best-time.biz/api/feed/drops/ua',
     'Тайм'),
    ('https://b2b.yugtorg.com/upload/yml/yml_256.xml',
     'Юг'),
    ('https://7bags.com.ua/yandexmarket/a59358ef-6a08-4481-86c3-0a9b1b737acf.xml',
     '7сум'),
    ('https://matroluxe.ua/index.php?route=extension/feed/yandex_yml9',
     'Люкс'),
    ('https://matroluxe.ua/index.php?route=extension/feed/yandex_yml8',
     'Люкс'),
    ('https://shop.uden-s.ua/products_feed.xml?hash_tag=062348e29497f18973544dace7cd8ad4&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=4185537%2C4192204%2C4192526%2C4235366%2C4272661%2C14539909%2C28341876&nested_group_ids=',
     'Уденс'),
    ('https://hanert.com.ua/shop.xml',
     'Ren'),
    ('https://gofin.biz/index.php?route=extension/feed/unixml/prom_for_estet',
     'Fin'),
    ('https://kukuruzabox.com.ua/products_feed.xml?hash_tag=58ee6724781917b0cf6d043572013925&sales_notes=&product_ids=&label_ids=&exclude_fields=description&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk&group_ids=2323313%2C2509099%2C22798006%2C85080759%2C98570328&nested_group_ids=2323313%2C2509099%2C22798006%2C85080759%2C98570328&extra_fields=',
     'Kuku')
]

get_and_save_data(drp, 'xml/drp.xml', 1000)
drp = []

sites = [
    generate_xml_f(getFormdekorData()).replace('&', '&amp;'),
    generate_xml_t(getTechnoOdisData()).replace('&', '&amp;'),
    generate_xml_h(getHitbetonData()).replace('&', '&amp;'),
    getProductsXML('https://velomarket24.com.ua/products_feed.xml?hash_tag=ed5e87b0f593a6b91642b9f6fa4cf737&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=', 'Tek'),
]

save_to_xml(build_done_xml(sites), 'xml/sites.xml')
sites = []

opt = [
    ('https://toybox.com.ua/index.php?route=extension/feed/prom_yml_data&sclad=4',
     'Бойкот'),
    ('https://royalshop.com.ua/feeds/dropshipping-prom-21.xml',
     'Ройшо'),
    ('https://posudograd.ua/dropship/19125/prom',
     'Посуд'),
    ('https://fashion-girl.ua/products_feed.xml?hash_tag=1ca2cdd7ba4b8e31b3f1abe28df6f809&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=&extra_fields=',
     'Гел'),
    ('https://dwn.royaltoys.com.ua/my/export/da9e4096-c520-4b31-af66-1b62cd42d345.xml',
     'Рояль'),
]

get_and_save_data(opt, 'xml/opt.xml')
opt = []

zakazn = [
    ('https://zenet-proizvoditel-klimaticheskoj-tehniki-i-cs2951573.prom.ua/products_feed.xml?hash_tag=c15bef90f54a3bbfd857a5f43cfb86e0&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=&extra_fields=',
     'Зен'),
    ('https://tradepartner.com.ua/content/export/7ee18c6c75274a1099c3d1d27d8599ee.xml?1676101329714',
     'Трейдп'),
    ('https://loft-mebel.com.ua/module/yamarket/generate',
     'Лофт'),
    ('https://raduga-mebel.com.ua/products_feed.xml?hash_tag=9eb3ca8841cfc674dbc8f671f7a7ad8f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=11346773&nested_group_ids=11346773',
     'Радуга'),
    ('https://raduga-mebel.com.ua/products_feed.xml?hash_tag=9eb3ca8841cfc674dbc8f671f7a7ad8f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=97791228&nested_group_ids=97791228',
     'Радуга'),
]
get_and_save_data(zakazn, 'xml/zakazn.xml')
zakazn = []

avto = [
    ('https://ddaudio.com.ua/uploads/xml/big_stock.xml',
     'da'),
    ('https://voodoocar.com/products_feed.xml?hash_tag=fdb2fca9f2a63e912ad7c8f88b81b436&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=',
     'car'),
    ('https://vitol.com.ua/export.php?exporttype=2%C2%A4cy=uah&saleprice=1&lang=ru&available=1&tofile=1&token=3c4ea03a3d59e7e2aa04bd87ad9b9244',
     'lot'),
]
get_and_save_data(avto, 'xml/avto.xml')
avto = []

dh = [
    ('https://abrisart.com/market-feed-ukraine',
     'Вишив'),
    ('https://bagland.com.ua/marketplace/43884.xml',
     'Багле'),
    ('https://levistella.com/products_feed.xml?hash_tag=94b05f555f35832558cabf51092dc40c&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=83613786%2C84269756%2C84454361%2C84541557%2C88799547%2C88800636%2C89099608%2C94782488%2C107706705%2C107825436%2C107926793&nested_group_ids=83613786%2C84269756%2C84454361%2C84541557%2C89099608%2C94782488%2C107706705%2C107825436',
     'Стелла'),
    ('http://buy-club.com.ua/buy-club.xml',
     'bul'),
    ('https://lurex.in.ua/uploads/export/marketplace_prom.xml',
     'Рекс'),
    ('https://wowshop.ua/index.php?route=extension/feed/ocext_feed_generator_yamarket&token=5287',
     'Воов'),
]
get_and_save_data(dh, 'xml/dh.xml')
dh = []

input("Press any key to exit...")