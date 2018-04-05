## Eureka

eureka主要用于服务的注册与发现, 可以将一个服务变成服务器, 也可以变成客户端.

### 优势

- EurekaServerConfigBean properties的属性
- EurekaServerConfiguration -> EurekaServerInitializerConfiguration server端的自动配置
- Eureka支持相互注册与复制, 支持高可用, 支持用户认证, 支持client消费端(不需要注册到注册中心server)注册表缓存
- 支持保护模式, 不会踢出实例, 可以支持服务方上传健康信息
- 支持rest协议

### eureka server

#### 1. 在Application.java主类上加注解 @EnableEurekaServer

#### 2. 在application.properties配置文件中

```properties
server.port=8666
spring.application.name=eureka-server
# 服务提供方的一些实例信息
eureka.instance.hostname=127.0.0.1

#留存的服务实例低于多少比例时, 就进入保护模式(不再进行心跳检测, 不再注销任何服务提供者的实例(当服务提供者的心跳失效后, 本来eureka会注销该实例的))
eureka.server.renewal-percent-threshold=0.5
#是否开启保护模式
eureka.server.enable-self-preservation=true
#是否注册eureka为client, 只有在高可用模式下才是true(禁用eureka客户端的功能)
eureka.client.register-with-eureka=false
#是否开启每隔一段时间client获取注册信息的请求(本身eureka-server是注册在中心, 没必要获取注册信息)(禁用eureka客户端的功能)
eureka.client.fetch-registry=false

#eureka服务器的地址, 注册和查询都需要依赖该地址, 多个用逗号分隔
#http://${eureka.instance.hostname}:${server.port}/eureka/
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:8666/eureka/

### 搭建集群时的配置
# 1. 新建两个配置文件, 2. 启动两个实例, 让这两个eureka server 相互注册
# mvn springboot:run -Dspring.profiles.active=peer
# eureka.client.serviceUrl.defaultZone=http://127.0.0.1:8666/eureka/
```



### eureka client 服务提供方

#### 1. 启动类 @EnableDiscoveryClient

#### 2. application.properties

```properties
# eureka的服务提供者(对应的api-gateway是服务消费者)
server.port=8083
spring.application.name=user

#添加的是eureka server的地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:8666/eureka/

#心跳间隔时间(eureka.instance是服务提供者的一些配置信息) client每隔5秒向server发送心跳
eureka.instance.lease-renewal-interval-in-seconds=5

#心跳过期时间, server端 10秒没收到instance的心跳, 则注销该实例
eureka.instance.lease-expiration-duration-in-seconds=10

#上面两个配置之所以配置在client端, 是说明server支持不同client有不同的配置

#把client的健康状态上报给eureka server, 需要依赖autuator依赖 (EurekaHealthCheckHandlerConfiguration)
eureka.client.healthcheck.enabled=true

# @EnableDiscoveryClient(通过此注解, 可以引入eureka client的自动配置) 
# 原因: @EnableDiscoveryClient-> @EnableDiscoveryClientImportSelector extends SpringFactoryImportSelector<EnableDiscoveryClient>
# 项目启动时, 会通过反射获取到泛型类 EnableDiscoveryClient, spring启动时, 会扫描所有的spring.factories SPI文件. 将关联注解(@EnableDiscoveryClient)的实现类(EnableDiscoveryClientConfiguration)获取并创建出来, 实现自动配置
# 在SpringFactoryImportSelector#selectImports中, 调用SpringFactoryLoader.loadFactoriesName, 加载spring.factories配置文件, 得到所有的auto Configuration classes

# 当关闭应用时, 容器停止, 触发一个EurekaDiscovery#@EventListener(ContextClosedEvent.class)事件, 被监听到之后, 执行 this.eurekaClient.shutdown()
# 如果直接kill -9 pid(通过jps -lv | grep user), 则不会触发上面的事件
```

#### 分析@EnableDiscoveryClient

通过此注解, 可以引入eureka client的自动配置)

##### 生效原因

- @EnableDiscoveryClient-> @EnableDiscoveryClientImportSelector extends SpringFactoryImportSelector<EnableDiscoveryClient>
- 项目启动时, 会通过反射获取到泛型类 EnableDiscoveryClient, spring启动时, 会扫描所有的spring.factories SPI文件. 将关联注解(@EnableDiscoveryClient)的实现类(EnableDiscoveryClientConfiguration)获取并创建出来, 实现自动配置
- 在SpringFactoryImportSelector#selectImports中, 调用SpringFactoryLoader.loadFactoriesName, 加载spring.factories配置文件, 得到所有的auto Configuration classes
- 当关闭应用时, 容器停止, 触发一个EurekaDiscovery#@EventListener(ContextClosedEvent.class)事件, 被监听到之后, 执行 this.eurekaClient.shutdown()
- 如果直接kill -9 pid(通过jps -lv | grep user), 则不会触发上面的事件

### eureka client 服务消费方(不需要向server注册)

#### 1. 启动类 @EnableDiscoveryClient

#### 2. application.properties

```properties
server.port=8080
# api-gateway是服务的消费者
spring.application.name=api-gateway
management.port=8023

# api-gateway是服务的消费者 所以不需要注册到eureka server中, 就有下面的配置
eureka.client.register-with-eureka=false
eureka.client.service-url.defaultZone=http://127.0.0.1:8666/eureka
```

#### 3. Controller

```java
//api-gateway是user服务的消费者, 通过DiscoveryClient来获取服务提供者user
@Autowired
private DiscoveryClient discoveryClient;

@RequestMapping("index1")
@ResponseBody
public List<ServiceInstance> getReister(){
    // 在user-service中定义了spring.application.name=user
    return discoveryClient.getInstances("user");
}
```

