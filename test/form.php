<?php
/**
 * Basic php form to test the Requester on POST mode.
 * To make it work this script must be executable by the web server.
 */

if (isset($_POST['submit']) && $_POST['submit'])
{
    echo $_POST['text_field'];
    exit();
}
?>
<html>
<head></head>
<body>
    <form method="post" action="#">
        <input type="text" value="" name="text_field" />
        <input type="submit" name="submit" value="Submit" />
    </form>
</body>
</html>