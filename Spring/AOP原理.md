# AOP原理

### @EnableAspectJAutoProxy

观察 @EnableAspectJAutoProxy 注解, 有一个 @Import 注解 @Import({AspectJAutoProxyRegistrar.class})

@Import注解的作用就是往Spring容器中导入组件的. 这里的组件是 `AspectJAutoProxyRegistrar`

```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Import({AspectJAutoProxyRegistrar.class})
public @interface EnableAspectJAutoProxy {
    boolean proxyTargetClass() default false;
    boolean exposeProxy() default false;
}
```

**下面观察 AspectJAutoProxyRegistrar**

class AspectJAutoProxyRegistrar implements ImportBeanDefinitionRegistrar

> ImportBeanDefinitionRegistrar 接口可以自定义的创建Bean的定义信息, 并添加到容器中.

原理就是 利用AspectJAutoProxyRegistrar给容器中注册自定义的bean

bean的值是AnnotationAwareAspectJAutoProxyCreator, 名字是internalAutoProxyCreator

#### 源码分析

1. AspectJAutoProxyRegistrar#registerBeanDefinitions()

```java
AopConfigUtils.registerAspectJAnnotationAutoProxyCreatorIfNecessary(registry);
```
2. AopConfigUtils#registerAspectJAnnotationAutoProxyCreatorIfNecessary(registry);

```java
public static BeanDefinition registerAspectJAnnotationAutoProxyCreatorIfNecessary(BeanDefinitionRegistry registry, Object source) {
    return registerOrEscalateApcAsRequired(AnnotationAwareAspectJAutoProxyCreator.class, registry, source);
}
```
3. AopConfigUtils#registerOrEscalateApcAsRequired()

```java
private static BeanDefinition registerOrEscalateApcAsRequired(Class<?> cls, BeanDefinitionRegistry registry, Object source) {
    Assert.notNull(registry, "BeanDefinitionRegistry must not be null");
    if (registry.containsBeanDefinition("org.springframework.aop.config.internalAutoProxyCreator")) {
        BeanDefinition apcDefinition = registry.getBeanDefinition("org.springframework.aop.config.internalAutoProxyCreator");
        if (!cls.getName().equals(apcDefinition.getBeanClassName())) {
            int currentPriority = findPriorityForClass(apcDefinition.getBeanClassName());
            int requiredPriority = findPriorityForClass(cls);
            if (currentPriority < requiredPriority) {
                apcDefinition.setBeanClassName(cls.getName());
            }
        }

        return null;
    } else {
        // 如果容器中没有 AnnotationAwareAspectJAutoProxyCreator, 则开始设置AnnotationAwareAspectJAutoProxyCreator类的信息和优先级等, 最终注册到容器中.
        RootBeanDefinition beanDefinition = new RootBeanDefinition(cls);
        beanDefinition.setSource(source);
        beanDefinition.getPropertyValues().add("order", -2147483648);
        beanDefinition.setRole(2);
        registry.registerBeanDefinition("org.springframework.aop.config.internalAutoProxyCreator", beanDefinition);
        return beanDefinition;
    }
}
```
4. 向容器中注册一个名字为internalAutoProxyCreator, 值为AnnotationAwareAspectJAutoProxyCreator的Bean (**internalAutoProxyCreator=AnnotationAwareAspectJAutoProxyCreator**)

### AnnotationAwareAspectJAutoProxyCreator

AnnotationAwareAspectJAutoProxyCreator有什么作用 ?

本质上是一个 BeanPostProcessor

下面是它的继承结构

```java
AnnotationAwareAspectJAutoProxyCreator：
	=> AnnotationAwareAspectJAutoProxyCreator
		=> AspectJAwareAdvisorAutoProxyCreator
			=> AbstractAdvisorAutoProxyCreator
				=> AbstractAutoProxyCreator 
					implements SmartInstantiationAwareBeanPostProcessor, BeanFactoryAware
```

**因为实现了两个接口, 所以需要关注后置处理器（在bean初始化完成前后做事情）(SmartInstantiationAwareBeanPostProcessor)、自动装配了BeanFactory(BeanFactoryAware)**

根据上述的继承关系, 找到和BeanFactoryAware接口, BeanPostProcessor接口有关的方法, 从父类开始找, 一直找到子类, 然后进行断点调试. 找到的类和方法如下

```java
AbstractAutoProxyCreator#setBeanFactory()
AbstractAutoProxyCreator#postProcessBeforeInstantiation()
AbstractAutoProxyCreator#postProcessAfterInitialization()
    
AbstractAdvisorAutoProxyCreator#setBeanFactory() => initBeanFactory()

AspectJAwareAdvisorAutoProxyCreator

AnnotationAwareAspectJAutoProxyCreator#initBeanFactory()
```

#### 创建和注册AnnotationAwareAspectJAutoProxyCreator的过程

1. 传入配置类, 创建ioc容器, 注册配置类, 调用refresh()刷新容器

2. 在refresh()方法中, 会调用 `AbstractApplicationContext#registerBeanPostProcessors(beanFactory);` 注册bean的后置处理器来方便拦截bean的创建；

3. PostProcessorRegistrationDelegate#registerBeanPostProcessors()

   ```java
   protected void registerBeanPostProcessors(ConfigurableListableBeanFactory beanFactory) {
       // 1. 先获取所有需要创建的后置处理器的定义
       // 比如配置类注解中新增的BeanPostProcessor接口的实现类对象的定义
       String[] postProcessorNames = beanFactory.getBeanNamesForType(BeanPostProcessor.class, true, false);

       // 2. 再给容器中添加其他实现了BeanPostProcessor接口的对象的定义
       beanFactory.addBeanPostProcessor(new BeanPostProcessorChecker(beanFactory, beanProcessorTargetCount));
       
       // 3.
       // First, register the BeanPostProcessors that implement PriorityOrdered.
       // 优先注册实现了PriorityOrdered接口的BeanPostProcessor；
       
   	// Next, register the BeanPostProcessors that implement Ordered.
       // 再给容器中注册实现了Ordered接口的BeanPostProcessor；
       
       List<BeanPostProcessor> orderedPostProcessors = new ArrayList<BeanPostProcessor>();
       for (String ppName : orderedPostProcessorNames) {
           // 先拿到BeanPostProcessor的名字
           // 通过 beanFactory.getBean()方法
           	BeanPostProcessor pp = beanFactory.getBean(ppName, BeanPostProcessor.class);
           // ==> AbstractBeanFactory#getBean()
               @Override
               public <T> T getBean(String name, Class<T> requiredType) throws BeansException {
                   return doGetBean(name, requiredType, null, false);
               }
           // ==> AbstractBeanFactory#doGetBean(), doGetBean方法中有getSingleton方法
           	Object sharedInstance = getSingleton(beanName);
           // ==> DefaultSingletonBeanRegistry#sharedInstance = getSingleton(beanName, new ObjectFactory<Object>() {}
           // 如果获取不到, 则创建Bean, 就是创建BeanPostProcessor实现类对象, 保存在容器中
           	AbstractBeanFactory#createBean(beanName, mbd, args);
       
   	// Now, register all regular BeanPostProcessors.
       // 嘴周注册没实现优先级接口的BeanPostProcessor；

       PostProcessorRegistrationDelegate.registerBeanPostProcessors(beanFactory, this);
   }
   ```

##### 2.1 获取ioc容器已经定义的实现了BeanPostProcessor接口的对象的定义

因为解析配置类, 而配置类上加了注解@EnableAspectJAutoProxy, 所以会有很多实现了BeanPostProcessor接口的对象, 这一步就是先收集所有这些对象的全类名, 其中就有一个是internalAutoProxyCreator

* 先获取配置类注解中新增的BeanPostProcessor接口的实现类对象的定义
* 再给容器中添加别的实现了BeanPostProcessor接口的对象的定义
* 优先注册实现了PriorityOrdered接口的BeanPostProcessor；
* 再给容器中注册实现了Ordered接口的BeanPostProcessor；
* 注册没实现优先级接口的BeanPostProcessor；

##### 2.2 创建这些实现了BeanPostProcessor接口的对象，保存在容器中

以创建 internalAutoProxyCreator的BeanPostProcessor【AnnotationAwareAspectJAutoProxyCreator】为例

* 在AbstractAutowireCapableBeanFactory类中创建Bean的实例 `protected Object doCreateBean(final String beanName, final RootBeanDefinition mbd, final Object[] args)`  => createBeanInstance(beanName, mbd, args);

* **然后进行初始化**

  ```java
  AbstractAutowireCapableBeanFactory#doCreateBean(final String beanName, final RootBeanDefinition mbd, final Object[] args)

  // Initialize the bean instance.
  Object exposedObject = bean;
  try {
      populateBean(beanName, mbd, instanceWrapper);
  ```

* populateBean: 给bean的各种属性赋值 populateBean(beanName, mbd, instanceWrapper);

* initializeBean：初始化bean；AbstractAutowireCapableBeanFactory#doCreateBean(final String beanName, final RootBeanDefinition mbd, final Object[] args) ==> initializeBean(beanName, exposedObject, mbd); 下述方法都是initializeBean()中的方法.

  * invokeAwareMethods()：处理Aware接口的方法回调. 

    ```java
    invokeAwareMethods ==>

    AbstractAdvisorAutoProxyCreator#setBeanFactory() ==> 

    AnnotationAwareAspectJAutoProxyCreator#initBeanFactory(ConfigurableListableBeanFactory beanFactory) ==> 

    this.aspectJAdvisorsBuilder = new AnnotationAwareAspectJAutoProxyCreator.BeanFactoryAspectJAdvisorsBuilderAdapter(beanFactory, this.aspectJAdvisorFactory);
    ```

  * applyBeanPostProcessorsBeforeInitialization()：应用后置处理器的postProcessBeforeInitialization()

  * invokeInitMethods()；执行自定义的初始化方法

  * applyBeanPostProcessorsAfterInitialization()；执行后置处理器的postProcessAfterInitialization()

* BeanPostProcessor(以AnnotationAwareAspectJAutoProxyCreator为例)创建成功

* 把这个BeanPostProcessor注册到BeanFactory中；

  * PostProcessorRegistrationDelegate#registerBeanPostProcessors==> beanFactory.addBeanPostProcessor(postProcessor);

> AnnotationAwareAspectJAutoProxyCreator 是 InstantiationAwareBeanPostProcessor 类型的后置处理器



#### 继续完成其他Bean的BeanFactory初始化工作

创建剩下的单实例bean

```java
AbstractApplicationContext#finishBeanFactoryInitialization(beanFactory); 
```

1）遍历获取容器中所有的Bean，依次创建对象getBean(beanName);

getBean -> doGetBean() -> getSingleton() -> 获取单实例对象, 没有的话就会创建

2）创建bean

先从缓存中获取当前bean，如果能获取到，说明bean是之前被创建过的，直接使用，否则再创建；只要创建好的Bean都会被缓存起来(单实例的原理)

createBean(); 创建bean

* resolveBeforeInstantiation(beanName, mbdToUse); 解析BeforeInstantiation. 希望后置处理器在此能返回一个代理对象；如果能返回代理对象, 就使用它，如果不能就创建doCreateBean(), 也就是第二步.

  ```java
  AbstractAutowireCapableBeanFactory#resolveBeforeInstantiation(String beanName, RootBeanDefinition mbd) ==> 

  // 看是否能获得一个代理对象
  bean = applyBeanPostProcessorsBeforeInstantiation()：
  // 拿到所有后置处理器，如果是实现了InstantiationAwareBeanPostProcessor接口的后置处理器;
  // 就执行postProcessBeforeInstantiation方法
  if (bean != null) {
  	bean = applyBeanPostProcessorsAfterInitialization(bean, beanName);
  }

  ==> applyBeanPostProcessorsBeforeInstantiation

  protected Object applyBeanPostProcessorsBeforeInstantiation(Class<?> beanClass, String beanName) {
  	// 拿到所有的后置处理器
  	for (BeanPostProcessor bp : getBeanPostProcessors()) {
  		// 如果某个后置处理器实现了 InstantiationAwareBeanPostProcessor 接口
  		// 就会调用 postProcessBeforeInstantiation 方法
  		// ==>
  		// AbstractAutoProxyCreato#postProcessBeforeInstantiation(Class<?> beanClass, String beanName)
  		if (bp instanceof InstantiationAwareBeanPostProcessor) {
  			InstantiationAwareBeanPostProcessor ibp = (InstantiationAwareBeanPostProcessor) bp;				
  			Object result = ibp.postProcessBeforeInstantiation(beanClass, beanName);
  			if (result != null) {
  				return result;
  			}			
  		}
  	}
  	return null;
  }
  ```

* doCreateBean(beanName, mbdToUse, args); 真正的去创建一个bean实例

> BeanPostProcessor是在Bean对象创建完成, 初始化前后调用的
>
> InstantiationAwareBeanPostProcessor是在创建Bean实例之前, 先尝试用后置处理器返回代理对象的
>
> ```java
> public interface InstantiationAwareBeanPostProcessor extends BeanPostProcessor {}
> ```

##### 总结

- AnnotationAwareAspectJAutoProxyCreator 实现了 InstantiationAwareBeanPostProcessor 接口
- AnnotationAwareAspectJAutoProxyCreator 是 InstantiationAwareBeanPostProcessor 类型的后置处理器
- AnnotationAwareAspectJAutoProxyCreator 在所有bean创建之前会拦截，会调用InstantiationAwareBeanPostProcessor#postProcessBeforeInstantiation()
- AnnotationAwareAspectJAutoProxyCreator 会在任何bean创建之前, 先尝试返回bean的代理实例对象



### postProcessBeforeInstantiation

在容器中的每一个bean创建之前，都会调用postProcessBeforeInstantiation()方法. 我们现在关心的是 MathCalculator和LogAspect 的创建.

1）判断当前bean是否在advisedBeans中(以key(bean名字)-value(true / false)记录哪些bean要增强) 第一次的时候, 肯定不在其中, 因为还没有添加进advisedBeans中.

2）判断当前bean是否是基础类型. 比如Advice、Pointcut、Advisor、AopInfrastructureBean，或者是否是切面（是否加了@Aspect注解）

3）是否需要跳过
	1）获取候选的增强器（切面里面的通知方法,logStart, logEnd...）【List<Advisor> candidateAdvisors】

​	就是把每一个通知方法进行包装, 变成了增强器(Advisor)

​	每一个封装的通知方法的增强器是 InstantiationModelAwarePointcutAdvisor；

​	判断每一个增强器是否是 AspectJPointcutAdvisor 类型的；我们的类型是InstantiationModelAwarePointcutAdvisor

​	2）到父类, 永远会返回false. 也就是要跳过了.

接下来就要创建业务逻辑对象了. 创建好之后, 会调用postProcessAfterInitialization方法 

### postProcessAfterInitialization

判断对象是否需要被包装, 如果需要, 就执行下面的步骤创建代理对象

1）获取当前bean(业务逻辑类)的所有增强器（通知方法）  Object[]  specificInterceptors

​	1、找到候选的所有的增强器（找哪些通知方法是需要切入当前bean方法的）

​	2、获取到能在bean使用的增强器。

​	3、给增强器排序

2）保存当前bean, 在advisedBeans中, 表示这个Bean已经被处理过了.

3）如果当前bean需要增强，创建当前bean的代理对象；

​	1）获取所有增强器（通知方法）保存到proxyFactory

​	2）创建代理对象：**Spring自动决定**(如果类实现了接口, 就用jdk动态代理)

​		JdkDynamicAopProxy(config);jdk动态代理；

​		ObjenesisCglibAopProxy(config);cglib的动态代理；

4）、最终的结果是给容器中返回当前组件使用cglib增强了的代理对象；

5）、以后容器中获取到的就是这个组件的代理对象，执行目标方法的时候，代理对象就会执行通知方法的流程；

### 目标方法的执行

目前, 容器中已经保存了组件的代理对象（cglib增强后的对象），这个对象里面保存了很多详细信息（比如所有的增强器，目标对象(被代理的对象)）；

首先来到, CglibAopProxy.intercept(); 拦截目标方法的执行

根据ProxyFactory对象获取**将要执行的目标方法**的拦截器链；

```java
// this就是ProxyFactory
List<Object> chain = this.advised.getInterceptorsAndDynamicInterceptionAdvice(method, targetClass);
```

* 先创建一个List, 当成拦截器链, List<Object> interceptorList, 并指定这个List的长度. 包括一个默认的ExposeInvocationInterceptor, 和剩下的全部增强器.
* 接着遍历所有的增强器，如果需要切入(实现了PointcutAdvidor, 则将Advisor类型转为Interceptor类型；registry.getInterceptors(advisor);
  * 将增强器转为List<MethodInterceptor>；如果是MethodInterceptor，直接加入到集合中, 如果不是，使用AdvisorAdapter将增强器转为MethodInterceptor；转换完成返回MethodInterceptor数组；

如果没有拦截器链，直接执行目标方法; 拦截器链**（每一个通知方法, 被包装为方法拦截器，利用MethodInterceptor机制）**

如果有拦截器链，把需要执行的目标对象，目标方法，拦截器链等信息传入, 创建一个 **CglibMethodInvocation** 对象，并调用其proceed方法. Object retVal =  mi.proceed();

> 在目标方法执行之前, 会把增强器Advisor转成MethodInterceptor, 组成拦截器链. 最终创建CglibMethodInvocation, 然后调用其proceed方法.

### 拦截器链的触发调用过程;

1) 使用currentInterceptorIndex来记录拦截器的索引(默认值是-1). 如果没有拦截器执行, 则执行目标方法，或者拦截器的索引和拦截器数组长度-1大小一样（指定到了最后一个拦截器）则执行目标方法, 调用invoke方法, 传入this作为参数, this就是CglibMethodInvocation对象, 其实就是执行CglibMethodInvocation.proceed()方法；

> 每次执行proceed, 索引都会自增, 也就是可以拿到下一个拦截器.

2) 链式获取每一个拦截器，拦截器执行invoke方法，每一个拦截器等待下一个拦截器执行完成返回以后再来执行；**拦截器链的机制，保证通知方法与目标方法的执行顺序；**

### 总结

```java
1）@EnableAspectJAutoProxy 开启AOP功能
2）@EnableAspectJAutoProxy 会给容器中注册一个组件 AnnotationAwareAspectJAutoProxyCreator
3）AnnotationAwareAspectJAutoProxyCreator是一个后置处理器；
4）容器的创建流程：
	1）、registerBeanPostProcessors（）注册后置处理器；创建AnnotationAwareAspectJAutoProxyCreator对象
	2）、finishBeanFactoryInitialization（）初始化剩下的单实例bean
		1）创建业务逻辑组件和切面组件
		2）AnnotationAwareAspectJAutoProxyCreator拦截组件的创建过程
		3）组件创建完之后，判断组件是否需要增强
		是：切面的通知方法，包装成增强器（Advisor）; 给业务逻辑组件创建一个代理对象（cglib）；
5）、执行目标方法：
	1）代理对象执行目标方法
	2）CglibAopProxy.intercept()；
		1）、得到目标方法的拦截器链（增强器包装成拦截器MethodInterceptor）
		2）、利用拦截器的链式机制，依次进入每一个拦截器进行执行；
		3）、效果：
			正常执行：前置通知-》目标方法-》后置通知-》返回通知
			出现异常：前置通知-》目标方法-》后置通知-》异常通知
```



## 其他原理

### BeanPostProcessor 接口

```java
Bean的后置处理器，bean创建对象初始化前后进行拦截工作的

BeanFactoryPostProcessor: BeanFactory对象的后置处理器
	在BeanFactory标准初始化之后调用，来定制和修改BeanFactory的内容；
	
	使用时机: 所有的bean定义已经保存加载到beanFactory，但是bean的实例还未创建时, 调用该接口实现类的postProcessBeanFactory方法

BeanFactoryPostProcessor的原理:
	1. 首先创建ioc容器, 调用AbstractApplicationContext#refresh()方法
	2. refresh()方法中有一步是 invokeBeanFactoryPostProcessors(beanFactory);
	3. 在类PostProcessorRegistrationDelegate中, 直接在BeanFactory中找到所有类型是BeanFactoryPostProcessor的组件，并执行他们的postProcessBeanFactory方法. 这一步在初始化创建其他组件前面执行
```



### BeanDefinitionRegistryPostProcessor 接口

```java
BeanDefinitionRegistryPostProcessor extends BeanFactoryPostProcessor {
	// BeanDefinitionRegistry 是Bean定义信息的保存中心
	// BeanFactory就是按照BeanDefinitionRegistry保存的每一个Bean定义创建Bean实例的
	postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry);
}

使用时机: 在所有bean定义信息将要被加载，bean实例还未创建的；

结论: 
	优先于BeanFactoryPostProcessor执行；
	使用场景是: 利用BeanDefinitionRegistryPostProcessor给容器中再额外添加一些组件；

原理：
	1. 首先创建ioc容器, 调用AbstractApplicationContext#refresh()方法
	2. refresh()方法中有一步是 invokeBeanFactoryPostProcessors(beanFactory);
	3. 从容器中获取到所有的实现了BeanDefinitionRegistryPostProcessor接口的组件。
	4. 依次触发所有实现了BeanDefinitionRegistryPostProcessor接口的组件的postProcessBeanDefinitionRegistry()方法
	5. 再来触发实现了BeanDefinitionRegistryPostProcessor接口的组件的postProcessBeanFactory()方法
	6. 注意, 4, 5步执行的都是实现了BeanDefinitionRegistryPostProcessor接口的组件的方法
	6. 再来从容器中找到实现了BeanFactoryPostProcessor接口的组件；依次触发postProcessBeanFactory()方法
```

### ApplicationListener 接口

```java
监听容器中发布的事件, 只要事件发生, 就执行回调, 完成事件的处理. 是一种事件驱动模型的开发

public interface ApplicationListener<E extends ApplicationEvent>
	泛型就是要监听的事件. 这里是监听 ApplicationEvent 及其下面的子事件；

测试:
	单纯的写一个类实现ApplicationListener, 在其onApplicationEvent(ApplicationEvent event)方法中, 打印参数中的event
	然后启动spring容器, 再关闭spring容器.
	则会收到两个事件. 分别是 ContextRefreshedEvent, ContextClosedEvent

步骤：
	1. 写一个监听器（ApplicationListener实现类）来监听某个事件（ApplicationEvent及其子类）
	2. 把监听器加入到容器
	3. 只要容器中有相关事件的发布，就能监听到这个事件；
		ContextRefreshedEvent：容器刷新完成（所有bean都完全创建）会发布这个事件；
		ContextClosedEvent：关闭容器会发布这个事件；
	4. 发布一个事件：
		applicationContext.publishEvent(new ApplicationEvent(new String("新发布的事件")){})；
	5. 由于写过了一个类实现ApplicationListener, 在在其onApplicationEvent(ApplicationEvent event)方法中, 打印参数中的event, 所以在控制台可以看到我们刚刚新发布的事件.
	(测试类的全类目$1[source=新发布的事件])

也可以用注解 @EventListener 加在某一个方法上
public class UserService {

	@EventListener(classes = {ApplicationEvent.class})
	public void listen(ApplicationEvent applicationEvent) {
		print(applicationEvent);
	}
}
原理：
	使用EventListenerMethodProcessor处理器来解析方法上的@EventListener
	EventListenerMethodProcessor 实现了 SmartInitializingSingleton接口
```

###  事件发布原理

```java
0. 首先, 创建容器, 然后调用容器的refresh()方法. 在refresh()方法的最后, 有一个finishRefresh()方法, 该方法中, 会发布一个事件
		publishEvent(new ContextRefreshedEvent(this));
	1. AbstractApplicationContext#publishEvent((Object event, ResolvableType eventType))
 	// Multicast right now if possible - or lazily once the multicaster is initialized
	if (this.earlyApplicationEvents != null) {
		this.earlyApplicationEvents.add(applicationEvent);
	}
	else {
		getApplicationEventMulticaster().multicastEvent(applicationEvent, eventType);
	}
	2. 获取事件的多播器getApplicationEventMulticaster（派发器）：AbstractApplicationContext#getApplicationEventMulticaster()
	3. 调用SimpleApplicationEventMulticaster#multicastEvent方法, 派发事件
		@Override
	public void multicastEvent(final ApplicationEvent event, ResolvableType eventType) {
		ResolvableType type = (eventType != null ? eventType : resolveDefaultEventType(event));
		for (final ApplicationListener<?> listener : getApplicationListeners(event, type)) {
			Executor executor = getTaskExecutor();
			if (executor != null) {
				executor.execute(new Runnable() {
					@Override
					public void run() {
						invokeListener(listener, event);
					}
				});
			}
			else {
				invokeListener(listener, event);
			}
		}
	}
		首先是获取到所有的ApplicationListener
			for (final ApplicationListener<?> listener : getApplicationListeners(event, type)) {}
		如果有Executor，可以支持使用Executor进行异步派发；
			Executor executor = getTaskExecutor();
		否则，同步的方式直接执行listener方法；
			invokeListener(listener, event); ==>
			doInvokeListener ==> 
			listener.onApplicationEvent(event);
		拿到实现了ApplicationEventListener接口的实现类, 回调onApplicationEvent方法；
```

#### 事件多播器(派发器)

```java
首先, 创建容器, 然后调用容器的refresh()方法. 在refresh()方法中, 有一个叫 initApplicationEventMulticaster() 的方法, 来初始化ApplicationEventMulticaster；

先去容器中找有没有id="applicationEventMulticaster"的组件, 如果有, 就从容器中拿到这个对象
如果没有, 就自己创建这个对象
	this.applicationEventMulticaster = new SimpleApplicationEventMulticaster(beanFactory);
并且加入到容器中，我们就可以在其他组件要派发事件，自动注入这个applicationEventMulticaster；
```

#### 容器如何获取所有的监听器

```java
创建容器, 然后调用容器的refresh()方法. 在refresh()方法中, 有一个叫 registerListeners() 的方法, 从容器中拿到所有的监听器，把他们注册到applicationEventMulticaster中.
	String[] listenerBeanNames = getBeanNamesForType(ApplicationListener.class, true, false);
	//将listener注册到ApplicationEventMulticaster中
	getApplicationEventMulticaster().addApplicationListenerBean(listenerBeanName);
```

### SmartInitializingSingleton 接口

```java
有一个方法是 afterSingletonsInstantiated();
作用时机: 所有单实例Bean初始化之后触发, 类似于容器刷新

1. 创建ioc容器, 并refresh()；
2. 其中有一个 finishBeanFactoryInitialization(beanFactory) 方法, 来初始化剩下的单实例bean

AbstractApplicationContext#finishBeanFactoryInitialization(ConfigurableListableBeanFactory beanFactory) ==> beanFactory.preInstantiateSingletons();
	先创建所有的单实例bean；用getBean();
	获取所有创建好的单实例bean，判断是否有实现了SmartInitializingSingleton接口的类；如果是, 就调用其afterSingletonsInstantiated()方法
```

