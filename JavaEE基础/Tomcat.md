## Tomcat

### tomcat修改端口号的三个地方

```xml
1.
<Server port="8005" ></Server>
2. 在Server节点内
<Connector port="8080" protocol="HTTP/1.1"></Connector>
3. 在Server节点内
<Connector port="8009" protocol="AJP/1.3"></Connector>
```



### 请求处理流程

- 请求A到Tomcat容器后, Tomcat会解析HTTP协议. 
- tomcat内部有一个线程池. 会从线程池中拿出一个线程, 处理有关请求A的业务. (发出业务线程A)
- 如果请求增加, tomcat线程池中已经没有空闲的线程, 那么新来的请求B会被放入请求队列中.
- 如果请求队列已经满了, 那么就会拒绝这个新来的请求

### 优化思路

- 增加线程池的容量
- 优化请求队列
- 业务线程的优化 (增大每一个线程可获得的资源数)
- tomcat线程模型的优化

### 线程池优化

#### 1. maxConnections 最大连接数

根据服务器性能和业务并发场景来设置.

- 受Linux内核的影响. 通过命令 `ulimit -a`查看Linux的最大连接数 也就是看显示结果中 `open files`对应的值. CentOS是1024, 太小. 目的是为了保护系统. 所以我们要修改这个值, 达到上限.

  > 修改 /etc/security/limits.conf 在文件末尾新增两行(65535是理论上Linux最大的)
  >
  > ```properties
  > *		soft		nofiles			65535
  > *		hard		nofiles			65535
  > ```

- 添加maxConnections的配置

  * 对CPU要求更高的计算密集型任务(spark storm), 尽量不要太高. 因为连接会占用CPU的资源.
  * IO密集型任务, 64G内存, 32核CPU, 建议配置在3000左右, 

- 配置的位置在 server.xml => connector

  ```xml
  <connector port="8080" maxConnections="3000" maxThreads="500" acceptCount="500" />
  ```

#### 2. maxThreads 线程池的最大线程数 (默认值是200)

建议配置成500  -  700

#### 3. acceptCount 最大排队等待数 (请求队列)

一般和maxThreads相同或略低即可

> tomcat的处理能力: maxThreads + acceptCount



> 1 2 3的优化是让干活的人更多, 但我们还要让每个干活的人更加强壮, 也就是让每一个连接的速度更快



### JVM优化

#### 1. -server 启用Server

服务器一定要开启

#### 2. -Xms 最小内存

建议与-Xmx相同. 

> JVM的内存是动态漂移的. 当内存使用率低于30%, 它就把JVM内存设置为最小内存. 当内存使用率为70%时, 就会设置为最大内存
>
> JVM内存的漂移过程是耗资源的. 所以要设置-Xms和-Xmx相同.

#### 3. -Xmx 最大内存

建议到可用内存的80%

#### 4. -XX:MetaspaceSize 元空间初始值 (配置成物理内存)

#### 5. -XX:MaxMetaspaceSize 元空间最大值 (就是物理内存, 配置成物理内存)

> 上述两个值都是jdk8中的新增部分. 从1.7中的持久空间, 变成了元空间, **元空间使用的就是物理内存**

#### 6. -XX:MaxNewSize 新生代内存. 在服务器环境下, 可以配置成64M或128M, 默认是16M, 保证新生代的快速迭代



#### 修改的方式: bin/catalina.sh

```sh
JAVA_OPTS="-server -Xms128m -Xmx128m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=128m -XX:MaxNewSize=32m"
```

#### 查看是否修改成功: jmap

先看进程编号 ps -ef | grep tomcat

jmap -heap 3506

就可以看到Heap Configuration



### 其他优化

#### gzip相关设置: 优化网络参数的, 比如原来下载1G, 现在下载100M

compression 设置开启Gzip压缩

compressableMimeType 压缩类型(使用默认的)

compressMinSize 压缩后输出内容大小

minSpareThread 最小的空闲线程数

##### 修改位置: conf/server.xml

```xml
<connector port="8080" maxConnections="3000" maxThreads="500" acceptCount="500" compression="true" compressionMinSize="2048" minSpareThread="100" />
```

#### 

#### 启动日志文件的位置

tail -f logs/catalina.out



### Tomcat的三种模式

#### BIO: 最稳定最老的连接器, 使用阻塞形式处理Request请求

#### NIO: 使用Java的异步IO技术, 使用非阻塞形式处理Request请求

jdk8开始的默认形式 (http-nio-8080)

#### APR: 原生C语言编写的非阻塞IO, 性能最理想

##### 网址: http://apr.apache.org/ http://apr.apache.org/download.cgi

##### 下载

APR 1.6.3

APR iconv 1.2.2 

APR-util 1.6.1

yum install -y expat expat-devel

##### 安装

1. apr

```java
解压至安装目录
./configure -prefix=/usr/local/apr
make
make install
```

2. apr-iconv

```java
解压至安装目录
./configure -prefix=/usr/local/apr-iconv --with-apr=/usr/local/apr
make
make install
```

3. apr-util

```java
解压至安装目录
./configure -prefix=/usr/local/apr-util --with-apr=/usr/local/apr --with-apriconv=/usr/local/apr-iconv
make
make install
```

##### tomcat的apr配置

在bin文件夹中, 有一个`tomcat-native.tar.gz`的包

tar -zxvf tomcat-native.tar.gz

cd tomcat-native-src/native

./configure —with-apr=/usr/local/apr

make & make install

修改bin/catalina.sh

```sh
JAVA_OPTS="-server -Xms128m -Xmx128m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=128m -XX:MaxNewSize=32m"

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/apr/lib export LD_LIBRARY_PATH
```

修改conf/server.xml

```xml
<connector port="8080" protocol="org.apache.coyote.http11.Http11AprProtocol" connectionTimeout="20000" maxConnections="3000" maxThreads="500" acceptCount="500" compression="true" compressionMinSize="2048" minSpareThread="100" />
```



#### 进行压力测试

##### 先安装apache的ab测试工具

yum install -y httpd-tools

##### nio测试结果：取第二大的吞吐量的值即可

###### ab -n 1000 -c 100 http://192.168.1.18:8085/mgr/list

###### requests per seconds

-  935
-  1072.52
-  1026.58
-  1989.36
-  2268.09

######  ab -n 10000 -c 100 http://192.168.1.18:8085/mgr/list

-  2606.95
-  3015.42 
-  5251.02

##### apr测试结果：取第二大的吞吐量的值即可

######  ab -n 1000 -c 100 http://192.168.1.18:8080/mgr/list

-  1113.56
-  1117.96
-  1503.52
-  1179.85
-  1459.72

######  ab -n 10000 -c 100 http://192.168.1.18:8080/mgr/list

-  3298.29
-  3660.72
-  3251.69

可以看出, apr更稳定, 吞吐量更高



### Tomcat集群

需要解决分布式的session问题.

#### Apache Tomcat Clustering

- session依然存在各自的tomcat中, 这个集群只是做了数据一致性的保障, 通过session的数据比较, 来确定session的数据是否存在不同, 如果有不同, 则会做session的迁移.
- session的比较耗时增加; 网络传输的session复制会降低服务器效率
- 优点是: 配置方便.

##### 搭建方式

https://tomcat.apache.org/tomcat-9.0-doc/cluster-howto.html

1. 分别在tomcatA和tomcatB的conf/server.xml中增加如下配置

```xml
<Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster"
                 channelSendOptions="8">

    <Manager className="org.apache.catalina.ha.session.DeltaManager"
             expireSessionsOnShutdown="false"
             notifyListenersOnReplication="true"/>

    <Channel className="org.apache.catalina.tribes.group.GroupChannel">
        <Membership className="org.apache.catalina.tribes.membership.McastService"
                    address="228.0.0.4"
                    port="45564"
                    frequency="500"
                    dropTime="3000"/>
        <Receiver className="org.apache.catalina.tribes.transport.nio.NioReceiver"
                  address="auto"
                  port="4000"
                  autoBind="100"
                  selectorTimeout="5000"
                  maxThreads="6"/>

        <Sender className="org.apache.catalina.tribes.transport.ReplicationTransmitter">
            <Transport className="org.apache.catalina.tribes.transport.nio.PooledParallelSender"/>
        </Sender>
        <Interceptor className="org.apache.catalina.tribes.group.interceptors.TcpFailureDetector"/>
        <Interceptor className="org.apache.catalina.tribes.group.interceptors.MessageDispatchInterceptor"/>
    </Channel>

    <Valve className="org.apache.catalina.ha.tcp.ReplicationValve"
           filter=""/>
    <Valve className="org.apache.catalina.ha.session.JvmRouteBinderValve"/>

    <Deployer className="org.apache.catalina.ha.deploy.FarmWarDeployer"
              tempDir="/tmp/war-temp/"
              deployDir="/tmp/war-deploy/"
              watchDir="/tmp/war-listen/"
              watchEnabled="false"/>

    <ClusterListener className="org.apache.catalina.ha.session.ClusterSessionListener"/>
</Cluster>
```

2. 在web.xml中增加一个配置, 来决定哪个web项目需要进行session的复制和同步

   - Make sure your `web.xml` has the `<distributable/>` element

3. 测试

   新建一个maven的web项目, 有web.xml和index.jsp

   web.xml

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <web-app version="2.4"
            xmlns="http://java.sun.com/xml/ns/j2ee"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://java.sun.com/xml/ns/j2ee
            http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd">
       <distributable/>
   </web-app>
   ```

   index.jsp

   ```jsp
   <%@ page contentType="text/html;charset=UTF-8" language="java" %>
   <html>
   <head>
       <title>测试Session共享内容</title>
   </head>
   <body>
       <%
           Object sessionMessage = session.getAttribute("sessionMessage");
           if (sessionMessage!=null && sessionMessage.toString().trim().length()>0) {
               out.println("session有值 session="+sessionMessage);
           }else{
               session.setAttribute("sessionMessage","Hello imooc jiangzh");
               out.println("session没有值");
           }
       %>
   </body>
   </html>
   ```

   访问http://localhost:8080/test/index.jsp

   演示效果是, 只有第一次会打印"session没有值", 剩下的情况, 无论访问到tomcatA还是tomcatB, 都有值, 都打印"session有值 session="+sessionMessage

#### JWT等类似机制

A请求访问tomcatA, tomcatA给A请求发一个钥匙. **这个钥匙串是无状态的.** 只要请求A携带这个钥匙去访问tomcat集群, 则如果访问到tomcatB, 也会通过. **但session是有状态的.** 所以JWT不算严格的tomcat集群方式.

#### MSM, Tomcat + Redis 等session统一管理

核心是将原本存在tomcat的session, 统一存放在tomcat外部的一个内存区域中. 比如Redis, 比如Memcached

> Memcached性能比Redis更好 3%-5%
>
> Redis可以持久化, 有多种数据结构

### 结构

#### webapps

其中有一个ROOT文件夹. 是tomcat默认访问的项目. 也就是直接输入默认的端口和地址 `localhost:8080`, 就会访问这个ROOT项目.

所以, 为了访问自己的项目时, 不显示项目的名称, 或者是为了访问项目时, 项目名称简短, 链接简短. 所有, 再将war包复制到webapps目录时, 可以改名. 把常用的改名为ROOT.war



### tomcat和session:

1. 对Tomcat而言，Session是一块在服务器开辟的内存空间，其存储结构为**ConcurrentHashMap**；**是线程安全的, 所有请求共享一个tomcat的Session区域.**
2. Http协议是一种无状态协议，即每次服务端接收到客户端的请求时，都是一个全新的请求，服务器并不知道客户端的历史请求记录；
3. Session的主要目的就是为了弥补Http的无状态特性。简单的说，就是服务器可以利用session存储客户端在同一个会话期间的一些操作记录；

#### 1. 服务器如何判断客户端发送过来的请求是属于同一个会话？

答：用Session id区分，Session id相同的即认为是同一个会话，在Tomcat中Session id用JSESSIONID表示；

#### 2. 服务器、客户端如何获取Session id？Session id在其之间是如何传输的呢？

- 服务器第一次接收到请求时，开辟了一块Session空间（创建了Session对象），同时生成一个Session id，并通过响应头的Set-Cookie：“JSESSIONID=XXXXXXX”命令，向客户端发送要求设置cookie的响应；
- 客户端收到响应后，在本机客户端设置了一个JSESSIONID=XXXXXXX的cookie信息，该cookie的过期时间为浏览器会话结束；
- 接下来客户端每次向同一个网站发送请求时，请求头都会带上该cookie信息（包含Session id）；
- 服务器通过读取请求头中的Cookie信息，获取名称为JSESSIONID的值，得到此次请求的Session id；

> 服务器只会在客户端第一次请求响应的时候，在响应头上添加Set-Cookie：“JSESSIONID=XXXXXXX”信息，接下来在同一个会话的第二第三次响应头里，是不会添加Set-Cookie：“JSESSIONID=XXXXXXX”信息的；
>
> 而客户端是会在每次请求头的cookie中带上JSESSIONID信息；



### tomcat中的session是如何实现的

- Tomcat中一个会话对应一个session，其实现类是StandardSession，查看源码，可以找到一个attributes成员属性，即存储session的数据结构，为ConcurrentHashMap，支持高并发的HashMap实现；

```java
protected Map<String, Object> attributes = new ConcurrentHashMap<String, Object>();
```

- Tomcat中多个会话对应的session是由ManagerBase类来维护，查看其代码，可以发现其有一个sessions成员属性，存储着各个会话的session信息

```java
protected Map<String, Session> sessions = new ConcurrentHashMap<String, Session>();
```

- 客户端每次的请求，tomcat都会在HashMap中查找对应的key为JSESSIONID的Session对象是否存在

先看doGetSession方法中的如下代码，这个一般是第一次访问的情况，即创建session对象，session的创建是调用了ManagerBase的createSession方法来实现的; 

response.addSessionCookieInternal方法的功能就是往响应头写入“Set-Cookie”信息；最后，还要调用session.access方法记录下该session的最后访问时间，因为session是可以设置过期时间的；

```java
session = manager.createSession(sessionId);

if ((session != null) && (getContext() != null) && getContext().getServletContext(). getEffectiveSessionTrackingModes().contains(SessionTrackingMode.COOKIE)) {
	Cookie cookie = ApplicationSessionCookieConfig.createSessionCookie(context, session.getIdInternal(), isSecure());
    response.addSessionCookieInternal(cookie);
}

if (session == null) {
    return null;
}

session.access();
return session;
```



再看doGetSession方法中的如下代码，这个一般是第二次以后访问的情况，通过ManagerBase的findSession方法查找session，其实就是利用map的key从ConcurrentHashMap中拿取对应的value，这里的key即requestedSessionId，也即JSESSIONID，同时还要调用session.access方法，记录下该session的最后访问时间；

```java
if (requestedSessionId != null) {
    try {
        session = manager.findSession(requestedSessionId);
    } catch (IOException e) {
        session = null;
    }

    if ((session != null) && !session.isValid()) {
        session = null;
    }

    if (session != null) {
        session.access();
        return (session);
    }
}
```

建立会话之后, 后续的request中的sessionid(请求头), cookie中的sessionid(在浏览器开发者工具中找到的cookie)和服务器端session.getId()拿到的是相同的sessionid. 

> 注意: tomcat重启之后, session就会改变