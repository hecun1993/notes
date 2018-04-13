# **四**、Web开发

## 1、简介

使用SpringBoot；

**1）、创建SpringBoot应用，选中我们需要的模块；**

**2）、SpringBoot已经默认将这些场景配置好了，只需要在配置文件中指定少量配置就可以运行起来**

**3）、自己编写业务代码；**



*自动配置原理*

这个场景SpringBoot帮我们配置了什么能不能修改？能修改哪些配置？能不能扩展？xxx

```
xxxxAutoConfiguration：帮我们给容器中自动配置组件；
xxxxProperties:配置类来封装配置文件的内容；
```



## 2、SpringBoot对静态资源的映射规则

### ResourceProperties

可以设置和静态资源有关的参数，比如, 静态资源的存放位置, 缓存时间等

```java
@ConfigurationProperties(prefix = "spring.resources", ignoreUnknownFields = false)
public class ResourceProperties implements ResourceLoaderAware {
```

### WebMvcAuotConfiguration

```java
@Override
public void addResourceHandlers(ResourceHandlerRegistry registry) {
    if (!this.resourceProperties.isAddMappings()) {
        logger.debug("Default resource handling disabled");
        return;
    }
    //1. webjars的方式
    Integer cachePeriod = this.resourceProperties.getCachePeriod();
    if (!registry.hasMappingForPattern("/webjars/**")) {
        customizeResourceHandlerRegistration(
            registry.addResourceHandler("/webjars/**")
            .addResourceLocations(
                "classpath:/META-INF/resources/webjars/")
            .setCachePeriod(cachePeriod));
    }
    String staticPathPattern = this.mvcProperties.getStaticPathPattern();
    //2. 静态资源文件夹映射(4个默认的静态资源存放位置)
    if (!registry.hasMappingForPattern(staticPathPattern)) {
        customizeResourceHandlerRegistration(
            registry.addResourceHandler(staticPathPattern)
            .addResourceLocations(
                this.resourceProperties.getStaticLocations())
            .setCachePeriod(cachePeriod));
    }
}

//3. 配置欢迎页映射
@Bean
public WelcomePageHandlerMapping welcomePageHandlerMapping(
    ResourceProperties resourceProperties) {
    return new WelcomePageHandlerMapping(resourceProperties.getWelcomePage(),
                                         this.mvcProperties.getStaticPathPattern());
}

//4. 配置喜欢的图标
@Configuration
@ConditionalOnProperty(value = "spring.mvc.favicon.enabled", matchIfMissing = true)
public static class FaviconConfiguration {

    private final ResourceProperties resourceProperties;

    public FaviconConfiguration(ResourceProperties resourceProperties) {
        this.resourceProperties = resourceProperties;
    }

    @Bean
    public SimpleUrlHandlerMapping faviconHandlerMapping() {
        SimpleUrlHandlerMapping mapping = new SimpleUrlHandlerMapping();
        mapping.setOrder(Ordered.HIGHEST_PRECEDENCE + 1);
        //所有  **/favicon.ico 
        mapping.setUrlMap(Collections.singletonMap("**/favicon.ico",
                                                   faviconRequestHandler()));
        return mapping;
    }

    @Bean
    public ResourceHttpRequestHandler faviconRequestHandler() {
        ResourceHttpRequestHandler requestHandler = new ResourceHttpRequestHandler();
        requestHandler
            .setLocations(this.resourceProperties.getFaviconLocations());
        return requestHandler;
    }

}

```



1）所有 /webjars/** ，都去 classpath:/META-INF/resources/webjars/ 找资源；

​	webjars：以jar包的方式引入静态资源；

http://www.webjars.org/

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180203181751.png)

比如, 访问的链接是: localhost:8080/webjars/jquery/3.3.1/jquery.js

则, 由于我们引入了jquery-webjar的jar包, 则就会到类路径下的META-INF/resources/webjars/中找资源.

```xml
<!--引入jquery-webjar-->
在访问的时候只需要写webjars下面资源的名称即可
<dependency>
    <groupId>org.webjars</groupId>
    <artifactId>jquery</artifactId>
    <version>3.3.1</version>
</dependency>
```

2）"/**" 访问当前项目的任何资源，都去（静态资源的文件夹）找映射

```
"classpath:/META-INF/resources/", 
"classpath:/resources/",
"classpath:/static/", 
"classpath:/public/" 
"/"：当前项目的根路径
```

访问 localhost:8080/asserts/js/my.js ==>  去每个静态资源文件夹里找

3）欢迎页； 每个静态资源文件夹下的所有index.html页面；被"/**"映射；

访问 localhost:8080/   找index页面

4）所有的 **/favicon.ico  都是在静态资源文件下找；

访问任意一个页面, 只要把favicon.ico放在静态资源文件夹中 则都会正常显示.



## 3、模板引擎

JSP、Velocity、Freemarker、Thymeleaf

![](images/template-engine.png)



SpringBoot推荐的Thymeleaf；

语法更简单，功能更强大；



### 1、引入thymeleaf；

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
    2.1.6
</dependency>

默认引入的版本是2.1.6, 可以切换成3版本, 在pom.xml中的<properties></properties>标签里, 添加如下支持, 来切换thymeleaf版本
<properties>
    <thymeleaf.version>3.0.9.RELEASE</thymeleaf.version>
    <!-- 布局功能的支持程序  thymeleaf3 <==> layout2以上版本 -->
    <!-- thymeleaf2 <==> layout1-->
    <thymeleaf-layout-dialect.version>2.2.2</thymeleaf-layout-dialect.version>
</properties>
```



### 2、Thymeleaf使用

#### ThymeleafProperties

```java
@ConfigurationProperties(prefix = "spring.thymeleaf")
public class ThymeleafProperties {

	private static final Charset DEFAULT_ENCODING = Charset.forName("UTF-8");

	private static final MimeType DEFAULT_CONTENT_TYPE = MimeType.valueOf("text/html");

	public static final String DEFAULT_PREFIX = "classpath:/templates/";

	public static final String DEFAULT_SUFFIX = ".html";
```

只要我们把HTML页面放在classpath:/templates/，thymeleaf就能自动渲染；

#### 使用

1、导入thymeleaf的名称空间

```xml
<html lang="en" xmlns:th="http://www.thymeleaf.org">
```

2、使用thymeleaf语法；

```html
<!DOCTYPE html>
<html lang="en" xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <h1>成功！</h1>
    <!--th:text 将div里面的文本内容设置为 -->
    <div th:text="${hello}">这是显示欢迎信息</div>
</body>
</html>
```

```java
@RequestMapping("/success")
public String hello(Map<String, Object> map) {
    map.put("hello", "你好");
    return "success";
}
```



### 3、语法规则

1）、th:text；改变当前元素里面的文本内容；

​	th：任意html属性；来替换原生属性的值

```html
<div id="div" th:id="${div}"></div>
```

![](images/2018-02-04_123955.png)



2）、表达式？

```properties
Simple expressions:（表达式语法）
    Variable Expressions: ${...}：获取变量值；OGNL；
    		1）、获取对象的属性、调用方法
    		2）、使用内置的基本对象：
    			#ctx : the context object.
    			#vars: the context variables.
                #locale : the context locale.
                #request : (only in Web Contexts) the HttpServletRequest object.
                #response : (only in Web Contexts) the HttpServletResponse object.
                #session : (only in Web Contexts) the HttpSession object.
                #servletContext : (only in Web Contexts) the ServletContext object.
                
                ${session.foo}
            3）、内置的一些工具对象：
#execInfo : information about the template being processed.
#messages : methods for obtaining externalized messages inside variables expressions, in the same way as they would be obtained using #{…} syntax.
#uris : methods for escaping parts of URLs/URIs
#conversions : methods for executing the configured conversion service (if any).
#dates : methods for java.util.Date objects: formatting, component extraction, etc.
#calendars : analogous to #dates , but for java.util.Calendar objects.
#numbers : methods for formatting numeric objects.
#strings : methods for String objects: contains, startsWith, prepending/appending, etc.
#objects : methods for objects in general.
#bools : methods for boolean evaluation.
#arrays : methods for arrays.
#lists : methods for lists.
#sets : methods for sets.
#maps : methods for maps.
#aggregates : methods for creating aggregates on arrays or collections.
#ids : methods for dealing with id attributes that might be repeated (for example, as a result of an iteration).

    Selection Variable Expressions: *{...}：选择表达式：和${}在功能上是一样；
    	补充：配合 th:object="${session.user}：
   <div th:object="${session.user}">
    <p>Name: <span th:text="*{firstName}">Sebastian</span>.</p>
    <p>Surname: <span th:text="*{lastName}">Pepper</span>.</p>
    <p>Nationality: <span th:text="*{nationality}">Saturn</span>.</p>
    </div>
    
    Message Expressions: #{...}：获取国际化内容
    Link URL Expressions: @{...}：定义URL；
    		@{/order/process(execId=${execId},execType='FAST')}
    Fragment Expressions: ~{...}：片段引用表达式
    		<div th:insert="~{commons :: main}">...</div>
    		
Literals（字面量）
      Text literals: 'one text' , 'Another one!' ,…
      Number literals: 0 , 34 , 3.0 , 12.3 ,…
      Boolean literals: true , false
      Null literal: null
      Literal tokens: one , sometext , main ,…
Text operations:（文本操作）
    String concatenation: +
    Literal substitutions: |The name is ${name}|
Arithmetic operations:（数学运算）
    Binary operators: + , - , * , / , %
    Minus sign (unary operator): -
Boolean operations:（布尔运算）
    Binary operators: and , or
    Boolean negation (unary operator): ! , not
Comparisons and equality:（比较运算）
    Comparators: > , < , >= , <= ( gt , lt , ge , le )
    Equality operators: == , != ( eq , ne )
Conditional operators:条件运算（三元运算符）
    If-then: (if) ? (then)
    If-then-else: (if) ? (then) : (else)
    Default: (value) ?: (defaultvalue)
Special tokens:
    No-Operation: _ 
```

#### 示例

```html
<!-- text会转义特殊字符, 也就是把<h1>按照原样输出-->
<div th:text="${hello}"></div>
<!-- utext不会转义特殊字符, 也就是把<h1>按照一级标题输出了-->
<div th:utext="${hello}"></div>
<hr/>

<!-- th:each每次遍历都会生成当前这个标签： 3个h4 -->
<h4 th:text="${user}"  th:each="user:${users}"></h4>
<hr/>
<!-- 会产生3个span标签, 在行内写的时候, 用 [[]] 来解析${}的值 -->
<h4>
    <span th:each="user:${users}"> [[${user}]] </span>
</h4>
```



## 4、SpringMVC自动配置原理

https://docs.spring.io/spring-boot/docs/1.5.10.RELEASE/reference/htmlsingle/#boot-features-developing-web-applications

### 1. Spring MVC auto-configuration

Spring Boot 自动配置好了SpringMVC. 以下是SpringBoot对SpringMVC的默认配置

#### WebMvcAutoConfiguration

- Inclusion of `ContentNegotiatingViewResolver` and `BeanNameViewResolver` beans.

  - 自动配置了ViewResolver（视图解析器：根据方法的返回值得到视图对象（View），视图对象决定如何渲染（转发？重定向？））

  - ContentNegotiatingViewResolver：先用BeanFactoryUtils工具获得所有的视图解析器(ViewResolver.class) 再组合容器中存在的所有的视图解析器；

  - **<u>如何定制：</u>**我们可以自己给容器中注册一个视图解析器；然后ContentNegotiatingViewResolver会自动将其组合进来；

    ```java
    // 自己创建的实现了ViewResolver接口的视图解析器对象
    public static class MyViewResolver implements ViewResolver {
        @Override
        public View resolveViewName(String viewName, Locale locale) throws Exception {
            return null;
        }
    }

    // 通过@Bean, 将这个自己的视图解析器对象放在spring容器中
    @Bean
    public ViewResolver myViewReolver(){
        return new MyViewResolver();
    }

    此时, 我们在DispatcherServlet的doDispatch方法上打断点, 就可以看到容器中的各种对象, 包括上述我们注册进去的MyViewResolver视图解析器
    ```

    ​

- Support for serving static resources, including support for WebJars (see below).静态资源文件夹路径,webjars

- Static `index.html` support. 静态首页访问

- Custom `Favicon` support (see below).  favicon.ico

  ​

- 自动注册了  `Converter`, `GenericConverter`, `Formatter` beans.

  - Converter：转换器；  public String hello(User user)：类型转换使用Converter. 把页面提交的18字符串, 转成Integer的18
  - Formatter  格式化器；  把页面提交的2017.12.17字符串, 转成Date类型

```java
@Bean
@ConditionalOnProperty(prefix = "spring.mvc", name = "date-format")
//@ConditionalOnProperty: 如果我们在配置文件中配置了日期格式化的规则, 就会注册Formatter组件
public Formatter<Date> dateFormatter() {
    return new DateFormatter(this.mvcProperties.getDateFormat());//日期格式化组件
}
```

**<u>如何定制：</u>**自己添加的格式化器转换器，我们只需要放在容器中即可

- Support for `HttpMessageConverters` (see below).

  - HttpMessageConverter：SpringMVC用来转换Http请求和响应的；比如把User对象转成Json；

  - HttpMessageConverters : 收集所有的HttpMessageConverter；

    **<u>如何定制：</u>**自己给容器中添加HttpMessageConverter，只需要将自己的组件注册到容器中

- Automatic registration of `MessageCodesResolver` .定义错误代码生成规则

- Automatic use of a `ConfigurableWebBindingInitializer` bean 

  **<u>如何定制：</u>**注册配置一个ConfigurableWebBindingInitializer, 添加到容器, 来替换默认的；

  初始化WebDataBinderweb数据绑定器；将请求数据与JavaBean绑定



#### org.springframework.boot.autoconfigure.web：web的所有自动配置场景

If you want to keep Spring Boot MVC features, and you just want to add additional [MVC configuration](https://docs.spring.io/spring/docs/4.3.14.RELEASE/spring-framework-reference/htmlsingle#mvc) (interceptors, formatters, view controllers etc.) you can add your own `@Configuration` class of type `WebMvcConfigurerAdapter`, but **without** `@EnableWebMvc`. If you wish to provide custom instances of `RequestMappingHandlerMapping`, `RequestMappingHandlerAdapter` or `ExceptionHandlerExceptionResolver` you can declare a `WebMvcRegistrationsAdapter` instance providing such components.

If you want to take complete control of Spring MVC, you can add your own `@Configuration` annotated with `@EnableWebMvc`.

### 2、扩展SpringMVC

##### 原始写法: 用xml文件

```xml
<mvc:view-controller path="/hello" view-name="success"/>
<mvc:interceptors>
    <mvc:interceptor>
        <mvc:mapping path="/hello"/>
        <bean></bean>
    </mvc:interceptor>
</mvc:interceptors>
```

##### 编写一个配置类（@Configuration）是WebMvcConfigurerAdapter类型；<u>不能标注@EnableWebMvc注解</u>

既保留了所有的自动配置，也能用我们扩展的配置；

```java
// 使用继承WebMvcConfigurerAdapter抽象类的配置类MyMvcConfig, 可以来扩展SpringMVC的功能
@Configuration
public class MyMvcConfig extends WebMvcConfigurerAdapter {
    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        //浏览器发送 /atguigu 请求来到 success
        registry.addViewController("/atguigu").setViewName("success");
    }
}
```

##### 原理：

​	1）WebMvcAutoConfiguration是SpringMVC的自动配置类

WebMvcAutoConfiguration类中有一个内部类WebMvcAutoConfigurationAdapter, 这个类就继承了WebMvcConfigurerAdapter抽象类. 重写了其中的很多扩展功能的方法, 也添加了各种组件.

​	2）在内部类WebMvcAutoConfigurationAdapter上, 有一个@Import注解, 会导入EnableWebMvcConfiguration；

@Import(**EnableWebMvcConfiguration**.class)

EnableWebMvcConfiguration类也是WebMvcAutoConfiguration的内部类, 源码如下: 

```java
@Configuration
public static class EnableWebMvcConfiguration extends DelegatingWebMvcConfiguration {
    private final WebMvcConfigurerComposite configurers = new WebMvcConfigurerComposite();

    // 下面这个方法在父类DelegatingWebMvcConfiguration中
    // 标注了@Autowired, 则方法的参数List<WebMvcConfigurer> configurers, 就要从容器中获取. 
    // 也就是要从容器中获取所有的WebMvcConfigurer接口的实现类
    @Autowired(required = false)
    public void setConfigurers(List<WebMvcConfigurer> configurers) {
        if (!CollectionUtils.isEmpty(configurers)) {
            this.configurers.addWebMvcConfigurers(configurers);
            
            //一个参考实现；将所有的WebMvcConfigurer相关配置都一起调用；  
            @Override
            // public void addViewControllers(ViewControllerRegistry registry) {
            //    for (WebMvcConfigurer delegate : this.delegates) {
            //       delegate.addViewControllers(registry);
            //   }
        }
    }
}
```

​	3）容器中所有的WebMvcConfigurer接口都会一起起作用；

​	4）我们的配置类也会被调用；

最终效果：SpringMVC的自动配置和我们的扩展配置都会起作用；

### 3、全面接管SpringMVC；

SpringBoot对SpringMVC的自动配置不需要了，所有都是我们自己配置；所有的SpringMVC的自动配置都失效了

**在配置类中添加@EnableWebMvc即可失效所有自动配置；**

```java
@EnableWebMvc
@Configuration
public class MyMvcConfig extends WebMvcConfigurerAdapter {
    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        //浏览器发送 /atguigu 请求来到 success
        registry.addViewController("/atguigu").setViewName("success");
    }
}
```

原理：

为什么@EnableWebMvc自动配置就失效了；

1）@EnableWebMvc的核心

```java
@Import(DelegatingWebMvcConfiguration.class)
public @interface EnableWebMvc {
```

2）、也就是说加了@EnableWebMvc之后, 容器中有了WebMvcConfigurationSupport类

```java
@Configuration
public class DelegatingWebMvcConfiguration extends WebMvcConfigurationSupport {
```

3）、WebMvcAutoConfiguration的源码显示, 只有容器中没有WebMvcConfigurationSupport组件时, 自动配置才生效

```java
@Configuration
@ConditionalOnWebApplication
@ConditionalOnClass({ Servlet.class, DispatcherServlet.class,
		WebMvcConfigurerAdapter.class })
//容器中没有这个组件的时候，这个自动配置类才生效
@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE + 10)
@AutoConfigureAfter({ DispatcherServletAutoConfiguration.class,
		ValidationAutoConfiguration.class })
public class WebMvcAutoConfiguration {
```

4）、@EnableWebMvc将WebMvcConfigurationSupport组件导入进来；

5）、导入的WebMvcConfigurationSupport只是SpringMVC最基本的功能；



## 5、如何修改SpringBoot的默认配置

模式：

​	1）、SpringBoot在自动配置很多组件的时候，先看容器中有没有用户自己配置的（@Bean、@Component）如果有就用用户配置的，如果没有，才自动配置；如果有些组件可以有多个（ViewResolver）将用户配置的和自己默认的组合起来；

​	2）、在SpringBoot中会有非常多的xxxConfigurer接口帮助我们进行扩展配置

​	3）、在SpringBoot中会有很多的xxxCustomizer帮助我们进行定制配置



## 6、错误处理机制

### 1）、SpringBoot默认的错误处理机制

#### 默认效果：

##### 1）浏览器，返回一个默认的错误页面

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180226173408.png)

> 浏览器发送请求的请求头：text/html

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180226180347.png)

##### 2）其他客户端，默认响应一个json数据

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180226173527.png)

​		![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180226180504.png)

##### 原理

参照ErrorMvcAutoConfiguration；错误处理的自动配置；

ErrorMvcAutoConfiguration给容器中添加了以下组件

###### 1. DefaultErrorAttributes implements ErrorAttributes

```java
// 在页面共享信息时, 需要收集所有的错误信息.
// getErrorAttributes()方法就是来将所有的默认错误信息放在Map中, 返回.
@Override
public Map<String, Object> getErrorAttributes(RequestAttributes requestAttributes,
                                              boolean includeStackTrace) {
    Map<String, Object> errorAttributes = new LinkedHashMap<String, Object>();
    errorAttributes.put("timestamp", new Date());
    addStatus(errorAttributes, requestAttributes);
    addErrorDetails(errorAttributes, requestAttributes, includeStackTrace);
    addPath(errorAttributes, requestAttributes);
    return errorAttributes;
}
```

###### 2. BasicErrorController extends AbstractErrorController implements ErrorController：处理/error请求

```java
@Controller
@RequestMapping("${server.error.path:${error.path:/error}}")
// 可以在全局配置文件进行配置 server.error.path, 或者 error.path 如果没有配置, 则就是/error
public class BasicErrorController extends AbstractErrorController {
    
    @RequestMapping(produces = "text/html")
    // 处理来自浏览器跳转页面时, 发送的请求
	public ModelAndView errorHtml(HttpServletRequest request,
			HttpServletResponse response) {
		HttpStatus status = getStatus(request);
        // 这里的getErrorAttributes就是上述的方法
		Map<String, Object> model = Collections.unmodifiableMap(getErrorAttributes(
				request, isIncludeStackTrace(request, MediaType.TEXT_HTML)));
		
        // 设置了状态码, 通过状态码来选择要返回的4xx, 5xx页面
        response.setStatus(status.value());
        	// status的源代码如下
        	protected HttpStatus getStatus(HttpServletRequest request) {
                Integer statusCode = (Integer)request.getAttribute("javax.servlet.error.status_code");
                if (statusCode == null) {
                    return HttpStatus.INTERNAL_SERVER_ERROR;
                } else {
                    try {
                        return HttpStatus.valueOf(statusCode);
                    } catch (Exception var4) {
                        return HttpStatus.INTERNAL_SERVER_ERROR;
                    }
                }
            }

        //去哪个页面作为错误页面；包含页面地址和页面内容
		ModelAndView modelAndView = resolveErrorView(request, response, status, model);
		return (modelAndView == null ? new ModelAndView("error", model) : modelAndView);
	}

	@RequestMapping
	@ResponseBody    
    // 产生json数据，其他客户端的请求来到这个方法处理；
	public ResponseEntity<Map<String, Object>> error(HttpServletRequest request) {
		Map<String, Object> body = getErrorAttributes(request,
				isIncludeStackTrace(request, MediaType.ALL));
		HttpStatus status = getStatus(request);
		return new ResponseEntity<Map<String, Object>>(body, status);
	}
```

###### 3. ErrorPageCustomizer：定制错误页面的访问路径 默认是path的值 /error

```java
@Value("${error.path:/error}")
private String path = "/error";  系统出现错误以后来到error请求进行处理；（web.xml注册的错误页面规则）

// getPath() 时返回的是 /error
private static class ErrorPageCustomizer implements ErrorPageRegistrar, Ordered {
    private final ServerProperties properties;

    protected ErrorPageCustomizer(ServerProperties properties) {
        this.properties = properties;
    }

    public void registerErrorPages(ErrorPageRegistry errorPageRegistry) {
        ErrorPage errorPage = new ErrorPage(this.properties.getServletPrefix() + this.properties.getError().getPath());
        errorPageRegistry.addErrorPages(new ErrorPage[]{errorPage});
    }

    public int getOrder() {
        return 0;
    }
}
```

###### 4. DefaultErrorViewResolver：解析错误页面, 看是否有模板解析引擎, 有的话, 就解析error/404, 放在templates目录下, 如果没有, 则说明放在静态资源文件下了, 直接返回.

```java
@Override
public ModelAndView resolveErrorView(HttpServletRequest request, HttpStatus status,
                                     Map<String, Object> model) {
    ModelAndView modelAndView = resolve(String.valueOf(status), model);
    if (modelAndView == null && SERIES_VIEWS.containsKey(status.series())) {
        modelAndView = resolve(SERIES_VIEWS.get(status.series()), model);
    }
    return modelAndView;
}

private ModelAndView resolve(String viewName, Map<String, Object> model) {
    //默认SpringBoot可以去找到一个页面  error/404
    //所以只需要在classpath下, 创建一个error文件夹, 里面放404.html页面, 即可跳转. error/404
    String errorViewName = "error/" + viewName;

    //模板引擎可以解析这个页面地址
    TemplateAvailabilityProvider provider = this.templateAvailabilityProviders
        .getProvider(errorViewName, this.applicationContext);
    if (provider != null) {
        //模板引擎可用的情况下返回到errorViewName指定的视图地址
        return new ModelAndView(errorViewName, model);
    }
    //模板引擎不可用，就在静态资源文件夹下找errorViewName对应的页面   error/404.html
    return resolveResource(errorViewName, model);
}
```

一但系统出现4xx或者5xx之类的错误；ErrorPageCustomizer就会生效（定制错误的响应规则）；就会来到/error请求；就会被**BasicErrorController**处理；

去哪个响应页面是由**DefaultErrorViewResolver**解析得到的；

```java
protected ModelAndView resolveErrorView(HttpServletRequest request,
    HttpServletResponse response, HttpStatus status, Map<String, Object> model) {
    // 所有的ErrorViewResolver得到ModelAndView
    for (ErrorViewResolver resolver : this.errorViewResolvers) {
        ModelAndView modelAndView = resolver.resolveErrorView(request, status, model);
        if (modelAndView != null) {
            return modelAndView;
        }
    }
    return null;
}
```



### 2）如何定制错误响应：

#### **1）如何定制错误的页面；**

​	**1）有模板引擎的情况下；error/状态码;** 【将错误页面命名为  错误状态码.html 放在模板引擎文件夹里面的 error文件夹下】，发生此状态码的错误就会来到对应的页面；

我们可以使用4xx和5xx作为错误页面的文件名来匹配这种类型的所有错误，精确优先（优先寻找精确的状态码.html）；		

​	页面能获取的信息；

​	timestamp：时间戳

​	status：状态码

​	error：错误提示

​	exception：异常对象

​	message：异常消息

​	errors：JSR303数据校验的错误都在这里

​	**2）没有模板引擎（模板引擎找不到这个错误页面），静态资源文件夹下找**

​	**3）以上都没有错误页面，就是默认来到SpringBoot默认的错误提示页面**

#### 2）如何定制错误的json数据；

1）自定义异常处理&返回定制json数据；

```java
@ControllerAdvice
public class MyExceptionHandler {

    @ResponseBody
    @ExceptionHandler(UserNotExistException.class)
    public Map<String,Object> handleException(Exception e){
        Map<String,Object> map = new HashMap<>();
        map.put("code","user.notexist");
        map.put("message",e.getMessage());
        return map;
    }
}
// 没有自适应效果, 无法实现根据浏览器还是json分别响应...
```

2）转发到/error进行自适应响应效果处理

```java
@ExceptionHandler(UserNotExistException.class)
public String handleException(Exception e, HttpServletRequest request){
    Map<String,Object> map = new HashMap<>();
    /*
Integer statusCode = (Integer) request.getAttribute("javax.servlet.error.status_code");
     */
    // 传入我们自己的错误状态码  4xx 5xx，否则就不会进入定制错误页面的解析流程
    request.setAttribute("javax.servlet.error.status_code",500);
    map.put("code","user.notexist");
    map.put("message",e.getMessage());
    //转发到/error, 来实现根据浏览器还是json分别响应
    return "forward:/error";
}
```

#### 3）将自定义响应数据添加到默认返回的json中

出现错误以后，会来到/error请求，会被BasicErrorController处理，响应出去可以获取的数据是由getErrorAttributes得到的（是AbstractErrorController抽象类（ErrorController接口）规定的方法）；

1、完全来编写一个ErrorController的实现类【或者是编写AbstractErrorController的子类】，放在容器中；

2、页面上能用的数据，或者是json返回能用的数据都是通过errorAttributes.getErrorAttributes得到；

容器中DefaultErrorAttributes#getErrorAttributes()；默认进行数据处理的；

自定义ErrorAttributes, 继承默认的DefaultErrorAttributes,  重写getErrorAttributes方法, 首先要调用父类的getErrorAttributes方法, 再添加一些我们的自定义属性.

一定要把自定义的ErrorAttributes注入到容器中.

```java
//给容器中加入我们自己定义的ErrorAttributes
@Component
public class MyErrorAttributes extends DefaultErrorAttributes {
    @Override
    public Map<String, Object> getErrorAttributes(RequestAttributes requestAttributes, boolean includeStackTrace) {
        Map<String, Object> map = super.getErrorAttributes(requestAttributes, includeStackTrace);
        map.put("company","atguigu");
        return map;
    }
}
```

最终的效果：响应是自适应的，可以通过定制ErrorAttributes改变需要返回的内容，

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180228135513.png)



## 7、配置嵌入式Servlet容器

SpringBoot默认使用Tomcat作为嵌入式的Servlet容器；

![](/Users/bytedance/Documents/Spring%20Boot%20%E7%AC%94%E8%AE%B0/images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180301142915.png)



### 1）如何定制和修改Servlet容器的相关配置

##### 1、修改和server有关的配置（ServerProperties【也是实现了EmbeddedServletContainerCustomizer接口】）

```properties
server.port=8081
server.context-path=/crud

server.tomcat.uri-encoding=UTF-8

# 通用的Servlet容器设置
server.xxx
# Tomcat的设置
server.tomcat.xxx
```

##### 2、编写一个**EmbeddedServletContainerCustomizer**：嵌入式的Servlet容器的定制器；

在配置类中创建一个EmbeddedServletContainerCustomizer接口的组件, 放入容器中, 通过实现这个接口中的customize方法, 利用参数ConfigurableEmbeddedServletContainer来设置属性, 修改Servlet容器的配置

```java
@Bean  
//一定要将这个定制器加入到容器中
public EmbeddedServletContainerCustomizer embeddedServletContainerCustomizer(){
    return new EmbeddedServletContainerCustomizer() {
        //定制嵌入式的Servlet容器相关的规则
        @Override
        public void customize(ConfigurableEmbeddedServletContainer container) {
            container.setPort(8083);
        }
    };
}
```

### 2）注册Servlet三大组件【Servlet、Filter、Listener】

由于SpringBoot默认是以jar包的方式启动嵌入式的Servlet容器来启动SpringBoot的web应用，没有web.xml文件。(webapps/WEB-INF/web.xml)

注册三大组件用以下方式

#### ServletRegistrationBean

```java
package com.atguigu.springboot.servlet;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class MyServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        doPost(req,resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.getWriter().write("Hello MyServlet");
    }
}


//注册三大组件
@Bean
public ServletRegistrationBean myServlet() {
    // /myServlet是映射路径
    ServletRegistrationBean registrationBean = new ServletRegistrationBean(new MyServlet(), "/myServlet");
    return registrationBean;
}
```

#### FilterRegistrationBean

```java
package com.atguigu.springboot.filter;

import javax.servlet.*;
import java.io.IOException;

public class MyFilter implements Filter {

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        System.out.println("MyFilter process...");
        chain.doFilter(request,response);
    }

    @Override
    public void destroy() {
    }
}


@Bean
public FilterRegistrationBean myFilter() {
    FilterRegistrationBean registrationBean = new FilterRegistrationBean();
    registrationBean.setFilter(new MyFilter());
    registrationBean.setUrlPatterns(Arrays.asList("/hello", "/myServlet"));
    return registrationBean;
}
```

#### ServletListenerRegistrationBean

```java
package com.atguigu.springboot.listener;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

public class MyListener implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent sce) {
        System.out.println("contextInitialized...web应用启动");
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("contextDestroyed...当前web项目销毁");
    }
}

@Bean
public ServletListenerRegistrationBean myListener(){
    ServletListenerRegistrationBean<MyListener> registrationBean = new ServletListenerRegistrationBean<>(new MyListener());
    return registrationBean;
}
```

#### 注意: DispatcherServlet

SpringBoot帮我们自动SpringMVC的时候，自动的注册SpringMVC的前端控制器；DispatcherServlet；

##### DispatcherServletAutoConfiguration中

```java
@Bean(name = DEFAULT_DISPATCHER_SERVLET_REGISTRATION_BEAN_NAME)
@ConditionalOnBean(value = DispatcherServlet.class, name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
public ServletRegistrationBean dispatcherServletRegistration(
      DispatcherServlet dispatcherServlet) {
   	ServletRegistrationBean registration = new ServletRegistrationBean(
         dispatcherServlet, this.serverProperties.getServletMapping());
    // 默认拦截： /  所有请求；包括静态资源，但是不拦截jsp请求；   
    // /*会拦截jsp
    // 可以通过server.servletPath来修改SpringMVC前端控制器默认拦截的请求路径
    registration.setName(DEFAULT_DISPATCHER_SERVLET_BEAN_NAME);
    registration.setLoadOnStartup(
        this.webMvcProperties.getServlet().getLoadOnStartup());
    if (this.multipartConfig != null) {
        registration.setMultipartConfig(this.multipartConfig);
    }
    return registration;
}
```

### 2）替换为其他嵌入式Servlet容器

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180302114401.png)

#### Tomcat（默认使用）

```xml
<dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-web</artifactId>
   引入web模块默认就是使用嵌入式的Tomcat作为Servlet容器；
</dependency>
```

#### Jetty: 适合开发长连接的应用, 聊天应用

```xml
<!-- 引入web模块 -->
<dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-web</artifactId>
   <exclusions>
      <exclusion>
         <artifactId>spring-boot-starter-tomcat</artifactId>
         <groupId>org.springframework.boot</groupId>
      </exclusion>
   </exclusions>
</dependency>

<!--引入其他的Servlet容器-->
<dependency>
   <artifactId>spring-boot-starter-jetty</artifactId>
   <groupId>org.springframework.boot</groupId>
</dependency>
```

#### Undertow: 不支持jsp, 但并发性能好

```xml
<!-- 引入web模块 -->
<dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-web</artifactId>
   <exclusions>
      <exclusion>
         <artifactId>spring-boot-starter-tomcat</artifactId>
         <groupId>org.springframework.boot</groupId>
      </exclusion>
   </exclusions>
</dependency>

<!--引入其他的Servlet容器-->
<dependency>
   <artifactId>spring-boot-starter-undertow</artifactId>
   <groupId>org.springframework.boot</groupId>
</dependency>
```

### 3）嵌入式Servlet容器自动配置原理；

EmbeddedServletContainerAutoConfiguration：嵌入式的Servlet容器自动配置？

```java
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@Configuration
@ConditionalOnWebApplication
@Import(BeanPostProcessorsRegistrar.class)
// 导入BeanPostProcessorsRegistrar类
// 这个类 implements ImportBeanDefinitionRegistrar
// 调用 registerBeanDefinitions()方法
// 导入了EmbeddedServletContainerCustomizerBeanPostProcessor类
// [后置处理器：bean初始化前后（创建完对象，还没赋值赋值）执行初始化工作]
public class EmbeddedServletContainerAutoConfiguration {
    
    @Configuration
	@ConditionalOnClass({ Servlet.class, Tomcat.class })
    // 判断当前类路径下是否有Servlet, Tomcat这两个类. 只要导入相关依赖, 就有
	@ConditionalOnMissingBean(value = EmbeddedServletContainerFactory.class, search = SearchStrategy.CURRENT)
    // 判断当前容器没有用户自己定义的EmbeddedServletContainerFactory：嵌入式的Servlet容器工厂；这个类的作用是：创建嵌入式的Servlet容器, 满足就注入下面这个类EmbeddedTomcat
	public static class EmbeddedTomcat {
		@Bean
		public TomcatEmbeddedServletContainerFactory tomcatEmbeddedServletContainerFactory() {
			return new TomcatEmbeddedServletContainerFactory();
		}
	}
    
    /**
	 * Nested configuration if Jetty is being used.
	 */
	@Configuration
	@ConditionalOnClass({ Servlet.class, Server.class, Loader.class,
			WebAppContext.class })
	@ConditionalOnMissingBean(value = EmbeddedServletContainerFactory.class, search = SearchStrategy.CURRENT)
	public static class EmbeddedJetty {

		@Bean
		public JettyEmbeddedServletContainerFactory jettyEmbeddedServletContainerFactory() {
			return new JettyEmbeddedServletContainerFactory();
		}

	}

	/**
	 * Nested configuration if Undertow is being used.
	 */
	@Configuration
	@ConditionalOnClass({ Servlet.class, Undertow.class, SslClientAuthMode.class })
	@ConditionalOnMissingBean(value = EmbeddedServletContainerFactory.class, search = SearchStrategy.CURRENT)
	public static class EmbeddedUndertow {

		@Bean
		public UndertowEmbeddedServletContainerFactory undertowEmbeddedServletContainerFactory() {
			return new UndertowEmbeddedServletContainerFactory();
		}

	}
```

#### 1）EmbeddedServletContainerFactory（嵌入式Servlet容器工厂）

有三种嵌入式Servlet容器工厂, 对应三种可以创建的Servlet容器

```java
public interface EmbeddedServletContainerFactory {
   //获取嵌入式的Servlet容器 EmbeddedServletContainer
   EmbeddedServletContainer getEmbeddedServletContainer(
         ServletContextInitializer... initializers);
}
```

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180302144835.png)

#### 2）EmbeddedServletContainer（嵌入式的Servlet容器）

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180302144910.png)



#### 3）以**TomcatEmbeddedServletContainerFactory**为例

```java
@Override
public EmbeddedServletContainer getEmbeddedServletContainer(
      ServletContextInitializer... initializers) {
    
    //1. 创建一个Tomcat
    Tomcat tomcat = new Tomcat();

    //2. 配置Tomcat的基本属性
    File baseDir = (this.baseDirectory != null ? this.baseDirectory
                    : createTempDir("tomcat"));
    tomcat.setBaseDir(baseDir.getAbsolutePath());
    Connector connector = new Connector(this.protocol);
    tomcat.getService().addConnector(connector);
    customizeConnector(connector);
    tomcat.setConnector(connector);
    tomcat.getHost().setAutoDeploy(false);
    configureEngine(tomcat.getEngine());
    for (Connector additionalConnector : this.additionalTomcatConnectors) {
        tomcat.getService().addConnector(additionalConnector);
    }
    prepareContext(tomcat.getHost(), initializers);

    //3. 将配置好的Tomcat传入getTomcatEmbeddedServletContainer方法，返回一个EmbeddedServletContainer
    // 注意: 同时还会启动Tomcat服务器
    return getTomcatEmbeddedServletContainer(tomcat);
}
```

#### 4）对嵌入式容器的配置修改是怎么生效？

```
ServerProperties
EmbeddedServletContainerCustomizer
```

**EmbeddedServletContainerCustomizer**：定制器帮我们修改了Servlet容器的配置



#### 5）容器中导入了 **EmbeddedServletContainerCustomizerBeanPostProcessor**

```java
//初始化之前
@Override
public Object postProcessBeforeInitialization(Object bean, String beanName)
      throws BeansException {
    // 判断: 如果当前初始化的是一个ConfigurableEmbeddedServletContainer类型的组件, 就进行操作
    // 而各种Servlet容器的工厂类, TomcatEmbeddedServletContainerFactory, 都实现了这个接口
    // 所以继续操作
    if (bean instanceof ConfigurableEmbeddedServletContainer) {
        postProcessBeforeInitialization((ConfigurableEmbeddedServletContainer) bean);
        	// postProcessBeforeInitialization方法如下
        	private void postProcessBeforeInitialization(
                        ConfigurableEmbeddedServletContainer bean) {
                // 获取所有的嵌入式容器定制器，
                // 调用每一个定制器的customize方法来给Servlet容器进行属性赋值；
                for (EmbeddedServletContainerCustomizer customizer : getCustomizers()) {
                    customizer.customize(bean);
                }
			}
    }
    return bean;
}

private Collection<EmbeddedServletContainerCustomizer> getCustomizers() {
    if (this.customizers == null) {
        this.customizers = new ArrayList<EmbeddedServletContainerCustomizer>(
            this.beanFactory
            // 从容器中获取所有这种类型的组件：EmbeddedServletContainerCustomizer
            .getBeansOfType(EmbeddedServletContainerCustomizer.class,
                            false, false)
            .values());
        Collections.sort(this.customizers, AnnotationAwareOrderComparator.INSTANCE);
        this.customizers = Collections.unmodifiableList(this.customizers);
    }
    return this.customizers;
}

// ServerProperties也是定制器
```

**想要定制Servlet容器, 重新设置一些属性, 只需要给容器中可以添加一个EmbeddedServletContainerCustomizer类型的组件, 也就是我们之前在Config类中做的操作.**



#### 原理与步骤：

1）、SpringBoot根据导入的依赖情况，给容器中添加相应的EmbeddedServletContainerFactory【TomcatEmbeddedServletContainerFactory】

2）、容器中某个组件要创建对象就会惊动后置处理器；EmbeddedServletContainerCustomizerBeanPostProcessor；

只要是嵌入式的Servlet容器工厂，后置处理器就工作；

3）、后置处理器，从容器中获取所有的**EmbeddedServletContainerCustomizer**，调用定制器的定制方法



### 5）嵌入式Servlet容器启动原理；

什么时候创建嵌入式的Servlet容器工厂？

什么时候获取嵌入式的Servlet容器并启动Tomcat；

#### 获取嵌入式的Servlet容器工厂：

1）SpringBoot应用启动运行run方法, 创建IOC容器

2）refreshContext(context); SpringBoot刷新IOC容器【创建IOC容器对象，并初始化容器，创建容器中的每一个组件】；如果是web应用创建**AnnotationConfigEmbeddedWebApplicationContext**，否则：**AnnotationConfigApplicationContext** 

3）、refresh(context); **刷新刚才创建好的ioc容器；**

```java
public void refresh() throws BeansException, IllegalStateException {
   synchronized (this.startupShutdownMonitor) {
      // Prepare this context for refreshing.
      prepareRefresh();

      // Tell the subclass to refresh the internal bean factory.
      ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();

      // Prepare the bean factory for use in this context.
      prepareBeanFactory(beanFactory);

      try {
         // Allows post-processing of the bean factory in context subclasses.
         postProcessBeanFactory(beanFactory);

         // Invoke factory processors registered as beans in the context.
         invokeBeanFactoryPostProcessors(beanFactory);

         // Register bean processors that intercept bean creation.
         registerBeanPostProcessors(beanFactory);

         // Initialize message source for this context.
         initMessageSource();

         // Initialize event multicaster for this context.
         initApplicationEventMulticaster();

         // Initialize other special beans in specific context subclasses.
         onRefresh();

         // Check for listener beans and register them.
         registerListeners();

         // Instantiate all remaining (non-lazy-init) singletons.
         finishBeanFactoryInitialization(beanFactory);

         // Last step: publish corresponding event.
         finishRefresh();
      }

      catch (BeansException ex) {
         if (logger.isWarnEnabled()) {
            logger.warn("Exception encountered during context initialization - " +
                  "cancelling refresh attempt: " + ex);
         }

         // Destroy already created singletons to avoid dangling resources.
         destroyBeans();

         // Reset 'active' flag.
         cancelRefresh(ex);

         // Propagate exception to caller.
         throw ex;
      }

      finally {
         // Reset common introspection caches in Spring's core, since we
         // might not ever need metadata for singleton beans anymore...
         resetCommonCaches();
      }
   }
}
```

4）onRefresh(); web的ioc容器重写了onRefresh方法

5）webioc容器会创建嵌入式的Servlet容器；EmbeddedWebApplicationContext#**createEmbeddedServletContainer**();

**6）获取嵌入式的Servlet容器工厂：**

EmbeddedServletContainerFactory containerFactory = getEmbeddedServletContainerFactory();

从ioc容器中获取EmbeddedServletContainerFactory 组件；**TomcatEmbeddedServletContainerFactory**创建对象，后置处理器一看是这个对象，就获取所有的定制器来先定制Servlet容器的相关配置；

7）**使用容器工厂获取嵌入式的Servlet容器**：this.embeddedServletContainer = containerFactory      .getEmbeddedServletContainer(getSelfInitializer());

8）嵌入式的Servlet容器创建对象并启动Servlet容器；

**先启动嵌入式的Servlet容器，再将ioc容器中剩下没有创建出的对象获取出来；**



## 8、使用外置的Servlet容器

嵌入式Servlet容器：应用打成可执行的jar

优点：简单、便携；

缺点：默认不支持JSP、优化定制比较复杂

（使用定制器【ServerProperties、自定义EmbeddedServletContainerCustomizer】，自己编写嵌入式Servlet容器的创建工厂【EmbeddedServletContainerFactory】）；



**外置的Servlet容器：外面安装Tomcat—应用以war包的方式打包；**

### 步骤

1）、创建一个war项目；（利用idea创建好目录结构）

2）、将嵌入式的Tomcat指定为provided；

```xml
<dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-tomcat</artifactId>
   <scope>provided</scope>
</dependency>
```

3）、必须编写一个**SpringBootServletInitializer**的子类，并调用configure方法

```java
public class ServletInitializer extends SpringBootServletInitializer {
   @Override
   protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
       //传入SpringBoot应用的主程序
      return application.sources(SpringBoot04WebJspApplication.class);
   }
}
```

4）、启动服务器就可以使用；



### 原理

jar包：执行SpringBoot主类的main方法，启动ioc容器，创建嵌入式的Servlet容器；

war包：启动服务器，**服务器启动SpringBoot应用**【SpringBootServletInitializer】，启动ioc容器；



servlet3.0（Spring注解版）：

8.2.4 Shared libraries / runtimes pluggability：

规则：

​	1）服务器启动（web应用启动）会创建当前web应用里面每一个jar包里面ServletContainerInitializer实现类的实例：

​	2）ServletContainerInitializer的实现类的位置: 放在jar包的META-INF/services文件夹下，有一个名为javax.servlet.ServletContainerInitializer的文件，内容就是ServletContainerInitializer的实现类的全类名

​	3）还可以使用@HandlesTypes，在应用启动的时候加载我们感兴趣的类；



流程：

1）启动Tomcat

2）org\springframework\spring-web\4.3.14.RELEASE\spring-web-4.3.14.RELEASE.jar!\META-INF\services\javax.servlet.ServletContainerInitializer：

Spring的web模块里面有这个文件, 内容是：**org.springframework.web.SpringServletContainerInitializer**

3）SpringServletContainerInitializer将@HandlesTypes(WebApplicationInitializer.class)标注的所有WebApplicationInitializer.class类型的类都传入到onStartup方法的Set<Class<?>>参数中；为这些WebApplicationInitializer类型的类创建实例；

4）每一个WebApplicationInitializer的实现类都调用自己的onStartup；

![](images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180302221835.png)

**相当于SpringBootServletInitializer的子类会被创建对象，并执行onStartup方法, 这个子类没有onStartup方法, 所以会调用父类SpringBootServletInitializer的onStartup方法**

5）SpringBootServletInitializer实例执行onStartup的时候会createRootApplicationContext；创建容器

```java
protected WebApplicationContext createRootApplicationContext(
      ServletContext servletContext) {
    //1、创建SpringApplicationBuilder
    SpringApplicationBuilder builder = createSpringApplicationBuilder();
    StandardServletEnvironment environment = new StandardServletEnvironment();
    environment.initPropertySources(servletContext, null);
    builder.environment(environment);
    builder.main(getClass());
    ApplicationContext parent = getExistingRootWebApplicationContext(servletContext);
    if (parent != null) {
        this.logger.info("Root context already created (using as parent).");
        servletContext.setAttribute(
            WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE, null);
        builder.initializers(new ParentContextApplicationContextInitializer(parent));
    }
    builder.initializers(
        new ServletContextApplicationContextInitializer(servletContext));
    builder.contextClass(AnnotationConfigEmbeddedWebApplicationContext.class);

    //2. 调用configure方法，子类重写了这个方法，将SpringBoot的主程序类传入了进来
    builder = configure(builder);

    //3. 使用builder创建一个Spring应用
    SpringApplication application = builder.build();
    if (application.getSources().isEmpty() && AnnotationUtils
        .findAnnotation(getClass(), Configuration.class) != null) {
        application.getSources().add(getClass());
    }
    Assert.state(!application.getSources().isEmpty(),
                 "No SpringApplication sources have been defined. Either override the "
                 + "configure method or add an @Configuration annotation");
    // Ensure error pages are registered
    if (this.registerErrorPageFilter) {
        application.getSources().add(ErrorPageFilterConfiguration.class);
    }
    //启动SpringBoot应用
    return run(application);
}
```

7）、Spring的应用就启动并且创建IOC容器

```java
public ConfigurableApplicationContext run(String... args) {
    StopWatch stopWatch = new StopWatch();
    stopWatch.start();
    ConfigurableApplicationContext context = null;
    FailureAnalyzers analyzers = null;
    configureHeadlessProperty();
    SpringApplicationRunListeners listeners = getRunListeners(args);
    listeners.starting();
    try {
        ApplicationArguments applicationArguments = new DefaultApplicationArguments(
            args);
        ConfigurableEnvironment environment = prepareEnvironment(listeners,
                                                                 applicationArguments);
        Banner printedBanner = printBanner(environment);
        context = createApplicationContext();
        analyzers = new FailureAnalyzers(context);
        prepareContext(context, environment, listeners, applicationArguments,
                       printedBanner);

        //刷新IOC容器
        refreshContext(context);
        afterRefresh(context, applicationArguments);
        listeners.finished(context, null);
        stopWatch.stop();
        if (this.logStartupInfo) {
            new StartupInfoLogger(this.mainApplicationClass)
                .logStarted(getApplicationLog(), stopWatch);
        }
        return context;
    }
    catch (Throwable ex) {
        handleRunFailure(context, listeners, analyzers, ex);
        throw new IllegalStateException(ex);
    }
}
```

**==启动Servlet容器，再启动SpringBoot应用==**

