<?php

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

function removeObjectsByValue($array, $key, $value)
{
    foreach ($array as $index => $object) {
        if (isset($object[$key]) && $object[$key] === $value) {
            unset($array[$index]);
        }
    }

    return array_values($array);
}

function downloadXML($output)
{
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
}