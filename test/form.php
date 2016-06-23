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

if (isset($_GET['redirected']) && $_GET['redirected'])
{
    if (isset($_COOKIE['TestCookie']))
    {
        echo $_GET['redirected'];
    } else {
        echo "ERROR: Redirected but cookie is missing";
    }
    exit();
}

if (isset($_POST['submit']) && $_POST['submit'])
{
    if (isset($_COOKIE['TestCookie']))
    {
        header(
            sprintf("Location: form.php?redirected=%s", $_POST['text_field']),
            TRUE,
            302
        );
    } else {
        echo "ERROR: Submitted but cookie is missing";
    }
} else {
    setcookie("TestCookie", "yes");
    setcookie("TestThirdCookie", "uJV8PDMAnZ1jWV0iuyiiYG8p_fVEKejDVOrbduOT876867");
    setcookie("TestSecondCookie", "CWuJV8PDMAnZ1jWV0CR0qmhQiYG8p_fVEKejDVOr765765Q", time() + 3600, '/', 'localhost', true, true);
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