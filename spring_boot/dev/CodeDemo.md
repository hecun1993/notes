## RestTemplate

* ClientHttpRequestFactory 接口有两个实现类 SimpleClientHttpRequestFactory 和 HttpComponentsClientHttpRequestFactory. 
* 前者是由javase内置实现的, 后者是由apache的 commons-httpclient 依赖提供的 HttpClient

### HttpComponentsClientHttpRequestFactory

可以配置连接池, ssl证书等信息. 比 SimpleClientHttpRequestFactory 功能更强大

* RestTemplate的简单配置方式 

```java
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate(ClientHttpRequestFactory factory) {
        return new RestTemplate(factory);
    }

    @Bean
    public ClientHttpRequestFactory simpleClientHttpRequestFactory() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        //单位是ms
        factory.setReadTimeout(5000);
        //单位是ms
        factory.setConnectTimeout(15000);
        return factory;
    }
}
```

实例

```java
// 设置header信息
HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
headers.set("Cookie", cookie);

// 设置post请求参数
MultiValueMap<String, String> map = new LinkedMultiValueMap<>();
map.add("format", "json");
map.add("maxDataPoints", "401");

// 整合header和请求参数
HttpEntity<MultiValueMap<String, String>> httpEntity = new HttpEntity<>(map, headers);
RestTemplate restTemplate = new RestTemplate();
String response = restTemplate.postForEntity(getDataUrl, request, String.class).getBody();

//====================================
//Gson解析复杂的response
Gson gson = new Gson();
JsonParser parser = new JsonParser();
//把json字符串转成JsonArray [{}, {}...]
JsonArray jsonArray = parser.parse(response).getAsJsonArray();
//[{}] -> {"datapoints":  [[], [], []...]} -> [[], [], []...]
JsonElement datapoints = jsonArray.get(0).getAsJsonObject().get("datapoints");
//把JsonElement变成List, List中放着的是Object, 实际上还是List
Type type = new TypeToken<List<Object>>() {}.getType();
List<Object> datapointList = gson.fromJson(datapoints, type);
```



### 通过HttpClient获取cookie信息

```java
public static String getCookie(String loginUser, String loginPassword) {
    // 创建HttpClient类
    HttpClient httpClient = new HttpClient();
    // 模拟登陆，发送post请求
    PostMethod postMethod = new PostMethod(LOGIN_URL);

    // 设置登陆时要求的信息，用户名和密码
    NameValuePair[] data = {new NameValuePair("user", loginUser), new NameValuePair("password", loginPassword), new NameValuePair("email", "")};
    postMethod.setRequestBody(data);
    try {
        // 设置 HttpClient 接收 Cookie,用与浏览器一样的策略
        httpClient.getParams().setCookiePolicy(CookiePolicy.BROWSER_COMPATIBILITY);
        httpClient.executeMethod(postMethod);

        // 获得登陆后的 Cookie
        Cookie[] cookies = httpClient.getState().getCookies();

        StringBuilder finalCookie = new StringBuilder();
        for (Cookie cookie : cookies) {
            finalCookie.append(cookie.toString() + ";");
        }

        return finalCookie.toString().substring(0, finalCookie.length() - 1);
    } catch (Exception e) {
        log.error("can't get correct cookies for grafana!");
    }

    return "";
}
```

### 通过OkHttp发送请求

```java
private static final okhttp3.OkHttpClient client = new okhttp3.OkHttpClient();

public static String getDataFromCMDB(String params) throws Exception {

    HttpUrl url = HttpUrl.parse("http://cmdb.elenet.me")
        .newBuilder()
        .addPathSegment("v1")
        .addPathSegment("entity")
        .addPathSegment("_search")
        .addQueryParameter("q", params)
        .addQueryParameter("page", "1")
        .addQueryParameter("size", "1000")
        .build();
    Request request = new Request.Builder()
        .url(url)
        .addHeader("content-type", "application/json; charset=utf-8")
        .addHeader("X-Client-ID", UID)
        .get()
        .build();
    Response response = null;
    try {
        response = client.newCall(request).execute();
        if (response.isSuccessful()) {
            return response.body().string();
        }
    } catch (IOException e) {
        log.error("IO error " + e);
    } finally {
        if (response != null) {
            response.body().close();
        }
    }
    return null;
}
```



## CorsConfig 允许跨域配置

```java
@Configuration
public class CorsConfig extends WebMvcConfigurerAdapter {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("*")
                .allowCredentials(true)
                .allowedMethods("GET", "POST", "DELETE", "PUT")
                .maxAge(3600);
    }
}
```



## Mongo与Spring Boot的整合

### 单数据源

引入pom依赖: spring-boot-starter-data-mongodb

```properties
spring.data.mongodb.uri=mongodb://name:pass@localhost:27017/test
# 多集群配置
spring.data.mongodb.uri=mongodb://user:pwd@ip1:port1,ip2:port2/database
```

单数据源可以不配置MongoDBFactory, 直接在DAO类中用@Autowired注入MongoTemplate

```java
@Autowired
private MongoTemplate mongoTemplate;

//MongoTemplate的API
//1. 查询操作
Query query = new Query();
query.addCriteria(Criteria.where("email").is(email).and("_id").is(new ObjectId(id)));
//分页, 排序查询
query.with(new Sort(Sort.Direction.DESC, Constants.START));
int skip = (pageModel.getPageNo() - 1 > 0) ? pageModel.getPageNo() - 1 : 0;
query.skip(skip * pageModel.getPageSize()).limit(pageModel.getPageSize());

//2. 更新操作
Query query = new Query(Criteria.where("id").is(user.getId()));
Update update = new Update();
update.set("userName", user.getUserName()).set("passWord", user.getPassWord());

UserEntity user = mongoTemplate.findOne(query, UserEntity.class);
//更新查询返回结果集的第一条
mongoTemplate.updateFirst(query, update, UserEntity.class);
//更新查询返回结果集的所有
mongoTemplate.updateMulti(query, update, UserEntity.class);
```

> ```
> MongoDB中存储的是标准时间，而通过System.currentTimeMillis()获得的是当前时区的时间，快8个小时.
> ```



* 配置文件的写法

```java
@Configuration
public class MultipleMongoConfig {

    @Autowired
    private MongoProperties mongoProperties;

    @Bean
    public MongoTemplate mongoTemplate() throws Exception {
        return new MongoTemplate(primaryFactory(mongoProperties));
    }

    @Bean
    public MongoDbFactory mongoDbFactory(MongoProperties mongoProperties) throws Exception {
        return new SimpleMongoDbFactory(new MongoClient(mongo.getHost(), mongo.getPort()), mongo.getDatabase());
    }
}
```



### 多数据源

1. yml文件

   ```yaml
   mongodb:
     primary:
       host: 192.168.9.60
       port: 20000
       database: test
     secondary:
       host: 192.168.9.60
       port: 20000
       database: test1
   ```

2. 读取不同的配置文件 && 不同包使用不同的数据源

   ```java
   @Data
   @ConfigurationProperties(prefix = "mongodb")
   public class MultipleMongoProperties {
       private MongoProperties primary = new MongoProperties();
       private MongoProperties secondary = new MongoProperties();
   }

   //不同数据源对应不同的包
   @Configuration
   @EnableMongoRepositories(basePackages = "com.neo.model.repository.primary",
           mongoTemplateRef = PrimaryMongoConfig.MONGO_TEMPLATE)
   public class PrimaryMongoConfig {
       protected static final String MONGO_TEMPLATE = "primaryMongoTemplate";
   }

   @Configuration
   @EnableMongoRepositories(basePackages = "com.neo.model.repository.secondary",
           mongoTemplateRef = SecondaryMongoConfig.MONGO_TEMPLATE)
   public class SecondaryMongoConfig {
       protected static final String MONGO_TEMPLATE = "secondaryMongoTemplate";
   }
   ```

3. 配置文件

   ```java
   @Configuration
   public class MultipleMongoConfig {
       
       @Autowired
       private MultipleMongoProperties mongoProperties;

       @Primary
       @Bean(name = PrimaryMongoConfig.MONGO_TEMPLATE)
       public MongoTemplate primaryMongoTemplate() throws Exception {
           return new MongoTemplate(primaryFactory(this.mongoProperties.getPrimary()));
       }

       @Bean
       @Qualifier(SecondaryMongoConfig.MONGO_TEMPLATE)
       public MongoTemplate secondaryMongoTemplate() throws Exception {
           return new MongoTemplate(secondaryFactory(this.mongoProperties.getSecondary()));
       }

       @Bean
       @Primary
       public MongoDbFactory primaryFactory(MongoProperties mongo) throws Exception {
           return new SimpleMongoDbFactory(new MongoClient(mongo.getHost(), mongo.getPort()),
                   mongo.getDatabase());
       }

       @Bean
       public MongoDbFactory secondaryFactory(MongoProperties mongo) throws Exception {
           return new SimpleMongoDbFactory(new MongoClient(mongo.getHost(), mongo.getPort()),
                   mongo.getDatabase());
       }
   }
   ```

   ​







## 分页操作

### 第一种方式

1.定义PageModel<T> 

```java
//PageModel对象, 有pageNo和pageSize两个默认值, 总共有四个属性, 还有一个方法
Data
@NoArgsConstructor
@AllArgsConstructor
public class PageModel<T> {
    //分页查询得到的结果集
    private List<T> datas;
    //总记录数
    private int rowCount;
    //每页显示条数
    private int pageSize = 10;
    //第几页
    private int pageNo = 1;

    //总页数
    public int getTotalPage() {
        return (rowCount + pageSize - 1) / pageSize;
    }
}
```

2.在controller中, 将PageModel当成controller方法的参数, 传入service层. 此时, 传入service层的PageModel, 要么是只有pageNo和pageSize默认值, 其他属性都为空; 要么就是通过postman等工具添加了pageNo和pageSize请求参数, 其他属性都为空的PageModel.

3.repository层的代码, 相当于为PageModel添加了rowCount属性和datas属性. 总页数就可以计算出来. 然后返回经过**填充**的PageModel<Result>

```java
//repository
public PageModel<Result> findResultsByPageModel(Date start, Date end, PageModel<Result> pageModel) {
    Query query = new Query();
query.addCriteria(Criteria.where(Constants.START).gte(start).and("end").lte(end).and(Constants.STORY).is(Constants.PERFTEST));
    
    //总记录数
    int rowCount = (int) mongoTemplate.count(query, Result.class);
    pageModel.setRowCount(rowCount);

    //倒序查询得到结果
    query.with(new Sort(Sort.Direction.DESC, Constants.START));

    //验证需要跳过的数据条数
    int skip = (pageModel.getPageNo() - 1 >= 0) ? pageModel.getPageNo() - 1 : 0;
    query.skip(skip * pageModel.getPageSize()).limit(pageModel.getPageSize());

    List<Result> resultList = mongoTemplate.find(query, Result.class);
    pageModel.setDatas(resultList);

    return pageModel;
}

//service
public PageModel<Result> findForewarningByPageModel(Date start, Date end, PageModel<Result> pageModel) {
    return resultRepository.findResultsByPageModel(start, end, pageModel);
}

//controller
@GetMapping("/test")
public ResponseEntity<GeneralResponse> getForewarning(PageModel<Result> pageModel,
                                                      @RequestParam(value = "start", required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm") Date start,
                                                      @RequestParam(value = "end", required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm") Date end) {
    PageModel<Result> pageModelResult = resultService.findForewarningByPageModel(start, end, pageModel);
    GeneralResponse generalResponse = new GeneralResponse(ResponseStatus.SUCCESS, "get forewarning results success", pageModelResult);
    return new ResponseEntity<>(generalResponse, HttpStatus.OK);
}
```





## 项目的请求返回类集合

### 第一种方式

```java
public class GeneralResponse {
    private ResponseStatus status;
    private String message;
    private Object data;
}

public enum ResponseStatus {
    SUCCESS,
    ERROR,
    INVALID_REQUEST
}

@GetMapping("/isfinished")
public ResponseEntity<GeneralResponse> isFinished(@RequestParam("roundId") String roundId) {
    Result result = resultService.getResultByRoundId(roundId);
    GeneralResponse generalResponse = new GeneralResponse(ResponseStatus.SUCCESS, "get result success", result);
    return new ResponseEntity<>(generalResponse, HttpStatus.OK);
}
```



## HttpMessageConverter

HttpMessageConverter<T> 是 Spring3.0 新添加的一个接口，负责将请求信息转换为一个对象（类型为 T），将对象（类型为T）输出为响应信息 

（1）**HttpInputMessage **将请求的信息先转为 **InputStream** 对象，InputStream 再由 **HttpMessageConverter** 转换为 SpringMVC 需要的java对象；

（2）SpringMVC 返回一个 java 对象， 并通过 HttpMessageConverter 转为响应信息，接着 **HttpOutputMessage** 将响应的信息转换为 **OutputStream**，接着给出响应。

1.DispatcherServlet 默认加载 HttpMessageConveter的6个实现类

2.加入 jackson jar包后，启动的时候加载7个HttpMessageConverter 的实现类

注意: 当控制器处理方法使用@RequestBody, 或者@ResponseBody时, spring首先根据请求头或响应头中的Accept属性, 选择匹配的HttpMessageConverter, 

自定义自己的消息转换器

```java
@Component
public class CustomJsonHttpMessageConverter implements HttpMessageConverter {

    //Jackson的json映射类
    private ObjectMapper objectMapper = new ObjectMapper();

    //该转换器支持的类型
    private List supportedMediaTypes = Arrays.asList(MediaType.APPLICATION_JSON);

    /**
     * 判断转换器是否可以将输入内容转换成 Java 类型
     *
     * @param clazz     需要转换的 Java 类型
     * @param mediaType 该请求的 MediaType
     * @return
     */
    @Override
    public boolean canRead(Class clazz, MediaType mediaType) {
        if (mediaType == null) {
            return true;
        }

        for (MediaType supportedMediaType : getSupportedMediaTypes()) {
            if (supportedMediaType.includes(mediaType)) {
                return true;
            }
        }

        return false;
    }

    /**
     * 判断转换器是否可以将 Java 类型转换成指定输出内容
     *
     * @param clazz     需要转换的 Java 类型
     * @param mediaType 该请求的 MediaType
     * @return
     */
    @Override
    public boolean canWrite(Class clazz, MediaType mediaType) {
        if (mediaType == null || MediaType.ALL.equals(mediaType)) {
            return true;
        }

        for (MediaType supportedMediaType : getSupportedMediaTypes()) {
            if (supportedMediaType.includes(mediaType)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 获得该转换器支持的 MediaType
     *
     * @return
     */
    @Override
    public List<MediaType> getSupportedMediaTypes() {
        return supportedMediaTypes;
    }

    /**
     * 读取请求内容，将其中的 Json 转换成 Java 对象
     *
     * @param clazz        需要转换的 Java 类型
     * @param inputMessage 请求对象
     * @return
     * @throws IOException
     * @throws HttpMessageNotReadableException
     */
    @Override
    public Object read(Class clazz, HttpInputMessage inputMessage) throws IOException, HttpMessageNotReadableException {
        return objectMapper.readValue(inputMessage.getBody(), clazz);
    }

    /**
     * 将 Java 对象转换成 Json 返回内容
     *
     * @param o             需要转换的对象
     * @param contentType   返回类型
     * @param outputMessage 回执对象
     * @throws IOException
     * @throws HttpMessageNotWritableException
     */
    @Override
    public void write(Object o, MediaType contentType, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException {
        objectMapper.writeValue(outputMessage.getBody(), o);
    }
}

```

```java
@Configuration
public class HttpMessageConverterConfig {

    @Bean
    public MappingJackson2HttpMessageConverter mappingJackson2HttpMessageConverter() {
        return new MappingJackson2HttpMessageConverter() {
            @Override
            protected void writeInternal(Object o, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException {
                ObjectMapper objectMapper = new ObjectMapper();
                String json = objectMapper.writeValueAsString(o);
                //加密
                String result = json + "加密";
                outputMessage.getBody().write(result.getBytes());
            }
        };
    }
}
```

```java
@Configuration
public class MyWebMvcConfigurer extends WebMvcConfigurerAdapter {

    @Autowired
    private MappingJackson2HttpMessageConverter mappingJackson2HttpMessageConverter;

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        converters.add(mappingJackson2HttpMessageConverter);
        super.configureMessageConverters(converters);
    }
}
```





## 其他操作

### 格式化打印某一对象

```java
@Slf4j
log.debug(ReflectionToStringBuilder.toString(queryResult, ToStringStyle.MULTI_LINE_STYLE));
```

### InfluxDB的操作

```yaml
spring:  
  influxdb:
    url: http://adco-esm-relay-1.vm.elenet.me:6666
    username: root
    password: root
    database: esm
    retention-policy: autogen
```

```java
@Autowired
private InfluxDBTemplate<?> influxDBTemplate;

Query query = new Query(expression, database);
QueryResult queryResult = influxDBTemplate.query(query);
List<QueryResult.Result> results = queryResult.getResults();
if (results != null) {
    for (QueryResult.Result result : results) {
        List<QueryResult.Series> resultSeries = result.getSeries();
        if (resultSeries != null) {
            Map<String, String> tags = resultSeries.get(i).getTags();
            List<List<Object>> values = resultSeries.get(i).getValues();
        }
    }
}
```

### Stream

1.Stream 不是集合元素，它不是数据结构并不保存数据，它是有关算法和计算的

2.Stream 就如同一个迭代器（Iterator），单向，不可往复，数据只能遍历一次，遍历过一次后即用尽了，就好比流水从面前流过，一去不复返。

3.Stream 可以并行化操作. Stream 的并行操作依赖于 Java7 中引入的 Fork/Join 框架（JSR166y）来拆分任务和加速处理过程。Stream 的另外一大特点是，数据源本身可以是无限的。

4.stream方法在任何Collection接口的子类中都有, 其返回值是一个Stream流对象

```java
//Collection接口中的默认方法
default Stream<E> stream() {
    return StreamSupport.stream(spliterator(), false);
}
default Stream<E> parallelStream() {
    return StreamSupport.stream(spliterator(), true);
}
```

5.这个Stream对象有很多方法, 比如map, flatMap, forEach, reduce, collect...

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
//最后输出的顺序不是List中的顺序
numbers.parallelStream().forEach(out::println);
//最后输出的顺序仍然是List中的顺序
numbers.parallelStream().forEachOrdered(out::println); 
```

### SpecialBeanUtils

```java
public class SpecificBeanUtils extends BeanUtils {

    private SpecificBeanUtils() {
    }

    /**
     * Override copyProperties method
     * in order not to copy the field when its value is null
     *
     * @param source
     * @param target
     * @throws BeansException
     */
    public static void copyProperties(Object source, Object target) {
        Class<?> actualEditable = target.getClass();
        PropertyDescriptor[] targetPds = getPropertyDescriptors(actualEditable);
        for (PropertyDescriptor targetPd : targetPds) {
            if (targetPd.getWriteMethod() != null) {
                PropertyDescriptor sourcePd = getPropertyDescriptor(
                        source.getClass(), targetPd.getName());
                if (sourcePd != null && sourcePd.getReadMethod() != null) {
                    try {
                        Method readMethod = sourcePd.getReadMethod();
                        if (!Modifier.isPublic(readMethod.getDeclaringClass().getModifiers())) {
                            readMethod.setAccessible(true);
                        }
                        Object value = readMethod.invoke(source);

                        if (value != null) {
                            Method writeMethod = targetPd.getWriteMethod();
                            if (!Modifier.isPublic(writeMethod.getDeclaringClass().getModifiers())) {
                                writeMethod.setAccessible(true);
                            }
                            writeMethod.invoke(target, value);
                        }
                    } catch (Exception ex) {
                        throw new FatalBeanException(
                                "Could not copy properties from source to target", ex);
                    }
                }
            }
        }
    }
}
```

### 通过线程id获取某一线程

```java
public class ThreadUtil {
	//对工具类, 要给这个类加上私有的构造函数
    private ThreadUtil() {
    }

    /**
     * 根据线程id获取某一线程
     * @param threadId
     * @return
     */
    public static Thread findThread(long threadId) {
        ThreadGroup group = Thread.currentThread().getThreadGroup();
        while(group != null) {
            Thread[] threads = new Thread[(int)(group.activeCount() * 1.2)];
            int count = group.enumerate(threads, true);
            for(int i = 0; i < count; i++) {
                if(threadId == threads[i].getId()) {
                    return threads[i];
                }
            }
            group = group.getParent();
        }
        return null;
    }
}
```

### UUIDUtils

```java
public class UuidUtil {

    private UuidUtil() {
    }

    private static final String[] CHARS = new String[]{
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C",
            "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
            "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"};

    /**
     * like 550E8400-E29B-11D4-A716-446655440000
     *
     * @return
     */
    public static String genTypicalUuid() {
        return UUID.randomUUID().toString();
    }

    private static String genUuid(int length, int radix) {
        StringBuilder buffer = new StringBuilder();
        String uuid = UUID.randomUUID().toString().replace("-", "");
        IntStream.range(0, length).forEach(i -> {
            String str = uuid.substring(i * 4, i * 4 + 4);
            int x = Integer.parseInt(str, radix);
            buffer.append(CHARS[x % 0x3E]);
        });
        return buffer.toString();
    }

    /**
     * like 5Ts8MFp3
     *
     * @return
     */
    public static String genShortUuid() {
        return genUuid(8, 16);
    }

}
```

或者可以使用commons-lang中提供的方法

```java
RandomStringUtils.randomAlphabetic(10);
```



### springboot中的异步任务

1.首先定义AsyncTask类, 加上@Component注解, 在其中定义几个方法, 分别在方法上加上@Async注解

2.在另外一个类(controller)中, @Autowired这个AsyncTask类, 然后在本类的一个方法中, 调用AsyncTask类中的方法即可.

3.在启动类上加上@EnableAsync, @EnableScheduling

```java
@Component
public class AsyncTask {
	
    @Async
    public void startMonitorSystem(String roundId) {
        MonitorController.threadIdMap.put("SystemThreadId", Thread.currentThread().getId());
        try {
            log.info("Begin monitor system matrix, roundId: {}", roundId);
            monitorService.monitorSystemMatrix(requestNum, roundId, source);
        } catch (Exception e) {
            log.info("System Monitor thread is killed, roundId: {}, {}", roundId, e.getMessage());
        }
    }

    @Async
    public void startMonitorUser(String roundId) {
        MonitorController.threadIdMap.put("UserThreadId", Thread.currentThread().getId());
        try {
            log.info("Begin monitor user matrix, roundId: {}", roundId);
            monitorService.monitorUserMatrix(requestNum, roundId);
        } catch (Exception e) {
            log.info("Custom Monitor thread is killed, roundId: {}, {}", roundId, e.getMessage());
        }
    }
}
```

```java
@RestController
@RequestMapping("/monitor")
@Slf4j
public class MonitorController {
    /**
     * 存储正在运行的线程id
     */
    public static Map<String, Long> threadIdMap = new HashMap<>();

    @Autowired
    private AsyncTask monitorTask;
    
    @GetMapping("/begin")
    public ResponseEntity<GeneralResponse> begin() {
        //开始监控
        monitorTask.startMonitorSystem(roundId);
        monitorTask.startMonitorUser(roundId);
    }
}
```

### 漏桶算法

```java
@Override
public void monitorUserMatrix(int requestNum, String roundId) {
    List<Mapping> mappings = mappingService.getAllCustomMapping();

    //1. 规定每秒可以发requestNum个请求
    RateLimiter rateLimiter = RateLimiter.create(requestNum, 1, TimeUnit.SECONDS);
	
    //不断循环
    while (!Thread.currentThread().isInterrupted()) {
        for (Mapping mapping : mappings) {
            //2. 获得执行的权限, 从而实现每秒可以发多少个请求
            rateLimiter.acquire();
            log.info("Custom monitor, matrix is {}, source is {}", mapping.getMatrix(), mapping.getSource());
            recordService.saveUserMatrix(mapping.getMatrix(), mapping.getSource(), roundId);
        }
    }
}
```

### 拦截器的简单配置

```java
@Slf4j
public class LoginHandlerInterceptor extends HandlerInterceptorAdapter {
    @Override
    public boolean preHandle(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, Object o) throws Exception {
        SSOUser user = (SSOUser) httpServletRequest.getSession().getAttribute("user");
        if (user != null) {
            return true;
        }
        httpServletResponse.sendError(HttpServletResponse.SC_UNAUTHORIZED);
        return false;
    }
}

```

### 先查缓存再查数据库

```java
//直接引入spring-redis依赖即可, 不用做java配置, 可以添加properties中的连接池配置

@Autowired
private StringRedisTemplate redisTemplate;

/**
     * 1.首先通过缓存获取
     * 2.不存在将从通过数据库获取用户对象
     * 3.将用户对象写入缓存，设置缓存时间5分钟
     * 4.返回对象
     *
     * @param id
     * @return
 */
public User getUserById(Long id) {
    String key = "user:" + id;
    String json = redisTemplate.opsForValue().get(key);
    User user = null;
    if (Strings.isNullOrEmpty(json)) {
        user = userMapper.selectById(id);
        String string = JSON.toJSONString(user);
        redisTemplate.opsForValue().set(key, string);
        redisTemplate.expire(key, 5, TimeUnit.MINUTES);
    } else {
        user = JSON.parseObject(json, User.class);
    }
    return user;
}
```

```properties
# spring为redis提供了默认的连接池
# 定义最大连接数
spring.redis.pool.max-active=3
spring.redis.host=localhost
spring.redis.port=6379
spring.redis.timeout=6000
```

### 注册用户为密码md5加密的工具类

```java
//需要借助Guava
public class HashUtils {
    private static final HashFunction FUNCTION = Hashing.md5();
    private static final HashFunction MURMUR_FUNC = Hashing.murmur3_128();
    private static final String SALT = "mooc.com";

    //为密码加盐并加密
    public static String encryPassword(String password) {
        HashCode code = FUNCTION.hashString(password + SALT, Charset.forName("UTF-8"));
        return code.toString();
    }

    //加密的方法
    public static String hashString(String input) {
        HashCode code = null;
        try {
            code = MURMUR_FUNC.hashBytes(input.getBytes("utf-8"));
        } catch (UnsupportedEncodingException e) {
            Throwables.propagate(e);
        }
        return code.toString();
    }
}
```

### 自动更新数据库的插入和更新时间

```java
public class BeanHelper {
    private static final String updateTimeKey = "updateTime";
    private static final String createTimeKey = "createTime";

    public static <T> void setDefaultProp(T target, Class<T> clazz) {
        PropertyDescriptor[] descriptors = PropertyUtils.getPropertyDescriptors(clazz);
        for (PropertyDescriptor propertyDescriptor : descriptors) {
            String fieldName = propertyDescriptor.getName();
            Object value;
            try {
                value = PropertyUtils.getProperty(target, fieldName);
            } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
                throw new RuntimeException("can not set property  when get for " + target + " and clazz " + clazz + " field " + fieldName);
            }
            if (String.class.isAssignableFrom(propertyDescriptor.getPropertyType()) && value == null) {
                try {
                    PropertyUtils.setProperty(target, fieldName, "");
                } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
                    throw new RuntimeException("can not set property when set for " + target + " and clazz " + clazz + " field " + fieldName);
                }
            } else if (Number.class.isAssignableFrom(propertyDescriptor.getPropertyType()) && value == null) {
                try {
                    BeanUtils.setProperty(target, fieldName, "0");
                } catch (Exception e) {
                    throw new RuntimeException("can not set property when set for " + target + " and clazz " + clazz + " field " + fieldName);
                }
            }
        }
    }

    public static <T> void onUpdate(T target) {
        try {
            PropertyUtils.setProperty(target, updateTimeKey, System.currentTimeMillis());
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
            return;
        }
    }

    public static <T> void onInsert(T target) {
        long time = System.currentTimeMillis();
        Date date = new Date(time);
        try {
            PropertyUtils.setProperty(target, updateTimeKey, date);
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
        }
        try {
            PropertyUtils.setProperty(target, createTimeKey, date);
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
        }
    }
}

//调用时
BeanHelper.onInsert(user);
```

### 一种自定义异常的方法

```java
public class UserException extends RuntimeException implements WithTypeException {
    private static final long serialVersionUID = 1L;
    private Type type;

    public UserException(String message) {
        super(message);
        this.type = Type.LACK_PARAMTER;
    }

    public UserException(Type type, String message) {
        super(message);
        this.type = type;
    }

    public Type type() {
        return type;
    }

    public enum Type {
        WRONG_PAGE_NUM, LACK_PARAMTER, USER_NOT_LOGIN, USER_NOT_FOUND, USER_AUTH_FAIL;
    }
}

/**
 * 包含类型的异常
 */
public interface WithTypeException {
}

//使用
if (StringUtils.isBlank(email)) {
    throw new UserException(UserException.Type.USER_NOT_FOUND, "无效的key");
}

@ControllerAdvice
public class GlobalExceptionHandler {
    
//    @Autowired
//    private Tracer tracer;

    private static final Logger LOGGER = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(value = Throwable.class)
    @ResponseBody
    public RestResponse<Object> handler(Throwable throwable) {
        //输出日志
        LOGGER.error(throwable.getMessage(), throwable);

//	    tracer.addTag(Span.SPAN_ERROR_TAG_NAME, ExceptionUtils.getExceptionMessage(throwable));
//	    System.out.println(tracer.getCurrentSpan().getTraceId());

        RestCode restCode = Exception2CodeRepo.getCode(throwable);
        return new RestResponse<>(restCode.code, restCode.msg);
    }

}

public class Exception2CodeRepo {

    private static final ImmutableMap<Object, RestCode> MAP = ImmutableMap.<Object, RestCode>builder()
            .put(IllegalParamsException.Type.WRONG_PAGE_NUM, RestCode.WRONG_PAGE)
            .put(IllegalStateException.class, RestCode.UNKNOWN_ERROR)
            .put(UserException.Type.USER_NOT_LOGIN, RestCode.TOKEN_INVALID)
            .put(UserException.Type.USER_NOT_FOUND, RestCode.USER_NOT_EXIST)
            .put(UserException.Type.USER_AUTH_FAIL, RestCode.USER_NOT_EXIST).build();

    private static Object getType(Throwable throwable) {
        try {
            return FieldUtils.readDeclaredField(throwable, "type", true);
        } catch (Exception e) {
            return null;
        }
    }

    public static RestCode getCode(Throwable throwable) {
        //返回未知异常
        if (throwable == null) {
            return RestCode.UNKNOWN_ERROR;
        }

        Object target = throwable;
        if (throwable instanceof WithTypeException) {
            //获取异常的类型
            Object type = getType(throwable);
            if (type != null) {
                target = type;
            }
        }

        RestCode restCode = MAP.get(target);
        if (restCode != null) {
            return restCode;
        }

        Throwable rootCause = ExceptionUtils.getRootCause(throwable);
        if (rootCause != null) {
            return getCode(rootCause);
        }

        return restCode.UNKNOWN_ERROR;
    }
}


/**
 * 包含类型的异常
 */
public interface WithTypeException {
}

//非法参数异常
public class IllegalParamsException extends RuntimeException implements WithTypeException {

    private static final long serialVersionUID = 1L;

    private Type type;

    public IllegalParamsException() {
    }

    public IllegalParamsException(Type type, String msg) {
        super(msg);
        this.type = type;
    }

    public Type type() {
        return type;
    }

    public enum Type {
        WRONG_PAGE_NUM, WRONG_TYPE
    }
}
```



===========================================================

### 1. 两种实现自动注入的方法

1. 创建 @EnableHttpClient 注解, 在注解上引入`HttpClientAutoConfiguration`自动配置类. 然后在启动类上加 @EnableHttpClient 注解

2. 在resources/META-INF/spring.factories中加上: 

   ```properties
   org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
   com.mooc1.house.autoconfig.HttpClientAutoConfiguration
   ```

注意, 如果上述的包名不是mooc1而是mooc, 则不需要添加这个配置文件. 因为在启动类的子包下.

两种方法都需要编写HttpClientAutoConfiguration.java

```java
package com.mooc1.house.autoconfig;

import org.apache.http.client.HttpClient;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.impl.NoConnectionReuseStrategy;
import org.apache.http.impl.client.HttpClientBuilder;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration //配置类
@ConditionalOnClass({HttpClient.class}) //当引入HttpClient的jar包后 下面的配置才会生效
@EnableConfigurationProperties(HttpClientProperties.class) //从配置文件中获得属性
public class HttpClientAutoConfiguration {
  //通过构造器注入HttpClientProperties
    private final HttpClientProperties properties;
  public HttpClientAutoConfiguration(HttpClientProperties properties){
    this.properties = properties;
  }
  
  /**
   * httpclient bean 的定义
   */
  @Bean //定义注入spring上下文中的Bean
  @ConditionalOnMissingBean(HttpClient.class) //如果上下文中没有HttpClient的Bean, 才会创建
  public HttpClient httpClient(){
    RequestConfig requestConfig = RequestConfig.custom().setConnectTimeout(properties.getConnectTimeOut())
        .setSocketTimeout(properties.getSocketTimeOut()).build();//构建requestConfig
    HttpClient client = HttpClientBuilder.create().setDefaultRequestConfig(requestConfig).setUserAgent(properties.getAgent()).setMaxConnPerRoute(properties.getMaxConnPerRoute()).setConnectionReuseStrategy(new NoConnectionReuseStrategy()).build();
    return client;
  }
}
```

HttpClientProperties.java

```java
//在application.properties中可以覆盖这些默认配置
@ConfigurationProperties(prefix = "spring.httpclient")
public class HttpClientProperties {
  private Integer connectTimeOut = 1000;
  private Integer socketTimeOut = 10000;
  private String agent = "agent";
  private Integer maxConnPerRoute = 10;
  private Integer maxConnTotaol = 50;
}
```

### 2. 配置Filter

FilterBeanConfig.java

(FilterRegistrationBean是spring提供的包装器类)

```java
@Configuration
public class FilterBeanConfig {
  /**
   * 1.构造filter
   * 2.配置拦截urlPattern
   * 3.利用FilterRegistrationBean进行包装
     * FilterRegistrationBean是spring提供的包装器类, 可以把原始的Filter包装成Spring Bean
   */
  @Bean
  public FilterRegistrationBean logFilter() {
    FilterRegistrationBean filterRegistrationBean = new FilterRegistrationBean();
    filterRegistrationBean.setFilter(new LogFilter());
    List<String> urList = new ArrayList<String>();
    urList.add("*");
    filterRegistrationBean.setUrlPatterns(urList);
    return filterRegistrationBean;
  }
}

public class LogFilter implements Filter {
  private Logger logger = LoggerFactory.getLogger(LogFilter.class);
  public void init(FilterConfig filterConfig) throws ServletException {
  }

  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
//        logger.info("Request--coming");
        chain.doFilter(request, response);
  }

  public void destroy() {
  }
}
```

### 3. 使用Druid连接池

DruidConfig.java

```java
@Configuration
public class DruidConfig {
    /**
     * 使用druid连接池, 就需要配置新的数据源, 而不是使用springboot默认提供的jdbc数据源
     */
  @ConfigurationProperties(prefix = "spring.druid")
  @Bean(initMethod = "init",destroyMethod = "close")
  public DruidDataSource dataSource() {
    DruidDataSource dataSource = new DruidDataSource();
    dataSource.setProxyFilters(Lists.newArrayList(statFilter()));
    return dataSource;
  }
  
    //配置监控的Filter
  @Bean
  public Filter statFilter() {
    StatFilter filter = new StatFilter();
    //打印sql的慢日志
    filter.setSlowSqlMillis(5000);
    filter.setLogSlowSql(true);
    filter.setMergeSql(true);
    return filter;
  }

    /**
     * 把监控功能的Filter配置到Servlet中, 启动后访问/druid接口, 就可以看到监控的信息
     */
  @Bean
  public ServletRegistrationBean servletRegistrationBean() {
    return new ServletRegistrationBean(new StatViewServlet(), "/druid/*");
  }
}
```

application.properties

```properties
spring.druid.driverClassName=com.mysql.jdbc.Driver
spring.druid.url=jdbc:mysql://127.0.0.1:3306/houses?useUnicode=true&amp;amp;characterEncoding=UTF-8&amp;amp;zeroDateTimeBehavior=convertToNull
spring.druid.username=root
spring.druid.password=123456
spring.druid.maxActive=30
spring.druid.minIdle=5
spring.druid.maxWait=10000
spring.druid.validationQuery=SELECT 'x'
```

### 4. Mybatis的配置

mybatis-config.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <settings>
        <!-- 关闭缓存  -->
        <setting name="cacheEnabled" value="false"/>
        <setting name="mapUnderscoreToCamelCase" value="true"/>
        <setting name="useGeneratedKeys" value="true"/>
        <!-- 提高性能 -->
        <setting name="defaultExecutorType" value="REUSE"/>
        <!-- 事务超时时间 -->
        <setting name="defaultStatementTimeout" value="600"/>
    </settings>

    <!-- 设置别名 -->
    <typeAliases>
        <typeAlias type="com.mooc.house.common.model.User" alias="user"/>
        <typeAlias type="com.mooc.house.common.model.Agency" alias="agency"/>
        <typeAlias type="com.mooc.house.common.model.House" alias="house"/>
        <typeAlias type="com.mooc.house.common.model.City" alias="city"/>
        <typeAlias type="com.mooc.house.common.model.Comment" alias="comment"/>
        <typeAlias type="com.mooc.house.common.model.Community" alias="community"/>
        <typeAlias type="com.mooc.house.common.model.HouseUser" alias="houseUser"/>
        <typeAlias type="com.mooc.house.common.model.Blog" alias="blog"/>
        <typeAlias type="com.mooc.house.common.model.User" alias="user"/>
        <typeAlias type="com.mooc.house.common.model.UserMsg" alias="userMsg"/>
        <typeAlias type="com.mooc.house.common.model.HouseUser" alias="houseUser"/>
    </typeAliases>

    <mappers>
        <mapper resource="mapper/user.xml"/>
        <mapper resource="mapper/blog.xml"/>
        <mapper resource="mapper/house.xml"/>
        <mapper resource="mapper/comment.xml"/>
        <mapper resource="mapper/agency.xml"/>
    </mappers>
</configuration>
```

application.properties

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/user?characterEncoding=UTF-8
spring.datasource.username=root
spring.datasource.password=123456
spring.datasource.driver-class-name=com.mysql.jdbc.Driver

# mybatis的配置
mybatis.config-location=classpath:/mybatis/mybatis-config.xml
```

user.xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.mooc.house.biz.mapper.UserMapper"> 
   <select id="selectUsersByQuery" resultType="user">
     select * from user
     <where>
        <if test="id !=null" >
           and id = #{id}
        </if>
        <if test="email != null">
          and email = #{email}
        </if>
        <if test="passwd != null">
          and passwd = #{passwd}
        </if>
        <if test="enable != null">
          and enable = #{enable}
        </if>
        <if test = "type != null and type!=0">
          and type = #{type}
        </if>
     </where>
   </select>

   <update id="update">
     update user
      <set>
         <if test="phone !=null and phone != '' ">
              phone = #{phone},
         </if>
         <if test="name !=null and name != '' ">
              name = #{name},
         </if>
         <if test="aboutme !=null and aboutme != '' ">
              aboutme = #{aboutme},
         </if>
         <if test="passwd !=null and passwd != '' ">
              passwd = #{passwd},
         </if>
         <if test="enable !=null ">
              enable = #{enable},
         </if>
      </set>
      where email = #{email}
   </update>
</mapper>
```

UserMapper.java

```java
@Mapper
public interface UserMapper {
  public List<User>  selectUsers();
  public int insert(User account);
  public int delete(String email);
  public int update(User updateUser);
  public List<User> selectUsersByQuery(User user);
}
```

### 5. maven多模块打包方式

* 如果pom文件继承spring-boot-starter-parent的话，只需要下面的指定就行。

```xml
<properties>
    <!-- The main class to start by executing java -jar -->
    <start-class>com.mycorp.starter.HelloWorldApplication</start-class>
</properties>
```

* 如果pom文件不是继承spring-boot-starter-parent的话，需要下面的指定。

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
            </configuration>
        </plugin>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <mainClass>com.mooc.house.HouseApplication</mainClass>
                <layout>ZIP</layout>
            </configuration>
            <executions>
                <execution>
                    <goals>
                        <goal>repackage</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

执行: mvn clean package -DskipTests

### 6. spring admin监控平台

* 1. 搭建spring-admin的springboot工程, 引入相关依赖

     ```xml
     <dependency>
        <groupId>de.codecentric</groupId>
        <artifactId>spring-boot-admin-server</artifactId>
        <version>1.3.2</version>
     </dependency>
     <dependency>
        <groupId>de.codecentric</groupId>
        <artifactId>spring-boot-admin-server-ui</artifactId>
        <version>1.3.2</version>
     </dependency>
     ```

* 2. 在启动类上加注解 @EnableAdminServer, 并配置server.port = 9090

  3. 在被监控的项目中引入依赖

     ```xml
     <dependency>
        <groupId>de.codecentric</groupId>
        <artifactId>spring-boot-admin-client</artifactId>
        <version>1.3.2</version>
     </dependency>
     ```

     然后在application.properties中加上以下配置

     ```properties
     spring.boot.admin.url=http://localhost:9090
     ```

* 4. 启动两个项目即可监控应用信息

### 7. spring boot actuator

/info 自定义信息

/health 健康监测

/beans  所有的bean

/autoconfig 所有的自定义配置

/env  系统和应用程序的环境 classpath 操作系统等

/mappings rest信息

/metrics  jvm 内存等信息

/trace  最近访问的快照

/dump 线程信息

/configprops  配置的属性值

/shutdown endpoints.shutdown.enabled = true, 可以关闭应用



### 生成订单号的方法

```java
public static synchronized String createOrderId() {
    char[] chars = new char[]{'A', 'B', 'C', 'D', 'E', 'F'};

    //获得当前年份
    Calendar calendar = Calendar.getInstance();
    int year = calendar.get(Calendar.YEAR);

    //产生六位随机数
    Random random = new Random();
    Integer number = random.nextInt(900000) + 100000;

    return chars[year - 2017] + String.valueOf(System.currentTimeMillis()) + String.valueOf(number);
}
```

### AOP的配置

```java
@Aspect
@Component
public class SnackScopeAspect {

    @Autowired
    private UserTokenService userTokenService;

    @Pointcut("execution(public * me.hds.snack.controller.UserAddressController.addOrUpdateUserAddress(..))")
    public void verifyScope() {}

    /**
     * 前置方法, 验证是否有权限访问该接口(写在上面的execution中的接口)
     * @return
     */
    @Before("verifyScope()")
    public boolean doVerifyScope() {
        //获得缓存中的scope的值
        Integer scope = getCachedValueScope();

        if (scope >= ScopeEnum.USER.getScope()) {
            return true;
        } else {
            throw new SnackException(SnackExceptionEnum.SCOPE_NOT_ENOUGH);
        }
    }

    @Pointcut("execution(public * me.hds.snack.controller.OrderController.*(..)) "
            + "&& execution(public * me.hds.snack.controller.PayController.*(..))")
    public void exclusiveSuperScope() {}

    /**
     * 前置方法, 验证是否有权限访问该接口(写在上面的execution中的接口)
     * @return
     */
    @Before("exclusiveSuperScope()")
    public boolean doExclusiveSuperScope() {
        //获得缓存中的scope的值
        Integer scope = getCachedValueScope();

        if (Objects.equals(scope, ScopeEnum.USER.getScope())) {
            return true;
        } else {
            throw new SnackException(SnackExceptionEnum.SCOPE_NOT_ENOUGH);
        }
    }

    /**
     * 获得缓存中的scope的值
     * @return
     */
    private Integer getCachedValueScope() {
        //在普通方法中获得request
        ServletRequestAttributes servletRequestAttributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest httpServletRequest = servletRequestAttributes.getRequest();

        String token = httpServletRequest.getHeader("token");

        String result = (String) userTokenService.getCurrentTokenValue(token, "scope");

        return Integer.parseInt(result);
    }
}
```

### 静态资源的配置

```java
@Configuration
public class StaticResourceConfiguration extends WebMvcConfigurerAdapter {
    private static final String[] CLASSPATH_RESOURCE_LOCATIONS = {
            "classpath:/META-INF/resources/", "classpath:/resources/",
            "classpath:/static/", "classpath:/public/" };

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/**").addResourceLocations(CLASSPATH_RESOURCE_LOCATIONS);
    }
}

```

### 枚举值的配置

```java
/**
 * Enum类型只能用getter
 */
public enum SnackExceptionEnum {

    THEME_NOT_EXIST(10, "该专题不存在"),
    PRODUCT_NOT_EXIST(11, "该商品不存在"),
    USER_NOT_EXIST(12, "该用户不存在"),
    USER_ADDRESS_ERROR(13, "用户地址错误"),
    USER_ADDRESS_NOT_EXIST(14, "用户地址不存在"),
    TOKEN_CODE_NOT_EXIST(15, "code不存在"),
    TOKEN_GET_ERROR(16, "生成Token失败"),
    TOKEN_IS_EXPIRE(17, "token不存在或过期"),
    TOKEN_KET_NOT_EXIST(18, "token中不存在这个key"),
    SCOPE_NOT_ENOUGH(19, "权限不够,不能访问本接口"),
    CART_PRODUCT_NOT_EXIST(20, "购物车中的该商品不存在"),
    OPENID_IS_VALID(21, "openid返回结果为空"),
    OPENID_ERROR(22, "openid返回errcode错误"),
    ORDERID_IS_EMPTY(23, "订单号为空"),
    ORDER_NOT_EXIST(24, "订单不存在"),
    USERID_IS_EMPTY(25, "用户的id为空"),
    USERID_ERROR(26, "用户id不匹配"),
    ORDER_HAS_PAID(27, "订单已经被支付"),
    ;

    private Integer code;

    private String message;

    SnackExceptionEnum(Integer code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public Integer getCode() {
        return code;
    }
}
```

### Exception的配置

```java
@EqualsAndHashCode(callSuper = true)
@Data
public class SnackException extends RuntimeException {
    private Integer code;
    private String message;

    public SnackException(SnackExceptionEnum resultEnum) {
        this.code = resultEnum.getCode();
        this.message = resultEnum.getMessage();
    }

    public SnackException(Integer code, String message) {
        this.message = message;
        this.code = code;
    }
}

//处理aop抛出的异常的注解
@ControllerAdvice
public class SellExceptionHandler {

    @ExceptionHandler(value = SnackException.class)
    @ResponseBody
    public ResultVO handlerSellerException(SnackException e) {
        return ResultVOUtil.error(e.getCode(), e.getMessage());
    }
}
```

### JPA的配置

```java
//不用加@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    User findByOpenid(String openid);
}

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "user")
public class User {
    @Id
    @GeneratedValue
    private Long id;

    private String openid;
    private String nickname;
    private String extend;
}
```

## Gson的操作

###  JsonToMap.java

```java
public class JsonToMap {

    /**
     * 获取JsonObject
     *
     * @param json
     * @return
     */
    public static JsonObject parseJson(String json) {
        JsonParser parser = new JsonParser();
        JsonObject jsonObj = parser.parse(json).getAsJsonObject();
        return jsonObj;
    }

    /**
     * 根据json字符串返回Map对象
     *
     * @param json
     * @return
     */
    public static Map<String, Object> toMap(String json) {
        return JsonToMap.toMap(JsonToMap.parseJson(json));
    }

    /**
     * 将JSONObject对象转换成Map-List集合
     *
     * @param json
     * @return
     */
    public static Map<String, Object> toMap(JsonObject json) {
        Map<String, Object> map = new HashMap<>();
        Set<Map.Entry<String, JsonElement>> entrySet = json.entrySet();
        for (Iterator<Map.Entry<String, JsonElement>> iter = entrySet.iterator(); iter.hasNext(); ) {
            Map.Entry<String, JsonElement> entry = iter.next();
            String key = entry.getKey();
            Object value = entry.getValue();
            if (value instanceof JsonArray)
                map.put(key, toList((JsonArray) value));
            else if (value instanceof JsonObject)
                map.put(key, toMap((JsonObject) value));
            else
                map.put(key, value);
        }
        return map;
    }

    /**
     * 将JSONArray对象转换成List集合
     *
     * @param json
     * @return
     */
    public static List<Object> toList(JsonArray json) {
        List<Object> list = new ArrayList<>();
        for (int i = 0; i < json.size(); i++) {
            Object value = json.get(i);
            if (value instanceof JsonArray) {
                list.add(toList((JsonArray) value));
            } else if (value instanceof JsonObject) {
                list.add(toMap((JsonObject) value));
            } else {
                list.add(value);
            }
        }
        return list;
    }
}
```

### Gson的基本使用(5个文件)

#### User.java

```java
@Data
@AllArgsConstructor
public class User {
    //省略其它
    public String name;
    public int age;

    @SerializedName(value = "emailAddress", alternate = {"email", "email_address"})
    //当上面的三个属性(email_address、email、emailAddress)都中出现任意一个时均可以得到正确的结果。
    //注：当多种情况同时出时，以最后一个出现的值为准。
    public String emailAddress;

    User(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

#### Result.java

```java
@Data
@AllArgsConstructor
public class Result<T> {
    public int code;
    public String message;
    public T data;
}
```

#### ParameterizedType.java

```java
/**
 Map<String, User>

 public interface ParameterizedType extends Type {
     // 返回Map<String, User>里的String和User，所以这里返回[String.class, User.class]
     Type[] getActualTypeArguments();

     // Map<String, User>里的Map,所以返回值是Map.class
     Type getRawType();

     // 用于这个泛型上中包含了内部类的情况,一般返回null
     Type getOwnerType();
 }

 */
public class ParameterizedTypeImpl implements ParameterizedType {

    private final Class raw;
    private final Type[] args;

    public ParameterizedTypeImpl(Class raw, Type[] args) {
        this.raw = raw;
        this.args = args != null ? args : new Type[0];
    }

    @Override
    public Type[] getActualTypeArguments() {
        return args;
    }

    @Override
    public Type getRawType() {
        return raw;
    }

    @Override
    public Type getOwnerType() {
        return null;
    }
}
```

#### GsonDemo.java

```java
public class GsonDemo {

    @Test
    public void test() {
        Gson gson = new Gson();

        //1. 基本数据类型的解析
        int i = gson.fromJson("100", int.class);              //100
        double d = gson.fromJson("\"99.99\"", double.class);  //99.99 (容错机制, 把String转成double类型)
        boolean b = gson.fromJson("true", boolean.class);     // true
        String str = gson.fromJson("String", String.class);   // String

        //2. 基本数据类型的生成
        String jsonNumber = gson.toJson(100);       // 100
        String jsonBoolean = gson.toJson(false);    // false
        String jsonString = gson.toJson("String"); //"String"

        //3. pojo类转成json
        User user = new User("怪盗kidou", 24);
        String jsonObject = gson.toJson(user); // {"name":"怪盗kidou","age":24}
        System.out.println(jsonObject);

        //4. json转成对应的pojo类
        String jsonString2 = "{\"name\":\"怪盗kidou\",\"age\":24}";
        User newUser = gson.fromJson(jsonString, User.class);
        System.out.println(newUser);
    }

    @Test
    public void test02() {
        //5. 属性重命名 @SerializedName 注解的使用
        /*
            Gson在序列化和反序列化时需要使用反射，说到反射就不得不想到注解.
            现在的目的是, 把json字符串转成pojo类, 但是pojo类的属性名, 可能与json中的键名不一致, 这时就需要用这个注解
         */
        Gson gson = new Gson();
        String json = "{\"name\":\"怪盗kidou\",\"age\":24,\"emailAddress\":\"ikidou_1@example.com\",\"email\":\"ikidou_2@example.com\",\"email_address\":\"ikidou_3@example.com\"}";
        User user = gson.fromJson(json, User.class);
        System.out.println(user.emailAddress); // ikidou_3@example.com
    }

    /**
     * Gson中使用泛型
     */
    @Test
    public void test03() {
        Gson gson = new Gson();
        String jsonArray = "[\"Android\",\"Java\",\"PHP\"]";
        //json字符串转成数组
        String[] strings = gson.fromJson(jsonArray, String[].class);
        /*
            json字符串转成List
            不能把String[].class转成List<String>.class
            因为: 对于Java来说List<String> 和List<User> 这俩个的字节码文件只一个那就是List.class，这是Java泛型使用时要注意的问题 泛型擦除。
            解决: 用TypeToken来存储泛型信息
                new TypeToken<List<String>>() {}.getType()

            TypeToken的构造方法是protected修饰的,所以上面才会写成new TypeToken<List<String>>() {}.getType() 而不是  new TypeToken<List<String>>().getType()
                原因: 匿名内部类, 这里其实是new了一个继承TypeToken的子类,
         */
        List<String> stringList = gson.fromJson(jsonArray, new TypeToken<List<String>>() {}.getType());
    }

    @Test
    public void test04() {
        /*
            要解析这样的json数据:
            {"code":"0","message":"success","data":{}}
            {"code":"0","message":"success","data":[]}

            原始做法:
                //=========
                public class UserResult {
                    public int code;
                    public String message;
                    public User data;
                }
                //=========
                public class UserListResult {
                    public int code;
                    public String message;
                    public List<User> data;
                }
                //=========
                String json = "{..........}";
                Gson gson = new Gson();
                UserResult userResult = gson.fromJson(json,UserResult.class);
                User user = userResult.data;

                UserListResult userListResult = gson.fromJson(json,UserListResult.class);
                List<User> users = userListResult.data;
                //=========
                但是重复定义了字段

                这时就要用TypeToken
         */

        String json = "{\"code\":\"0\",\"message\":\"success\",\"data\":{}}";

        Gson gson = new Gson();
        Type userType = new TypeToken<Result<User>>(){}.getType();
        Result<User> userResult = gson.fromJson(json, userType);
        User user = userResult.data;

        Type userListType = new TypeToken<List<User>>(){}.getType();
        Result<List<User>> userListResult = gson.fromJson(json, userListType);
        List<User> users = userListResult.data;
    }

    /**
     * 自定义的gson带泛型的解析
     */
    public void test05() {
        String json = "{\"code\":\"0\",\"message\":\"success\",\"data\":{}}";
        Result<User> userResult = GenerateTypeForGson.fromJsonObject(json, User.class);
        Result<List<User>> listResult = GenerateTypeForGson.fromJsonArray(json, User.class);
    }

    /**
     * 使用工具类生成泛型信息
     */
    public void test06() {
        String json = "{\"code\":\"0\",\"message\":\"success\",\"data\":{}}";
        Result<User> userResult = GenerateTypeForGson.fromJsonObject2(json, User.class);
        Result<List<User>> listResult = GenerateTypeForGson.fromJsonArray2(json, User.class);
    }

    /**
     * Gson提供了fromJson()和toJson() 两个直接用于解析和生成的方法，前者实现反序列化，后者实现了序列化。同时每个方法都提供了重载方法，我常用的总共有5个。
         Gson.toJson(Object);
         Gson.fromJson(Reader,Class);
         Gson.fromJson(String,Class);
         Gson.fromJson(Reader,Type);
         Gson.fromJson(String,Type);
     */
    public void test07() {

    }
}
```

#### GenerateTypeForGson.java

```java
public class GenerateTypeForGson {

    public static Gson gson = new Gson();

    public static <T> Result<T> fromJsonObject(String json, Class<T> clazz) {
        Type type = new ParameterizedTypeImpl(Result.class, new Class[]{clazz});
        return gson.fromJson(json, type);
    }

    public static <T> Result<List<T>> fromJsonArray(String json, Class<T> clazz) {
        // 生成List<T> 中的 List<T>
        Type listType = new ParameterizedTypeImpl(List.class, new Class[]{clazz});
        // 根据List<T>生成完整的Result<List<T>>
        Type type = new ParameterizedTypeImpl(Result.class, new Type[]{listType});
        return gson.fromJson(json, type);
    }

    public static <T> Result<T> fromJsonObject2(String json, Class<T> clazz) {
        Type type = TypeBuilder
                .newInstance(Result.class)
                .addTypeParam(clazz)
                .build();
        return gson.fromJson(json, type);
    }

    public static <T> Result<List<T>> fromJsonArray2(String json, Class<T> clazz) {
        Type type = TypeBuilder
                .newInstance(Result.class)
                .beginSubType(List.class)
                .addTypeParam(clazz)
                .endSubType()
                .build();
        return gson.fromJson(json, type);
    }

```

