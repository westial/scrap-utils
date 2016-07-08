<?php
/**
 * Common functions
 */

function printHead()
{
    foreach (getallheaders() as $name => $value) {
        echo "$name: $value\n";
    }
}
//printHead();

function printRequest()
{
    if (isset($_POST))
    {
        echo "<ul>";
        foreach ($_POST as $name => $value) {
            echo "<li>$name: $value</li>";
        }
        echo "</ul>";
    }
    if (isset($_REQUEST))
    {
        echo "<ul>";
        foreach ($_REQUEST as $name => $value) {
            echo "<li>$name: $value</li>";
        }
        echo "</ul>";
    }
}
//printRequest();

function printCookies()
{
    if (isset($_COOKIE))
    {
        echo "<ul>";
        foreach ($_COOKIE as $name => $value) {
            echo "<li>$name: $value</li>";
        }
        echo "</ul>";
    }
}