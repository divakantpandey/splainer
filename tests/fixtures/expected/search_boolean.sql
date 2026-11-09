SELECT *
FROM security
WHERE (((index = 'security') AND ((action = 'blocked') OR (action = 'denied'))) AND (src_ip != '10.0.0.*'));
