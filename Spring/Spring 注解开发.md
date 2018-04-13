# Spring 注解开发

## 组件注册和生命周期

### spring4核心包

引入spring4的核心包, 只需要搜索 spring-context 即可

> spring-context, spring-aop, spring-beans, spring-core, spring-expression, commons-logging

### @Configuration

**@Configuration** 相当于 beans.xml

#### 如果是xml, 创建容器的方式是

```java
ApplicationContext applicationContext = new ClassPathXmlApplicationContext("beans.xml");
```

#### 如果是注解, 创建容器的方式是

```java
ApplicationContext applicationContext = new AnnotationConfigApplicationContext(MainConfig.class);

// 获得容器中所有定义的bean的名字
String[] names = applicationContext.getBeanDefinitionNames();
// 获得Person类型的所有的Bean
String[] names = applicationContext.getBeanNamesForType(Person.class);

// key是bean的名称, value就是这个对象(toString)
Map<String, Person> persons = applicationContext.getBeansofType();
```

> @Configuration相当于是@Component, 所以, 配置类肯定会被加入容器.



### @Bean

**@Bean** 注解的方法名, 就是bean在IOC容器中的id

@Bean注解的方法返回值类型, 就是bean在IOC容器中的类型. 如果想重新命名bean的名称, 则可以写成@Bean(value=""), 来修改.

类似

```xml
<bean id="person" class="me.hds.model.Person">
```



### @ComponentScan

#### xml配置的包扫描

```xml
<!-- 凡是注解了@Controller, @Service, @Repository, @Component的类, 都会被扫描到加入容器 -->
<context:component-scan base-package="me.hds"></context:component-scan>
```

#### 注解配置的包扫描

**@ComponentScan(value = "me.hds")**, 就写在配置类上, 也就是和 **@Configuration** 放在一起. 

#### excludeFilters Filter[]

指定扫描的时候需要排除哪些组件

```java
@ComponentScan(value = "me.hds", excludeFilters = {
	@Filter(type = FilterType.ANNOTATION, classes = {Controller.class, Service.class})
})
@Configuration
public class MyConfig {}
```

#### includeFilters Filter[]

指定扫描的时候只包含哪些组件

```java
// includeFilters 需要加 useDefaultFilters = false 因为默认是全部扫描的
@ComponentScan(value = "me.hds", includeFilters = {
	@Filter(type = FilterType.ANNOTATION, classes = {Controller.class, Service.class})
}, useDefaultFilters = false)
@Configuration
public class MyConfig {}
```

#### FilterType

##### FilterType.ANNOTATION

根据注解来选择组件

##### FilterType.ASSIGNBLE_TYPE

按照给定的类型来选择组件（子类或者是实现类都可以）

##### FilterType.CUSTOM

自定义规则: 自己写一个 `MyTypeFilter` 实现 `TypeFilter` 接口

```java
package com.atguigu.config;

import org.springframework.core.io.Resource;
import org.springframework.core.type.AnnotationMetadata;
import org.springframework.core.type.ClassMetadata;
import org.springframework.core.type.classreading.MetadataReader;
import org.springframework.core.type.classreading.MetadataReaderFactory;
import org.springframework.core.type.filter.TypeFilter;

// 根据match方法的返回值是true或者false来判断是否匹配, 也就是是否要加入ioc容器
public class MyTypeFilter implements TypeFilter {
	/**
	 * metadataReader: 读取到的正在扫描的类信息
	 * metadataReaderFactory: 获取到的其他任何类的信息
	 */
	@Override
	public boolean match(MetadataReader metadataReader, MetadataReaderFactory metadataReaderFactory) {
		// 获取当前类的注解信息
		AnnotationMetadata annotationMetadata = metadataReader.getAnnotationMetadata();
		// 获取当前正在扫描的类的类信息
		ClassMetadata classMetadata = metadataReader.getClassMetadata();
		// 获取当前类资源（类的路径...）
		Resource resource = metadataReader.getResource();
		
        // 获得全类名
		String className = classMetadata.getClassName();
		System.out.println("--->" + className);
		return className.contains("er");
	}
}
```



### @Scope

调整ioc容器中Bean的加载方式, 是单例的还是多例的.

**该注解放在配置类的方法上**

#### singleton

单实例的（默认值）：ioc容器启动, 会调用方法创建对象放到ioc容器中。以后每次获取就是直接从容器（map.get()）中拿.

#### prototype

多实例的：ioc容器启动, 并不会去调用方法创建对象放在容器中, 每次获取的时候才会调用方法创建对象. 每次获取, 都会创建一次. 所以用"=="判断是否是同一个对象时, 会返回false

#### request

同一次请求创建一个实例

#### session

同一个session创建一个实例



### @Lazy

懒加载

**该注解放在配置类的方法上**

专门针对于 **单实例** 的情况

单实例bean, 默认在容器启动的时候就创建对象；

懒加载后, 容器启动时不创建对象, 只有在第一次使用(获取)Bean时才创建对象，并初始化



### @Conditional(spring 4)

可以加在类上, 也可以加在方法上

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Conditional {
	Class<? extends Condition>[] value();
}

package org.springframework.context.annotation;

import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.core.type.AnnotatedTypeMetadata;

public interface Condition {
	boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata);
}
```



#### 获取当前操作系统的方法

```java
ConfigurableEnvironment environment = applicationContext.getEnvironment();
//动态获取当前操作系统的值；Windows 8
String property = environment.getProperty("os.name");
```

#### 实例

##### LinuxCondition

```java
package com.atguigu.condition;

import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.env.Environment;
import org.springframework.core.type.AnnotatedTypeMetadata;

//判断是否linux系统
public class LinuxCondition implements Condition {

	/**
	 * ConditionContext：判断条件 能使用的上下文（环境）
	 * AnnotatedTypeMetadata：注释信息
	 */
	@Override
	public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
		// 判断操作系统是否是linux系统

		//1、能获取到ioc使用的BeanFactory（BeanFactory：创建对象并装配的工厂）
		ConfigurableListableBeanFactory beanFactory = context.getBeanFactory();
		//2、获取类加载器
		ClassLoader classLoader = context.getClassLoader();
		//3、获取当前环境信息
		Environment environment = context.getEnvironment();
		//4、获取到bean定义的注册类(所有的Bean定义都存放在BeanDefinitionRegistry中)
		// 可以注册一个bean的定义, 也可以移除, 或者查询一个bean的定义
		BeanDefinitionRegistry registry = context.getRegistry();
		
		String property = environment.getProperty("os.name");
		
		//可以判断容器中的bean注册情况，也可以给容器中注册bean
		boolean definition = registry.containsBeanDefinition("person");

		if(property.contains("linux")){
			return true;
		}
		return false;
	}
}
```

##### WindowsCondition

```java
package com.atguigu.condition;

import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.env.Environment;
import org.springframework.core.type.AnnotatedTypeMetadata;

//判断是否windows系统
public class WindowsCondition implements Condition {
	@Override
	public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
		Environment environment = context.getEnvironment();
		String property = environment.getProperty("os.name");
		if(property.contains("Windows")){
			return true;
		}
		return false;
	}
}
```

##### MyConfig

```java
/**
 * @Conditional({Condition}) ： 按照一定的条件进行判断，满足条件给容器中注册bean
 * 
 * 如果系统是windows，给容器中注册("bill")
 * 如果是linux系统，给容器中注册("linus")
 */
// 如果Condition接口的实现类WindowsCondition的match方法返回的是true, 则会向容器中注册这个Bean
@Conditional(value = {WindowsCondition.class})
@Bean("bill")
public Person person01(){
    return new Person("Bill Gates",62);
}

// 如果Condition接口的实现类LinuxCondition的match方法返回的是true, 则会向容器中注册这个Bean
@Conditional(LinuxCondition.class)
@Bean("linus")
public Person person02(){
    return new Person("linus", 48);
}
```

> 如果@Conditional(value = {WindowsCondition.class})放在类上, 则如果满足条件, 这个配置类中的所有方法创建的Bean才会生效



### @Import

快速给容器中导入一个组件. 比如, 想把一个Color类, 注册到ioc容器中, 则只需要在配置类上加注解

```java
@Import({Color.class})
public class MyConfig {}

public class Color {	
}
```

就可以将Color放入Spring的容器中.

#### MyImportSelector

`@Import({Color.class, MyImportSelector.class})`

@Import中的参数不仅可以是一个真正要放入Spring容器的类, 也可以是一个实现了ImportSelector接口的MyImportSelector类. 这个类中有一个方法selectImports, 这个方法返回的String[], 就是要注入到Spring容器中的类的全类名. 

```java
package com.atguigu.condition;

import org.springframework.context.annotation.ImportSelector;
import org.springframework.core.type.AnnotationMetadata;

//自定义逻辑返回需要导入的组件
public class MyImportSelector implements ImportSelector {

	//返回值，就是到导入到容器中的组件全类名
	//AnnotationMetadata:当前标注@Import注解的类的所有注解信息
	@Override
	public String[] selectImports(AnnotationMetadata importingClassMetadata) {
		//还可以调用importingClassMetadata的方法
		return new String[]{"com.atguigu.bean.Blue","com.atguigu.bean.Yellow"};
	}
}

// 注意: selectImports方法不要返回null值
// 源码分析
// 如果是return null; 则进入如下类的方法中
// ConfigurationClassParser#processImports

// importClassNames == null
String[] importClassNames = selector.selectImports(currentSourceClass.getMetadata());
Collection<SourceClass> importSourceClasses = asSourceClasses(importClassNames);
processImports(configClass, currentSourceClass, importSourceClasses, false);

private Collection<SourceClass> asSourceClasses(String[] classNames) throws IOException {
	// classNames == null 所以 classNames.length会有空指针异常
	List<SourceClass> annotatedClasses = new ArrayList<SourceClass>(classNames.length);
	for (String className : classNames) {
		annotatedClasses.add(asSourceClass(className));
	}
	return annotatedClasses;
}
```

#### ImportBeanDefinitionRegistrar

`@Import({Color.class, MyImportSelector.class, MyImportBeanDefinitionRegistrar.class})`

手动注册bean到容器中

```java
package com.atguigu.condition;

import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.beans.factory.support.RootBeanDefinition;
import org.springframework.context.annotation.ImportBeanDefinitionRegistrar;
import org.springframework.core.type.AnnotationMetadata;

import com.atguigu.bean.RainBow;

public class MyImportBeanDefinitionRegistrar implements ImportBeanDefinitionRegistrar {
	/**
	 * AnnotationMetadata：当前类的注解信息
	 * BeanDefinitionRegistry:BeanDefinition注册类；
	 * 		把所有需要添加到容器中的bean；调用
	 * 		BeanDefinitionRegistry.registerBeanDefinition手工注册进来
	 */
	@Override
	public void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry) {
        // 查看Spring容器中是否含有某个Bean
		boolean definition = registry.containsBeanDefinition("com.atguigu.bean.Red");
		boolean definition2 = registry.containsBeanDefinition("com.atguigu.bean.Blue");
		// 如果都有
        if(definition && definition2){
			// 创建指定Bean定义信息；（Bean的类型，Bean的作用域...）
            // RootBeanDefinition是BeanDefinition接口的实现类
            // 参数先只有Bean的类型
			RootBeanDefinition beanDefinition = new RootBeanDefinition(RainBow.class);
			// 注册一个Bean，并指定bean在spring中的名称
			registry.registerBeanDefinition("rainBow", beanDefinition);
		}
	}
}
```

#### FactoryBean

工厂Bean, 是一个接口, FactoryBean接口, 里面有一个getObject方法. 

自己写一个实现类, 实现FactoryBean接口, 泛型为要创建的对象类型. 容器会调用getObject方法, 返回的对象T, 放在Spring的容器中.

自己写的这个实现类, 通过@Bean注解, 放在Spring的容器中即可.

```java
package com.atguigu.bean;

import org.springframework.beans.factory.FactoryBean;

//创建一个Spring定义的FactoryBean
public class ColorFactoryBean implements FactoryBean<Color> {

	//返回一个Color对象，这个对象会添加到容器中
	@Override
	public Color getObject() throws Exception {
		System.out.println("ColorFactoryBean...getObject...");
		return new Color();
	}

	@Override
	public Class<?> getObjectType() {
		return Color.class;
	}

	//判断是否是单例
	//true：这个bean是单实例，在容器中只保存一份, 在容器初始化之后就会创建, 而不是等到获取时才创建.
	//false：多实例，每次获取都会创建一个新的bean, 都会调用getObject方法
	@Override
	public boolean isSingleton() {
		return false;
	}
}
```

然后在MyConfig类中配置@Bean即可

```java
@Bean
public ColorFactoryBean colorFactoryBean(){
    return new ColorFactoryBean();
}
```

接下来要获取容器中的Bean

```java
// getBean的参数是colorFactoryBean, 但最后获取的bean的类型是Color类型, 也就是在FactoryBean的实现类的getObject方法返回的那种Bean
Object bean = applicationContext.getBean("colorFactoryBean");

// getBean的参数是&colorFactoryBean, 最后获取的bean的类型是ColorFactoryBean类型, 也就是FactoryBean的实现类
Object bean = applicationContext.getBean("&colorFactoryBean");
```

##### 打印容器中所有的Bean的方法

```java
private void printBeans(AnnotationConfigApplicationContext applicationContext){
    String[] definitionNames = applicationContext.getBeanDefinitionNames();
    for (String name : definitionNames) {
        System.out.println(name);
    }
}
```

### 总结: 给容器中注册Bean的方法

* 包扫描 + 组件标注注解（@Controller/@Service/@Repository/@Component）**[用于自己写的类]**
* @Bean **[导入的第三方包里面的组件, 这些组件无法加@Component注解, 比如RestTemplate]**
* @Import **[直接写类的类型当成参数, 容器中就会自动注册这个组件，id默认是全类名]**
* ImportSelector **返回需要导入的组件的全类名数组**
* ImportBeanDefinitionRegistrar **手动注册bean到容器中**
* 使用Spring提供的 FactoryBean**（工厂Bean）**



### Bean的生命周期

包括Bean的创建, 初始化, 销毁.

由容器管理Bean的生命周期

我们可以自定义初始化和销毁的方法

容器在bean进行到当前生命周期的时候, 调用自定义的初始化和销毁方法

#### 1. 在xml的<bean>中指定init-method和destroy-method

这些方法不能抛出异常, 也不能带有参数.

#### 2. 使用@Bean

在@Bean注解的参数中, 设置initMethod和destroyMethod

```java
package com.atguigu.bean;

import org.springframework.stereotype.Component;

public class Car {
    // 构造方法(创建对象. 先创建再初始化)
	public Car(){
		System.out.println("car constructor...");
	}
    
    // 初始化方法
	public void init(){
		System.out.println("car ... init...");
	}
    
	// 销毁方法
    public void detory(){
		System.out.println("car ... detory...");
	}
}
```

在配置类中

```java
//@Scope("prototype")
@Bean(initMethod = "init", destroyMethod = "detory")
public Car car() {
    return new Car();
}
```

##### 对单实例对象

在容器创建之后, 就会先调用constructor方法创建对象, 然后调用init方法初始化对象. 当手动调用关闭容器的方法applicationContext.close()之后, 会调用destroy()销毁方法.

##### 对多实例对象

也就是在@Bean上加了@Scope("prototype")的对象, 在容器创建时, 不会调用constructor方法创建对象. 只有在获取对象的时候, 才会先调用constructor方法创建对象, 然后调用init方法初始化对象. 但是, 容器不会管理这个bean. 也就是说, 当关闭容器的时候, 容器不会调用销毁方法

#### 3. InitializingBean和DisposableBean

通过让一个自定义的类实现上述两个接口, 并实现其中的afterPropertiesSet方法和destroy方法, 就可以实现初始化方法和销毁方法

```java
package com.atguigu.bean;

import org.springframework.beans.factory.DisposableBean;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.stereotype.Component;

@Component
public class Cat implements InitializingBean,DisposableBean {
	
	public Cat(){
		System.out.println("cat constructor...");
	}

	@Override
	public void destroy() throws Exception {
		System.out.println("cat...destroy...");
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		System.out.println("cat...afterPropertiesSet...");
	}
}

// 这里没有使用@Bean将Cat类放入Spring容器, 而是通过
// @Component和在配置类上的@ComponentScan("com.atguigu.bean")放入Spring容器的
```

#### 3. @PostConstruct和@PreDestroy

都是加在方法上的注解. 是JSR250规范(java的规范)

@PostConstruct：在bean创建完成并且属性赋值完成；来执行初始化方法

@PreDestroy：在容器销毁bean之前通知我们进行清理工作

```java
package com.atguigu.bean;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

@Component
public class Dog implements ApplicationContextAware {

    //@Autowired
    private ApplicationContext applicationContext;

    public Dog() {
        System.out.println("dog constructor...");
    }

    //对象创建并赋值之后调用
    @PostConstruct
    public void init() {
        System.out.println("Dog....@PostConstruct...");
    }

    //容器移除对象之前
    @PreDestroy
    public void detory() {
        System.out.println("Dog....@PreDestroy...");
    }

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
    }
}
```

#### 4. BeanPostProcessor

是接口, 是Bean的后置处理器

在bean初始化前后进行一些处理工作, 有两个方法.

- postProcessBeforeInitialization 在初始化之前工作
- postProcessAfterInitialization 在初始化之后工作

**对容器中所有的Bean都起作用.**

```java
package com.atguigu.bean;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.stereotype.Component;

/**
 * 后置处理器：初始化前后进行处理工作
 * 注意: 需要将后置处理器加入到容器中
 */
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {

	@Override
	public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
		System.out.println("postProcessBeforeInitialization..."+beanName+"=>"+bean);
		return bean;
	}

	@Override
	public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
		System.out.println("postProcessAfterInitialization..."+beanName+"=>"+bean);
		return bean;
	}
}
```

这样的结果是, 对任意一个类Cat来说, 创建容器对象之后, 先调用constructor方法, 然后调用postProcessBeforeInitialization方法, 再调用初始化方法(initMethod, @PostConstruct, InitializingBean), 最后调用postProcessAfterInitialization方法.

#### 源码分析

调用AnnotationConfigApplicationContext的构造方法, 传入配置类, 创建ApplicationContext对象时, 该构造方法会调用AnnotationConfigApplicationContext#refresh()方法.

AbstractApplicationContext#refresh()

```java
// 核心是 this.finishBeanFactoryInitialization(beanFactory);
// 初始化所有的单实例对象
public void refresh() throws BeansException, IllegalStateException {
    Object var1 = this.startupShutdownMonitor;
    synchronized(this.startupShutdownMonitor) {
        this.prepareRefresh();
        ConfigurableListableBeanFactory beanFactory = this.obtainFreshBeanFactory();
        this.prepareBeanFactory(beanFactory);

        try {
            this.postProcessBeanFactory(beanFactory);
            this.invokeBeanFactoryPostProcessors(beanFactory);
            this.registerBeanPostProcessors(beanFactory);
            this.initMessageSource();
            this.initApplicationEventMulticaster();
            this.onRefresh();
            this.registerListeners();
            this.finishBeanFactoryInitialization(beanFactory);
            this.finishRefresh();
        } catch (BeansException var9) {
            if (this.logger.isWarnEnabled()) {
                this.logger.warn("Exception encountered during context initialization - cancelling refresh attempt: " + var9);
            }

            this.destroyBeans();
            this.cancelRefresh(var9);
            throw var9;
        } finally {
            this.resetCommonCaches();
        }

    }
}
```

AbstractApplicationContext#finishBeanFactoryInitialization()

```java
protected void finishBeanFactoryInitialization(ConfigurableListableBeanFactory beanFactory) {
    if (beanFactory.containsBean("conversionService") && beanFactory.isTypeMatch("conversionService", ConversionService.class)) {
        beanFactory.setConversionService((ConversionService)beanFactory.getBean("conversionService", ConversionService.class));
    }

    if (!beanFactory.hasEmbeddedValueResolver()) {
        beanFactory.addEmbeddedValueResolver(new StringValueResolver() {
            public String resolveStringValue(String strVal) {
                return AbstractApplicationContext.this.getEnvironment().resolvePlaceholders(strVal);
            }
        });
    }

    String[] weaverAwareNames = beanFactory.getBeanNamesForType(LoadTimeWeaverAware.class, false, false);
    String[] var3 = weaverAwareNames;
    int var4 = weaverAwareNames.length;

    for(int var5 = 0; var5 < var4; ++var5) {
        String weaverAwareName = var3[var5];
        this.getBean(weaverAwareName);
    }

    beanFactory.setTempClassLoader((ClassLoader)null);
    beanFactory.freezeConfiguration();
    beanFactory.preInstantiateSingletons();
}
```

DefaultListableBeanFactory#preInstantiateSingletons()

AbstractBeanFactory#getBean()

AbstractBeanFactory#doGetBean()

DefaultSingletonBeanRegistry#getSingleton() 尝试获取Bean, 如果获取不到

AbstractBeanFactory#createBean()

AbstractAutowireCapableBeanFactory#doCreateBean() 先调用populateBean(为Bean赋值, 再调initializeBean

AbstractAutowireCapableBeanFactory#initializeBean()

```java
protected Object initializeBean(final String beanName, final Object bean, RootBeanDefinition mbd) {
    if (System.getSecurityManager() != null) {
        AccessController.doPrivileged(new PrivilegedAction<Object>() {
            public Object run() {
                AbstractAutowireCapableBeanFactory.this.invokeAwareMethods(beanName, bean);
                return null;
            }
        }, this.getAccessControlContext());
    } else {
        this.invokeAwareMethods(beanName, bean);
    }

    Object wrappedBean = bean;
    if (mbd == null || !mbd.isSynthetic()) {
        // 初始化之前
        wrappedBean = this.applyBeanPostProcessorsBeforeInitialization(bean, beanName);
    }

    try {
        // 执行初始化方法
        this.invokeInitMethods(beanName, wrappedBean, mbd);
    } catch (Throwable var6) {
        throw new BeanCreationException(mbd != null ? mbd.getResourceDescription() : null, beanName, "Invocation of init method failed", var6);
    }

    if (mbd == null || !mbd.isSynthetic()) {
        // 初始化之后
        wrappedBean = this.applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
    }

    return wrappedBean;
}
```

* populateBean(beanName, mbd, instanceWrapper); 给bean进行属性赋值
* initializeBean
  * applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);
  * invokeInitMethods(beanName, wrappedBean, mbd); 执行自定义初始化
  * applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
  * applyBeanPostProcessorsBeforeInitialization: 
    * 遍历得到容器中所有的BeanPostProcessor；挨个执行postProcessorsBeforeInitialization, 一但postProcessorsBeforeInitialization方法返回null，跳出for循环，不会执行后面的postProcessorsBeforeInitialization

#### 

#### BeanPostPrecessor的应用

##### ApplicationContextAwareProcessor

>  ApplicationContextAware的原理(ApplicationContextAwareProcessor), 可以为实现ApplicationContextAware接口的对象, 注入ApplicationContext容器对象.

**原理**

class ApplicationContextAwareProcessor implements BeanPostProcessor {}

在postProcessBeforeInitialization中, 判断当前的Dog类实现的是哪个Aware接口, 如果是ApplicationContextAware接口, 就把ApplicationContext注入进去

```java
public Object postProcessBeforeInitialization(final Object bean, String beanName) throws BeansException {
    AccessControlContext acc = null;
    if (System.getSecurityManager() != null && (bean instanceof EnvironmentAware || bean instanceof EmbeddedValueResolverAware || bean instanceof ResourceLoaderAware || bean instanceof ApplicationEventPublisherAware || bean instanceof MessageSourceAware || bean instanceof ApplicationContextAware)) {
        acc = this.applicationContext.getBeanFactory().getAccessControlContext();
    }

    if (acc != null) {
        AccessController.doPrivileged(new PrivilegedAction<Object>() {
            public Object run() {
                ApplicationContextAwareProcessor.this.invokeAwareInterfaces(bean);
                return null;
            }
        }, acc);
    } else {
        this.invokeAwareInterfaces(bean);
    }

    return bean;
}

private void invokeAwareInterfaces(Object bean) {
    if (bean instanceof Aware) {
        if (bean instanceof EnvironmentAware) {
            ((EnvironmentAware)bean).setEnvironment(this.applicationContext.getEnvironment());
        }

        if (bean instanceof EmbeddedValueResolverAware) {
            ((EmbeddedValueResolverAware)bean).setEmbeddedValueResolver(this.embeddedValueResolver);
        }

        if (bean instanceof ResourceLoaderAware) {
            ((ResourceLoaderAware)bean).setResourceLoader(this.applicationContext);
        }

        if (bean instanceof ApplicationEventPublisherAware) {
            ((ApplicationEventPublisherAware)bean).setApplicationEventPublisher(this.applicationContext);
        }

        if (bean instanceof MessageSourceAware) {
            ((MessageSourceAware)bean).setMessageSource(this.applicationContext);
        }

        // 注入ApplicationContext
        if (bean instanceof ApplicationContextAware) {
            ((ApplicationContextAware)bean).setApplicationContext(this.applicationContext);
        }
    }

}
```

##### BeanValidationPostProcessor

##### AutowiredAnnotationBeanPostProcessor

##### 生命周期注解的功能