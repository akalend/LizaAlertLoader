![image](img/LizaAlert.jpg)
# LizaAlertLoader
The photo loader for LizaAlert project. More info in the docs folder. 

Description of the [Archicture](docs/Archicture.pdf) - russian documentation


Relationships Schema 
![shema ](/img/schema.png)

1. the client upload files to server

2. the server call ML model and check photo

3. the server save result to redis

4. the  client check the result in the redis

### installation
```bash
pip install -r requriments
```
change config file modules/config.py

```python
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
    
```

```bash
./api start   # start server on port
mode=prodaction         # output server
server 127.0.0.1:8000;  # output server


./api stop    # stop server

./api status  # check status
```
