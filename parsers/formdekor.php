<?php
 function getFormdekorData(){
    $categories = [
        'poliuretanovye-shtampy',
        'formy-dlya-3d-panelej',
        'dekorativnij-kamin',
        'formy-dlya-3d-blokov',
        'formy-dlya-dekora',
        'formy-dlya-sadovyh-figur',
        'master-shtampy'
    ];
    $products = [];
    $i = 0;
    foreach ($categories as $category) {
        $paginate = file_get_contents('https://formdekor.com/' . $category . '/');
        $paginate = phpQuery::newDocument($paginate);
        $paginate = $paginate->find('.pagination')->text();
        $paginate = str_split($paginate);
        $pages = [];
        foreach ($paginate as $page) {
            if ($page != '|' && $page != '<' && $page != '>') {
                $pages[] = $page;
            }
        }
        foreach ($pages as $page) {
            $file = file_get_contents('https://formdekor.com/' . $category . '/?page=' . $page);
            $pq = phpQuery::newDocument($file);
            $data = [];
            $productsList = $pq->find('.products-category .products-list');
            $pqProducts = $productsList->find('.product-layout');

            foreach ($pqProducts as $key => $product) {
                $pqProduct = pq($product);
                $products[$i]['url'] = $pqProduct->find('a')->attr('href');
                $products[$i]['price'] = str_replace(['$', ' '], '', trim($pqProduct->find('.price-new')->text()));
                
                $nameDiv = $pqProduct->find('h4 a');
                $products[$i]['name'] = str_replace('&', '&quot;', trim($nameDiv->contents()->not($nameDiv->children())->text()));

                $products[$i]['category'] = $category;

                $productPage = file_get_contents($products[$i]['url']);
                $pqProductPage = phpQuery::newDocument($productPage);

                $products[$i]['brand'] = trim($pqProductPage->find('.brand a span')->text());

                $modelDiv = $pqProductPage->find('.model');
                $products[$i]['model'] = trim($modelDiv->contents()->not($modelDiv->children())->text());

                $products[$i]['material'] = trim($pqProductPage->find('.propery-title')->text());
                $products[$i]['description'] = htmlspecialchars(trim($pqProductPage->find('#collapse-description')->html()));

                $keyWords = [];
                $pqProductPage->find('#tab-tags a')->each(function ($item) use (&$keyWords) {
                    $keyWords[] = pq($item)->text();
                });

                $images = [];
                $pqProductPage->find('.image-additional a')->each(function ($item) use (&$images) {
                    $images[] = pq($item)->attr('data-image');
                });

                $products[$i]['images'] = $images;

                $products[$i]['key_words'] = $keyWords;
                $products[$i]['address'] = trim($pqProductPage->find('.adres')->text());
                $i++;
            }
        }
    };
    $output = '<?xml version="1.0" encoding="UTF-8"?>
        <yml_catalog date="'.date('Y-m-d').' '.date('H:i').'">
            <shop>
                <name>ПУ формы и штампы</name>
                <company>ФОРМДЕКОР-UA</company>
                <url>https://formdekor.com/</url>
                <platform>Opencart</platform>
                <version>3.0.3.8/1.2.1</version>
                <currencies>
                    <currency id="USD" rate="1"/>
                    </currencies>
                <categories>
                    <category id="59"> Поліуретанові штампи</category>
                    <category id="60"> Форми для 3d панелей</category>
                </categories>
                <offers>';
    foreach ($products as $index => $product) {
        $output .= '<offer id="' . $index + 1 . '" available="true">
        <url>'.$product['url'].'</url>
        <price>'.$product['price'].'</price>
        <currencyId>USD</currencyId>
        <categoryId></categoryId>
        <quantity_in_stock></quantity_in_stock>
        <name>'.$product['name'].'</name>
        <vendor>'.$product['brand'].'</vendor>
        <vendorCode>'.$product['model'].'</vendorCode>
        <description><![CDATA['.
        $product['description']
        .']]></description>
        <keywords>';
        foreach($product['key_words'] as $key =>$word){
            if ($word != end($product['key_words'])) {
                $output .= $word .', &lt;/br&gt;';
            } else{
                $output .= $word;
            }
        }
        $output .='</keywords>
        <country>Украина</country>
        <param name="Матеріал">'.$product['material'].'</param>
        <param name="Бренд">'.$product['brand'].'</param>
        ';
        foreach($product['images'] as $image){
            $output .= '<picture>'.$image.'</picture>';
        }
        $output .=  '</offer>';
    }
    $output .= '
                </offers>
            </shop>
        </yml_catalog>';
     return $output;
 }
