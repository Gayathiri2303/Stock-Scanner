<?php
$output = shell_exec('cd /home2/thekidsw/gayathiriportfolio.xyz/stockscanner && /home2/thekidsw/virtualenv/gayathiriportfolio.xyz/stockscanner/3.10/bin/python setup_db.py 2>&1');
echo "<pre>" . $output . "</pre>";
?>