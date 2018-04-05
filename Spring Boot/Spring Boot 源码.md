## Spring Boot

### Spring Boot Starter 

是 Spring Boot 启动器, 包含以下两种模块

- 自动装配模块 (Autoconfigure Module)

  > 包含类库中(class文件)的每种必要(条件化配置)启动单元. 
  >
  > - 配置键的定义: @ConfigurationProperties
  > - 自定义已初始化组件的回调接口: EmbeddedServletContainerCustomizer

  - 自动装配的类型

    > 自动装配Bean : 是由标准Spring3.0 的@Configuration实现. 结合Spring4.0中的@Conditional以及Spring Boot的派生注解, @ConditionalOnClass
    >
    > - Spring配置(@Configuration)
    > - Spring Boot管理上下文配置(@ManagementContextConfiguration)
    >
    > Spring Boot 组件
    >
    > - FailureAnalysisReporter
    > - SpringApplicationRunListener
    > - AutoConfigurationImportListener

- 启动器模块 (Starter Module)

> META-INF/spring.factories >> SpringFactoriesLoader
>
> META-INF/services >> ServiceLoader



### EmbeddedServletContainer

SpringBoot的Web容器是通过`META-INF/spring.factories`注入了`EmbeddedServletContainerAutoConfiguration` 来自动装配的。

以tomcat为例，这里判断如果存在Tomcat等类，就会注入TomcatEmbeddedServletContainerFactory

#### EmbeddedServletContainerAutoConfiguration

```java
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@Configuration
@ConditionalOnWebApplication
@Import(EmbeddedServletContainerCustomizerBeanPostProcessorRegistrar.class)
public class EmbeddedServletContainerAutoConfiguration {
    @Configuration
    @ConditionalOnClass({ Servlet.class, Tomcat.class })
    @ConditionalOnMissingBean(value = EmbeddedServletContainerFactory.class, search = SearchStrategy.CURRENT)
    public static class EmbeddedTomcat {
        @Bean
        public TomcatEmbeddedServletContainerFactory tomcatEmbeddedServletContainerFactory() {
            return new TomcatEmbeddedServletContainerFactory();
        }
    }
}
```

TomcatEmbeddedServletContainerFactory 类实现了 EmbeddedServletContainerFactory 接口

#### EmbeddedServletContainerFactory

```java
public interface EmbeddedServletContainerFactory {
    EmbeddedServletContainer getEmbeddedServletContainer(ServletContextInitializer... initializers);
}
```

初始化Tomcat并根据ServletContextInitializer对servletContext进行初始化。

```java
// EmbeddedServletContainer 是具体的Web容器，提供http的服务
public EmbeddedServletContainer getEmbeddedServletContainer(ServletContextInitializer... initializers) {
    Tomcat tomcat = new Tomcat();
    File baseDir = (this.baseDirectory != null ? this.baseDirectory
            : createTempDir("tomcat"));
    tomcat.setBaseDir(baseDir.getAbsolutePath());
    Connector connector = new Connector(this.protocol);
    tomcat.getService().addConnector(connector);
    customizeConnector(connector);
    tomcat.setConnector(connector);
    tomcat.getHost().setAutoDeploy(false);
    tomcat.getEngine().setBackgroundProcessorDelay(-1);
    for (Connector additionalConnector : this.additionalTomcatConnectors) {
        tomcat.getService().addConnector(additionalConnector);
    }
    prepareContext(tomcat.getHost(), initializers);
    return getTomcatEmbeddedServletContainer(tomcat);
}

protected TomcatEmbeddedServletContainer getTomcatEmbeddedServletContainer(Tomcat tomcat) {
    return new TomcatEmbeddedServletContainer(tomcat, this.getPort() >= 0);
}
```

#### ServletContextInitializer

```java
interface ServletContextInitializer {
    // Configure the given ServletContext with any servlets, filters, listeners context-params and attributes necessary for initialization.
    void onStartup(ServletContext servletContext) throws ServletException;
}
```

#### 实例

通过在application.properties设置对应的key-value对，可以配置Spring Boot应用程序的很多特性，例如POST、SSL、MySQL等等。如果需要更加复杂的调优，则可以利用Spring Boot提供的EmbeddedServletContainerCustomizer接口通过编程方式和修改配置信息。

尽管可以通过application.properties设置server.session-timeout属性来配置服务器的会话超时时间，这里我们用EmbeddedServletContainerCustomizer接口修改，来说明该接口的用法。

```java
@Bean
public static EmbeddedServletContainerCustomizer embeddedServletContainerCustomizer() {
    return new EmbeddedServletContainerCustomizer() {
        @Override
        public void customize(ConfigurableEmbeddedServletContainer container) {
            container.setSessionTimeout(1, TimeUnit.MINUTES);
            if (container instanceof TomcatEmbeddedServletContainerFactory) {
                TomcatEmbeddedServletContainerFactory factory = TomcatEmbeddedServletContainerFactory.class.cast(container);

                factory.addContextCustomizers(new TomcatContextCustomizer() {
                    @Override
                    public void customize(Context context) {
                        context.setPath("/spring-boot");
                    }
                });

                factory.addConnectorCustomizers(new TomcatConnectorCustomizer() {
                    @Override
                    public void customize(Connector connector) {
                        connector.setPort(8888);
                        connector.setProtocol(Http11Nio2Protocol.class.getName());
                    }
                });
            }
        }
    };
}
```



### EnableAutoConfiguration

#### @Import

@Import用来导入一个或多个类（会被spring容器管理），或者配置类（配置类里的@Bean标记的类也会被spring容器管理）

我们要将这四个类纳入到spring容器中，我们之前的做法是在User，People上加上了@Component注解(或者@Service，@Controller）或者在MyConfig类上加上@Configuration注解。很显然我们这边并没有这般做，使用@Import注解也可以加对象纳入到spring容器中。

```java
@Import({User.class,People.class, MyConfig.class})
public class Application {
    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(Application.class,args);
        System.out.println(context.getBean(User.class));
        System.out.println(context.getBean(Dog.class));
        System.out.println(context.getBean(Cat.class));
        System.out.println(context.getBean(People.class));
    }
}
```

#### ImportSelector接口

- 进入`EnableAutoConfiguration`注解源码，发现是导入`EnableAutoConfigurationImportSelector`类，它继承了`ImportSelector`接口, `ImportSelector`接口的`selectImports`方法返回的String[]数组（类的全类名）, 这些类都会被纳入到spring容器中.


- `EnableAutoConfigurationImportSelector` 类继承了 `AutoConfigurationImportSelector` 类



- 进入org.springframework.boot.autoconfigure.AutoConfigurationImportSelector类，进入`getCandidateConfigurations`方法. `getCandidateConfigurations`会到classpath下的读取META-INF/spring.factories文件的配置，并返回一个字符串数组。

  ```java
  protected List<String> getCandidateConfigurations(AnnotationMetadata metadata, AnnotationAttributes attributes) {

      List<String> configurations = SpringFactoriesLoader.loadFactoryNames(this.getSpringFactoriesLoaderFactoryClass(), this.getBeanClassLoader());

      Assert.notEmpty(configurations, "No auto configuration classes found in META-INF/spring.factories. If you are using a custom packaging, make sure that file is correct.");

      return configurations;

  }
  ```


- 调试的时候读取到了我们在spring.factories中配置的core.bean.MyConfig，也读到了一些其他的配置

> springboot项目B依赖了A项目中的一个类, 并且把A中的配置类的全类名放在B中的classpath下的META-INF/spring.factories中

#### @EnableAutoConfiguration 作用:

1. 从classpath中搜索所有META-INF/spring.factories配置文件然后，将其中org.springframework.boot.autoconfigure.EnableAutoConfiguration key对应的配置项加载到spring容器

> 只有spring.boot.enableautoconfiguration为true（默认为true）的时候，才启用自动配置

2. @EnableAutoConfiguration还可以进行排除，排除方式有2中，一是根据class来排除（注解上的属性exclude），二是根据class name（excludeName）来排除
3. @EnableConfigurationProperties注解一般和ConfigurationProperties注解搭配使用，可以将配置文件属性注入到bean中。

#### @Condition注解: spring4提供的

- @ConditionalOnBean（仅仅在当前上下文中存在某个对象时，才会实例化一个Bean）
- @ConditionalOnClass（某个class位于类路径上，才会实例化一个Bean）
- @ConditionalOnExpression（当表达式为true的时候，才会实例化一个Bean）
- @ConditionalOnMissingBean（仅仅在当前上下文中不存在某个对象时，才会实例化一个Bean）
- @ConditionalOnMissingClass（某个class类路径上不存在的时候，才会实例化一个Bean）
- @ConditionalOnNotWebApplication（不是web应用）

```java
@ConditionalOnClass：该注解的参数对应的类必须存在，否则不创建该注解修饰的配置类；
@ConditionalOnMissingBean：可以给该注解传入参数例如@ConditionOnMissingBean(name = "example")，这个表示如果name为“example”的bean存在，该注解修饰的代码块不执行。
```
#### 自动加载的源码分析

1. RedisProperties -> RedisConnectionConfiguration -> RedisAutoConfiguration


2. SpringApplication对象被实例化 -> 加载spring.factories文件

- 比如在主配置文件application.yml中配置了redis的配置项
- spring.redis.port = 6379
- 则首先会有RedisProperties类从配置文件中读取到这些属性，然后封装成RedisProperties类
- 接着，这个类会变成RedisConnectionConfiguration类的一个属性，而这个RedisConnectionConfiguration类又会成为RedisAutoConfiguration类的一个属性。
- 这样，就会自动配置redis了。
- springboot启动的时候，会实例化SpringApplication对象，在这个过程中，会加载META-INF/spring.factories文件，在这个文件中定

3. 其内部实现的关键点有

* ImportSelector 该接口的方法的返回值都会被纳入到spring容器管理中定义了类似于RedisAutoConfiguration等一系列的类，这些类都会被加载到spring容器中
* SpringFactoriesLoader 该类可以从classpath中搜索所有META-INF/spring.factories配置文件，并读取配置

4. `META-INF/spring.factories`
   在spring3.2中, 放在`SpringFactoriesLoader`类中定义的常量属性 `FACTORIES_RESOURCE_LOCATION`

   类似于java中的ServiceLoader(META-INT/service.factories)



### SpringBoot的启动过程

1. SpringBoot的启动过程中，需要调用`SpringApplication`类的静态方法run(). 这个run方法的返回值，是`ApplicationContext`接口的实现类`ConfigurableApplicationContext`。

    > SpringBoot的启动过程，实际上就是对ApplicationContext的初始化过程

2. 所以，我们需要首先创建SpringApplication对象。也就是调用其构造方法，在构造方法中传入一些初始化参数。这个初始化参数一般是项目的配置类. 比如是否开启日志等。然后调用其构造函数中的initialize方法。在initialize方法中，有四点需要注意。

    ```java
    private void initialize(Object[] sources) {
       	if (sources != null && sources.length > 0) {
       		this.sources.addAll(Arrays.asList(sources));
       	}
        
        //4.
       	this.webEnvironment = deduceWebEnvironment();
        
        //1.
        this.setInitializers(
    		this.getSpringFactoriesInstances(ApplicationContextInitializer.class));

        //2.
       	this.setListeners(this.getSpringFactoriesInstances(ApplicationListener.class));
        
        //3.
       	this.mainApplicationClass = this.deduceMainApplicationClass();
       }
    ```

    #### 2.1 找到声明的所有ApplicationContextInitializer的实现类并将其实例化。

    ApplicationContextInitializer是Spring框架中的接口，其作用可以理解为在ApplicationContext执行refresh之前，调用ApplicationContextInitializer的initialize()方法，对ApplicationContext做进一步的设置和处理。

    ```java
    public interface ApplicationContextInitializer<C extends ConfigurableApplicationContext> {
    	/**
    	 * Initialize the given application context.
    	 * @param applicationContext the application to configure
    	 */
    	void initialize(C applicationContext);
    }
    ```

    #### 2.2 找到声明的所有ApplicationListener的实现类并将其实例化。

    ApplicationListener 是Spring框架中的接口，就是事件监听器，其作用可以理解为在SpringApplicationRunListener发布通知事件时，由ApplicationListener负责接收。

    ```java
    public interface ApplicationListener<E extends ApplicationEvent> extends EventListener {
    	/**
    	 * Handle an application event.
    	 * @param event the event to respond to
    	 */
    	void onApplicationEvent(E event);
    }
    ```

    #### 2.3 获得当前执行main方法的类对象，这里就是SpringBootWebDemoApplication的实例。

    #### 2.4 判断当前是否是web环境。

3. 当创建好SpringApplication对象后，就要调用其run方法，来产生ApplicationContext接口的实现类了

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
		//1. 设置环境
		ConfigurableEnvironment environment = prepareEnvironment(listeners,
				applicationArguments);
		Banner printedBanner = printBanner(environment);
		//2. 创建上下文
		context = createApplicationContext();
		analyzers = new FailureAnalyzers(context);
		prepareContext(context, environment, listeners, applicationArguments,
				printedBanner);
		refreshContext(context);
		afterRefresh(context, applicationArguments);
		listeners.finished(context, null);
		stopWatch.stop();
		if (this.logStartupInfo) {
			new StartupInfoLogger(this.mainApplicationClass)
					.logStarted(getApplicationLog(), stopWatch);
		}
		return context;
	} catch (Throwable ex) {
		handleRunFailure(context, listeners, analyzers, ex);
		throw new IllegalStateException(ex);
	}
}
```

3.1 ApplicationContext创建后立刻为其设置Environment，并由ApplicationContextInitializer对其进一步封装。

3.2 通过SpringApplicationRunListener在ApplicationContext初始化过程中各个时点发布各种广播事件，并由ApplicationListener负责接收广播事件。

3.3 初始化过程中完成IoC的注入，包括通过@EnableAutoConfiguration导入的各种自动配置类。



### @SpringBootApplication

1. @SpringBootConfiguration实际上就是@Configuration，说明这是一个JavaConfig
2. @ComponentScan，启用注解自动扫描
3. @EnableAutoConfiguration: 自动配置. 其作用是根据类路径中jar包是否存在来决定是否开启某一个功能的自动配置，比如，我们项目中添加了spring-boot-starter-web依赖，因其关联Tomcat和Srping MVC，所以类路径下就会存在Tomcat和Spring MVC的jar包，SpringBoot项目扫描到这些jar包后会自动开启两者的配置，当然，这个配置是默认配置，我们可以根据需要进行修改
4. exclude和excludeName用于关闭指定的自动配置，比如关闭数据源相关的自动配置
    @SpringBootApplication(exclude={DataSourceAutoConfiguration.class})
5. spring-boot-autoconfigure-1.4.2.RELEASE.jar中就有一个spring.factories，可以看到org.springframework.boot.autoconfigure.EnableAutoConfiguration参数中列出了自动配置类列表



### SpringBootServletInitializer（用在打成war包，发布到tomcat中）

#### 打包springboot项目 

1. 添加provided依赖, 只在编译时使用tomcat的依赖, 因为打包成war包, 发布到服务器上, 服务器有tomcat
  所以, 要用provided

  ```xml
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-tomcat</artifactId>
      <scope>provided</scope>
  </dependency>
  ```

2. 添加maven-war-plugin插件

   ```xml
   <plugin>
       <groupId>org.apache.maven.plugins</groupId>
       <artifactId>maven-war-plugin</artifactId>
       <configuration>
           <failOnMissingWebXml>false</failOnMissingWebXml>
       </configuration>
   </plugin>
   ```

3. 修改打包方式为war

   ```xml
   <packaging>war</packaging>
   ```

4. 将项目的启动类Application.java继承SpringBootServletInitializer并重写configure方法

  ```java
  @SpringBootApplication
  public class Application extends SpringBootServletInitializer {
  	
      @Override
  	protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
  		return application.sources(Application.class);
  	}

      public static void main(String[] args) throws Exception {
  		SpringApplication.run(Application.class, args);
  	}
  }
  ```

5. 如果是多模块应用，提示找不到主类，需要把build节点的信息放在web模块（核心模块）中，同时添加主类信息

   ```xml
   <build>
   	<plugins>
           <plugin>
               <grounpId>org.spring.framework.boot</grounpId>
               <artifactId>spring-boot-maven-plugin</artifactId>
               <configuration>
                   <mainClass>com.imooc.firstappdemo.FirstAppDemoApplication</mainClass>
               </configuration>
           </plugin>
       </plugins>
   </build>
   ```

6. 多模块应用，主模块可以删掉src文件夹，要注意不同模块之间的依赖关系

7. 如果打包方式是war，则需要添加webapp/WEB-INF/web.xml

#### 源码分析

1. SpringServletContainerInitializer implements ServletContainerInitializer 接口, 该接口在启动容器时负责加载相关配置

  ```java
  public interface ServletContainerInitializer {
  	public abstract void onStartup(Set<Class<?>> paramSet, ServletContext paramServletContext) throws ServletException;
  }
  ```

2. 在SpringServletContainerInitializer类上有注解@HandlesTypes(WebApplicationInitializer.class)

3. 因为这个类声明了HandlesTypes，并指定了类型为WebApplicationInitializer.class，在Servlet3.0+的web容器启动时，会扫描类路径下所有的WebApplicationInitializer接口实现类，并把它们放到一个set集合, 提供给给onStartup方法执行。

4. `abstract class SpringBootServletInitializer implements WebApplicationInitializer {}` 也就是说, SpringBootServletInitializer是WebApplicationInitializer的实现类, 所以会放入set集合中, 而DemoApplication也是WebApplicationInitializer的实现类, 也会放入set集合中.


4. onStartup方法执行时，会遍历该set，并使用newInstance()方式进行实例化，实例化后依据@Order注解进行排序，最后在依次调用onStartup(ServletContext)方法

   ```java
   for (WebApplicationInitializer initializer : initializers) {
       initializer.onStartup(servletContext);
   }
   ```

   在initializer.onStartup(servletContext);方法中, 会调用createRootApplicationContext方法，通过SpringApplicationBuilder构建并封装SpringApplication对象，并最终调用SpringApplication的run方法的过程, 完成初始化。

   ```java
   protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
       builder.sources(DemoApplication.class);
       return builder;
   }
   ```

5. 所以，打成war包的时候，需要启动类继承自SpringBootServletInitializer，方可正常部署至常规tomcat下，其主要能够起到web.xml的作用，注入一些filter，listener的配置。

> 在web容器启动时为提供给第三方组件机会做一些初始化的工作，例如注册servlet或者filtes等
>
> 容器根据Servlet规范, 提供了javax.servlet.ServletContainerInitializer。
>
> 第三方的应用需要基于SPI机制，来实现javax.servlet.ServletContainerInitializer 接口。
>
> 也就是需要在对应的jar包的META-INF/services 目录创建一个名为javax.servlet.ServletContainerInitializer的文件，文件内容指定具体的ServletContainerInitializer实现类，那么，当web容器启动时就会运行这个初始化类做一些组件内的初始化工作。 



### Environment接口

* StandardEnvironment

- StandardServletEnvironment  

```java
// 在测试时, 实例化MockEnvironment对象, 获得系统属性
assertNotNull(System.getProperty("os.arch"));
MockEnvironment environment = new MockEnvironment();
environment.setProperty("user.country", "EN");
assertEquals("EN", environment.getProperty("user.country"));
```

> idea提供了测试过程中的coverage信息, 可以重点关注行覆盖度. 因为行覆盖度比方法覆盖度更精准. 比如在一个方法中有条件判断, 5个分支. 即使这个方法被覆盖了, 也只能测出20%的覆盖面. 但是行覆盖度就更全面.



### SpringBoot 加载静态文件

#### 默认加载文件的路径

```properties
/META-INF/resources/
/resources/
/static/
/public/
```

#### 加载resources下面的自定义配置文件

##### 方式一

```java
@Configuration
@PropertySource("classpath:test.properties")
public class ELConfig {
    
    @Value("${book.name}")
    private String bookName;

    //注意！配置一个PropertySourcesPlaceholderConfigurer的Bean
    @Bean
    public static PropertySourcesPlaceholderConfigurer propertyConfigure() {
        return new PropertySourcesPlaceholderConfigurer();
    }

    public void outputSource() {
        System.out.println(bookName);
    }
}
```

##### 方式二

```java
@Component
//使用locations指定读取的properties文件路径，如果不指定locations就会读取默认的properties配置文件
@ConfigurationProperties(prefix = "author")
public class AuthorSettings {
    private String name;
    private Long age;
}
```

#### 继承springmvc提供的WebMvcConfigurerAdapter, 配置静态资源的访问路径  

```java
@EnableWebMvc  
@Configuration  
public class WebConfig extends WebMvcConfigurerAdapter {  

    @Override  
    public void addResourceHandlers(ResourceHandlerRegistry registry) {  
        registry.addResourceHandler("/templates/**").addResourceLocations(ResourceUtils.CLASSPATH_URL_PREFIX + "/templates/");  
        registry.addResourceHandler("/static/**").addResourceLocations(ResourceUtils.CLASSPATH_URL_PREFIX + "/static/");  
        super.addResourceHandlers(registry);  
    }  
}  

// http://localhost:8003/templates/home.html
// <image src="/static/image/267862-1212151Z12099.jpg" width="100px" height="50px" />  

// 在springboot的classpath下(也就是和java对应的resources文件夹), 也有访问的优先级:
// /META-INF/resources >> /resources >> /static >> /public
```



### springboot的配置

1. springboot默认的全局配置文件在application.properties或application.yml（推荐使用）。此文件默认可以放在classpath路径，或者放在classpath:/config，springboot应用都是默认读取到的。

```java
// local.ip=192.168.1.111

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(Application.class, args);
        System.out.println(context.getEnvironment().getProperty("local.ip"));
        context.close();
    }
}
```

2. 使用 Environment 类或者 @Value 注解获取配置

```java
@Component
public class UserConfig {
    @Autowired
    private Environment environment;

    @Value("${local.name}")
    private String localName;

    //默认值
    @Value("${tomcat.port:10000}")
    private int port;

    public void show(){
        System.out.println(environment.getProperty("local.ip"));
        //重载方法，使得读取到的数据是Integer类型的
        System.out.println(environment.getProperty("local.port", Integer.class));
        System.out.println(localName);

        //在配置文件中引用引用已有的变量
        //local.url=http://${local.ip}:${local.port}
        System.out.println(environment.getProperty("local.url"));
    }
}
```

3. 设置默认值

```java
@SpringBootApplication
public class Application {

    @Value("${server.host:localhost}")
    private String serverHost;

    public static void main(String[] args) {
        SpringApplication application = new SpringApplication(Application.class);
        
        Map<String,Object> defaultProperties = new HashMap<>();
        defaultProperties.put("server.host","192.168.1.111");
        defaultProperties.put("server.ip","8080");
        application.setDefaultProperties(defaultProperties);
        
        Properties defaultProperties2 = new Properties();
        defaultProperties2.put("server.ip","8080");
        application.setDefaultProperties(defaultProperties2);
        
        ConfigurableApplicationContext context = application.run(args);
        System.out.println(context.getBean(Application.class).serverHost);
        System.out.println(context.getEnvironment().getProperty("server.host"));
        System.out.println(context.getEnvironment().getProperty("server.ip"));
        context.close();
    }
}
```

4. 使用@ConfigurationProperties注解加载配置文件

注意：使用 @ConfigurationProperties，那么配置的属性必须要加get, set方法。

5. 加载外部文件的方式

```java
@Configuration
@PropertySource({"classpath:jdbc.properties", "classpath:user.properties"})
@PropertySources({@PropertySource("classpath:jdbc.properties"),@PropertySource("classpath:user.properties")})
public class FileConfig {
}
```

@PropertySources注解容器式注解，将@PropertySource注解复合在一起使用。

然后再写一个FileConfig.java的配置类, 读取jdbc.properties中的属性