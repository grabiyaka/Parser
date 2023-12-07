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


def getProductsXML(url, article=''):
    global score

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
            
        # elif  root.tag.endswith('ym_catalog'):
            
        ###
        
        offers = root.xpath('//offers/offer')
        
        for offer in offers:
            pictures = offer.xpath('.//picture')
            
            for picture in pictures:
                picture.tag = 'image'
        
        offers_to_remove = root.xpath('//offers/offer[@in_stock!="true"]')
        for offer in offers_to_remove:
            offer.getparent().remove(offer)
            
        offers_to_remove = []
            
        offers_to_remove = root.xpath('//offers/offer[number(price) < 500]')
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

                if vendor_code_element is not None:
                    if vendor_code_element.text is not None:
                        vendor_code_element.text = vendor_code_element.text + ' ' + article
                    else:
                        vendor_code_element.text = article
                else:
                    new_vendor_code_element = etree.Element('vendorCode')
                    new_vendor_code_element.text = offer.get('id') + ' ' + article
                    offer.append(new_vendor_code_element)


        result = ''.join(etree.tostring(child, encoding='unicode') for child in root.xpath('//offers/*'))

        score = score + len(root.xpath('//offers/offer'))

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error during HTTP request: {e}")
        return None

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
        return None


print('program launch...')

drp = [
    getProductsXML('https://cs3852032.prom.ua/products_feed.xml?hash_tag=873abdb034aaeb2b57a36797818f1e6a&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=121186603%2C121186630&nested_group_ids=121186603%2C121186630&extra_fields=keywords',
        'Сейм'),
    getProductsXML('https://molli.com.ua/price/prom.xml', 'Молі'),
    getProductsXML('https://cs3218374.prom.ua/products_feed.xml?hash_tag=7dccd0184ad811ba59f127366e3525d2&sales_notes=&product_ids=1932135796%2C1932135795%2C1927190939%2C1927190940%2C1927190941%2C1927190938%2C1927190937%2C1927190934%2C1927190933%2C1927190932%2C1927190930%2C1927190931%2C1927190929%2C1927190927%2C1927190928%2C1927190924%2C1927190926%2C1927190925%2C1927190923%2C1927190922%2C1927190921%2C1927190920%2C1927190919%2C1927190918%2C1927190915%2C1927190917%2C1927190916%2C1927190913%2C1927190914%2C1927190909%2C1927190910%2C1927190911%2C1927190912%2C1867919325%2C1867919326%2C1867919323%2C1867919324%2C1867919321%2C1867919322%2C1867919320%2C1867919319%2C1867919318%2C1867919317%2C1867919316%2C1867919315%2C1867919314%2C1867919312%2C1867919313%2C1867919309%2C1867919311%2C1867919310%2C1867919307%2C1867919308%2C1867919306%2C1867919305%2C1867919303%2C1867919304%2C1867919301%2C1867919302%2C1867919300%2C1867919299%2C1867919297%2C1867919298%2C1867919296%2C1867919295%2C1867919293%2C1867919294%2C1867919292%2C1867919290%2C1867919291%2C1867919289%2C1867919287%2C1867919288%2C1867919286%2C1867919285%2C1867919284%2C1867919282%2C1867919283%2C1867919280%2C1867919281%2C1867919279%2C1867919276%2C1867919278%2C1867919277%2C1867919274%2C1867919273%2C1867919275%2C1867919272%2C1867919271%2C1867919270%2C1867919269%2C1867919268%2C1867919267%2C1867919266%2C1867919265&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Фонет'),


    getProductsXML('https://ranger.ua/public/zalivkaukr.xml', 'Палати'),
    getProductsXML('https://vitergear.com.ua/content/export/079b9966a7d87a1f38054780026dc271.xml', 'Подорож'),
    getProductsXML('https://ersamed.prom.ua/products_feed.xml?hash_tag=961c85cfa9c663ec283418017830efb4&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Ерс'),
    getProductsXML('https://terrasport.ua/xml/sveltus.xml', 'Терас'),
    getProductsXML('https://www.websklad.biz.ua/wp-content/uploads/randomize_prom_40282.xml', 'Складвеб'),
    getProductsXML('https://bona-store.prom.ua/google_merchant_center.xml?hash_tag=bd35f3ed6dd506edb27edbc0be2345a5&product_ids=&label_ids=&export_lang=ru&group_ids=73357627%2C73420209%2C73420212%2C73420213%2C82869744&nested_group_ids=73357627%2C73420209%2C73420212%2C73420213%2C82869744', 'Бонагиль'),
    getProductsXML('https://kaloriferu.com.ua/products_feed.xml?hash_tag=d993b7f2c54cae4e758c4f7e4cab6874&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=2445141%2C4623178&nested_group_ids=2445141%2C4623178', 'Дід'),
    getProductsXML('https://my.foks.biz/s/pb/f?key=69d0d2a7-70c9-41ff-b7ce-c545f41368aa&type=prom&ext=xml', 'Ян'),
    getProductsXML('http://drop.co.ua/feed/dropprom.xml', 'Інстор'),
    # getProductsXML('https://api.emass.ua/upload/api/ua/cd11d654a2466544600dbfd17d6a7bdc.xml', 'Гро-Гро'),
    getProductsXML('https://himate.com.ua/index.php?route=feed/unixml/prom', 'Gro'),

    getProductsXML('https://uadron.com/products_feed.xml?hash_tag=281dd6d99f9dd4625d3c5e6ffe15f88d&sales_notes=&product_ids=&label_ids=11323491&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Дрон'),
    getProductsXML('https://abrisart.com/market-feed-ukraine', 'Вишив'),
    getProductsXML('https://elektreka.com.ua/system/storage/download/v_nayavnost_yml.xml', 'Електр'),
    getProductsXML('http://itsellopt.com.ua/price_lists/general_price_cC9Ulx.xml', 'Ітсел'),

    getProductsXML('https://gastrorag.ua/feed.xml', 'Гастро'),
    getProductsXML('https://airon.ua/xml-prices/airon_partner.xml', 'Айрон'),
    getProductsXML('https://bagland.com.ua/marketplace/43884.xml', 'Багле'),
    getProductsXML('https://blanknote.ua/index.php?route=feed/yandex_marketnew_ua', 'Блокнот'),
    getProductsXML('https://spok.ua/content/export/5b0fa426f203508f146837a161303a3a.xml', 'Кіндер'),
    getProductsXML('https://hanert.com.ua/my-account-2/', 'Хане'),
    getProductsXML('https://sanpid.in.ua/products_feed.xml?hash_tag=975ae322d8fca4749aefe37020928260&sales_notes=&product_ids=&label_ids=9722762&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Санп'),
    getProductsXML('http://ol.partners/api/ApiXml_v2/e4fd23e3-cbf8-44b2-ad72-690d7c6da701', 'Ол'),
    getProductsXML('https://newtea.ua/facebook.xml', 'Чай'),
    getProductsXML('https://gofin.biz/index.php?route=extension/feed/neoseo_product_feed&name=prom_ru', 'Гофі'),
    getProductsXML('https://nosisvoe.com.ua/rozetka_feed.xml', 'Носи'),
    getProductsXML('https://baby-comfrt.prom.ua/yandex_market.xml?hash_tag=06bbd7ee5bcaac2dab84f1337a54434f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=86546354%2C86546356%2C86546358%2C86546359%2C91593455%2C94597402%2C95833412%2C97079049&nested_group_ids=', 'Бебі'),
    getProductsXML('https://kukuruzabox.com.ua/ua/cp35969-programma-loyalnosti-dlya-postoyannyh-klientov.html', 'Ку'),
    getProductsXML('https://loveyouhome.ua/index.php?route=extension/feed/unixml/prom', 'Лав'),
    getProductsXML('https://lekos.com.ua/partner/', 'Еко'),
    getProductsXML('https://support.best-time.biz/api/feed/drops/ua', 'Тайм'),
    getProductsXML('https://b2b.yugtorg.com/upload/yml/yml_256.xml', 'Юг'),
    getProductsXML('https://7bags.com.ua/yandexmarket/a59358ef-6a08-4481-86c3-0a9b1b737acf.xml', '7сум'),
    getProductsXML('https://lurex.in.ua/uploads/export/marketplace_prom.xml', 'Рекс'),
    getProductsXML('https://matroluxe.ua/index.php?route=extension/feed/yandex_yml9', 'Люкс'),
    getProductsXML('https://matroluxe.ua/index.php?route=extension/feed/yandex_yml8', 'Люкс'),
    getProductsXML('https://levistella.com/products_feed.xml?hash_tag=94b05f555f35832558cabf51092dc40c&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=83613786%2C84269756%2C84454361%2C84541557%2C88799547%2C88800636%2C89099608%2C94782488%2C107706705%2C107825436%2C107926793&nested_group_ids=83613786%2C84269756%2C84454361%2C84541557%2C89099608%2C94782488%2C107706705%2C107825436', 'Стелла'),
    getProductsXML('https://shop.uden-s.ua/products_feed.xml?hash_tag=062348e29497f18973544dace7cd8ad4&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=4185537%2C4192204%2C4192526%2C4235366%2C4272661%2C14539909%2C28341876&nested_group_ids=', 'Уденс'),
]
save_to_xml(build_done_xml(drp), 'xml/drp.xml')

# sites = [
#     generate_xml_f(getFormdekorData()).replace('&', '&amp;'),
#     generate_xml_t(getTechnoOdisData()).replace('&', '&amp;'),
#     generate_xml_h(getHitbetonData()).replace('&', '&amp;'),
#     getProductsXML('https://velomarket24.com.ua/products_feed.xml?hash_tag=ed5e87b0f593a6b91642b9f6fa4cf737&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=', 'Tek'),
# ]
# save_to_xml(build_done_xml(sites), 'xml/sites.xml')

opt = [
    getProductsXML('https://toybox.com.ua/index.php?route=extension/feed/prom_yml_data&sclad=4', 'Бойкот'),
    getProductsXML('https://royalshop.com.ua/feeds/dropshipping-prom-21.xml', 'Ройшо'),
    getProductsXML('https://posudograd.ua/dropship/19125/prom', 'Посуд'),
    getProductsXML('https://fashion-girl.ua/products_feed.xml?hash_tag=1ca2cdd7ba4b8e31b3f1abe28df6f809&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=&extra_fields=', 'Гел'),
    getProductsXML('http://dwn.royaltoys.com.ua/my/export/dffc79a2-df78-492b-9323-4658bef84449.xml', 'Рояль'),
]
save_to_xml(build_done_xml(opt), 'xml/opt.xml')

zakazn = [
    getProductsXML('https://zenet-proizvoditel-klimaticheskoj-tehniki-i-cs2951573.prom.ua/products_feed.xml?hash_tag=c15bef90f54a3bbfd857a5f43cfb86e0&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=&extra_fields=', 'Зен'),
    getProductsXML('https://tradepartner.com.ua/content/export/7ee18c6c75274a1099c3d1d27d8599ee.xml?1676101329714', 'Трейдп'),
    getProductsXML('https://loft-mebel.com.ua/module/yamarket/generate', 'Лофт'),
    getProductsXML('https://raduga-mebel.com.ua/products_feed.xml?hash_tag=9eb3ca8841cfc674dbc8f671f7a7ad8f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=11346773&nested_group_ids=11346773', 'Радуга'),
    getProductsXML('https://raduga-mebel.com.ua/products_feed.xml?hash_tag=9eb3ca8841cfc674dbc8f671f7a7ad8f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=97791228&nested_group_ids=97791228', 'Радуга'),
    getProductsXML('https://detechnik.com.ua/products_feed.xml?hash_tag=5ee69bb0fff0d94a4fe0f4687d340a79&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=&extra_fields=quantityInStock', 'Мегез'),
]
save_to_xml(build_done_xml(zakazn), 'xml/zakazn.xml')

avto = [
    getProductsXML('https://ddaudio.com.ua/uploads/xml/big_stock.xml', 'da'),
    getProductsXML('https://voodoocar.com/products_feed.xml?hash_tag=fdb2fca9f2a63e912ad7c8f88b81b436&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=', 'car'),
    getProductsXML('https://vitol.com.ua/export.php?exporttype=2%C2%A4cy=uah&saleprice=1&lang=ru&available=1&tofile=1&token=3c4ea03a3d59e7e2aa04bd87ad9b9244', 'lot'),
]
save_to_xml(build_done_xml(avto), 'xml/avto.xml')

input("Press any key to exit...")