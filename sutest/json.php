<?php
/**
 * Basic php form to test the Requester when content type is json
 */
//require("functions.php");
//printRequest();

if (isset($_POST['result']) && $_POST['result'])
{
    echo $_POST['result'];
    exit(0);
}

echo "error";