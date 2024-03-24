conf = {
    
    'confirm_url' : 'https://api.hideman.net/confirm',
    'from' : 'sales@hideman.net',
    'email_passwd' : 'foofahh1queiZ2ai',

    'template_path' : {
        'prodaction': '/home/git/api/src/templates/',
        'localhost' : '/home/akalend/projects/api/src/templates/'
    },

    'expire_cached': 21600,
    'expire_free': {
        'localhost': 100,
        'stage': 14400,
        'prodaction':   11000 }, #  16 час   4 часа 14400

    'free_wait_time': {
        'localhost': 100,
        'stage': 600,
        'prodaction': 100000}, # 604800 = 7 * 86400 (1 week ) * 12 = 1 квартал


    'port' : {
       'prodaction' : [8000],
       'stage' : [8000],
       'localhost' : [8001]
    },
    'nginx_conf' : {
        'localhost': 'api_servers.conf',
        'stage': '/etc/nginx/api_servers.conf',
        'prodaction_old': '/etc/nginx/api_servers.conf' ,
        'prodaction': 'api_servers.conf',
    }
}


redis_conf = {
    'localhost': 'localhost',
    'stage': '127.0.0.1:6380',
    'prodaction': '127.0.0.1:6379',
}

mysql_conf = {
    'home': {
        'mysql_user': 'hidman56',
        'mysql_db': 'hidman',
        'mysql_host': 'localhost',
        'mysql_password': '12345',
    },

    'localhost': {
        'mysql_user': 'hidman',
        'mysql_db': 'hidman',
        'mysql_host': 'localhost',
        'mysql_password': '12345',
    },
    'stage': {
        'mysql_user': 'hideman',
        'mysql_db': 'hideman_new',
        'mysql_host': '1.254.254.8',
        'mysql_password': 'mo6tohY0',
    },

    'prodaction': {
        'mysql_user': 'hideman',
        'mysql_db': 'hideman_new',
        'mysql_host': '1.254.254.8',
        'mysql_password': 'mo6tohY0',
    }
}
