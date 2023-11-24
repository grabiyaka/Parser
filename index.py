from settings import requests, datetime, etree, ET, re, score

from parsers.formdekor import *
from parsers.hitbeton import *
from parsers.technoOdis import *


def convert_to_offer_bona(xml_data):
    # Парсим XML
    xml_data = ET.tostring(xml_data, encoding='utf-8').decode('utf-8')
    root = ET.fromstring(xml_data)

    offer_data = {}

    try:
        offer_data["id"] = root.find(".//{*}id").text
    except AttributeError:
        print("ID not found for an item.")
        return None

    offer_data["available"] = "true"

    # Заполняем остальные элементы
    offer_data["url"] = root.find(".//{*}link").text
    offer_data["price"] = root.find(".//{*}price").text.split()[0]  # Убираем валюту и оставляем только цифры
    offer_data["currencyId"] = root.find(".//{*}price").text.split()[1]  # Получаем валюту
    offer_data["categoryId"] = "2073"  # Указываем фиксированную категорию, как в примере

    # Добавляем изображения
    offer_data["picture"] = "\n".join([f'    <picture>{img.text}</picture>' for img in root.findall(".//{*}image_link")])

    # Добавляем остальные элементы
    offer_data["name"] = root.find(".//{*}title").text
    offer_data["vendor"] = root.find(".//{*}brand").text
    offer_data["description"] = f'    <description>\n{root.find(".//{*}description").text}\n    </description>'

    # Добавляем параметры
    param_elements = [f'    <param name="{detail.find("{*}attribute_name").text}">{detail.find("{*}attribute_value").text}</param>'
                      for detail in root.findall(".//{*}product_detail")]
    offer_data["params"] = "\n".join(param_elements)

    # Генерируем строку XML
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

    # Create the new XML string
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

        root = etree.fromstring(xml_data_bytes)
        
        offers = root.xpath('//offers/offer')

        if not offers:
        #     items = root.xpath('//items')
            
        #     if items:
        #         items[0].tag = 'offers'

        #         for item in root.xpath('//offers/item'):
        #             item.tag = 'offer'

        #         offers = root.xpath('//offers/offer')
                    
        #         offers_to_remove = root.xpath('//offers/offer[@in_stock="false"]')
        #         for offer in offers_to_remove:
        #             offer.getparent().remove(offer)
                    
        #     if not items:
        #         entries = root.xpath('//g:entry', namespaces={'g': 'http://www.w3.org/2005/Atom'})
        #         for entry in entries:
        #             new_offer = convert_xml_to_offer(entry)
        #             offers.append(new_offer)
        #         all_offers = '<offers>'
        #         for el in offers:
        #             all_offers = all_offers + str(el)
                    
        #         all_offers = all_offers.replace('&', '&amp;') + '</offers>'
                
        #         save_to_xml(all_offers, 'offers.xml')
                    
        #         root = etree.fromstring(all_offers)
             
            items = root.xpath("//item", namespaces={'g': 'http://www.w3.org/2005/Atom'})
            for el in items:
                new_offer = convert_to_offer_bona(el)
                offers.append(new_offer)
            all_offers = '<offers>'
            for el in offers:
                all_offers = all_offers + str(el)
                    
            all_offers = all_offers.replace('&', '&amp;') + '</offers>'
                
            save_to_xml(all_offers, 'offers.xml')
                    
            root = etree.fromstring(all_offers)
                    
            
        offers_to_remove = []
            
        offers_to_remove = root.xpath('//offers/offer[number(price) < 500]')
        for offer in offers_to_remove:
            offer.getparent().remove(offer)

        available_false_elements = root.xpath('//offers/offer[@available="false"]')
        for element in available_false_elements:
            element.getparent().remove(element)

        if isinstance(offers, list):
            for offer in offers:
                save_to_xml(offer, 'offer.xml')
                if article:
                    vendor_element = offer.find('vendor')
                    vendor_code_element = offer.find('vendorCode')

                    if vendor_element is not None:
                        if hasattr(vendor_element, 'text') and vendor_element.text is not None:
                            vendor_element.text = str(vendor_element.text) + ' ' + article

                    if vendor_code_element is not None:
                        if hasattr(vendor_code_element, 'text') and vendor_code_element.text is not None:
                            vendor_code_element.text = str(vendor_code_element.text) + ' ' + article

        result = ''.join(etree.tostring(child, encoding='unicode') for child in root.xpath('//offers/*'))

        score = score + len(root.xpath('//offers/offer'))

        return result.replace('&', '&amp;')

    except requests.exceptions.RequestException as e:
        print(f"Error during HTTP request: {e}")
        return None

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
        return None


print('program launch...')

xmlData = {
    # 'formdekor_data': generate_xml_f(getFormdekorData()).replace('&', '&amp;'),
    # 'techno_odis_data': generate_xml_t(getTechnoOdisData()).replace('&', '&amp;'),
    # 'hitbeton_data': generate_xml_h(getHitbetonData()).replace('&', '&amp;'),
    # 'semj_data':            getProductsXML('https://cs3852032.prom.ua/products_feed.xml?hash_tag=873abdb034aaeb2b57a36797818f1e6a&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=121186603%2C121186630&nested_group_ids=121186603%2C121186630&extra_fields=keywords',
    #                             'Сейм'),
    # 'molli_data':           getProductsXML('https://molli.com.ua/price/prom.xml', 'Молі'),
    # 'fortechne_data':       getProductsXML('https://cs3218374.prom.ua/products_feed.xml?hash_tag=7dccd0184ad811ba59f127366e3525d2&sales_notes=&product_ids=1932135796%2C1932135795%2C1927190939%2C1927190940%2C1927190941%2C1927190938%2C1927190937%2C1927190934%2C1927190933%2C1927190932%2C1927190930%2C1927190931%2C1927190929%2C1927190927%2C1927190928%2C1927190924%2C1927190926%2C1927190925%2C1927190923%2C1927190922%2C1927190921%2C1927190920%2C1927190919%2C1927190918%2C1927190915%2C1927190917%2C1927190916%2C1927190913%2C1927190914%2C1927190909%2C1927190910%2C1927190911%2C1927190912%2C1867919325%2C1867919326%2C1867919323%2C1867919324%2C1867919321%2C1867919322%2C1867919320%2C1867919319%2C1867919318%2C1867919317%2C1867919316%2C1867919315%2C1867919314%2C1867919312%2C1867919313%2C1867919309%2C1867919311%2C1867919310%2C1867919307%2C1867919308%2C1867919306%2C1867919305%2C1867919303%2C1867919304%2C1867919301%2C1867919302%2C1867919300%2C1867919299%2C1867919297%2C1867919298%2C1867919296%2C1867919295%2C1867919293%2C1867919294%2C1867919292%2C1867919290%2C1867919291%2C1867919289%2C1867919287%2C1867919288%2C1867919286%2C1867919285%2C1867919284%2C1867919282%2C1867919283%2C1867919280%2C1867919281%2C1867919279%2C1867919276%2C1867919278%2C1867919277%2C1867919274%2C1867919273%2C1867919275%2C1867919272%2C1867919271%2C1867919270%2C1867919269%2C1867919268%2C1867919267%2C1867919266%2C1867919265&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Фонет'),
    # 'de_technik_data':      getProductsXML('https://detechnik.com.ua/products_feed.xml?hash_tag=5ee69bb0fff0d94a4fe0f4687d340a79&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=&extra_fields=quantityInStock', 'Мегез'),
    # 'raduga_data_1':        getProductsXML('https://raduga-mebel.com.ua/products_feed.xml?hash_tag=9eb3ca8841cfc674dbc8f671f7a7ad8f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=11346773&nested_group_ids=11346773', 'Дуга'),
    # 'loft-mebel':           getProductsXML('https://loft-mebel.com.ua/module/yamarket/generate', 'Лофт'),
    
    # 'ranger':               getProductsXML('https://ranger.ua/public/zalivkaukr.xml', 'Палати'),
    # 'vitergear':            getProductsXML('https://vitergear.com.ua/content/export/079b9966a7d87a1f38054780026dc271.xml', 'Подорож'),
    # 'ersamed':              getProductsXML('https://ersamed.prom.ua/products_feed.xml?hash_tag=961c85cfa9c663ec283418017830efb4&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Ерс'),
    # 'terrasport':           getProductsXML('https://terrasport.ua/xml/sveltus.xml', 'Терас'),
    # 'websklad':             getProductsXML('https://www.websklad.biz.ua/wp-content/uploads/randomize_prom_40282.xml', 'Складвеб'),
    'bona':                 getProductsXML('https://bona-store.prom.ua/google_merchant_center.xml?hash_tag=bd35f3ed6dd506edb27edbc0be2345a5&product_ids=&label_ids=&export_lang=ru&group_ids=73357627%2C73420209%2C73420212%2C73420213%2C82869744&nested_group_ids=73357627%2C73420209%2C73420212%2C73420213%2C82869744', 'Бонагиль'),
    # 'kaloriferu':           getProductsXML('https://kaloriferu.com.ua/products_feed.xml?hash_tag=d993b7f2c54cae4e758c4f7e4cab6874&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=2445141%2C4623178&nested_group_ids=2445141%2C4623178', 'Дід'),
    # 'foks':                 getProductsXML('https://my.foks.biz/s/pb/f?key=69d0d2a7-70c9-41ff-b7ce-c545f41368aa&type=prom&ext=xml', 'Ян'),
    # 'drop':                 getProductsXML('http://drop.co.ua/feed/dropprom.xml', 'Інстор'),
    # 'emass':                getProductsXML('https://api.emass.ua/upload/api/ua/cd11d654a2466544600dbfd17d6a7bdc.xml', 'Гро-Гро'),
    # 'zenet':                getProductsXML('https://zenet-proizvoditel-klimaticheskoj-tehniki-i-cs2951573.prom.ua/products_feed.xml?hash_tag=c15bef90f54a3bbfd857a5f43cfb86e0&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=&extra_fields=', 'Зен'),
    # 'uadron':               getProductsXML('https://uadron.com/products_feed.xml?hash_tag=281dd6d99f9dd4625d3c5e6ffe15f88d&sales_notes=&product_ids=&label_ids=11323491&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Дрон'),
    # 'abrisart':             getProductsXML('https://abrisart.com/market-feed-ukraine', 'Вишив'),
    # 'elektreka':            getProductsXML('https://elektreka.com.ua/system/storage/download/v_nayavnost_yml.xml', 'Електр'),
    # 'itsellopt':            getProductsXML('http://itsellopt.com.ua/price_lists/general_price_cC9Ulx.xml', 'Ітсел'),
    # 'tradepartner':         getProductsXML('https://tradepartner.com.ua/content/export/7ee18c6c75274a1099c3d1d27d8599ee.xml?1676101329714', 'Трейдп'),
    # 'gastrorag':            getProductsXML('https://gastrorag.ua/feed.xml', 'Гастро'),
    # 'airon':                getProductsXML('https://airon.ua/xml-prices/airon_partner.xml', 'Айрон'),
    # 'bagland':              getProductsXML('https://bagland.com.ua/marketplace/43884.xml', 'Багле'),
    # 'blanknote':            getProductsXML('https://blanknote.ua/index.php?route=feed/yandex_marketnew_ua', 'Блокнот'),
    # 'spok':                 getProductsXML('https://spok.ua/content/export/5b0fa426f203508f146837a161303a3a.xml', 'Кіндер'),
    ### Ссылка не актуальна 'hanert':               getProductsXML('https://hanert.com.ua/my-account-2/', 'Хане'),
    # 'sanpid':               getProductsXML('https://sanpid.in.ua/products_feed.xml?hash_tag=975ae322d8fca4749aefe37020928260&sales_notes=&product_ids=&label_ids=9722762&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=', 'Санп'),
    # 'partners':             getProductsXML('http://ol.partners/api/ApiXml_v2/e4fd23e3-cbf8-44b2-ad72-690d7c6da701', 'Ол'),
    # 'newtea':               getProductsXML('https://newtea.ua/facebook.xml', 'Чай'),
    ### Ссылка не актуальна 'gofin':                getProductsXML('https://gofin.biz/index.php?route=extension/feed/neoseo_product_feed&name=prom_ru', 'Гофі'),
    # 'nosisvoe':             getProductsXML('https://nosisvoe.com.ua/rozetka_feed.xml', 'Носи'),
    # 'baby-comfrt':          getProductsXML('https://baby-comfrt.prom.ua/yandex_market.xml?hash_tag=06bbd7ee5bcaac2dab84f1337a54434f&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=86546354%2C86546356%2C86546358%2C86546359%2C91593455%2C94597402%2C95833412%2C97079049&nested_group_ids=', 'Бебі'),
    ### Ссылка не актуальна 'kukuruzabox':          getProductsXML('https://kukuruzabox.com.ua/ua/cp35969-programma-loyalnosti-dlya-postoyannyh-klientov.html', 'Ку'),
    # 'loveyouhome':          getProductsXML('https://loveyouhome.ua/index.php?route=extension/feed/unixml/prom', 'Лав'),
    # 'lekos':                getProductsXML('https://lekos.com.ua/partner/', 'Еко'),
    # 'best-time':            getProductsXML('https://support.best-time.biz/api/feed/drops/ua', 'Тайм'),
    # 'yugtorg':              getProductsXML('https://b2b.yugtorg.com/upload/yml/yml_256.xml', 'Юг'),
    # '7bags':                getProductsXML('https://7bags.com.ua/yandexmarket/a59358ef-6a08-4481-86c3-0a9b1b737acf.xml', '7сум'),
    # 'lurex':                getProductsXML('https://lurex.in.ua/uploads/export/marketplace_prom.xml', 'Рекс'),
    # 'matroluxe_1':          getProductsXML('https://matroluxe.ua/index.php?route=extension/feed/yandex_yml9', 'Люкс'),
    # 'matroluxe_2':          getProductsXML('https://matroluxe.ua/index.php?route=extension/feed/yandex_yml8', 'Люкс'),
    # 'matroluxe':            getProductsXML('https://levistella.com/products_feed.xml?hash_tag=94b05f555f35832558cabf51092dc40c&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=83613786%2C84269756%2C84454361%2C84541557%2C88799547%2C88800636%2C89099608%2C94782488%2C107706705%2C107825436%2C107926793&nested_group_ids=83613786%2C84269756%2C84454361%2C84541557%2C89099608%2C94782488%2C107706705%2C107825436', 'Стелла'),
    # 'uden':                 getProductsXML('https://shop.uden-s.ua/products_feed.xml?hash_tag=062348e29497f18973544dace7cd8ad4&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids=4185537%2C4192204%2C4192526%2C4235366%2C4272661%2C14539909%2C28341876&nested_group_ids=', 'Уденс'),
    # 'toybox':               getProductsXML('https://toybox.com.ua/index.php?route=extension/feed/prom_yml_data&sclad=4', 'Бойкот'),
    # 'royalshop':            getProductsXML('https://royalshop.com.ua/feeds/dropshipping-prom-21.xml', 'Ройшо'),
    # 'posudograd':           getProductsXML('https://posudograd.ua/dropship/19125/prom', 'Посуд'),
    # 'fashion_girl':           getProductsXML('https://fashion-girl.ua/products_feed.xml?hash_tag=1ca2cdd7ba4b8e31b3f1abe28df6f809&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&languages=ru&group_ids=&extra_fields=', 'Гел'),
}

for key, el in xmlData.items():
    send_xml_to_server(el, key)

response = requests.post('https://parser-for-grabiyaka.000webhostapp.com', data={"success": "true"})
if response.status_code == 200:
    if response.text == 'success':
        print('Все файлы успешно выгружены и объединены! Программу можно закрывать.')
else:
    print("Произошла ошибка при получении ответа")

input("Press any key to exit...")






