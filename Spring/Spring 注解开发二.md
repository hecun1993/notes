# Spring 注解开发

## 属性赋值

### @Value和@PropertySource

#### @Value赋值

1. 基本数值
2. 可以写SpEL； #{}
3. 可以写${}；取出配置文件【properties】中的值（在运行环境变量Enviroment里面的值）

```java
package com.atguigu.bean;

import org.springframework.beans.factory.annotation.Value;

public class Person {
	@Value("张三")
	private String name;
	@Value("#{20-2}")
	private Integer age;
	
	@Value("${person.nickName}")
	private String nickName;
}
```

#### @PropertySource

使用@PropertySource注解, 读取外部配置文件中的k/v属性, 保存到运行的环境变量中;

加载完外部的配置文件以后使用${}取出配置文件的值

@PropertySource(value={"classpath:/person.properties"})

```java
package com.atguigu.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.PropertySource;

import com.atguigu.bean.Person;

@PropertySource(value={"classpath:/person.properties"})
@Configuration
public class MainConfigOfPropertyValues {
	@Bean
	public Person person(){
		return new Person();
	}
}
```

#### 测试

```java
// 从Enviroment中获取配置的属性值
ConfigurableEnvironment environment = applicationContext.getEnvironment();
String property = environment.getProperty("person.nickName");
System.out.println(property);
```



## 自动装配

Spring利用依赖注入（DI），完成对IOC容器中各个组件的依赖关系的管理

### @Autowired

比如要在BookService中注入BookDao.

- 默认优先按照**类型**去容器中找对应的组件: 也就是applicationContext.getBean(BookDao.class); 找到就赋值

> 当只通过@Repository注解和@ComponentScan两个注解往容器中添加BookDao时, 会根据类型直接注入.

- 如果找到多个相同类型的组件，再将属性的名称作为组件的id去容器中查找. 也就是 applicationContext.getBean("bookDao")

> 当通过@Repository注解和@ComponentScan两个注解往容器中添加BookDao, 同时也通过@Bean注解添加另外一个BookDao, 此时, 就会根据名称注入. @Bean(name="bookDao2")
>
> 也就是说, 在BookService中, BookDao这个属性的属性名是bookDao, 则会注入第一个BookDao

- 在@Autowired注解上再加一个@Qualifier("bookDao"). 使用@Qualifier指定需要装配的组件的id，而不是使用BookService中的属性名.


- 自动装配默认一定要将属性赋值好，没有就会报错；可以使用@Autowired(required=false);


- @Primary：让spring进行自动装配的时候，默认使用首选的bean；也可以继续使用@Qualifier指定需要装配的bean的名字

#### @Autowired可以放在构造器，参数，方法，属性上

>  @Component, 默认加载ioc容器中的组件的方式是，容器启动会调用无参构造器创建对象，再进行初始化赋值等操作

##### @Autowired放在方法上, 构造器上, 参数上, 所需要的参数都是从ioc容器获取的

* @Autowired标注在方法上，容器创建当前Boss对象，就会调用Boss对象的setCar方法，完成赋值；方法使用的参数Car，会从ioc容器中获取.

* **如果是@Bean注册对象到容器中, 则@Bean注解的那个方法的参数, 也是从Spring容器获取的. 可以不给这个方法参数加@Autowired**

  ```java
  @Bean
  // Cat参数从容器中获取
  public Car car(Cat cat) {
      return new Car();
  }
  ```

* @Autowired可以加在有参的构造函数上. 这样的含义是, 构造函数所需要的参数也是从容器中获取的. 当然, 如果只有一个有参构造器. 可以省去这个@Autowired, 省去之后, 构造函数所需的参数还是从容器中获取.

```java
package com.atguigu.bean;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class Boss {
	
	private Car car;
	
	// 构造器要用的参数，是从容器中获取
    // 不需要给Car参数添加@Autowired
	public Boss(Car car){
		this.car = car;
		System.out.println("Boss...有参构造器");
	}

    public Car getCar() {
		return car;
	}

	@Autowired 
	// @Autowired标注在方法上，容器创建当前Boss对象，就会调用Boss对象的setCar方法，完成赋值；
	// 方法使用的参数Car，是自定义类型, 会从ioc容器中获取
	public void setCar(Car car) {
		this.car = car;
	}

	@Override
	public String toString() {
		return "Boss [car=" + car + "]";
	}
}
```

### @Resouce(JSR250)和@Inject(JSR330)[java规范的注解]

#### @Resource

可以和@Autowired一样实现自动装配功能；默认是按照组件名称进行装配的；

没有能支持@Primary的功能, 没有支持@Autowired (reqiured=false)

#### @Inject

需要导入javax.inject的包，和Autowired的功能一样。没有required=false的功能；

#### 三种自动装配方式的区别

@Autowired是Spring定义的； @Resource、@Inject都是java规范

> AutowiredAnnotationBeanPostProcessor 解析上述注解, 来完成自动装配功能



### 实现Aware接口来实现自动装配

```java
package com.atguigu.bean;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.BeanNameAware;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.context.EmbeddedValueResolverAware;
import org.springframework.stereotype.Component;
import org.springframework.util.StringValueResolver;

@Component
public class Red implements ApplicationContextAware, BeanNameAware, EmbeddedValueResolverAware {
	
	private ApplicationContext applicationContext;

	@Override
	public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
		System.out.println("传入的ioc：" + applicationContext);
		this.applicationContext = applicationContext;
	}

    // BeanNameAware 获取Bean的名字
	@Override
	public void setBeanName(String name) {
		System.out.println("当前bean的名字：" + name);
	}

    // EmbeddedValueResolverAware 注入StringValueResolver字符串解析器, 来解析${}或者#{}
	@Override
	public void setEmbeddedValueResolver(StringValueResolver resolver) {
		String resolveStringValue = resolver.resolveStringValue("你好 ${os.name} 我是 #{20*18}");
		System.out.println("解析的字符串：" + resolveStringValue);
	}
}
```

自定义组件想要使用Spring容器底层的一些组件（ApplicationContext，BeanFactory，xxx）

只需要自定义组件实现xxxAware接口；在创建对象的时候，会调用接口规定的方法注入相关组件；

核心是spring3.1提供的Aware接口

- xxxAware：原理是 xxxProcessor => BeanPostProcessor
- ApplicationContextAware ==> ApplicationContextAwareProcessor



### @Profile

Spring提供的可以根据当前环境，动态的激活和切换一系列组件的功能

主要用于指定组件在哪种环境下, 才能被注册到容器中，如果不指定，则任何环境下都能注册这个组件

#### MainConfigOfProfile

```java
// 选择属性注入的前提条件, 引入properties文件
@PropertySource("classpath:/dbconfig.properties")
@Configuration
public class MainConfigOfProfile implements EmbeddedValueResolverAware{
	
    // 属性注入的方式一 @Value("${db.user}")放在属性上 user
    // 属性注入的方式二 @Value("${db.user}")放在方法参数上 password
	@Value("${db.user}")
	private String user;
	
    // 属性注入的方式三 StringValueResolver + ${db.driverClass}
	private StringValueResolver valueResolver;
	private String  driverClass;
	
	@Override
	public void setEmbeddedValueResolver(StringValueResolver resolver) {
		this.valueResolver = resolver;
		driverClass = valueResolver.resolveStringValue("${db.driverClass}");
	}
    
    // 没有标明@Profile注解, 则在任何情况下, 都会注入到spring容器中
	@Bean
	public Yellow yellow(){
		return new Yellow();
	}
	
    // 注册数据源, 并且标明@Profile, 是在test环境下使用.
	@Profile("test")
	@Bean("testDataSource")
	public DataSource dataSourceTest(@Value("${db.password}")String pwd) throws Exception{
		ComboPooledDataSource dataSource = new ComboPooledDataSource();
		dataSource.setUser(user);
		dataSource.setPassword(pwd);
		dataSource.setJdbcUrl("jdbc:mysql://localhost:3306/test");
		dataSource.setDriverClass(driverClass);
		return dataSource;
	}
	
	
	@Profile("dev")
	@Bean("devDataSource")
	public DataSource dataSourceDev(@Value("${db.password}")String pwd) throws Exception{
		ComboPooledDataSource dataSource = new ComboPooledDataSource();
		dataSource.setUser(user);
		dataSource.setPassword(pwd);
		dataSource.setJdbcUrl("jdbc:mysql://localhost:3306/ssm_crud");
		dataSource.setDriverClass(driverClass);
		return dataSource;
	}
	
	@Profile("prod")
	@Bean("prodDataSource")
	public DataSource dataSourceProd(@Value("${db.password}")String pwd) throws Exception{
		ComboPooledDataSource dataSource = new ComboPooledDataSource();
		dataSource.setUser(user);
		dataSource.setPassword(pwd);
		dataSource.setJdbcUrl("jdbc:mysql://localhost:3306/scw_0515");
		
		dataSource.setDriverClass(driverClass);
		return dataSource;
	}

	
}
```

#### db.properties

```properties
db.user=root
db.password=123456
db.driverClass=com.mysql.jdbc.Driver
```

#### 带环境信息的启动方式

1. 使用命令行动态参数: 在虚拟机参数位置加启动参数来激活环境配置 -Dspring.profiles.active=test
2. 使用代码的方式激活环境. 

#### 测试

> 在使用代码方式注册的时候, 不能直接使用AnnotationConfigApplicationContext的有参构造函数来创建容器. 因为有参的构造函数会直接执行创建 / 注册 / 刷新. 我们无法为其设置环境变量信息.
>
> 所以应该使用无参构造创建容器.
>
> ```java
> public AnnotationConfigApplicationContext(Class... annotatedClasses) {
>     this();
>     this.register(annotatedClasses);
>     this.refresh();
> }
> ```

```java
package com.atguigu.test;

import javax.sql.DataSource;

import org.junit.Test;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

import com.atguigu.bean.Boss;
import com.atguigu.bean.Car;
import com.atguigu.bean.Color;
import com.atguigu.bean.Red;
import com.atguigu.bean.Yellow;
import com.atguigu.config.MainConfigOfProfile;
import com.atguigu.config.MainConifgOfAutowired;
import com.atguigu.dao.BookDao;
import com.atguigu.service.BookService;

public class IOCTest_Profile {
	
	//1、使用命令行动态参数: 在虚拟机参数位置加载 -Dspring.profiles.active=test
	//2、代码的方式激活某种环境；
	@Test
	public void test01(){
        //1、创建一个applicationContext
		AnnotationConfigApplicationContext applicationContext = 
				new AnnotationConfigApplicationContext();
		//2、设置需要激活的环境, 可以设置多个环境
		applicationContext.getEnvironment().setActiveProfiles("dev", "test");
		//3、注册主配置类
		applicationContext.register(MainConfigOfProfile.class);
		//4、启动刷新容器
		applicationContext.refresh();
		
		String[] namesForType = applicationContext.getBeanNamesForType(DataSource.class);
		for (String string : namesForType) {
			System.out.println(string);
		}
		
		Yellow bean = applicationContext.getBean(Yellow.class);
		System.out.println(bean);
		applicationContext.close();
	}
}
```

#### 注意

* 加了环境标识@Profile的Bean，只有这个环境被激活的时候才能注册到容器中。默认是default环境. 也就是默认是@Profile("default")
* @Profile写在配置类上时，只有是指定的环境的时候，整个配置类里面的所有配置的Bean才能开始生效
* 没有标注环境标识@Profile的bean, 在任何环境下都是加载的；



## AOP

导入依赖 spring-aspects 

#### Demo示例

##### 业务类 MathCalculator

```java
package com.atguigu.aop;

public class MathCalculator {
    public int div(int i, int j) {
        System.out.println("MathCalculator...div...");
        return i / j;
    }
}
```

##### 切面类 LogAspects

```java
package com.atguigu.aop;

import java.util.Arrays;

import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.After;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.aspectj.lang.annotation.Pointcut;

/**
 * @Aspect： 告诉Spring当前类是一个切面类
 */
@Aspect
public class LogAspects {

    // 抽取公共的切入点表达式(否则, 每个通知方法都需要写一次切入点表达式)
    // 1、本类引用: pointCut() => @Before("pointCut()")
    // 2、其他的切面引用: com.atguigu.aop.LogAspects.pointCut() => @After("com.atguigu.aop.LogAspects.pointCut()")
    @Pointcut("execution(public int com.atguigu.aop.MathCalculator.*(..))")
    // 切入点表达式如上所示
    public void pointCut() {
    }

    // @Before在目标方法之前切入；切入点表达式（指定在哪个方法切入）
    @Before("pointCut()")
    // 将JoinPoint当成参数传入通知方法, 则可以根据JoinPoint获取一些和被aop方法的信息
    // 1. 方法名: joinPoint.getSignature().getName()
    // 2. 方法参数: Object[] args = joinPoint.getArgs(); Arrays.asList(args)
    public void logStart(JoinPoint joinPoint) {
        Object[] args = joinPoint.getArgs();
        System.out.println("" + joinPoint.getSignature().getName() + "运行。。。@Before:参数列表是：{" + Arrays.asList(args) + "}");
    }

    @After("com.atguigu.aop.LogAspects.pointCut()")
    public void logEnd(JoinPoint joinPoint) {
        System.out.println("" + joinPoint.getSignature().getName() + "结束。。。@After");
    }

    // JoinPoint一定要出现在参数表的第一位
    // 用returning = "result"表示, 将被aop的业务方法的返回值放到Object result参数中, 在通知方法中可以获取并打印.
    @AfterReturning(value = "pointCut()", returning = "result")
    public void logReturn(JoinPoint joinPoint, Object result) {
        System.out.println("" + joinPoint.getSignature().getName() + "正常返回。。。@AfterReturning:运行结果：{" + result + "}");
    }

    // 用throwing = "exception"表示, 将被aop的业务方法的异常放到Exception exception参数中, 在通知方法中可以获取并打印.
    @AfterThrowing(value = "pointCut()", throwing = "exception")
    public void logException(JoinPoint joinPoint, Exception exception) {
        System.out.println("" + joinPoint.getSignature().getName() + "异常。。。异常信息：{" + exception + "}");
    }
}
```

##### 配置类 MyConfig

```java
@EnableAspectJAutoProxy
@Configuration
public class MainConfigOfAOP {
	 
	//业务逻辑类加入容器中
	@Bean
	public MathCalculator calculator(){
		return new MathCalculator();
	}

	//切面类加入到容器中
	@Bean
	public LogAspects logAspects(){
		return new LogAspects();
	}
}
```

##### 测试类 Test_AOP

```java
package com.atguigu.test;

import org.junit.Test;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

import com.atguigu.aop.MathCalculator;
import com.atguigu.bean.Boss;
import com.atguigu.bean.Car;
import com.atguigu.bean.Color;
import com.atguigu.bean.Red;
import com.atguigu.config.MainConfigOfAOP;
import com.atguigu.config.MainConifgOfAutowired;
import com.atguigu.dao.BookDao;
import com.atguigu.service.BookService;

public class Test_AOP {

    @Test
    public void test01() {
        AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext(MainConfigOfAOP.class);

        //不要自己创建业务对象, 而是要从Spring容器中获取业务对象, 这样, 且切面类才能起作用.
//		MathCalculator mathCalculator = new MathCalculator();
//		mathCalculator.div(1, 1);
        
        MathCalculator mathCalculator = applicationContext.getBean(MathCalculator.class);

        mathCalculator.div(1, 0);
        applicationContext.close();
    }
}
```

【动态代理】指在程序运行期间, 动态的将某段代码切入到指定方法的指定位置, 再运行的编程方式；

#### 开发步骤

1. 导入aop模块；Spring AOP：(spring-aspects)
2. 定义一个业务逻辑类（MathCalculator）在业务逻辑运行的时候将日志进行打印（方法运行之前、方法运行之后, 方法正常返回结果、方法出现异常...）
3. 定义一个日志切面类（LogAspects）切面类里面的方法需要动态感知MathCalculator#div() 运行到哪里然后执行

**通知方法包括:**

- 前置通知(@Before)：logStart：在目标方法(div)运行之前运行
- 后置通知(@After)：logEnd：在目标方法(div)运行结束之后运行（无论方法正常结束还是异常结束）
- 返回通知(@AfterReturning)：logReturn：在目标方法(div)正常返回之后运行
- 异常通知(@AfterThrowing)：logException：在目标方法(div)出现异常以后运行
- 环绕通知(@Around)：动态代理，手动指定并推进目标方法运行（joinPoint.procced()）

4. 给切面类的每个目标方法加上述的五个注解, 来指定这些通知方法何时何地运行（通知注解）

5. 将切面类和业务逻辑类（目标方法所在类）都加入到容器中

6. 必须告诉Spring哪个类是切面类(给切面类上加一个注解：@Aspect)

7. **给配置类中加 @EnableAspectJAutoProxy 【开启基于注解的aop模式】类似如下xml配置**

   ```xml
   <!-- 开启基于注解版的切面功能 -->
   <aop:aspectj-autoproxy></aop:aspectj-autoproxy>
   ```

#### 总结

- 将业务逻辑组件和切面类都加入到容器中；告诉Spring哪个是切面类（@Aspect）
- 在切面类上的每一个通知方法上标注通知注解，告诉Spring何时何地运行（切入点表达式）
- 开启基于注解的aop模式；@EnableAspectJAutoProxy

