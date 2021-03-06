## Ribbon

1. api-gateway服务消费者, 本身已经是eureka client. 而eureka中已经依赖了ribbon, 所以, pom文件中不需要再次引入.
2. 在api-gateway的服务消费者的项目中, 单独引入ribbon的依赖, 然后在配置文件中加入
3. `user.ribbon.listOfServers=127.0.0.1:8083,127.0.0.1:8084`

> DefaultClientConfigUrl#loadProperties中有上述配置的信息
>
> IClientConfig -> DefaultClientConfigUrl
>
> IPing -> NoOpPing(每隔10秒, 向服务提供者user发送心跳确认信息)



### 自定义配置Ribbon

#### 在启动类上加上注解

```java
//使用服务提供者user的时候, 使用NewRuleConfig
@RibbonClient(name="user", configuration=NewRuleConfig.class)
```

#### 创建NewRuleConfig.java

```java
public class NewRuleConfig {
    @Autowired
    private IClientConfig ribbonClientConfig;
    
    //加上这个配置, 则不会请求那些已经失效的服务提供方
    @Bean
    public IPing ribbonPing(IClientConfig config) {
        return new PingUrl(false, "/health"); //每次进行健康检查时, 向服务提供者user请求的url. 因为服务提供者引入了actuator依赖, 所以有/health依赖
    }
    
    //负载均衡规则
    @Bean
    public IRule ribbonRule(IClientConfig config) {
//		return new RandomRule();
        //更智能, 会对调用成功或者失败做记录, 下次做负载均衡的时候, 会优先选择那些调用成功的服务提供者
        return new AvailabilityFilteringRule();
    }
}
```

#### 原理

@LoadBalanced(来自springcloud-common) -> LoadBalancerAutoConfiguration

spring自动创建LoadBalancerAutoConfiguration中的一些@Bean类, 其中的loadBalancedRestTemplateInitializer方法做了RestTemplate定制化

还可以再本类中找到LoadBalanceInterceptor, 也就是说, 对加了@LoadBalanced注解的RestTemplate加了拦截器
这个拦截器, 就是LoadBalanceInterceptor

进入LoadBalanceInterceptor, 其中有intercept方法, 对请求的request做拦截, 使用LoadBalancerClient.execute方法

RibbonLoadBalanceClient#execute -> #getLoadBalancer, 目的是加在spring为user服务单独创建了ApplicationContext

然后getServer()就是做负载均衡. 我们配置的各种策略都是放在ILoadBalancer类中的



### LogBook的引入

#### pom.xml

```xml
<logbook.version>1.3.0</logbook.version>
<dependency>
	<groupId>org.zalando</groupId>
    <artifactId>logbook-core</artifactId>
    <version>${logbook.version}</version>
</dependency>
<dependency>
    <groupId>org.zalando</groupId>
    <artifactId>logbook-servlet</artifactId>
    <version>${logbook.version}</version>
</dependency>
<dependency>
    <groupId>org.zalando</groupId>
    <artifactId>logbook-httpclient</artifactId>
    <version>${logbook.version}</version>
</dependency>
<dependency>
    <groupId>org.zalando</groupId>
    <artifactId>logbook-spring-boot-starter</artifactId>
    <version>${logbook.version}</version>
</dependency>
```

#### application.properties

```properties
logbook.write.level=INFO
logbook.format.style=http
```

#### 添加拦截器

```java
@Bean
@ConditionalOnMissingBean(HttpClient.class)
public HttpClient httpClient() {
    RequestConfig requestConfig = RequestConfig.custom()
            .setConnectTimeout(properties.getConnectTimeOut())
            .setSocketTimeout(properties.getSocketTimeOut()).build();// 构建requestConfig
    HttpClient client = HttpClientBuilder.create().setDefaultRequestConfig(requestConfig)
            .setUserAgent(properties.getAgent())
            .setMaxConnPerRoute(properties.getMaxConnPerRoute())
            .setMaxConnTotal(properties.getMaxConnTotaol())
            
            // add LogBook Interceptor
            // 客户端的请求的interceptor配置开启
            // 服务端的默认开启
            .addInterceptorFirst(logbookHttpRequestInterceptor)
            .addInterceptorFirst(logbookHttpResponseInterceptor)
            
            .build();
    return client;
}
```

