import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests_html import HTMLSession
import random
import requests
from lxml import etree
import xml.etree.ElementTree as ET

id = 1

def getFormdekorData():
    categories = [
        'poliuretanovye-shtampy',
        'formy-dlya-3d-panelej',
        'dekorativnij-kamin',
        'formy-dlya-3d-blokov',
        'formy-dlya-dekora',
        'formy-dlya-sadovyh-figur',
        'master-shtampy'
    ]
    products = []

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0',
        'referer': 'https://formdekor.com/',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': 'OCSESSID=077481e943b5ef1531aeda1f01; _ga=GA1.1.1198526705.1687263981; language=ru-ru; currency=USD; sorecentproduct=109%2C149%2C115%2C162%2C50%2C118%2C177; _ga_BRFVKH6K7T=GS1.1.1690027036.31.0.1690027036.0.0.0',
        'Host': 'formdekor.com'
    }

    session = requests.Session()
    session.headers.update(headers)

    for category_index, category in enumerate(categories):
        url = 'https://formdekor.com/' + category + '/'
        response = session.get(url)

        if response.status_code == 200:
            paginate = response.text
            soup = BeautifulSoup(paginate, 'html.parser')
            paginate_element = soup.select_one('.pagination')
            if(paginate_element):
                paginate_text = paginate_element.get_text()
            else:
                paginate_text = ['1']
            pages = [page for page in paginate_text if page not in '|<>']

            for page in pages:
                url = 'https://formdekor.com/' + category + '/' + '?page=' + page
                response = session.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    productsList = soup.select(
                        '.products-category .products-list .product-layout')
                    num_product = 1
                    for product in productsList:
                        product_data = {}
                        pqProduct = BeautifulSoup(str(product), 'html.parser')
                        product_data['url'] = pqProduct.find('a')['href']
                        product_data['price'] = pqProduct.select_one(
                            '.price-new').get_text().replace('$', '').strip()

                        nameDiv = pqProduct.select_one('h4 a')
                        product_data['name'] = nameDiv.get_text().strip()
                        product_data['category'] = category

                        productPageUrl = product_data['url']
                        response = session.get(productPageUrl.strip())
                        if response.status_code == 200:
                            productPage = response.text
                            pqProductPage = BeautifulSoup(
                                productPage, 'html.parser')
                            product_data['brand'] = pqProductPage.select_one(
                                '.brand a span').get_text().strip()

                            modelDiv = pqProductPage.select_one('.model')
                            product_data['model'] = modelDiv.get_text().strip()

                            product_data['material'] = pqProductPage.select_one(
                                '.propery-title').get_text().strip() if pqProductPage.select_one('.propery-title') else ''

                            product_data['description'] = pqProductPage.select_one(
                                '#collapse-description').get_text().strip()

                            keyWords = [kw.get_text().strip()
                                        for kw in pqProductPage.select('#tab-tags a')]
                            product_data['key_words'] = keyWords

                            images = [img['data-image']
                                      for img in pqProductPage.select('.image-additional a')]
                            product_data['images'] = images

                            address_element = pqProductPage.select_one(
                                '.adres')
                            if address_element:
                                product_data['address'] = address_element.get_text(
                                ).strip()
                            else:
                                product_data['address'] = ''

                        products.append(product_data)
                        print(f'formdekor: product: {num_product}/{len(productsList)}, page: {page}/{len(pages)} category: {category_index + 1}/{len(categories)}')
                        num_product = num_product + 1

    print('Formdekor done!')
    return products


def generate_xml_f(products):
    global id
    output = ''

    for index, product in enumerate(products):
        output += '<offer id="' + str(id) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>USD</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + product['brand'] + '</vendor>\n' \
                  '        <vendorCode>' + product['model'] + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>'
        for key, word in enumerate(product['key_words']):
            if word != product['key_words'][-1]:
                output += word + ', <br/>'
            else:
                output += word
        output += '</keywords>\n' \
                  '        <country>Украина</country>\n' \
                  '        <param name="Матеріал">' + product['material'] + '</param>\n' \
                  '        <param name="Бренд">' + \
            product['brand'] + '</param>\n'

        for image in product['images']:
            output += '<picture>' + image + '</picture>'
        output += '</offer>'
        id = id + 1
    return output


def save_to_xml(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def getTechnoOdisData():
    categories = [
        'carpet-stones',
        'antichnyi-kamen',
        '400h400',
        'staryi-gorod',
        'bazalt',
        'staryi-arbat',
        'landshaftnaia',
        'manezh',
        'parket-taverna',
        '300h300',
        'oblitsovka-dekor',
        '320h320',
        'bordiur'
    ]
    products = []
    i = 0

    for category_index, category in enumerate(categories):
        url = 'https://techno-odis.com/catalogue/category/' + category
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            productsList = soup.select('#items-catalog-main .globalFrameProduct')
        num_product = 1
        for product in productsList:
            product_data = {}
            pqProduct = BeautifulSoup(str(product), 'html.parser')
            product_title = pqProduct.find('.frame-photo-title')
            product_data['url'] = pqProduct.find('a')['href']  
            product_data['name'] = product_title['title'] if product_title else ''
            productPageUrl = product_data['url']
            response = requests.get(productPageUrl)

            if response.status_code == 200:
                pqProductPage = BeautifulSoup(response.text, 'html.parser')
                product_data['price'] = pqProductPage.select_one('.priceVariant').text.strip()

                brand_element = pqProductPage.select_one('.brand a span')
                product_data['brand'] = brand_element.get_text().strip() if brand_element else ''

                modelDiv = pqProductPage.select_one('.js-code')
                product_data['model'] = modelDiv.get_text().strip() if modelDiv else ''

                material_element = pqProductPage.select_one('.propery-title')
                product_data['material'] = material_element.get_text().strip() if material_element else ''

                description_element = pqProductPage.select_one('.short-desc')
                product_data['description'] = description_element.get_text().strip() if description_element else ''

                keyWords = [kw.get_text().strip() for kw in pqProductPage.select('#tab-tags a')]
                product_data['key_words'] = keyWords

                images = [img['src'] for img in pqProductPage.select('.items-thumbs .photo-block img')]
                images = list(set(images))
                product_data['images'] = images

                address_element = pqProductPage.select_one('.adres')
                product_data['address'] = address_element.get_text().strip() if address_element else ''

                stockDiv = pqProductPage.select_one('.stock')
                product_data['stock'] = stockDiv.get_text().strip().replace('"', '').replace(' ', '') if stockDiv else ''

                products.append(product_data)
                print(f'techno-odis: product: {num_product}/{len(productsList)}, category: {category_index + 1}/{len(categories)}')
                num_product = num_product + 1 


    print('Techno-odis done!')
    return products


def generate_xml_t(products):
    global id
    output = ''
    for index, product in enumerate(products):
        output += '<offer id="' + str(id) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>USD</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + 'techno-odis' + '</vendor>\n' \
                  '        <vendorCode>' + product['model'] + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>'
        for key, word in enumerate(product['key_words']):
            if word != product['key_words'][-1]:
                output += word + ', <br/>'
            else:
                output += word
        output += '</keywords>\n' \
                  '        <country>Украина</country>\n' \
                  '        <param name="Матеріал">' + product['material'] + '</param>\n' \
                  '        <param name="Бренд">' + \
            product['brand'] + '</param>\n'

        for image in product['images']:
            output += '<picture>https://techno-odis.com/' + image + '</picture>'
        output += '</offer>'
        id = id + 1
    return output


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

    # Проверяем статусы ответов
    if response.status_code == 200:
        print("XML успешно отправлен на сервер!")

        # Выводим содержимое ответа сервера
        print("Ответ сервера на XML:")
        print(response.text)
    else:
        print("Ошибка при отправке XML на сервер.")
        
def getHitbetonData():
    categories = [
        'tvaryny',
        'ptakhy',
        'anhely',
        'liudy',
        'fentezi',
        'kashpo',
        'baliasyny-altanky-ta-inshe',
        'rizne'
    ]
    products = []
    i = 0
    productsList = []
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0',
        'referer': 'https://hitbeton.com.ua/',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '_gcl_au=1.1.1382130868.1692686260; _ga=GA1.1.1438058064.1692686260; _ga_9TN454D01M=GS1.1.1692716581.4.0.1692716598.0.0.0',
        'accept-charset': 'utf-8'
    }

    session = HTMLSession()

    for category_index, category in enumerate(categories):
        num_page = 1
        while True: 
            num_product = 1
            url = 'https://hitbeton.com.ua/product-category/' + category + '/page/' + str(num_page) + '/'
            response = session.get(url)
            if response.status_code == 200:
                page = response.html
                product_links = page.find('.products a')
                for link in product_links:
                    products_request = session.get(link.attrs['href'])
                    if products_request.status_code == 200:
                        product_page = products_request.html
                        product_data = {}
                        
                        product_data['url'] = link.attrs['href']
                        
                        description_element = product_page.find('.woocommerce-Tabs-panel--description p', first=True)
                        if description_element:
                            product_data['description'] = description_element.text
                        else:
                            product_data['description'] = ''

                        name_element = product_page.find('.product_title', first=True)
                        if name_element:
                            product_data['name'] = name_element.text
                        else:
                            product_data['name'] = ''

                        price_element = product_page.find('.woocommerce-Price-amount bdi', first=True)
                        if price_element:
                            product_data['price'] = price_element.text.split()[0]
                        else:
                            product_data['price'] = ''

                        picture_elements = product_page.find('figure .woocommerce-product-gallery__image a')
                        pictures = [picture.attrs['href'] for picture in picture_elements]
                        if pictures:
                            product_data['pictures'] = pictures
                        else:
                            product_data['pictures'] = []

                        
                        products.append(product_data)
                        print(f'hitbeton: product: {num_product}/{len(product_links)}, page: {num_page}, category: {category_index + 1}/{len(categories)}')
                        num_product = num_product + 1
                        
                    
                num_page = num_page + 1
            else: break
          
    print('Hitbeton done!')
    return products

def generate_xml_h(products):
    global id
    output = ''
    for index, product in enumerate(products):
        output += '<offer id="' + str(id) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>UAH</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + 'hitbeton' + '</vendor>\n' \
                  '        <vendorCode>' + '' + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>''</keywords>\n' \
                  '        <country>Украина</country>\n' \

        for image in product['pictures']:
            output += '<picture>' + image + '</picture>'
        output += '</offer>'
        id = id + 1
    return output


def generate_fake_data():
    names = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    prices = ['10.99', '24.99', '35.00', '15.49', '19.99']
    descriptions = ['Description A', 'Description B', 'Description C', 'Description D', 'Description E']
    picture_urls = ['url1.jpg', 'url2.jpg', 'url3.jpg', 'url4.jpg', 'url5.jpg']

    fake_data = []
    for _ in range(10):
        product = {
            'name': random.choice(names),
            'price': random.choice(prices),
            'description': random.choice(descriptions),
            'pictures': [random.choice(picture_urls) for _ in range(random.randint(1, 5))],
            'url': 'https://example.com/products/' + str(random.randint(1, 100))
        }
        fake_data.append(product)
    
    return fake_data

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

def save_string_to_xml_file(string_to_save, file_path):
    root = ET.Element("root")

    element = ET.Element("element")
    root.append(element)

    text = ET.Element("text")
    text.text = string_to_save
    element.append(text)

    tree = ET.ElementTree(root)

    tree.write(file_path, encoding="utf-8")


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
    print("Ответ сервера:")
    print(response.text)
else:
    print("Произошла ошибка при получении ответа")

input("Press any key to exit...")






