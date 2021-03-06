## Hystrix

### 服务的消费方: api-gateway中引入pom

### application.properties

```properties
management.port = 8023
#超时时间
hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds=1
#最小线程数
hystrix.threadpool.default.coreSize=1
#最大队列
hystrix.threadpool.default.maxQueueSize=1
hystrix.threadpool.default.maximumSize=1
hystrix.command.default.circuitBreaker.errorThresholdPercentage=1
#进入断路之后, 多久可以重新调用本服务
hystrix.command.default.circuitBreaker.sleepWindowInMilliseconds=100000
```

### UserController

```java
//专门针对用户服务的配置
@Repository
@DefaultProperties(groupKey = "userDao",
        commandProperties = {@HystrixProperty(name = "execution.isolation.thread.timeoutInMilliseconds", value = "2000")},
        threadPoolProperties = {@HystrixProperty(name = "coreSize", value = "10")
                , @HystrixProperty(name = "maxQueueSize", value = "1000")},
        threadPoolKey = "userDao"
)
public class UserDao {

    @Autowired
    private GenericRest rest;

    @Value("${user.service.name}")
    private String userServiceName;

    @HystrixCommand
    public List<User> getUserList(User query) {
        ResponseEntity<RestResponse<List<User>>> resultEntity = rest.post("http://" + userServiceName + "/user/getList", query, new ParameterizedTypeReference<RestResponse<List<User>>>() {
        });
        RestResponse<List<User>> restResponse = resultEntity.getBody();
        if (restResponse.getCode() == 0) {
            return restResponse.getResult();
        } else {
            return null;
        }
    }

    //降级方法, 参数要一直, 方法名可以不一致
    public User getUserByTokenFb(String token) {
        return new User();
    }

    /**
     * 调用鉴权服务
     */
    @HystrixCommand(fallbackMethod = "getUserByTokenFb")
    public User getUserByToken(String token) {
        String url = "http://" + userServiceName + "/user/get?token=" + token;
        ResponseEntity<RestResponse<User>> responseEntity = rest.get(url, new ParameterizedTypeReference<RestResponse<User>>() {
        });
        RestResponse<User> response = responseEntity.getBody();
        if (response == null || response.getCode() != 0) {
            return null;
        }
        return response.getResult();
    }
}
```

### 在启动类上加@EnableCircuitBreaker



### 监控面板

#### 1. 在启动类上加@EnableHystrixDashboard

#### 2. server.port = 9097

#### 3. 输入: http://localhost:9097/hystrix

#### 4. 在页面上输入地址, 就是api-gateway中management.port暴露的地址: http://localhost:8023/hystrix.stream

#### 5. 然后启动api-gateway, 然后访问其接口, 就可以看到监控信息