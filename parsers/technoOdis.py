from settings import BeautifulSoup, requests, id, score

def getTechnoOdisData():
    global score
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
                
                score = score + 1


    print('Techno-odis done!')
    return products

def generate_xml_t(products, article):
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
                  '        <vendorCode>' + product['model'] + ' ' + article + '</vendorCode>\n' \
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