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

function removeObjectsByValue($array, $key, $value) {
    foreach ($array as $index => $object) {
        if (isset($object[$key]) && $object[$key] === $value) {
            unset($array[$index]);
        }
    }
    
    return array_values($array);
}