## Spring Boot

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



### 自定义Bean验证

#### MyConstraint

```java
/**
 * 自定义校验注解
 */
@Target({ElementType.METHOD, ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = MyConstraintValidator.class) //表示当前的注解是一个校验的注解
public @interface MyConstraint {

    //如果校验没通过时,展示给用户的信息
    String message() default "my validator";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
```

#### MyConstraintValidator

```java
/**
 * 自定义验证注解的背后支持类, 两个泛型分别的意思是,第一个是自定义验证注解, 第二个是验证的字段的数据类型, 可以写成Object
 */
//不用写@Component, spring会自动放入容器中
public class MyConstraintValidator implements ConstraintValidator<MyConstraint, Object> {

    //在这个校验器中,可以使用依赖注入任何Spring容器中的类,来执行校验逻辑

    //初始化
    @Override
    public void initialize(MyConstraint myConstraint) {
        System.out.println("自定义校验器初始化了...");
    }

    //校验时调用isValid方法,把被加上这个自定义注解的属性(username)的值传入这个方法的第一个参数, 然后对这个值进行校验, 最后返回true或者false
    @Override
    public boolean isValid(Object o, ConstraintValidatorContext constraintValidatorContext) {

        System.out.println("被自定义注解校验的属性的值是" + o.toString());

        //true表示校验通过, 这里写成false是为了打印出@MyConstraint(message = "自定义的校验注解")的message信息
        return false;
    }
}
```



#### 上传和下载功能

```java
@RestController
@RequestMapping("/file")
public class FileController {

    //设置存放上传的文件的本地的目录
    private String folder = "/Users/hecun/IdeaProjects";

    //文件上传, 要用post
    @PostMapping
    //参数的名字file, 要和发请求时第一个参数名file匹配
    public FileInfo upload(MultipartFile file) throws IOException {
        System.out.println(file.getName());//上传时的参数名字
        System.out.println(file.getOriginalFilename());//test.txt
        System.out.println(file.getSize());//尺寸

        //设置存放上传的文件的本地的文件名
        File localFile = new File(folder, new Date().getTime() + ".txt");
        //上传文件
        file.transferTo(localFile);

        return new FileInfo(localFile.getAbsolutePath());
    }

    @GetMapping("/{id}")
    public void download(@PathVariable String id, HttpServletRequest request, HttpServletResponse resources) throws Exception {

        //jdk7新语法
        try (InputStream inputStream = new FileInputStream(new File(folder, id + ".txt"));
             OutputStream outputStream = resources.getOutputStream()) {

            resources.setContentType("application/x-download");
            //定义下载时的文件名
            resources.addHeader("Content-Disposition", "attachment;filename=test.txt");

            IOUtils.copy(inputStream, outputStream);
            outputStream.flush();
        }
    }
}

@Test
public void whenUploadSuccess() throws Exception {
    String result = mockMvc.perform(MockMvcRequestBuilders.fileUpload("/file")
                                    //文件对应的整体的参数名字, 文件名, 文件类型, 文件内容(要用字节数组)
                                    .file(new MockMultipartFile("file", "test.txt", "multipart/form-data", "hello".getBytes("UTF-8"))))
        .andExpect(MockMvcResultMatchers.status().isOk())
        .andReturn().getResponse().getContentAsString();

    System.out.println(result);
}
```



### Spring使用swagger生产文档

#### 1. maven上搜索`springfox`

#### 2. 在启动类上加 `@EnableSwagger2`

#### 3. 访问localhost:8080/swagger-ui.html

- @ApiOperation(value = "用户查询服务")    方法的api描述
- @ApiModelProperty(value = "用户名")       方法参数的字段是被封装到对象中的, 则在对象的属性上加描述
- @ApiParam("用户id")                                     直接在controller方法的参数前加描述



### 注解

#### @RequestHeader: 获取请求头的注解 

```java
@GetMapping(path = "/html/demo/header")
public String htmlHeader(@RequestHeader(value = "Accept") String acceptHeader, HttpServletRequest request) {
    return "<html><body>Request 'Accept' header value : " + acceptHeader + " </body></html>";
}
```

#### @DateTimeFormat

```java
@RequestParam("start") @DateTimeFormat(pattern="yyyy-MM-dd hh:mm:ss") Date start,
// 前端传入的参数是字符串，但service的方法需要的数据类型是Date类型，可以加注解解决：
```

#### @EnableScheduling : 开启对计划任务的支持(定时器) 

```java
// 需要有注解@Scheduled配合，类的方法中有@Scheduled注解，则该类必须加上@Component注解
@Service
public class ScheduledTaskService {
    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm:ss");

    @Scheduled(fixedRate = 5000) 
    //通过@Scheduled声明该方法是计划任务，使用fixedRate属性每隔固定时间执行
    public void reportCurrentTime(){
        System.out.println("每隔5秒执行一次 " + dateFormat.format(new Date()));
    }

    @Scheduled(cron = "0 07 20 ? * *" ) 
    //使用cron属性可按照指定时间执行，本例指的是每天20点07分执行；
    public void fixTimeExecution(){
        System.out.println("在指定时间 " + dateFormat.format(new Date()) + " 执行");
    }
}
```

#### @ModelAttribute

##### 请求的FORM表单数据

```html
<form method="post" action="hao.do">
    a: <input id="a" type="text" name="a"/>
    b: <input id="b" type="text" name="b"/>
    <input type="submit" value="Submit" />
</form>
```

##### Controller

```java
public class Pojo {
    private String a;
    private int b;
}

@RequestMapping(method = RequestMethod.POST) 
public String processSubmit(@ModelAttribute("pojo") Pojo pojo) { 
	return "hello World"; 
}
```

#### @RequestBody: springmvc接收JSON类型的参数数据

```java
* 多个参数以对象的形式传入controller时, 可以不写@RequestParam, 直接把对象当做参数即可
* Pageable也可以不写@RequestParam,把Pageable对象当做参数传入即可
* 当post创建时, @RequestBody的意义是:映射请求体到java方法的参数(把json中的每个键值映射到对应对象的字段中)
* 当controller返回的类型是对象或者list时,springmvc会自动把它转成json格式

处理的是ajax提交来的json数据!!!!!
1、用来处理content-type是application/json类型。
2、通过@requestBody可以将请求体中的JSON字符串绑定到相应的bean上，当然，也可以将其分别绑定到对应的字符串上。
    例如以下情况：
　　　　$.ajax({
　　　　　　　　url:"/login",
　　　　　　　　type:"POST",
　　　　　　　　data:'{"userName":"admin","pwd","admin123"}',
　　　　　　　　content-type:"application/json charset=utf-8",
　　　　　　　　success:function(data) {
　　　　　　　　　　alert("request success!");
　　　　　　　　}
　　　　});

　　　　@requestMapping("/login")
　　　　public void login(@RequestBody String userName, @RequestBody String pwd){
　　　　　　System.out.println(userName + "：" + pwd);
　　　　}
       这种情况是将JSON字符串中的两个变量的值分别赋予了两个字符串
    
    如果有一个User类，拥有如下字段：
        String userName; String pwd;
    那么上述参数可以改为以下形式：@requestBody User user 
    这种形式会将JSON字符串中的值赋予user中对应的属性上
　　 需要注意的是，JSON字符串中的key必须对应user中的属性名
```

#### 对时间类型的处理

##### 核心: 因为一个后端会被不同的前端使用, 所以只传时间戳, 不同的客户端决定如何显示这个时间

```java
// 当创建对象时(private Date birthday;)

1. 传入的json字符串中的birthday键名对应的键值是时间戳, 则pojo类不需要加任何注解,可以直接转成date类型,存入pojo属性中
2. 传入的json字符串中的birthday键名对应的键值是"yyyy-MM-dd"之类的字符串, 则在pojo类的属性上加@JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss"). 前后必须匹配, 此时, 就可以把String转成Date类型

// 当返回user对象时,springmvc会自动把Date类型的birthday转成字符串或者时间戳返回!
({"id":"1","username":"tom","password":null,"birthday":"2017-09-09 11:11:11"})

// 当直接传入字符串:("start", "1999-09-09")时
需要在controller的接收参数中加@RequestParam("start") @DateTimeFormat(pattern = "yyyy-MM-dd") Date start, 然后springmvc就可以把字符串转成Date类型
```

#### @Valid

json转成User对象时,会对每个属性进行校验. 如果校验没通过,则不会进入controller方法中.

但实际上,需要带着错误信息,进入controller方法,做一些记录日志的工作,这时需要用BindingResult bindingResult,校验中发现的错误信息,都会放到BindingResult对象中

> @Valid @RequestBody User user, BindingResult bindingResult 在controller中,这两个参数必须紧挨着!

#### @Autowired

1. @Autowired是根据类型注入的, 可以对成员变量、方法以及构造函数进行注释。@Resource是根据名字注入的
2. 推荐对构造函数进行注解, 而不是对成员变量进行注解

```java
// 原来是
@Autowired
private UserService userService;

// 建议写成
private final UserService userService;

@Autowired
private UserController(UserService userService) {
	this.userService = userService;
}
```

##### 构造器注入的原因

```java
@Autowired
private User user;
private String school;

public UserAccountServiceImpl() {
	this.school = user.getSchool();
}

这段代码会报错. 因为Java类会先执行构造方法，然后再给注解了@Autowired 的user注入值，
但在构造方法中要有user对象, 此时还没有注入, 所以在执行构造方法的时候，就会报错。

// 改正: 使用构造器注入

private User user;
private String school;

@Autowired
public UserAccountServiceImpl(User user) {
    this.user = user;
    this.school = user.getSchool();
}

可以看出，使用构造器注入的方法，可以明确成员变量的加载顺序。

Java变量的初始化顺序为：
静态变量或静态语句块 –> 实例变量或初始化语句块 –> 构造方法 –> @Autowired

@Autowired本身就是单例模式，只会在程序启动时执行一次，即使不定义final也不会初始化第二次，可能是为了防止，在程序运行的时候，又执行了一遍构造函数；或者是更容易让人理解的意思，加上final只会在程序启动的时候初始化一次，并且在程序运行的时候不会再改变。
```

#### @CookieValue:

从Http请求头中的Cookie提取指定的某个Cookie.

在控制器的方法参数中使用注解把请求路径指定的参数提取出来作为实参注入形参中

```java
@RequestMapping(value = "/jsessionId")    
public String jsessionId( 
    
    @CookieValue(value = "JSESSIONID", required = true, defaultValue = "MyJsessionId") String jsessionId, Model model) {  
    model.addAttribute("jsessionId", jsessionId);  
    return "request/cookieValue";  
}  
```

#### @NoRepositoryBean:

spring data的通用实现中, 该注解用作标记当前接口或类不应该作为@Repository的bean注册到spring上下文中.

比如在jpa中, 我们只需要写Repository的接口, 不需要写实现类. 这是因为spring提供了自动代理加了@Repository Bean的机制.

该机制的前提是, 该接口或类必须实现spring data提供的Repository接口

#### cousumes的样例：

```java
@Controller
@RequestMapping(value = "/pets", method = RequestMethod.POST, consumes = "application/json")
public void addPet(@RequestBody Pet pet, Model model) {    
    // implementation omitted
}

// 方法仅处理request Content-Type为“application/json”类型的请求。
```

#### produces的样例：

```java
@Controller
@RequestMapping(value = "/pets/{petId}", method = RequestMethod.GET, produces="application/json")
@ResponseBody
public Pet getPet(@PathVariable String petId, Model model) {    
    // implementation omitted
}

// 方法仅处理request请求中Accept头中包含了"application/json"的请求，同时暗示了返回的内容类型为application/json;
```



### 全局异常处理

#### 如果是浏览器

在resources文件夹下建立resources/error目录,根据错误码建立html页面, 此时,显示的就是我们自定义的错误页面

#### 如果是RESTful

##### 方法一 实现接口`HandlerExceptionResolver`

```java
@Component
@Slf4j
public class ExceptionResolver implements HandlerExceptionResolver {

    /**
     * 解决异常的方法
     */
    @Override
    public ModelAndView resolveException(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, Object o, Exception e) {
        log.error("{} Exception", httpServletRequest.getRequestURI(), e);
        //因为是前后端分离的, 所以要转化成JsonView
        //当使用是jackson2.x的时候使用MappingJackson2JsonView，课程中使用的是1.9。
        ModelAndView modelAndView = new ModelAndView(new MappingJacksonJsonView());

        modelAndView.addObject("status", ResponseCode.ERROR.getCode());
        modelAndView.addObject("msg", "接口异常,详情请查看服务端日志的异常信息");
        modelAndView.addObject("data", e.toString());

        return modelAndView;
    }
}
```

##### 方法二 加`@ControllerAdvice`注解

```java
@ControllerAdvice
public class SellExceptionHandler {

    @Autowired
    private ProjectUrlConfig projectUrlConfig;

    //拦截登录异常(加注解捕获）然后跳转到下面这个链接所代表的登录页面
    //http://sell.natapp4.cc/sell/wechat/qrAuthorize?returnUrl=http://sell.natapp4.cc/sell/seller/login
    
    @ExceptionHandler(value = SellerAuthorizeException.class)
    public ModelAndView handlerAuthorizeException() {
        //直接跳转到登录页面
        return new ModelAndView("redirect:"
        .concat(projectUrlConfig.getWechatOpenAuthorize())
        .concat("/sell/wechat/qrAuthorize")
        .concat("?returnUrl=")
        .concat(projectUrlConfig.getSell())
        .concat("/sell/seller/login"));
    }

    @ExceptionHandler(value = SellException.class)
    @ResponseBody
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ResultVO handlerSellerException(SellException e) {
        return ResultVOUtil.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(value = ResponseBankException.class)
    @ResponseBody
    @ResponseStatus(HttpStatus.FORBIDDEN)
    public void handlerResponseBankException() {
        return ResultVOUtil.error(e.getCode(), e.getMessage());
    }
}
```



### Spring中的缓存

#### 说明

1. 添加缓存不能影响正常业务逻辑。所以要使用try catch
2. 命中 失效 更新
3. 在启动类上加@EnableCaching的注解
4. 在查询方法上加@Cacheable(cacheNames = "product", key = "123") 要返回的实体类继承序列化接口
   1. 第一次访问时, 会访问数据库, 同时把数据存在redis中
   2. redis中的key: "product:123"
   3. 如果不写括号中的key, 那么其值就是方法中的参数的值
   4. 根据参数进行判断决定是否缓存: 
      @Cacheable(cacheNames = "product", key = "#sellerId", condition = "#sellerId.length() > 3")
   5. 根据结果的code判断是否要缓存: 
      @Cacheable(cacheNames = "product", key = "#sellerId", unless = "#result.getCode() != 0")
      public ResultVO list(String sellerId) {}
5. 在更新方法上加@CachePut(cacheNames = "product", key = "123")
   这样就会更新缓存
   ==> @CachePut 每次都会执行方法, 然后把更新同步到redis中. 
   	但是, 如果更新方法返回的是视图ModelAndView对象, 那么, 无法让ModelAndView对象实现序列化接口, 所以, @CachePut不行. ==> 需要换一种缓存同步的方式
   	如果想用@CachePut和@Cacheable, 就需要查询方法和更新方法返回的数据一致.
   ==> @CacheEvict(cacheNames = "product", key = "123") 只要访问这个更新方法, 就会把redis中的缓存清除掉. 从而实现缓存同步.
6. Redis中只能保存字符串,所以要把list等都转成json字符串，要有JsonUtils类

#### BookServiceImpl

```java
package me.hds.cache;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service("bookService")
//@Transactional
public class BookServiceImpl {

    @Autowired
    private CacheManager cacheManager;

    /**
     * @Cacheable("books") 第一次会到数据库查出BookInfo的信息
     * 再次请求这个接口的时候, 就不查询数据库了, 直接从缓存中拿
     * 拿的时候, 会把参数id通过keyGenerator生成redis中的key, 来获取缓存

     * 如果方法没有参数, 就会用SimpleKey类中的EMPTY属性作为key
     * 否则, 就会返回由多个参数构造出的SimpleKey对象
     */
    @Cacheable("books") //缓存的key为: "books:SimpleKey(id)"
    public BookInfo getInfo(Long id) {
        BookInfo info = new BookInfo();
        return info;
    }

    //编程式缓存
    public BookInfo getInfoTestCacheByProgram(Long id) {

        Cache.ValueWrapper books = cacheManager.getCache("books").get(id);

        if (books == null) {
            //Book book = bookRepository.findOne(id);
            BookInfo bookInfo = new BookInfo();
            //BeanUtils.copyProperties(book, bookInfo);

            //编程缓存
            cacheManager.getCache("books").put(id, bookInfo);

            return bookInfo;
        } else {
            return (BookInfo) books.get();
        }
    }

    @CacheEvict(cacheNames = "books", allEntries = true, beforeInvocation = true)
    //此刻, getInfo方法放入缓存, query方法清除缓存(先访问两次getInfo方法, 缓存有效, 再访问一次query方法, 再访问getInfo方法, 则缓存失效了)
    //allEntries = true: 把所有的缓存都清除
    //清除缓存, beforeInvocation = true; 在调用这个方法之前就清除缓存

    @Cacheable(cacheNames = "books", key = "#condition.name", condition = "#pageable.pageSize > 10")
    //key = "#condition.name" : 只用查询条件中的name属性作为key. 因此, 只有传入的name参数改变时, 才会重新缓存, 如果只是size参数改变, 则不会记缓存
    //condition = "#pageable.pageSize > 10": 当pageable的size大于10时才会缓存
    public Page<BookInfo> query(BookCondition condition, Pageable pageable) {
        return null;
    }
}
```

#### RedisCacheConfig

```java
package me.hds.cache;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.autoconfigure.cache.CacheManagerCustomizer;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.interceptor.KeyGenerator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.serializer.Jackson2JsonRedisSerializer;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableCaching //使用缓存1 还需要在yml文件中进行配置 spring.cache.type=redis, 引入redis依赖
public class RedisCacheConfig {

    @Bean
    public KeyGenerator wiselyKeyGenerator() {
        return new KeyGenerator() {
            @Override
            public Object generate(Object target, Method method, Object... params) {
                StringBuilder sb = new StringBuilder();
                sb.append(target.getClass().getName());
                sb.append(method.getName());
                for (Object obj : params) {
                    sb.append(obj.toString());
                }
                return sb.toString();
            }
        };
    }

    @Bean
    public RedisTemplate<String, String> redisTemplate(RedisConnectionFactory factory) {
        StringRedisTemplate template = new StringRedisTemplate(factory);
        Jackson2JsonRedisSerializer jackson2JsonRedisSerializer = new Jackson2JsonRedisSerializer(Object.class);

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        objectMapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);

        jackson2JsonRedisSerializer.setObjectMapper(objectMapper);

        template.setValueSerializer(jackson2JsonRedisSerializer);
        template.afterPropertiesSet();

        return template;
    }

    @Bean
    public RedisCacheManager redisCacheManager(RedisTemplate redisTemplate) {
        return new RedisCacheManager(redisTemplate);
    }

    //自定义缓存的过期时间
    @Bean
    public CacheManagerCustomizer<RedisCacheManager> customizer() {
        return new CacheManagerCustomizer<RedisCacheManager>() {
            @Override
            public void customize(RedisCacheManager redisCacheManager) {
                //往redis里放的缓存, 过期时间都是10s
                redisCacheManager.setDefaultExpiration(10);

                //单独设置某一类(书/用户)缓存的过期时间
                Map<String, Long> map = new HashMap<>();
                map.put("books", 1000L);
                map.put("users", 2000L);
                redisCacheManager.setExpires(map);
            }
        };
    }
}
```



### RestTemplate

#### 创建RestTemplate的两种方式

##### 方式一 直接实例化

```java
RestTemplate restTemplate = new RestTemplate();
```

##### 方式二 借助Apache的HttpClient实现

```java
// 1.
HttpClientBuilder httpClientBuilder = HttpClientBuilder.create();
// 2.
HttpClient httpClient = httpClientBuilder.build();
// 3.
HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory(httpClient);
// 4.
RestTemplate restTemplate = new RestTemplate(factory);
```

- ClientHttpRequestFactory 接口有两个实现类 SimpleClientHttpRequestFactory 和 HttpComponentsClientHttpRequestFactory. 
- 前者是由javase内置实现的, 后者是由apache的 commons-httpclient 依赖提供的 HttpClient

#### HttpComponentsClientHttpRequestFactory

可以配置连接池, ssl证书等信息. 比 SimpleClientHttpRequestFactory 功能更强大

- RestTemplate的简单配置方式 

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

#### RestTemplate的使用示例

##### 一 设置header来请求和响应

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

##### 二 通过HttpClient获取cookie信息

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

##### 三 通过OkHttp发送请求

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



### 返回前端页面的两种方式

#### 方式一

```java
//返回值：String（前端页面名称）
//参数：Model model
//model.addAttribute("currentCity", city.getResult());
//返回值: return "redirect:/index"; || return "index";

@GetMapping("rent/house")
public String rentHousePage(@ModelAttribute RentSearch rentSearch,
                            Model model, HttpSession session,
                            RedirectAttributes redirectAttributes) {
    //首先, 查询房源信息必须要有城市信息
    //如果搜索类里没有, 就去session中拿, 如果session还没有, 就跳转到主页
    if (rentSearch.getCityEnName() == null) {
        String cityEnNameInSession = (String) session.getAttribute("cityEnName");
        if (cityEnNameInSession == null) {
            redirectAttributes.addAttribute("msg", "must_chose_city");
            return "redirect:/index";
        } else {
            rentSearch.setCityEnName(cityEnNameInSession);
        }
    } else {
        session.setAttribute("cityEnName", rentSearch.getCityEnName());
    }

    model.addAttribute("searchBody", rentSearch);
    model.addAttribute("regions", addressResult.getResult());

    //前端需要展示的价格区间(是一个map)
    model.addAttribute("priceBlocks", RentValueBlock.PRICE_BLOCK);
    model.addAttribute("areaBlocks", RentValueBlock.AREA_BLOCK);

    return "rent-list";
}
```

#### 方式二

```java
//返回值: ModelAndView
//返回: return new ModelAndView("页面的名称(从resources/templates/下写起)", "整体的模版名", model)
//参数: Model model
//model.addAttribute("title", "老卫的天气预报");
//前端: <h3 th:text=${reportModel.title}></h3>

@GetMapping("/cityId/{cityId}")
public ModelAndView getReportByCityId(@PathVariable("cityId") String cityId, Model model) throws Exception {
    model.addAttribute("title", "老卫的天气预报");
    model.addAttribute("cityId", cityId);
    model.addAttribute("cityList", cityDataService.listCity());
    model.addAttribute("report", weatherReportService.getDataByCityId(cityId));
    return new ModelAndView("weather/report", "reportModel", model);
}
```

#### Model和ModelAndView的区别

**ModelAndView需要分别设置数据和视图**

* modelAndView.addObject("item", item);
* modelAndView.setViewName("itemEdit");

**Model只需要设置数据, 然后以字符串形式返回视图即可**

* model.addAttribute("item", item);
* return "itemEdit";



### 事务 @Transactional

#### 说明

1. 在一个类或者一个方法上使用 @Transactional 注解
2. 在一个配置类上加入一个 @EnableTransactionManagement 注解代表启动事务。
3. 配置类需要实现 TransactionManagementConfigurer 事务管理器配置接口。并实现 annotationDrivenTransactionManager 方法返回一个包含了配置好数据源的 DataSourceTransactionManager 事务对象。
4. 这样就完成了事务配置，就可以在Spring使用事务的回滚或者提交功能了。
5. @Transactional注解加载A类的a方法上, 则A类的b方法调用a方法, 该注解无效, 必须在非A类中调用a方法才有效.
6. @Transactional(rollback = Exception.class) 只发生Exception异常, 才会回滚
7. save方法有事务, getInfo方法也有事务, getInfo方法中调用了save方法. 由于save方法配置的事务的传播级别是REQUIED, 所以这两个事务会合并在一个事务中(getInfo)
    `@Transactional(propagation = Propagation.REQUIRES_NEW)`
    则无论如何都会新开一个事务
    **应用场景**: 在创建订单之前, 要加一个日志信息, 无论成功与否, 这个日志都需要提交. 这时就要重新设置其传播级别为REQUIRES_NEW

> @Transactional(isolation = Isolation.DEFAULT) 隔离级别
> @Transactional(propagation = Propagation.REQUIRED) 传播行为



#### 编程实现说明

1. 在Spring Boot中，关于事务管理器，不管是JPA还是JDBC等都实现自接口 PlatformTransactionManager.
2.  当我们使用了spring-boot-starter-jdbc或spring-boot-starter-data-jpa依赖的时候，框架会自动默认分别注入DataSourceTransactionManager或JpaTransactionManager。所以我们不需要任何额外配置就可以用@Transactional注解进行事务的使用。
3. 首先使用注解 @EnableTransactionManagement 开启事务支持后，然后在访问数据库的Service方法上添加注解 @Transactional 便可。



PlatformTransactionManager： 事务管理器
TransactionDefinition： 事务的一些基础信息，如超时时间、隔离级别、传播属性等
TransactionStatus： 事务的一些状态信息，如是否是一个新的事务、是否已被标记为回滚

**事务的隔离级别是数据库本身的事务功能，然而事务的传播属性则是Spring自己为我们提供的功能，数据库事务没有事务的传播属性这一说法。**

#### 编程实现

```java
@EnableTransactionManagement 
// 开启注解事务管理，等同于xml配置文件中的 <tx:annotation-driven />
@SpringBootApplication
public class ProfiledemoApplication implements TransactionManagementConfigurer {

    // 创建事务管理器1
    @Bean(name = "txManager1")
    public PlatformTransactionManager txManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }

    // 创建事务管理器2
    @Bean(name = "txManager2")
    public PlatformTransactionManager txManager2(EntityManagerFactory factory) {
        return new JpaTransactionManager(factory);
    }

    // 实现接口 TransactionManagementConfigurer 方法 annotationDrivenTransactionManager，其返回值代表在拥有多个事务管理器的情况下默认使用的事务管理器
    @Override
    public PlatformTransactionManager annotationDrivenTransactionManager() {
        return txManager2;
    }

    public static void main(String[] args) {
        SpringApplication.run(ProfiledemoApplication.class, args);
    }
}

@Component
public class DevSendMessage implements SendMessage {

    // 使用value具体指定使用哪个事务管理器
    @Transactional(value = "txManager1")
    @Override
    public void send() {
        System.out.println(">>>>>>>>Dev Send()<<<<<<<<");
        send2();
    }

    // 在存在多个事务管理器的情况下，如果使用value具体指定
    // 则默认使用方法 annotationDrivenTransactionManager() 返回的事务管理器
    @Transactional
    public void send2() {
        System.out.println(">>>>>>>>Dev Send2()<<<<<<<<");
    }
}
```

#### 多数据源的配置

```java
// 配置主数据源
@Primary
@Bean(name = "prodDataSource")
@ConfigurationProperties(prefix = "spring.datasource")
public DataSource dataSource() {
    return DataSourceBuilder.create().build();
}

// 配置主数据源对应的JdbcTemplate
@Bean(name = "prodJdbc")
public JdbcTemplate prodJdbcTemplate(@Qualifier("prodDataSource") DataSource prodDataSource){ 
    return new JdbcTemplate(prodJdbcTemplate);
}

// 配置开发数据源
@Bean(name = "devDataSource")
@ConfigurationProperties(prefix = "spring.datasource.dev")
public DataSource devDataSource() {
    return DataSourceBuilder.create().build();
}

// 配置开发数据源对应的JdbcTemplate
@Bean(name = "devJdbc")
public JdbcTemplate devJdbcTemplate(@Qualifier("devDataSource") DataSource devDataSource) {
    return new JdbcTemplate(devDataSource);
}

// 注入到其他类时需要指定JdbcTemplate的名字
@Autowired
@Qualifier("prodJdbc")
private JdbcTemplate prodJdbcTemplate;
```

#### 查看某种数据库是否支持事务

```java
connection = dataSource.getConnection();
DatabaseMetaData databaseMetaData = connection.getMetaData();
supported = databaseMetaData.supportsTransactions();
```



### 其他

#### 获取HttpServletRequest的方法

```java
// 注意: interface HttpServletRequest extends ServletRequest
public void doSomething() {
    RequestAttributes requestAttributes = RequestContextHolder.getRequestAttributes();
    ServletRequestAttributes servletRequestAttributes = (ServletRequestAttributes) requestAttributes;
    HttpServletRequest request = servletRequestAttributes.getRequest();
    ServletContext servletContext = request.getServletContext();
    String requestURI = request.getRequestURI();
    servletContext.log(requestURI + " was filtered!");
}
```

#### 获取WebApplicationContext的方法

##### 方法一 在springmvc中获得ServletContext

```java
// 从ContextLoader类中获得当前的WebApplicationContext对象;
// 再从WebApplicationContext中获得ServletContext
WebApplicationContext webApplicationContext = ContextLoader.getCurrentWebApplicationContext();    
ServletContext servletContext = webApplicationContext.getServletContext(); 

// 从HttpServletRequest中获得HttpSession;
// 从HttpSession中获得ServletContext
ServletContext servletContext = request.getSession().getServletContext();   
```

##### 方法二 从servletContext获得WebApplicationContext

```java
// 方法1: 从ServletContext中获得属性名为ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE的属性值
WebApplicationContext webApplicationContext = (WebApplicationContext)servletContext.getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE);  

// 方法2: 使用spring提供的WebApplicationContextUtils工具类获取
// servletContext sc 可以具体换成 ServletConfig.getServletContext() 或者 this.getServletContext() 或者 request.getSession().getServletContext();   
WebApplicationContext webApplicationContext = WebApplicationContextUtils.getWebApplicationContext(ServletContext sc);  

```

#### 从Spring容器中获得Request对象的方法

```java
ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();  
HttpServletRequest request = attributes.getRequest();  
//页面请求路径  
String URL = request.getRequestURL().toString();  
```



### Controller和实体类的示例

#### UserController

```java
package me.hds.web.controller;

import com.fasterxml.jackson.annotation.JsonView;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import me.hds.dto.User;
import me.hds.dto.UserCondition;
import org.apache.commons.lang.builder.ReflectionToStringBuilder;
import org.apache.commons.lang.builder.ToStringStyle;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {

    @GetMapping
    @JsonView(User.UserSimpleView.class) //3.JsonView显示用户的简单视图, 也就是不显示密码的注解
    @ApiOperation(value = "用户查询服务") //swagger文档的注解
    public List<User> query(UserCondition userCondition, //执行查询时, 可以将所有的条件拼装在一个类中, 当成参数传入
                            @PageableDefault(page = 1, size = 5, sort = "username,asc") Pageable pageable) {

        //-----查看Spring security的过滤器链 开始------
        //Context是在第一个过滤器时SecurityContextPersistenceFilter, 从session中获取的, 如果是空, 则生成一个新的空的Context
        //保存当前用户的信息Authentication是由后续的用户名密码过滤器/Basic过滤器产生的

        //获取当前登录的用户信息
//        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
//        System.out.println(authentication);
//        if (authentication != null) {
//            System.out.println(authentication.getPrincipal());
//        }
        //-----查看Spring security的过滤器链 结束------

        System.out.println(ReflectionToStringBuilder.toString(userCondition, ToStringStyle.MULTI_LINE_STYLE));

        System.out.println(pageable.getPageSize());
        System.out.println(pageable.getPageNumber());
        System.out.println(pageable.getSort());

        List<User> users = new ArrayList<>();
        users.add(new User());
        users.add(new User());
        users.add(new User());
        return users;
    }


    //访问路径的正则表达式匹配, 只能接收数字
    @GetMapping("/{id:\\d+}")
    @JsonView(User.UserDetailView.class)    
    //3.JsonView显示用户的详细视图, 也就是在查询单个用户时, 显示密码的注解
    public User getInfo(@ApiParam("用户id") @PathVariable String id) {
        User user = new User();
        user.setUsername("tom");

        return user;
    }


    @PostMapping
    @ApiOperation(value = "创建用户")
    public User create(@Valid @RequestBody User user,
                       BindingResult bindingResult, //加了@Valid注解后, 需要从BindingResult拿到错误信息
                       @RequestParam("start") @DateTimeFormat(pattern = "yyyy-MM-dd") Date start) {

        if (bindingResult.hasErrors()) {
            bindingResult.getAllErrors().forEach(error -> System.out.println(error.getDefaultMessage()));
        }

        System.out.println(start); //Thu Sep 09 00:00:00 CST 1999

        System.out.println(user.getId());
        System.out.println(user.getUsername());
        System.out.println(user.getPassword());
        System.out.println(user.getBirthday()); //Sat Sep 09 11:11:11 CST 2017

        user.setId("1");
        return user; //这时, 返回的user中就带着id信息了, 但在创建时, 没有传id. 用来模拟数据库为user添加主键id字段
    }


    @PutMapping("/{id:\\d+}")
    public User update(@Valid @RequestBody User user,
                       BindingResult bindingResult) {

        if (bindingResult.hasErrors()) {
            bindingResult.getAllErrors().forEach(error -> {
                System.out.println(error.getDefaultMessage());

                System.out.println("下面是带有出错字段的错误信息");

                FieldError fieldError = (FieldError)error;
                String field = fieldError.getField();
                System.out.println(field + " " + error.getDefaultMessage());
            });
        }

        System.out.println(user.getId());
        System.out.println(user.getUsername());
        System.out.println(user.getPassword());
        System.out.println(user.getBirthday());

        user.setId("1");
        return user;
    }

    @DeleteMapping("/{id:\\d+}")
    public void delete(@PathVariable String id) {
        System.out.println(id);
    }


    @GetMapping("/exception/{id:\\d+}")
    @JsonView(User.UserDetailView.class)
    public User getInfo_exception(@PathVariable String id) {
        //默认异常
        //throw new RuntimeException("用户不存在");

        //自定义异常
        throw new UserNotExistException(id);
    }
}
```

#### User

```java
package me.hds.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonView;
import lombok.Data;
import me.hds.validator.MyConstraint;
import org.hibernate.validator.constraints.NotBlank;

import javax.validation.constraints.Past;
import java.util.Date;

@Data
public class User {

    //1.定义JsonView注解之用户简单视图
    public interface UserSimpleView {}
    //1.定义JsonView注解之用户详细视图
    public interface UserDetailView extends UserSimpleView {}

    @JsonView(UserSimpleView.class)
    private String id;

    @JsonView(UserSimpleView.class) //2. JsonView之在属性字段上加注解
    @MyConstraint(message = "自定义的校验注解")
    private String username;

    @JsonView(UserDetailView.class) //2.JsonView之在属性字段上加注解
    @NotBlank(message = "密码不能为空") //@Valid注解的使用
    private String password;

    @JsonView(UserSimpleView.class)
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    //当创建一个User时, 如果传入的生日是时间戳, 则会转成pattern格式的字符串: "birthday":"2017-10-16-11:34:26"
    //如果传入的生日是字符串, 则格式必须是yyyy-MM-dd HH:mm:ss, 否则会报错
    @Past(message = "生日必须是过去的时间") //人的生日必须是过去的时间
    private Date birthday;
}
```