## NGINX CONFIG

We are using Nginx for the Reverse Proxy Role , It is helping us in **IP** base ***Rate Limiting*** , Understanding of Nginx is pretty much required before setting up , Nginx beside as a Reverse proxy it is a Web Server, Load Balancer, Reverse Proxy, HTTP Cache
You can have your website redirection , Web Server and for many other things . (But Reverse Proxy is the most used one)
> [Docs for further Learning or help]( https://nginx.org/en/docs/)

So mostly nginx ship with sample  config (at, **/etc/nginx/nginx.conf**)  but that is not for our usecase , it only acts as the  main one nothing else 
we can remove it and all or make few changes nothing else,  But we cant add our config there . So In linux for any application the most preferred way is the adding all user specific configuration in the conf.d/ (a special directory just for the  better use case), 
if you want you can have in one , but it is the best good standard and easy to maintain 

> It is a quite niche software we have in this software world 

#### Steps for setting up :
- Download the Nginx using package manager or through compressed folder (it is very easy to download & very small binary)
- Put your all config file in the `/etc/nginx/conf.d/**` , I have already provided two custom config `base.conf` and `myapp.conf` .
- And make sure include those config in the your main `nginx.conf` (which is at ... /etc/nginx/nginx.conf yess) by writing
  ```
    include /etc/nginx/conf.d/*.conf
  ```
  your nginx.conf 
  
  
  
