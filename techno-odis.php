<?php
require __DIR__ . "/phpQuery-onefile.php";
function dd($value)
{
    echo '<pre>';
    print_r($value);
    echo '</pre>';
    die();
}

function removeDuplicates($array, $key)
{
    $uniqueValues = array();
    $result = array();

    foreach ($array as $item) {
        if (!in_array($item[$key], $uniqueValues)) {
            $uniqueValues[] = $item[$key];
            $result[] = $item;
        }
    }

    return $result;
}

function removeObjectsByValue($array, $key, $value) {
    foreach ($array as $index => $object) {
        if (isset($object[$key]) && $object[$key] === $value) {
            unset($array[$index]);
        }
    }
    
    return array_values($array);
}



set_time_limit(700);

$categories = [
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
];
$products = [];
$i = 0;
foreach ($categories as $category) {
    $file = file_get_contents('https://techno-odis.com/catalogue/category/'.$category);
    $pq = phpQuery::newDocument($file);
    $data = [];
    $productsList = $pq->find('#items-catalog-main');
    $pqProducts = $productsList->find('.globalFrameProduct');

    foreach ($pqProducts as $key => $product) {
        $pqProduct = pq($product);
        $products[$i]['url'] = $pqProduct->find('a')->attr('href');

        $productPage = file_get_contents($products[$i]['url']);
        $pqProductPage = phpQuery::newDocument($productPage);

        $products[$i]['name'] = $pqProduct->find('.frame-photo-title')->attr('title');

        $products[$i]['price'] = $pqProductPage->find('.priceVariant')->text();

        $products[$i]['brand'] = trim($pqProductPage->find('.brand a span')->text());

        $modelDiv = $pqProductPage->find('.js-code');
        $products[$i]['model'] = trim($modelDiv->contents()->not($modelDiv->children())->text());

        $products[$i]['material'] = trim($pqProductPage->find('.propery-title')->text());
        $products[$i]['description'] = htmlspecialchars(trim($pqProductPage->find('.short-desc')->html()));

        $keyWords = [];
        $pqProductPage->find('#tab-tags a')->each(function ($item) use (&$keyWords) {
            $keyWords[] = pq($item)->text();
        });

        $images = [];
        $pqProductPage->find('.items-thumbs .photo-block img')->each(function ($item) use (&$images) {
            $images[] = pq($item)->attr('src');
        });
        $images = array_unique($images);

        $products[$i]['images'] = $images;

        $products[$i]['key_words'] = $keyWords;
        $products[$i]['address'] = trim($pqProductPage->find('.adres')->text());

        $stockDiv = $pqProductPage->find('.stock');
        $products[$i]['stock'] = str_replace(['"', ' '], '', trim($stockDiv->contents()->not($stockDiv->children())->text()));

        $i++;
    }
};

$products = removeDuplicates($products, 'url');

$products = removeObjectsByValue($products, 'price', '');

$output = '<?xml version="1.0" encoding="UTF-8"?>
        <yml_catalog date="2023-06-25 11:18">
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
foreach ($products as $key=>$product) {
    $output .= '<offer id="' . $key . '" available="true">
        <url>' . $product['url'] . '</url>
        <price>' . $product['price'] . '</price>
        <currencyId>USD</currencyId>
        <categoryId></categoryId>
        <quantity_in_stock></quantity_in_stock>
        <name>' . $product['name'] . '</name>
        <vendor>' . 'techno-odis' . '</vendor>
        <vendorCode>' . $product['model'] . '</vendorCode>
        <description><![CDATA[' .
        $product['description']
        . ']]></description>
        <minimum_order_quantity>1</minimum_order_quantity>
        <keywords></keywords>
        <manufacturer_warranty>1</manufacturer_warranty>
        <country>Украина</country>
        <param name="Матеріал"></param>
        <param name="Бренд">' . 'techno-odis' . '</param>
        ';
    foreach ($product['images'] as $image) {
        $output .= '<picture>' . $image . '</picture>';
    }
    $output .= '</offer>';
}
$output .= '
                </offers>
            </shop>
        </yml_catalog>';
$filename = uniqid() . '.xml';
file_put_contents($filename, $output);
header('Content-Type: application/xml');
header('Content-Disposition: attachment; filename=' . $filename);
header('Content-Length: ' . filesize($filename));
header('Pragma: no-cache');
header('Expires: 0');

// Отправка содержимого файла на скачивание
readfile($filename);

// Удаление временного файла
unlink($filename);
exit();
?>