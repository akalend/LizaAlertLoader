![image](img/LizaAlert_logo.jpg)
# LizaAlertLoader
The photo loader for LizaAlert project. More info in the docs folder. 

Description of the [Archicture](docs/Archicture.pdf) - russian documentation


Relationships Schema 
![shema ](/img/schema.png)

1. the client upload files to server

2. the server call ML model and check photo

3. the server save result to redis

4. the  client check the result in the redis
