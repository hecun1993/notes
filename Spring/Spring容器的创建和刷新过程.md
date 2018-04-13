## Spring容器的创建和刷新过程

1到4步为关于BeanFactory的创建及预准备方法

### 1. AbstractApplicationContext#prepareRefresh() 

**刷新前的预处理**

1. initPropertySources() 初始化一些属性设置; 子类可以自定义个性化的属性设置方
2. getEnvironment().validateRequiredProperties();检验属性的合法
3. earlyApplicationEvents= new LinkedHashSet<ApplicationEvent>();保存容器中的一些早期的事件

### 2. AbstractApplicationContext#obtainFreshBeanFactory() 

**获取BeanFactory**

1. refreshBeanFactory(); 刷新【实际上是创建】BeanFactory

  创建了一个 this.beanFactory = new DefaultListableBeanFactory();

  同时设置了id

2. getBeanFactory(); 返回刚才由GenericApplicationContext创建的BeanFactory对象

3. 将创建的BeanFactory【DefaultListableBeanFactory】返回；

### 3. AbstractApplicationContext#prepareBeanFactory(beanFactory); 

**BeanFactory的预准备工作（对BeanFactory进行一些设置）**

1. 设置BeanFactory的类加载器, 支持表达式操作的解析器...
2. 添加部分的BeanPostProcessor【ApplicationContextAwareProcessor】
3. 设置要忽略的自动装配接口 EnvironmentAware. EmbeddedValueResolverAware. xxx；
4. 注册可以解析的自动装配BeanFactory. ResourceLoader. ApplicationEventPublisher. ApplicationContext；
  这样我们能直接在任何组件中自动注入这些组件.
5. 添加BeanPostProcessor【ApplicationListenerDetector】
6. 添加编译时需要的的AspectJ支持；
7. 给BeanFactory中注册一些能用的组件；
  * environment【ConfigurableEnvironment】
  * systemProperties【Map<String, Object>】 
  * systemEnvironment【Map<String, Object>】

### 4. postProcessBeanFactory(beanFactory) 

**BeanFactory准备工作完成后进行的后置处理工作**

子类通过重写这个方法来在BeanFactory创建并预准备完成以后做进一步的设置

### 5. invokeBeanFactoryPostProcessors(beanFactory)

执行BeanFactoryPostProcessor的方法；

```java
BeanFactoryPostProcessor：BeanFactory的后置处理器。在BeanFactory标准初始化(就是前面的4步)之后执行的；
	
	两个重要的接口：BeanFactoryPostProcessor, 及其子接口 BeanDefinitionRegistryPostProcessor
		1. 执行BeanFactoryPostProcessor的方法；
		
			先执行BeanDefinitionRegistryPostProcessor
				1. 获取所有的BeanDefinitionRegistryPostProcessor；
				2. 先执行实现了PriorityOrdered优先级接口的BeanDefinitionRegistryPostProcessor. 
					postProcessor.postProcessBeanDefinitionRegistry(registry)
				3. 再执行实现了Ordered顺序接口的BeanDefinitionRegistryPostProcessor；
					postProcessor.postProcessBeanDefinitionRegistry(registry)
				4. 最后执行没有实现任何优先级或者是顺序接口的BeanDefinitionRegistryPostProcessors；
					postProcessor.postProcessBeanDefinitionRegistry(registry)
				
		
			再执行BeanFactoryPostProcessor的方法
				1. 获取所有的BeanFactoryPostProcessor
				2. 先执行实现了PriorityOrdered优先级接口的BeanFactoryPostProcessor. 
					postProcessor.postProcessBeanFactory()
				3. 再执行实现了Ordered顺序接口的BeanFactoryPostProcessor；
					postProcessor.postProcessBeanFactory()
				4. 最后执行没有实现任何优先级或者是顺序接口的BeanFactoryPostProcessor；
					postProcessor.postProcessBeanFactory()
```

### 6. registerBeanPostProcessors(beanFactory) 

注册BeanPostProcessor（Bean的后置处理器）不执行

```java
拦截整个Bean的创建过程, 在Bean初始化前后做一些事
	
	不同接口类型的BeanPostProcessor, 在Bean创建前后的执行时机是不一样的
		BeanPostProcessor 接口
			DestructionAwareBeanPostProcessor 接口
			InstantiationAwareBeanPostProcessor 接口
			SmartInstantiationAwareBeanPostProcessor 接口
			MergedBeanDefinitionPostProcessor【internalPostProcessors】. 
	
	1. 获取所有的 BeanPostProcessor 后置处理器都默认可以通过PriorityOrdered. Ordered接口来指定执行的优先级
	2. 先注册PriorityOrdered优先级接口的BeanPostProcessor；把每一个BeanPostProcessor添加到BeanFactory中
		beanFactory.addBeanPostProcessor(postProcessor);
	3. 再注册Ordered接口的BeanPostProcessor
	4. 最后注册没有实现任何优先级接口的BeanPostProcessor
	5. 最终注册MergedBeanDefinitionPostProcessor；
	6. 然后注册了一个ApplicationListenerDetector；将来在Bean创建完成后, 检查是否是ApplicationListener，如果是, 则
		applicationContext.addApplicationListener((ApplicationListener<?>) bean);
```

### 7. initMessageSource()

初始化MessageSource组件

```java
做国际化功能；消息绑定，消息解析
	1. 获取BeanFactory
	2. 看容器中是否有id为messageSource的，类型是MessageSource的组件
		如果有, 则赋值给messageSource
		如果没有, 则创建一个DelegatingMessageSource
			MessageSource：取出国际化配置文件中的某个key的值；能按照区域信息获取；
	3. 把创建好的MessageSource注册在容器中，以后获取国际化配置文件的值的时候，可以自动注入MessageSource；
		beanFactory.registerSingleton(MESSAGE_SOURCE_BEAN_NAME, this.messageSource);	
		调用以下方法
		MessageSource.getMessage(String code, Object[] args, String defaultMessage, Locale locale);
```

### 8. initApplicationEventMulticaster() 

初始化事件派发器

1. 获取BeanFactory
2. 从BeanFactory中获取名称为applicationEventMulticaster的ApplicationEventMulticaster；
3. 如果上一步没有配置；则创建一个SimpleApplicationEventMulticaster
4. 将创建的ApplicationEventMulticaster添加到BeanFactory中，以后其他组件可以直接自动注入这个事件派发器.

### 9. onRefresh()

留给子容器（子类）

子类重写这个方法，在容器刷新的时候可以自定义逻辑；

### 10. registerListeners() 

给容器中将所有项目里面的ApplicationListener注册进来；

1. 从容器中拿到所有的ApplicationListener
2. 将每个监听器添加到事件派发器中；
  getApplicationEventMulticaster().addApplicationListenerBean(listenerBeanName);
3. 派发之前步骤产生的事件；

### 11. finishBeanFactoryInitialization(beanFactory) 

初始化所有剩下的单实例bean

```java
1. beanFactory.preInstantiateSingletons() 初始化后剩下的单实例bean
		1. 获取容器中的所有Bean，依次进行初始化和创建对象
		2. 获取Bean的定义信息；RootBeanDefinition
		3. 如果Bean不是抽象的，是单实例的，是懒加载:
			1. 判断是否是FactoryBean；是否是实现FactoryBean接口的Bean；如果是, 会调用getObject()方法创建对象.
			2. 不是工厂Bean。利用getBean(beanName) 创建对象
				0. getBean(beanName)； 实际上就是调用applicationContext.getBean(); 方法
				1. doGetBean(name, null, null, false);
				2. 先获取缓存中保存的单实例Bean。如果能获取到说明这个Bean之前被创建过（所有创建过的单实例Bean都会被缓存起来）
					private final Map<String, Object> singletonObjects = new ConcurrentHashMap<String, Object>(256);
					从上述Map中获取
				3. 缓存中获取不到，开始Bean的创建对象流程；
				4. 标记当前bean已经被创建, 预防在多线程下, 某个单实例Bean会被多次创建
				5. 获取Bean的定义信息；
				6. 获取当前Bean依赖的其他Bean; 如果有依赖的Bean, 也就是depend-on属性配置的Bean, 则调用getBean()把依赖的Bean先创建出来；
				
				7. 启动单实例Bean的创建流程
					getSingleton(beanName, new ObjectFactory<Object>() {
						createBean(beanName, mdb, args);
					})

					1. createBean(beanName, mbd, args);

					2. 先拿到Bean的定义信息, 解析要创建的Bean的类型(比如就是一个普通类型的Bean, 不需要动态代理)
						// 给BeanPostProcessor一个机会, 让BeanPostProcessor先尝试返回代理对象
						Object bean = resolveBeforeInstantiation(beanName, mbdToUse); 
						
						1. 如果某个Bean实现了InstantiationAwareBeanPostProcessor接口, 则会返回代理对象.
						2. 每个Bean在创建的时候, 都会先触发：postProcessBeforeInstantiation()
						3. 如果有返回值：触发postProcessAfterInitialization() 返回代理对象
					
					3. 如果前面的InstantiationAwareBeanPostProcessor没有返回代理对象；调用第四步
					
					4. Object beanInstance = doCreateBean(beanName, mbdToUse, args) 创建Bean
						1. 【创建Bean实例】: createBeanInstance(beanName, mbd, args);
						 		利用工厂方法或者对象的构造器创建出Bean实例
						2. applyMergedBeanDefinitionPostProcessors(mbd, beanType, beanName);
						 	如果实现了MergedBeanDefinitionPostProcessor接口, 则会调用MergedBeanDefinitionPostProcessor的postProcessMergedBeanDefinition(mbd, beanType, beanName);
						3. 【Bean属性赋值】populateBean(beanName, mbd, instanceWrapper);
						 	赋值之前：
						 	1. 拿到所有实现了InstantiationAwareBeanPostProcessor接口的后置处理器；
						 		postProcessAfterInstantiation()；
						 	2. 拿到所有实现了InstantiationAwareBeanPostProcessor接口的后置处理器；执行
						 		postProcessPropertyValues()；方法, 拿到属性值.
						 	=====赋值之前=====
						 	3. 应用Bean属性的值；为属性利用setter方法等进行赋值；
						 		applyPropertyValues(beanName, mbd, bw, pvs);
						4. 【Bean初始化】initializeBean(beanName, exposedObject, mbd);
						 	1. 【执行Aware接口方法】invokeAwareMethods(beanName, bean); 执行xxxAware接口的方法
						 		BeanNameAware \ BeanClassLoaderAware \ BeanFactoryAware
						 	2. 【执行后置处理器初始化之前】applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);
						 		BeanPostProcessor.postProcessBeforeInitialization（）;
						 	3. 【执行初始化方法】invokeInitMethods(beanName, wrappedBean, mbd);
						 		1. 是否是InitializingBean接口的实现；执行接口规定的初始化方法；
						 		2. 是否自定义初始化方法；
						 	4. 【执行后置处理器初始化之后】applyBeanPostProcessorsAfterInitialization
						 		BeanPostProcessor.postProcessAfterInitialization()；
						 5. 注册Bean的销毁方法；
					5. 将创建的Bean添加到缓存中singletonObjects；
				
				ioc容器就是Map, 里面保存了单实例Bean, 环境信息
		
		所有Bean都利用getBean创建完成以后
			检查所有的Bean是否是SmartInitializingSingleton接口的；如果是；就执行afterSingletonsInstantiated()；
```

### 12. finishRefresh() 

完成BeanFactory的初始化创建工作；IOC容器就创建完成；

```java
1. initLifecycleProcessor(); 初始化和生命周期有关的后置处理器；LifecycleProcessor
	默认从容器中找是否有lifecycleProcessor的组件【LifecycleProcessor】；
	如果没有new DefaultLifecycleProcessor(); 加入到容器；
	
	写一个LifecycleProcessor的实现类，可以在BeanFactory的生命周期出进行拦截调用
		void onRefresh();
		void onClose();	
2. 	getLifecycleProcessor().onRefresh();
	拿到前面定义的生命周期处理器（监听BeanFactory的生命周期）, 回调 onRefresh()方法
3. publishEvent(new ContextRefreshedEvent(this)); 发布容器刷新完成事件；
4. liveBeansView.registerApplicationContext(this);
```

### 总结

```java
1. Spring容器在启动的时候，先会保存所有注册进来的Bean的定义信息；
	1. xml注册bean；<bean>
	2. 注解注册Bean；@Service. @Component. @Bean. 
2. Spring容器会合适的时机创建这些Bean
	1. 用到这个bean的时候；利用getBean创建bean；创建好以后保存在容器中；
	2. 统一创建剩下所有的bean的时候；finishBeanFactoryInitialization()；
3. 后置处理器；BeanPostProcessor
	1. 每一个bean创建完成，都会使用各种后置处理器进行处理；来增强bean的功能；
		AutowiredAnnotationBeanPostProcessor: 处理自动注入
		AnnotationAwareAspectJAutoProxyCreator: 来做AOP功能；
		AsyncAnnotationBeanPostProcessor
4. 事件驱动模型；
	ApplicationListener；事件监听；
	ApplicationEventMulticaster；事件派发：
```

