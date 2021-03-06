## Nginx

### 中间件的作用

* 安全
* 请求转发
* 负载均衡
* http的缓存服务

### nginx是一个开源, 高性能, 可靠的HTTP中间件, 代理服务

#### IO多路复用epoll

nginx是多进程的，是异步非阻塞的，多个描述符的I/O操作都能在一个线程内并发交替地顺序完成. 这里的复用, 指的是复用同一个线程.

#### 轻量级

功能模块少, 代码模块化

#### CPU亲和

把cpu核心和nginx工作进程绑定, 也就是把每个worker进程固定在一个cpu内核上, 减少切换cpu核的消耗

#### master和worker进程

其中有一个master进程，有多个worker进程（根据电脑的核数，在nginx.conf中配置）

工作时，客户端首先和master连接，然后master负责分配任务给worker

每个worker进程独立，避免了锁竞争的开销

高可用, 如果一个worker失效, 其他worker可以持续提供服务

#### 对比apache

apache是多线程的，但是某个线程的通信是阻塞的，面对并发访问，就必须开很多的线程，但是线程切换很耗时耗资源. 线程比进程更不安全，但通信效率高



### nginx的模块

#### limit_conn_module: 连接频率限制

#### limit_req_module: 请求频率限制



### 安装

#### 1. 解压nginx-1.8.0.tar.gz

#### 2. 进入解压后的nginx文件中

#### 3. 执行 ./configure --prefix=/hadoop/app/nginx

#### 4. 执行 make && make install

#### 5. 修改 nginx.conf文件

##### 将nginx作为图片服务器的配置

```properties
# 如果请求是以/images开头的, 则访问alias后面配置的那个文件夹里面的图片文件即可
location /images { 
	alias /hadoop/static/imgs;
	expires 1d;
}
```

#### 6. 启动

sbin/nginx

sbin/nginx -s reload

##### 其他命令

	nginx -t -c /etc/nginx/nginx.conf
	检查配置文件是否正确
	
	nginx -s reload -c /etc/nginx/nginx.conf
	重新启动nginx 
	
	ps aux | grep nginx
	ps ef|grep nginx
	查看nginx是否启动成功
	
	netstat -ntpl 查看端口占用
	kill -9 $pid



### 负载均衡的配置

在nginx.conf中的server节点下加上    include vhost/*.conf;

然后在nginx.conf同级目录创建vhost文件夹, 然后在里面创建各种配置文件.

#### 负载均衡的分类

* 轮询
* 权重
* ip hash(同一个用户访问同一台机器)
* url hash(同一个服务访问同一台机器)
* fair(后端服务器响应时间短的优先分配)

```properties
upstream www.happymmall.com {
	server 127.0.0.1:8080;
	server 127.0.0.1:9080;

	server 127.0.0.1:8080 weight=15;
	server 127.0.0.1:9080 weight=10;

	ip_hash;
	server 127.0.0.1:8080 weight=15;
	server 127.0.0.1:9080 weight=10;

	server 127.0.0.1:8080 weight=15;
	server 127.0.0.1:9080 weight=10;
	hash $request_uri;

	server 127.0.0.1:8080 weight=15;
	server 127.0.0.1:9080 weight=10;
	fair;
}
```
