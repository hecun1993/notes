## Dubbo

分布式服务架构的治理系统，用来进行资源调度，使得所有的服务有统一的入口.

采用SOA架构，使用Zookeeper作为注册中心，子系统之间通过Dubbo通信、调用服务.

rpc(远程过程调用,直接调用方法)协议进行远程调用，使用socket通信。传输效率高，并且可以统计出系统之间的调用关系、调用次数。

### 五部分组成

Provider: 暴露服务的服务提供方。

Consumer: 调用远程服务的服务消费方。

Registry: 服务注册与发现的注册中心。

Monitor: 统计服务的调用次调和调用时间的监控中心。

Container: 服务运行容器。

### 原理

0. 容器负责启动，加载，运行服务提供者。
1. 服务提供者在启动时，向注册中心注册自己提供的服务。
2. 服务消费者在启动时，向注册中心订阅自己所需的服务。
3. 注册中心返回服务提供者地址列表给消费者，如果有变更，注册中心将基于长连接推送变更数据给消费者。
4. 服务消费者，从提供者地址列表中基于软负载均衡算法，选一台提供者调用，如果调用失败，再选另一台。
5. 服务消费者和提供者，在内存中累计调用次数和调用时间，定时每分钟发送一次统计数据到监控中心。

#### 注册中心zookeeper

奇数个节点

适合做集群管理中心

注册中心负责服务地址的注册与查找，相当于目录服务，服务提供者和消费者只在启动时与注册中心交互，注册中心不转发请求，压力较小

### 开发

#### 综述

1. 声明服务接口, 所有的服务接口都单独打包放在一个项目中
2. 服务提供者开发, 实现服务接口
3. 服务提供者配置, 发布服务
4. 服务消费者配置, 引用服务
5. 服务调用

#### 1. 在服务消费者和提供者两个module分别引用jar

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>dubbo</artifactId>
    <version>2.4.9</version>
    <exclusions>
        <exclusion>
            <groupId>org.springframework</groupId>
            <artifactId>spring</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>com.101tec</groupId>
    <artifactId>zkclient</artifactId>
    <version>0.8</version>
    <exclusions>
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

#### 2. consumer.xml

```xml
消费方应用信息, 用于计算依赖关系
<dubbo:application name="bookshop-admin"/>
使用zookeeper注册中心暴露服务地址
<dubbo:registry protocol="zookeeper" address="127.0.0.1:2181"></dubbo:registry>
生成远程服务代理, 可以和本地bean一样使用service
<dubbo:reference id="bookService" interface="com.lesson.service.BookService" version="1.0" group="hds"></dubbo:reference>
```

#### 3. provider.xml

```xml
提供方应用信息, 用于计算依赖关系
<dubbo:application name="bookshop-provider"/>
使用zookeeper注册中心暴露服务地址
<dubbo:registry protocol="zookeeper" address="127.0.0.1:2181"></dubbo:registry>
声明需要暴露的服务接口
<dubbo:service interface="com.lesson.service.BookService" ref="bookServiceImpl" version="1.0" group="hds"></dubbo:service>
```

#### 4. 启动zk

```properties
./zkServer.sh start
```

> 实体类需要实现序列化接口