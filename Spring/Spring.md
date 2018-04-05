## Spring

Spring通过一个配置文件描述Bean及Bean直接的依赖关系，利用Java语言的反射功能实例化Bean并建立Bean之间的依赖关系。

Sprig的IoC容器在完成这些底层工作的基础上，还提供了Bean实例缓存、生命周期管理、Bean实例代理、事件发布、资源装载等高级服务。

### AOP

#### 概念

1. AOP指面向切面编程。通过预编译方式，或者主要是运行期间的动态代理技术来实现功能。它可以使业务逻辑各部分之间的耦合度降低，提高程序的可重用性
2. 采取横向抽取机制，取代了传统纵向继承体系重复性代码
  **具体指**，比如原来要为Service中的add和delete两个方法添加事务的操作，而且不能修改原先的代码。那么我们只能另外写一个类A来继承Service类，然后分别在add和delete方法的前后，加事务开启和事务提交。  
  但是，如果使用AOP，我们就可以直接写一个A类，里面是开启和提交事务的方法，然后把A类和Service全部交给Spring，让它为我们产生代理对象。  
3. 经典应用：事务管理、性能监视、安全检查、缓存 、日志等。  

>  第一种情况，有接口情况，使用动态代理创建接口实现类代理对象  
>
> 第二种情况，没有接口情况，使用cglib代理创建类的子类代理对象

#### 术语

Joinpoint(连接点): 指类里面可以被增强的方法

Pointcut(切入点)：指我们要进行拦截增强的那些连接点。

Advice(通知/增强)：指对切入点所做的事情。通知分为前置通知,后置通知,异常通知,最终通知,环绕通知(切面要完成的功能)  

Aspect(切面): 是切入点和通知的结合。 

Weaving(织入)：把增强advice应用到目标对象target来创建新的代理对象proxy的过程。

目标类：需要被代理的类。  

代理类：Proxy  

#### 底层原理(BeanPostProcessor)

spring 提供一种机制，只要我们写的类实现`BeanPostProcessor`接口，并将实现类提供给spring容器，spring容器将自动在容器初始化方法(init)前执行before()，在初始化方法后执行after() 

目的是修改容器中所有的bean对象，创建代理对象，是AOP的底层原理。

这里创建的代理对象，可以在before方法中返回代理对象，也可以在after方法中返回代理对象。  

#### 示例

```java
public class MyBeanPostProcessor implements BeanPostProcessor {
    
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
    	System.out.println("前方法 ： " + beanName);
        // 没有生成代理对象
    	return bean;
    }
    
    @Override
    public Object postProcessAfterInitialization(final Object bean, String beanName) throws BeansException {
    	System.out.println("后方法 ： " + beanName);
    	// bean 目标对象
    	// 生成 jdk 代理
    	return Proxy.newProxyInstance(
            // 本类的类加载器
            MyBeanPostProcessor.class.getClassLoader(), 
            // 动态代理需要接口
            bean.getClass().getInterfaces(), 
            new InvocationHandler(){
            	@Override
            	public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                    System.out.println("开启事务");
            		
                    //执行目标方法
                    Object obj = method.invoke(bean, args);
                    
                    System.out.println("提交事务");
                    return obj;
            	}
            }
        );
    }
}
```



### ApplicationContext

#### 获取Spring的上下文ApplicationContext的方法

##### 1. 手动创建ApplicationContext对象，并保存起来

```java
public class ApplicationContextUtil {  
    private static ApplicationContext context;  
    static {  
        context = new ClassPathXmlApplicationContext("applicationContext.xml");  
    }  
  
    public static ApplicationContext getApplicationContext() {  
        return context;  
    }  
}  
```

##### 2.通过spring提供的工具类WebApplicationContextUtils获取

* 在web环境中通过spring提供的工具类获取，需要ServletContext对象作为参数。然后才通过ApplicationContext对象获取bean.
* 下面两个工具方式的区别是，前者在获取失败时返回null，后者抛出异常。另外，由于spring是容器的对象, 放在ServletContext中的，所以可以直接在ServletContext取出 WebApplicationContext 对象

```java
// 获取失败时 返回null
ApplicationContext context1 = WebApplicationContextUtils.getWebApplicationContext(ServletContext sc);  

// 获取失败时 抛出异常
ApplicationContext context2 = WebApplicationContextUtils.getRequiredWebApplicationContext(ServletContext sc);  

// 从ServletContext中获取
WebApplicationContext webApplicationContext = (WebApplicationContext) servletContext.getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE);  
```

##### 3. 继承ApplicationObjectSupport

* 工具类继承抽象类 ApplicationObjectSupport，并在工具类上使用@Component交由spring管理。

- 这样spring容器在启动的时候，会通过父类ApplicationObjectSupport中的setApplicationContext()方法将ApplicationContext对象设置进去。可以通过getApplicationContext()得到ApplicationContext对象。

##### 4. 继承WebApplicationObjectSupport

- 工具类继承抽象类WebApplicationObjectSupport
- 查看源码可知WebApplicationObjectSupport是继承了ApplicationObjectSupport，所以获取ApplicationContext对象的方式和上面一样，也是使用getApplicationContext()方法。

##### 5. ApplicationContextAware接口

- 工具类实现ApplicationContextAware接口，并重写setApplicationContext(ApplicationContext applicationContext)方法，在工具类中使用@Component注解让spring进行管理。
- spring容器在启动的时候，会调用setApplicationContext()方法将ApplicationContext 对象设置进去。

```java
@Component  
public class ApplicationContextUtil implements ApplicationContextAware {  
    private static ApplicationContext context;  
  
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {  
        context = applicationContext;  
    }  
      
    public static ApplicationContext getApplicationContext() {  
        return context;  
    }  
}
```

#### 注意事项

1. 使用XML作为配置的时候，实例化接口 `ApplicationContext` 的是 `ClassPathXmlApplicationContext`
2. 通过 `@Configuration` 注解的类，实例化接口 `ApplicationContext` 的是 `AnnotationConfigApplicationContext`

```java
ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
```

3.  `AnnotationConfigApplicationContext` 不仅仅可以和注解了 `@Configuration` 的类配合，任何注解了 `@Component` 的类同样可以作为输入参数来构造Spring容器(ApplicationContext)

```java
ApplicationContext ctx = new AnnotationConfigApplicationContext(MyServiceImpl.class, Dependency1.class, Dependency2.class);
```

4. `AnnotationConfigApplicationContext` 类除了通过类来初始化，也可以通过无惨构造函数来进行构造，之后通过 `register()` 方法来配置。这种方法在通过编程的方式来构建 `AnnotationConfigApplicationContext` 的过程很有用。

```java
public static void main(String[] args) {
    AnnotationConfigApplicationContext ctx = new AnnotationConfigApplicationContext();
    ctx.register(AppConfig.class, OtherConfig.class);
    ctx.register(AdditionalConfig.class);
    ctx.scan("me.hds");
    ctx.refresh();
    MyService myService = ctx.getBean(MyService.class);
    myService.doStuff();
}
```

5. `ConfigurableApplicationContext` 接口和 `WebApplicationContext` 接口 都继承了 `ApplicationContext` 接口.

   `ConfigurableWebApplicationContext` 接口结合了上述两者的优点, 继承了上述两个接口, 允许通过配置的方式实例化 `WebApplicationContext`. 凡是以 `Configurable` 开头的, 都是可配置的, 就会有addxxx的方法

   `AnnotationConfigApplicationContext` 类就实现了这个根接口 `ConfigurableApplicationContext`



### ApplicationContextAware

Spring中提供一些Aware相关接口，BeanFactoryAware、ApplicationContextAware、ResourceLoaderAware、ServletContextAware等等，实现这些Aware接口的Bean在被初始之后，可以取得一些相对应的资源.

例如实现BeanFactoryAware的Bean在初始后，Spring容器将会注入BeanFactory的实例; 

实现ApplicationContextAware的Bean，在Bean被初始后，将会被注入ApplicationContext的实例.

这样, 注入了ApplicationContext的spring上下文的Bean, 就可以利用spring上下文, 获得容器中的资源, 或者调用容器的方法. 

#### 源码

```java
public interface ApplicationContextAware extends Aware {
    void setApplicationContext(ApplicationContext applicationContext) throws BeansException;
}
```
#### 使用

```java
public class SpringContextUtils implements ApplicationContextAware {
    private static ApplicationContext context;
    @Override
    public void setApplicationContext(ApplicationContext context)
            throws BeansException {
        SpringContextUtils.context = context;
    }
    public static ApplicationContext getContext(){
        return context;
    }
}

// 获取其他的Bean
SpringContextUtils.getContext().getBean("userDao");
```

#### 示例

```java
@Component
public class HelloBean implements ApplicationContextAware {
    private ApplicationContext applicationContext;
    private String helloWord = "Hello!World!";
    
    //通过实现这个方法, spring会默认把ApplicationContext上下文注入到HelloBean中, 通过getContext就可以获得这个上下文
    @Override
    public void setApplicationContext(ApplicationContext context) {
        this.applicationContext = context;
    }
 
    public void setHelloWord(String helloWord) {
        this.helloWord = helloWord;
    }
 
    public String getHelloWord() {
        applicationContext.publishEvent(new PropertyGettedEvent("[" + helloWord + "] is getted"));
        return helloWord;
    }
    
    public static ApplicationContext getContext(){
        return context;
    }
}

// ApplicationEvent Spring事件
public class PropertyGettedEvent extends ApplicationEvent {
    public PropertyGettedEvent(Object source) {
        super(source);
    }
}

// ApplicationListener Spring监听器
@Component
public class PropertyGettedListener implements ApplicationListener {
    public void onApplicationEvent(ApplicationEvent event) {
        System.out.println(event.getSource().toString());  
    }
}

// 测试类
public class Test {
    public static void main(String[] args) {
        ApplicationContext context = new ClassPathXmlApplicationContext("bean.xml");
        //这里获得的Bean就有ApplicationContext对象, 可以调用其publishEvent方法
        HelloBean hello = (HelloBean) context.getBean("helloBean");
        System.out.println(hello.getHelloWord());
    }
}
```



### BeanDefinition

#### 综述

Bean对象在Spring实现中是以BeanDefinition来描述的

Spring IoC容器对Bean定义资源的载入是从`refresh()`函数开始的，`refresh()`是一个模板方法

refresh()方法的作用是：

>  在创建IoC容器前，如果已经有容器存在，则需要把已有的容器销毁和关闭，以保证在refresh之后使用的是新建立起来的IoC容器。
>
> refresh的作用类似于对IoC容器的重启，在新建立好的容器中对容器进行初始化，对Bean定义资源进行载入

#### IoC容器的加载

IoC容器的初始化包括三个过程，`BeanDefinition`的资源`Resource`的定位、载入和注册。

- 1. Resource的定位。指BeanDefinition的资源定位，通过ResourceLoader接口中的getResource方法完成。（对各种形式的BeanDefinition提供统一的接口）

- 2. BeanDefinition的载入。这个载入过程是把用户定义好的Bean表示成IOC容器内部的数据结构，而这个容器内部的数据结构就是BeanDefinition。BeanDefinition实际上就是POJO对象在IOC容器中的抽象，通过这个BeanDefinition定义的数据结构，使IOC容器能够方便地对POJO对象也就是Bean进行管理。

- 3. 向IOC容器注册BeanDefinition。通过调用BeanDefinitionRegistry接口的实现来完成。通过分析，在IOC容器内部将BeanDefinition注入到一个HashMap中去，IOC容器就是通过这个HashMap来持有这些BeanDefinition数据的

- 注意，在IOC设计中，Bean定义的载入和依赖注入是两个独立的过程。依赖注入一般发生在应用第一次通过getBean向容器索取Bean的时候。但可以通过设置<bean lazyinit="true" />来配置。



### BeanFactory

#### 综述

Bean工厂（com.springframework.beans.factory.BeanFactory）是Spring框架最核心的接口，它提供了高级IoC的配置机制, BeanFactory使管理不同类型的Java对象成为可能.

应用上下文（com.springframework.context.ApplicationContext）建立在BeanFactory基础之上，提供了更多面向应用的功能，它提供了国际化支持和框架事件体系，更易于创建实际应用。

我们一般称BeanFactory为IoC容器，而称 ApplicationContext为应用上下文。但有时为了行文方便，我们也将ApplicationContext称为Spring容器。

BeanFactory是Spring框架的基础设施，面向Spring本身；ApplicationContext面向使用Spring框架的开发者，几乎所有的应用场合都直接使用ApplicationContext而非底层的BeanFactory。

#### BeanFactory的使用

```java
public class BeanFactoryTest {
    public static void main(String[] args) throws IOException {
        ResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        Resource res = resolver.getResource("classpath:beans.xml");
        BeanFactory bf = new XmlBeanFactory(res);
        System.out.println("init BeanFactory.");

        BeanFactory factory = new XmlBeanFactory(new ClassPathResource("com/hsp/ioc/beans.xml"));
    }
}
```

**在初始化BeanFactory时，必须为其提供一种日志框架，我们使用Log4J，即在类路径下提供Log4J配置文件，这样启动Spring容器才不会报错。**

```xml
log4j.properties
log4j.rootLogger=INFO,A1
log4j.appender.A1=org.apache.log4j.ConsoleAppender
log4j.appender.A1.layout=org.apache.log4j.PatternLayout
log4j.appender.A1.layout.ConversionPattern=%d %5p [%t] (%F:%L) - %m%n
```

#### ApplicationContext的使用

ApplicationContext使用 `ClassPathXmlApplicationContext` 和 `FileSystemXMLApplicationContext`，前者默认从类路径下加载配置文件，后者默认从文件系统中装载配置文件。

在获取ApplicationContext实例后，就可以像BeanFactory一样调用getBean(beanName)返回Bean了。

**BeanFactory在初始化容器时，并未实例化Bean，直到第一次访问某个Bean时才实例目标Bean；而ApplicationContext则在初始化应用上下文时就实例化所以单实例的Bean。**

```java
public class AnnotationApplicationContext {
    public static void main(String[] args) {
        ApplicationContext ctx = new AnnotationConfigApplicationContext(Beans.class);
        Car car = ctx.getBean("car", Car.class);
        System.out.println(car.getBrand());
        System.out.println(car.getMaxSpeed());
    }
}

@Configurable
public class Beans {
    @Bean(name = "car")
    public Car buildCar() {
        Car car = new Car();
        car.setBrand("英菲迪尼");
        car.setMaxSpeed(300);
        return car;
    }
}
```

>  AnnotationConfigEmbeddedWebApplicationContext(Spring Boot提供的) -> ApplicationContext -> BeanFactory

#### AnnotationConfigApplicationContext

专门用Java配置 + 注解方式来获取Bean的容器类



#### FactoryBean和BeanFactory的区别

##### BeanFactory

以Factory结尾，它是一个工厂类，用于管理Bean的一个工厂. `BeanFactory` 是IOC最基本的容器，负责生产和管理bean，它为其他具体的IOC容器提供了最基本的规范.

例如 `DefaultListableBeanFactory`, `XmlBeanFactory`, `ApplicationContext` 等具体的容器都是实现了`BeanFactory`，再在其基础之上附加了其他的功能。

##### FactoryBean

以Bean结尾，表示它是一个Bean. 

`FactoryBean` 是一个接口，当在IOC容器中的Bean实现了`FactoryBean`后，通过`getBean(String BeanName)`获取到的Bean对象并不是 `FactoryBean` 的实现类对象，而是这个实现类中的`getObject()`方法返回的对象。

要想获取`FactoryBean`的实现类，就要`getBean(&BeanName)`，在BeanName之前加上&。



#### ApplicationContext和BeanFactory的区别

1. BeanFactroy采用的是延迟加载形式来注入Bean的，即只有在使用到某个Bean时**(调用getBean())**，才对该Bean进行加载实例化，这样，我们就不能发现Spring的配置问题。

2. ApplicationContext则相反，它是在容器启动时，一次性创建了所有的Bean。这样，在容器启动时，我们就可以发现Spring中存在的配置错误。 

3. 使用applicationContext的好处就是：所有的对象都可以预加载，缺点就是消耗服务器的内存；而使用BeanFactory的话，好处是节约内存，缺点则是速度会相对来说慢一些。而且有可能会出现空指针异常的错误。而且通过BeanFactory创建的bean生命周期会简单一些。

4. BeanFactory和ApplicationContext都支持BeanPostProcessor、BeanFactoryPostProcessor的使用，但两者之间的区别是：BeanFactory需要手动注册，而ApplicationContext则是自动注册.

5. ApplicationContext扩展了ResourceLoader(资源加载器)接口，从而可以用来加载多个Resource，而BeanFactory是没有扩展ResourceLoader 

6. BeanFactory是不支持国际化功能的，因为BeanFactory没有扩展Spring中MessageResource接口。相反，由于ApplicationContext扩展了MessageResource接口，因而具有消息处理的能力(i18N)

7. 强大的事件机制(Event) 

  >  ApplicationContext的事件机制主要通过ApplicationEvent和ApplicationListener这两个接口来提供的，
  >
  > 即当ApplicationContext中发布一个事件的时，所有扩展了ApplicationListener的Bean都将会接受到这个事件，并进行相应的处理。 



#### BeanFactory设计路径

BeanFactory -> HierarchicalBeanFactory -> ConfigurableBeanFactory，是一个主要的BeanFactory设计路径。

BeanFactory：基本规范，比如说getBean()这样的方法。

HierarchicalBeanFactory：管理双亲IoC容器规范，比如说getParentBeanFactory()这样的方法。

ConfigurableBeanFactory：对BeanFactory的配置功能，比如通过setParentBeanFactory()设置双亲IoC容器，通过addBeanPostProcessor()配置Bean后置处理器。

#### ApplicationContext设计路径

BeanFactory -> ListableBeanFactory 

HierarchicalBeanFactory -> ApplicationContext -> ConfigurableApplicationContext，是另外一个主要的ApplicationContext设计路径。

ListableBeanFactory：细化了许多BeanFactory的功能，比如说getBeanDefinitionNames()。
ApplicationContext：通过继承MessageSource、ResourceLoader、ApplicationEventPublisher接口，添加了许多高级特性。



### BeanPostProcessor

#### 1. BeanPostProcessor与InitializingBean的区别

- BeanPostProcessor接口对所有的bean都起作用，即所有的bean初始化前后都会调BeanPostProcessor实现类中的方法;


- InitializingBean和DisposableBean接口是针对单个bean的，即只有在对应的bean实现了InitializingBean或DisposableBean接口才会调用其方法;
- 两个方法的参数以及返回值对应的意义都是一样的，其中参数bean表示当前状态的bean，参数beanName表示当前bean的名称，而方法对应的返回值即表示需要放入到bean容器中的bean; 所以用户如果有需要完全可以在这两个方法中对bean进行修改，即封装自己的bean进行返回。

##### 执行顺序

Bean自己的构造方法-->BeanPostProcessor-->InitializingBean-->bean中的初始化方法。

```java
public interface BeanPostProcessor {
	Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException;
	Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException;
}
```



#### 2. 调用时机

##### postProcessBeforeInitialization的调用时机

在**bean实例化，依赖注入之后**及**自定义初始化方法之前**调用

- 配置文件中bean标签添加init-method属性指定Java类中初始化方法


- @PostConstruct注解指定初始化方法


-  Java类实现InitializingBean接口而产生的afterPropertiesSet()方法之前

##### postProcessAfterInitialization的调用时机

在**bean实例化、依赖注入之后**及**自定义初始化方法之后**调用

- 即在调用实现 InitializingBean接口 而新产生的 afterPropertiesSet()方法 或对应 init-method方法 之后, 调用postProcessAfterInitialization 方法



#### 3. 特点

- 只需要把实现BeanPostProcessor接口的类当做一个普通的bean定义到Spring的bean容器中，Spring将能够自动检测到它，并将它注册到当前的bean容器中。



- BeanPostProcessor是与容器绑定的，即BeanPostProcessor只能对跟它属于同一个bean容器中的bean进行回调，即BeanPostProcessor不能对属于它父容器或子容器中的bean进行回调。



- 在bean容器中定义了BeanPostProcessor之后，Spring将最先将BeanPostProcessor对应的bean进行实例化，如果我们制定BeanPostProcessor的lazy-initialization=”true”或default-lazy-initialization=”true”，Spring将对其进行忽略，即这些配置对BeanPostProcessor不起作用


##### 定义多个BeanPostProcessor的情况

- 在bean容器中可以同时定义多个BeanPostProcessor，这样在新实例化一个bean后将依次使用每个BeanPostProcessor回调一遍. 当然，如果某一个BeanPostProcessor回调后的返回的bean为null，则不再继续往下回调，将直接返回null，这个时候bean容器中对应beanName对应的bean也是null。


- 当在一个bean容器中同时定义有多个BeanPostProcessor时，默认将根据BeanPostProcessor在bean容器中定义的先后顺序对新实例化的bean进行回调。



- 还有一种定义BeanPostProcessor回调顺序的方法是: 将我们自定义的BeanPostProcessor实现类同时实现Ordered接口，然后Spring将根据Ordered接口定义的getOrder()方法的返回值来决定BeanPostProcessor回调的先后顺序，getOrder()返回值越小的越先进行回调。



- 此外，实现了Ordered接口的BeanPostProcessor总是比没有实现Ordered接口的BeanPostProcessor先进行回调，为了便于管理，推荐要么都实现Ordered接口，要么都不实现。


#### 4. 实例

```java
@Component
public class HelloBeanPostProcessor implements BeanPostProcessor, Ordered {
	private int order;
	
    public Object postProcessBeforeInitialization(Object bean, String beanName)
			throws BeansException {
		System.out.println("beanName-----------" + beanName);
		return bean;
	}

	public Object postProcessAfterInitialization(Object bean, String beanName)
			throws BeansException {
		return bean;
	}

	public void setOrder(int order) {
		this.order = order;
	}
	
	public int getOrder() {
		return order;
	}
}
```

#### 5. BeanFactory和ApplicationContext在BeanPostProcessor的区别

1. ApplicationContext会**自动检测**在配置文件中实现了BeanPostProcessor接口的所有bean。并把他们注册为后置处理器，然后在容器创建bean的适当时候调用它。因此部署一个后置处理器同部署其他bean并没有什么区别。直接用注解或者xml配置即可

2. 而使用BeanFactory实现的时候，bean后置处理器必须通过代码显式的去注册，在IOC容器集成体系中ConfingurableBeanFactory接口中定义了注册方法。

```java
TestBeanPostPrcessor beanPostProcessor = new TestBeanPostPrcessor();
Resource resource = new FileSystemResource("applicationContext.xml");
ConfigurableBeanFactory factory = new XmlBeanFactory(resource);
factory.addBeanPostProcessor(beanPostProcessor);
factory.getBean("logic");
```


### Spring中的classpath

#### 综述

- WEB应用中的classpath专指项目 `WEB-INF/classes` 和 `WEB-INF/lib`


- web容器在启动时会对WEB-INF/classes和WEB-INF/lib目录下的class文件、配置文件以及jar文件进行加载，配置文件的加载是根据web.xml中的配置来的，web容器并不会自动加载WEB-INF/classes下的配置文件。


- 【classpath:】此配置表示告诉web容器去classpath（WEB-INF/classes和WEB-INF/lib）中去加载指定名称的配置文件，若是有同名文件，则只会加载一个。**只会到你的class路径中查找找文件;**



- 【classpath*:】此配置表示告诉web容器去classpath（WEB-INF/classes和WEB-INF/lib）中去加载指定名称的配置文件，若是有同名文件则会全部加载。**不仅包含class路径，还包括jar文件中(class路径)进行查找。**


#### 注意事项

1. src不是classpath, WEB-INF/classes, WEB-INF/lib才是classpath，WEB-INF/ 是资源目录, 客户端不能访问。
2. WEB-INF/classes目录存放src目录Java文件编译之后的class文件 / xml / properties等资源配置文件，这是一个定位资源的入口。
3. 引用classpath路径下的文件，只需在文件名前加classpath:

​    <param-value>classpath:applicationContext-*.xml</param-value> 
    <!-- 引用其子目录下的文件,如 -->
    <param-value>classpath:context/conf/controller.xml</param-value>

4. lib和classes同属classpath，两者的访问优先级为: **lib > classes**
5. 把classpath理解成编译后target/classes这个文件夹, 里面有classes文件, 也有xml, properties等配置文件. 项目运行的时候先加载web.xml，然后通过web.xml中的配置信息(classpath:spring/spring-*.xml)



### InitializingBean

```java
public interface InitializingBean {
	void afterPropertiesSet() throws Exception;
}
```
InitializingBean接口为bean提供了初始化方法的方式，它只包括afterPropertiesSet方法，凡是继承该接口的类，在初始化bean的时候(指实例化上下文, 但并没有执行getBean方法的时刻)会执行该方法。

> 初始化方法包括
>
> * afterPropertiesSet
> * 已声明的init-method方法

#### 注意

在spring初始化bean的时候，如果该bean是实现了InitializingBean接口，并且同时在配置文件中指定了init-method，**系统则是先调用afterPropertiesSet方法，然后在调用init-method中指定的方法**。

#### 总结

1. spring为bean提供了两种初始化bean的方式，实现InitializingBean接口，实现afterPropertiesSet方法，或者在配置文件中同过init-method指定，两种方式可以同时使用
2. 实现InitializingBean接口是直接调用afterPropertiesSet方法，比通过反射调用init-method指定的方法效率相对来说要高点。但是init-method方式消除了对spring的依赖
3. 如果调用afterPropertiesSet方法时出错，则不调用init-method指定的方法。

> 源码来自: AbstractAutowireCapableBeanFactory#invokeInitMethods

4. DisposableBean接口和InitializingBean接口一样, 是在销毁之前执行.
5. 在指定方法上加上@PostConstruct或@PreDestroy注解来制定该方法是在初始化之后还是销毁之前调用。



### Spring中的事件

#### Java中的事件

Java中的标准事件接口是 EventObject

对Spring来说, 根抽象类是 ApplicationEvent extends EventObject

Java中的标准监听器是 EventListener

对Spring来说, 是 ApplicationListener<E extends ApplicationEvent> extends EventListener
(泛型表示: 监听器监听什么事件, 这个事件必须继承自ApplicationEvent)

spring中发布事件的根接口 ApplicationEventPublisher, 里面有publishEvent方法

被根上下文接口 ConfigurableApplicationContext 接口继承, 也被 AnnotationConfigApplicationContext 类实现, 所以实例化 AnnotationConfigApplicationContext 上下文后, 就可以发布事件

#### Servlet中的事件

```java
public interface ServletContextListener extends EventListener {
    public void contextInitialized(ServletContextEvent sce);
    public void contextDestroyed(ServletContextEvent sce);
}

public class ServletContextEvent extends java.util.EventObject {
    public ServletContextEvent(ServletContext source) {
        super(source);
    }
    public ServletContext getServletContext() {
        return (ServletContext) super.getSource();
    }
}
```

- public ServletContextEvent(ServletContext source); 这个方法是从一个给定的ServletContext构建一个ServletContextEvent。也就是Servlet一初始化, 就可以构建一个ServletContextEvent事件
- public ServletContext getServletContext();则是返回已经改变的ServletContext
- ServletContextListener则监听ServletContextEvent事件. 然后初始化ServletContext容器



#### 几种和Spring容器有关的事件

##### ContextRefreshedEvent

ApplicationContext 发送该事件时，表示该容器中所有的Bean都已经被装载完成，此ApplicationContext已就绪可用 

##### ContextStartedEvent

生命周期 beans的启动信号

##### ContextStoppedEvent:

生命周期 beans的停止信号

##### ContextClosedEvent

ApplicationContext关闭事件，则context不能刷新和重启，从而所有的singleton bean全部销毁(因为singleton bean是存在容器缓存中的) 

> 虽然spring提供了许多内置事件，但用户也可根据自己需要来扩展spring中的事件。注意，要扩展的事件都要实现ApplicationEvent接口。



#### ServletContextEvent 

```java
// Servlet容器的事件
// EventObject是抽象类, 里面有构造方法
class ServletContextEvent extends EventObject {
    public ServletContextEvent(ServletContext source) {
        //source 事件发生的源(比如, Servlet本身, 鼠标点击, 传入的源可能是鼠标的位置等)
        super(source); 
    }

    public ServletContext getServletContext() {
        return (ServletContext) super.getSource();
    }
}


```

#### ServletContextListener

```java
// 有事件就有监听器 ServletContextListener
interface ServletContextListener extends EventListener(标记接口)
```

ServletContextListener 接口能监听 ServletContext 对象（web应用）的生命周期。

当 Servlet 容器启动或者终止web应用时，会触发 ServletContextEvent 事件。该事件由 ServletContextListener 处理，在ServletContextListener 接口中定义了处理该事件的两个方法：

```java
//当Servlet容器终止web应用时调用该方法。在调用该方法之前，容器会先销毁所有的Servlet和Filter。
void contextDestroyed(ServletContextEvent sce) 

//当Servlet容器启动web应用时调用该方法，调用后容器再初始化filter，初始化需要被初始化的Servlet
void contextInitialized(ServletContextEvent sce)
```

#### 其他监听器

##### ServletContextAttributeListener

监听对ServletContext属性的操作. 比如增加、删除、修改属性

##### HttpSessionListener

监听HttpSession的操作

当创建一个Session时，激发sessionCreated(HttpSessionEvent se)方法；

当销毁一个Session时，激发sessionDestroyed(HttpSessionEvent se)方法。

##### HttpSessionAttributeListener

监听HttpSession中的属性的操作

当在Session增加一个属性时，激发attributeAdded(HttpSessionBindingEvent se) 方法；

当在Session删除一个属性时，激发attributeRemoved(HttpSessionBindingEvent se) 方法；

当在Session属性被重新设置时，激发attributeReplaced(HttpSessionBindingEvent se) 方法



#### Spring容器加载的事件监听器

```java
class ContextLoadListener extends ContextLoad implements ServletContextListener {
    public ContextLoadListener(WebApplicationContext context) {
        super(context);
    }

    public void contextInitialized(ServletContextEvent event) {
        this.initWebApplicationContext(event.getServletContext());
    }
    
	public void contextDestroyed(ServletContextEvent event) {
        this.closeWebApplicationContext(event.getServletContext());
        ContextCleanupListener.cleanupAttributes(event.getServletContext());
    }

    // 该方法在父类ContextLoad中, 当容器启动的时候, 创建spring的上下文
    this.createWebApplicationContext(servletContext); 
}
```



### Resource

#### 获取资源文件的方法说明

```java
// 以下方法均通过 Class / ClassLoader 来调用:
getResourceAsStream()               返回的是inputstream
getResource()                       返回的是URL

Class.getResource("")               返回的是当前Class这个类所在包开始的为置
Class.getResource("/")              返回的是classpath的位置
getClassLoader().getResource("")    返回的是classpath的位置
getClassLoader().getResource("/")   错误的!!
```

#### Class.getResourceAsStream 和 ClassLoader.getResourceAsStream 

1. 两者都可以从classpath中获取资源, 所谓的classpath, 包含classpath中的路径和classpath中的jar
2. 在使用Class.getResourceAsStream时， 资源路径有两种方式，一种以 / 开头，则这样的路径是指定绝对路径， 如果不以 / 开头， 则路径是相对与这个class所在的包的。
3. 在使用ClassLoader.getResourceAsStream时， 路径直接使用相对于classpath的绝对路径, 不能以 / 开头!

```java
// 三者的效果是一致的
com.explorers.Test.class.getResourceAsStream("abc.jpg") 
com.explorers.Test.class.getResourceAsStream("/com/explorers/abc.jpg") 
ClassLoader.getResourceAsStream("com/explorers/abc.jpg") 
```

4. ServletContext.getResourceAsStream(String path)：默认从WebApp根目录下取资源，Tomcat下path是否以’/'开头无所谓，当然这和具体的容器实现有关。

```java
ServletContext.getRealPath("/");  得到Web应用程序的根目录的绝对路径。
System.getProperty("user.dir");   得到项目的根路径
```

**示例**

```java
// 读取classpath下的application.properties文件
// 通过ClassLoader来读取
ClassLoader cl = Thread.currentThread.getContextClassLoader();
InputStream is = cl.getResourceAsStream("application.properties");
Properties prop = new Properties();
prop.load(is);
String appName = prop.getProperty("spring.application.name");
```


#### Resource接口

1. Resource接口统一了资源的访问，而且提供了便利的接口

```java
public interface InputStreamSource {  
    InputStream getInputStream() throws IOException;  
}  

public interface Resource extends InputStreamSource {  
       boolean exists();  
       boolean isReadable();  
       // 返回当前Resource代表的底层资源是否已经打开，如果返回true，则只能被读取一次然后关闭以避免资源泄露；常见的Resource实现一般返回false。
       boolean isOpen();  
       URL getURL() throws IOException;  
       URI getURI() throws IOException;  
       File getFile() throws IOException;  
       long contentLength() throws IOException;  
       long lastModified() throws IOException;  
       Resource createRelative(String relativePath) throws IOException;  
       String getFilename();  
       String getDescription();  
}  
```

2. 内置Resource的实现

**ClassPathResource / FileSystemResource / ServletContextResource**

**ClassPathResource** 

- 代表classpath路径的资源，**将使用ClassLoader进行加载资源**
- classpath 资源存在于类路径中的文件系统中或jar包里，且“isOpen”永远返回false，表示可多次读取资源。
- 用ClassPathResource 加载资源, 本质是替代了Class类和ClassLoader类的“getResource(String name)”和“getResourceAsStream(String name)”两个加载类路径资源方法，提供一致的访问方式。


- ClassPathResource的构造方法

  > **public ClassPathResource(String path)**：使用默认的ClassLoader加载“path”类路径资源；
  >
  > **public ClassPathResource(String path, ClassLoader classLoader)**：使用指定的ClassLoader加载“path”类路径资源；将加载指定的ClassLoader类路径上相对于根路径的资源：

```java
Resource resource = new ClassPathResource("cn/javass/spring/chapter4/test1.properties");

ClassLoader cl = this.getClass().getClassLoader();  
Resource resource = new ClassPathResource("cn/javass/spring/chapter4/test1.properties", cl);  

Class clazz = this.getClass();  
Resource resource = new ClassPathResource("cn/javass/spring/chapter4/test.properties", clazz);
```

> 加载jar包里的资源，如果在当前类路径下找不到，才到Jar包里找，而且在第一个Jar包里找到的将被返回



#### ResourceLoader接口

**ResourceLoader接口用于返回Resource对象；其实现可以看作是一个生产Resource的工厂类。**

```java
public interface ResourceLoader {
    String CLASSPATH_URL_PREFIX = ResourceUtils.CLASSPATH_URL_PREFIX;
    // 根据提供的location参数返回相应的Resource对象
    Resource getResource(String location);
    // 返回加载这些Resource的ClassLoader
    ClassLoader getClassLoader();
}
```

Spring提供了一个适用于所有环境的`DefaultResourceLoader`实现，可以返回`ClassPathResource`、`UrlResource`；还提供一个用于web环境的`ServletContextResourceLoader`，它继承了`DefaultResourceLoader`的所有功能，又额外提供了获取ServletContextResource的支持。

- ResourceLoader在进行加载资源时需要使用前缀来指定需要加载的资源位置：“classpath:path”表示返回ClasspathResource


- “http://path”和“file:path”表示返回UrlResource资源


- 如果不加前缀则需要根据当前上下文来决定，DefaultResourceLoader默认实现可以加载classpath资源

```java
@Test 
public void testResourceLoad() {  
    ResourceLoader loader = new DefaultResourceLoader();  
    Resource resource = loader.getResource("classpath:cn/javass/spring/chapter4/test1.txt");  
    //验证返回的是ClassPathResource  
    Assert.assertEquals(ClassPathResource.class, resource.getClass());  
    
    Resource resource2 = loader.getResource("file:cn/javass/spring/chapter4/test1.txt");  
	//验证返回的是UrlResource
    Assert.assertEquals(UrlResource.class, resource2.getClass());  
    
    Resource resource3 = loader.getResource("cn/javass/spring/chapter4/test1.txt");  
    //验证返默认可以加载ClasspathResource  
    Assert.assertTrue(resource3 instanceof ClassPathResource);  
}  
```



**所有ApplicationContext都实现了ResourceLoader，因此可以使用其来加载资源**

- ClassPathXmlApplicationContext：不指定前缀将返回默认的`ClassPathResource`资源，否则将根据前缀来加载资源；
- FileSystemXmlApplicationContext: 不指定前缀将返回`FileSystemResource`，否则根据前缀来加载资源；
- WebApplicationContext：不指定前缀将返回`ServletContextResource`，否则将根据前缀来加载资源；
- 其他：不指定前缀根据当前上下文返回Resource实现，否则将根据前缀来加载资源。



**ResourceLoaderAware是一个标记接口，用于通过ApplicationContext上下文注入ResourceLoader**

```java
public class ResourceBean implements ResourceLoaderAware {  
    private ResourceLoader resourceLoader;  

    @Override  
    public void setResourceLoader(ResourceLoader resourceLoader) {  
        this.resourceLoader = resourceLoader;  
    }  

    public ResourceLoader getResourceLoader() {  
        return resourceLoader;  
    }  
}  
```

**实例**

```java
ResourceLoader rl = new DefaultResourceLoader();
Resource resource = rl.getResource("classpath:application.properties");
InputStream is = resource.getInputStream();
String content = StreamUtils.copytoString(is, Charset.forName("UTF-8"));
```



#### Resource与ResourceLoader对比

１、Resource接口定义了应用访问底层资源的能力。

- 通过FileSystemResource以文件系统绝对路径的方式进行访问；

- 通过ClassPathResource以类路径的方式进行访问；

- 通过ServletContextResource以相对于Web应用根目录的方式进行访问。

- 在获取资源后，用户就可以通过Resource接口定义的多个方法访问文件的数据和其他的信息：

  > 可以通过getFileName()获取文件名
  >
  > getFile()获取资源对应的File对象
  >
  > getInputStream()直接获取文件的输入流
  >
  > createRelative(String relativePath) 在资源相对地址上创建新的文件

２、ResourceLoader接口提供了一个加载文件的策略。它提供了一个默认的实现类DefaultResourceLoader

#### classpath: / classpath*:

- ResourceLoader接口只提供了classpath前缀的支持


- classpath*的前缀支持是在它的子接口ResourcePatternResolver中

  ```java
  public interface ResourcePatternResolver extends ResourceLoader {
      String CLASSPATH_ALL_URL_PREFIX = "classpath*:";
      Resource[] getResources(String var1) throws IOException;
  }
  ```


- `ResourceLoader`提供 classpath下单资源文件的载入，而`ResourcePatternResolver`提供了多资源文件的载入。


- `ResourcePatternResolver`有一个实现类：`PathMatchingResourcePatternResolver`，查看`PathMatchingResourcePatternResolver`的`getResources()`

1. 无论是classpath还是classpath*都可以加载整个classpath下（包括jar包里面）的资源文件。
2. classpath只会返回第一个匹配的资源，查找路径是优先在项目中存在资源文件，再查找jar包。
3. 文件名字包含通配符资源(如果spring-*.xml，spring*.xml)，  如果根目录为""， classpath加载不到任何资源， 而classpath*则可以加载到classpath中可以匹配的目录中的资源，但是不能加载到jar包中的资源



### WebApplicationContext

WebApplicationContext是专门为Web应用准备的，它允许从相对于Web根目录的路径中装载配置文件完成初始化工作。

#### 获取WebApplicationContext的方法:
##### 方法一: 根据WebApplicationContextUtils和ServletContext来获取

```java
HttpServletRequest request = ServletActionContext.getRequest();
ServletContext servletContext = request.getServletContext();
WebApplicationContext ctx = WebApplicationContextUtils.getWebApplicationContext(servletContext);
```

##### 方法二: 直接根据ServletContext获取其中的属性

```java
WebApplicationContext ctx1 = (WebApplicationContext)servletContext.getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE);
```

##### Spring的Web应用上下文和Web容器的上下文就可以实现互访.

1. WebApplicationContext#getServletContext();

   > 从WebApplicationContext中可以获得ServletContext的引用;
   >
   > 整个Web应用上下文对象将作为属性放置到ServletContext中，以便Web应用环境可以访问Spring应用上下文

2. WebApplicationContextUtils#getWebApplicationContext

- Spring专门为此提供一个工具类 WebApplicationContextUtils，通过该类的getWebApplicationContext(ServletContext sc)方法，即可以从ServletContext中获取WebApplicationContext实例。


- WebApplicationContext定义了一个常量ROOT_WEB_APPLICATION_ CONTEXT_ATTRIBUTE，在上下文启动时，WebApplicationContext实例即以此为键放置在ServletContext的属性列表中，因此我们可以直接通过以下语句从Web容器中获取WebApplicationContext：

> WebApplicationContext wac = (WebApplicationContext)servletContext.getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE);



#### WebApplicationContext的初始化

WebApplicationContext的初始化方式和BeanFactory、ApplicationContext有所区别，**因为WebApplicationContext需要ServletContext实例，也就是说它必须在拥有Web容器的前提下才能完成启动的工作。**

Spring分别提供了用于启动WebApplicationContext的Servlet和Web容器监听器：类ContextLoader 有两个实现：`ContextLoaderListener` 和 `ContextLoaderServlet`

```xml
1. org.springframework.web.context.ContextLoaderServlet: 适用于不支持容器监听器的低版本Web容器中

<context-param> 
    <param-name>contextConfigLocation</param-name>   
    <param-value>/WEB-INF/baobaotao-dao.xml, /WEB-INF/baobaotao-service.xml</param-value> 
</context-param> 

<!--①声明自动启动的Servlet --> 
<servlet>   
    <servlet-name>springContextLoaderServlet</servlet-name> 
    <servlet-class>org.springframework.web.context.ContextLoaderServlet </servlet-class> 
    <!--②启动顺序--> 
    <load-on-startup>1</load-on-startup> 
</servlet> 

2. org.springframework.web.context.ContextLoaderListener: 现代容器适用

class ContextLoaderListener extends ContextLoader implements ServletContextListener extends EventListener

这个监听器所在的jar包为：spring-web.jar

注意: ContextLoadListener 会在创建时自动查找WEB-INF/下的applicationContext.xml文件，因此，如果只有一个配置文件，并且文件名为applicationContext.xml,则只需要在web.xml中加入对Listener的配置就可以。否则, 就用逗号加载多个配置文件, 配置文件的key是contextConfigLocation

<!--①指定配置文件--> 
<context-param>                                                        
    <param-name>contextConfigLocation</param-name>   
    <param-value> 
        /WEB-INF/baobaotao-dao.xml, /WEB-INF/baobaotao-service.xml  
    </param-value> 
</context-param> 

<!--②声明Web容器监听器--> 
<listener>   
    <listener-class>org.springframework.web.context.ContextLoaderListener </listener-class> 
</listener> 
```

##### ServletContext:  

tomcat启动时, 创建ServletContext，作为全局上下文以及spring容器的宿主环境.

当执行Servlet的init()方法时，会触发 `ServletContextListener` 的 

`public void contextInitialized(ServletContextEvent sce);` 方法, 创建ServletContext对象


##### WebApplicationContext:  

在web.xml中配置了`ContextLoaderListener`的监听器，该listener实现了`ServletContextListener`接口, 也就实现了`contextInitialized`方法, 来监听Servlet初始化事件。
    

```java
public class ContextLoaderListener extends ContextLoader implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent event) {
        initWebApplicationContext(event.getServletContext());
    }
}

在该方法中, 初始化了根上下文（即IOC容器），也就是WebApplicationContext。该类是一个接口类，其默认实现为XmlWebApplicationContext。

在initWebApplicationContext这个方法中进行了创建根上下文，并将该上下文以key-value的方式存储到ServletContext中.以WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE为key，this.context则为value.

在web.xml中还有一对重要的标签
<context-param>该标签内的<param-name>的值. 该常量的值就是contextConfigLocation。通过该方法去寻找定义spring的配置文件。来初始化IOC容器的相关信息。
```

##### DispatcherServlet上下文:  

在`WebApplicationContext`初始化完后。开始初始化web.xml中的servlet。这个servlet可以有多个。默认我们都使用`DispatcherServlet`。<servlet>标签中可以有<init-param>标签用来配置一些DispatcherServlet的初始化参数。

```java
该servlet初始化流程是由tomcat的Servlet的init()方法触发。

DispatcherServleet-继承->FrameworkServlet-继承->HttpServletBean-继承-GenericServlet- 实现 ->Servlet。这样的一条关系链。其核心方法在FrameworkServlet中的initServletBean()中的initWebApplicationContext()方法中。

首先去获取之前存在Servlet中的WebApplicationContext。通过上面说的WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE作为key

取到之后，设置为当前DispatcherServlet的父上下文。并且也把该上下文存在ServletContext中。

通过init方法创建的dispatcherServlet上下文可以访问通过ServletContextListener中创建的WebApplicationContext上下文中的bean，反之则不行。因为WebApplicationContext是dispatcherServlet上下文的父容器。
```

##### 三者的联系

- web容器可以说就是Servlet容器--ServletContext，启动tomcat必然有这个。


- dispatcherServlet只是一个Servlet，必然装在容器里。当然容器可以装其它任何Servlet，不一定必须有dispatcherServlet。


- WebApplicationContext是IOC容器，里面是装spring的bean的。可以说与上面的容器及具体的Servlet没有直接联系。



### WebMvcConfigurerAdapter

#### 使用 java 的方式配置 sping mvc 时

1. 采用继承 WebMvcConfigurerAdapter 类
2. 采用继承 WebMvcConfigurationSupport 类

    两个类都是来自包org.springframework.web.servlet.config.annotation
    两个类都可以实现配置mvc。两者都可以配置视图解析器以及静态资源等 

3. 区别： 

> WebMvcConfigurationSupport 与 WebMvcConfigurerAdapter 都可以配置MVC
>
> WebMvcConfigurationSupport 支持的自定义的配置更多更全，WebMvcConfigurerAdapter有的WebMvcConfigurationSupport 都有

#### 使用方式

**@EnableWebMvc = WebMvcConfigurationSupport**，使用了@EnableWebMvc注解等于扩展了WebMvcConfigurationSupport但是没有重写任何方法

所以有以下几种使用方式：

```java
@EnableWebMvc + extends WebMvcConfigurerAdapter
在扩展的类中重写父类的方法即可，这种方式会屏蔽springboot的@EnableAutoConfiguration中的设置

extends WebMvcConfigurationSupport
在扩展的类中重写父类的方法即可，这种方式会屏蔽springboot的@EnableAutoConfiguration中的设置

extends WebMvcConfigurerAdapter
在扩展的类中重写父类的方法即可，这种方式依旧使用springboot的@EnableAutoConfiguration中的设置

// 在WebMvcConfigurationSupport类（@EnableWebMvc）和 @EnableAutoConfiguration 都有一些默认的设定 

当你使用@EnableWebMvc来配置spring mvc时，会把WebMvcConfigurationSupport当成配置文件来用，将其中所有标识有@Bean注解的方法配置成bean，这就成了Spring mvc的默认配置

Spring mvc提供的默认实现是 DelegatingWebMvcConfiguration ，覆盖父类的方法之前，它会寻找容器中所有的WebMvcConfigurer实现类，将所有WebMvcConfigurer实现类中的配置组合起来，组成一个超级配置，这样，WebMvcConfigurationSupport中的bean发布时，就会把这所有配置都带上了。
(public class DelegatingWebMvcConfiguration extends WebMvcConfigurationSupport)
```


### Spring MVC

#### springmvc执行流程

1. 每一个请求都会先发给DispatcherServlet，然后由其负责请求的分发，给相应的HandlerMapping处理器映射器，然后根据请求的url，找到对应的处理器，生成处理器对象，返回给DispatcherServlet。
2. DispatcherServlet通过HandlerAdapter处理器适配器来调用处理器Handler, 它是继DispatcherServlet之后的后端控制器，执行处理器的业务逻辑。执行完成后，将返回ModelAndView对象给处理器适配器，然后处理器适配器再把ModelAndView返回给前端控制器。
3. DispatcherServlet把ModelAndView传递给ViewResolver视图解析器，解析之后返回具体的View给前端控制器。
4. DispatcherServlet对View进行渲染，也就是将模型数据填充到视图中，然后响应给用户。

#### 优势

使用了前端控制器(DispatcherServlet)这一组件，会使各个功能模块解耦。

#### 组件

* DispatcherServlet：前端控制器 
* HandlerMapping：处理器映射器 
* Handler：处理器 
* HandlAdapter：处理器适配器 
* ViewResolver：视图解析器 
* View：视图 

> 在springmvc的各个组件中，处理器映射器、处理器适配器、视图解析器称为springmvc的三大组件。需要用户开发的组件有handler、view。



### 两种实现自动注入的方法

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



### 配置Filter

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

### 