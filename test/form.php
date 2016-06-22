<?php
/**
 * Basic php form to test the Requester on POST mode.
 * To make it work this script must be executable by the web server.
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
}
//printRequest();

if (isset($_POST['submit']) && $_POST['submit'])
{
    if (isset($_COOKIE['TestCookie']))
    {
        echo $_POST['text_field'];
    } else {
        var_dump($_COOKIE);
    }
    exit();
} else {
    setcookie("TestCookie", "yes");
}
?>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
</head>
<body>
    <form method="post" action="#">
        <input type="text" value="" name="text_field" />
        <input type="submit" name="submit" value="Submit" />
    </form>
</body>
</html>