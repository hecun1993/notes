## Servlet 3.0

### @WebServlet

```java
package com.atguigu.servlet;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/hello")
// 括号中的参数就是Servlet的访问路径
public class HelloServlet extends HttpServlet {
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		//super.doGet(req, resp);
		System.out.println(Thread.currentThread()+" start...");
		try {
			sayHello();
		} catch (Exception e) {
			e.printStackTrace();
		}
		resp.getWriter().write("hello...");
		System.out.println(Thread.currentThread()+" end...");
	}
	
	public void sayHello() throws Exception{
		System.out.println(Thread.currentThread() + " processing...");
		Thread.sleep(3000);
	}
}
```



### ServletContainerInitializer

1. 容器在启动应用的时候，会扫描当前应用里面每一个jar包的 ServletContainerInitializer 接口的实现, 再扫描当前应用每一个jar包里面的 META-INF/services/javax.servlet.ServletContainerInitializer
  指定的实现类;

> 首先要提供ServletContainerInitializer的实现类；其次, 这个实现类必须绑定在类路径下的META-INF/services/javax.servlet.ServletContainerInitializer 文件中. 文件的内容就是ServletContainerInitializer实现类的全类名；

2. 然后启动并运行这个实现类的onStartup()方法. 该方法有两个参数

   * 一个是: ServletContext, 每一个web应用对应一个ServletContext
   * 一个是: Set<Class<?>>, 首先, 给 ServletContainerInitializer 接口的实现类上添加注解 

   ​	@HandleTypes(value = {HelloService.class})

   * 在容器启动的时候, 会将@HandlesTypes指定的类型的子类型（实现类，子接口, 抽象类）传入Set<Class<?>>中, 该参数可以在onStartup()方法中使用. 
     * 比如可以在容器启动后, 就打印这些参数. 或者用反射创建对象.



### 使用ServletContext注册Web组件（Servlet、Filter、Listener）

- 如果是我们自己写的组件, 可以用@WebServlet, @WebFilter, @WebListener来修饰.
- 但如果是第三方组件, 我们必须配置到ServletContext中, 无法加上述注解. 所以需要直接向ServletContext中注册三大组件.

#### 示例

##### UserServlet

```java
package com.atguigu.servlet;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class UserServlet extends HttpServlet {
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		resp.getWriter().write("tomcat...");
	}
}
```

##### UserListener

```java
package com.atguigu.servlet;

import javax.servlet.ServletContext;
import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

/**
 * 监听项目的启动和停止
 */
public class UserListener implements ServletContextListener {

	//监听ServletContext销毁
	@Override
	public void contextDestroyed(ServletContextEvent arg0) {
		System.out.println("UserListener...contextDestroyed...");
	}

	//监听ServletContext启动初始化
	@Override
	public void contextInitialized(ServletContextEvent arg0) {
		ServletContext servletContext = arg0.getServletContext();
		System.out.println("UserListener...contextInitialized...");
	}
}
```

##### UserFilter

```java
package com.atguigu.servlet;

import java.io.IOException;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

public class UserFilter implements Filter {

	@Override
	public void destroy() {
	}

	@Override
	public void doFilter(ServletRequest arg0, ServletResponse arg1, FilterChain arg2)
			throws IOException, ServletException {
		// 过滤请求
		System.out.println("UserFilter...doFilter...");
		// 放行
		arg2.doFilter(arg0, arg1);
		
	}

	@Override
	public void init(FilterConfig arg0) throws ServletException {
	}
}
```

##### MyServletContainerInitializer

```java
package com.atguigu.servlet;

import java.util.EnumSet;
import java.util.Set;

import javax.servlet.DispatcherType;
import javax.servlet.FilterRegistration;
import javax.servlet.ServletContainerInitializer;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.ServletRegistration;
import javax.servlet.annotation.HandlesTypes;

import com.atguigu.service.HelloService;

//容器启动的时候会将@HandlesTypes指定的这个类型下面的子类（实现类，子接口等）传递给onStartup方法中的Set<Class<?>>
@HandlesTypes(value = {HelloService.class})
public class MyServletContainerInitializer implements ServletContainerInitializer {

    /**
     * 应用启动的时候，会运行onStartup方法；
     
     * Set<Class<?>> arg0：感兴趣的类型的所有子类型；
     * ServletContext arg1:代表当前Web应用的ServletContext；一个Web应用一个ServletContext；
     
     * 1）、使用ServletContext注册Web组件（Servlet、Filter、Listener）
     * 2）、使用编码的方式，在项目启动的时候给ServletContext里面添加组件；
     * 必须在项目启动的时候来添加；
     * 	通过ServletContainerInitializer得到的ServletContext；
     * 	通过ServletContextListener的contextInitialized方法得到的ServletContext；
     */
    @Override
    public void onStartup(Set<Class<?>> arg0, ServletContext sc) throws ServletException {
        System.out.println("感兴趣的类型：");
        for (Class<?> claz : arg0) {
            System.out.println(claz);
        }

        // 注册组件  ServletRegistration  
        // 返回值是ServletRegistration.Dynamic
        ServletRegistration.Dynamic servlet = sc.addServlet("userServlet", new UserServlet());
        // 配置servlet的映射信息
        servlet.addMapping("/user");

        // 注册Listener
        sc.addListener(UserListener.class);

        // 注册Filter  FilterRegistration
        // 返回值是FilterRegistration.Dynamic
        FilterRegistration.Dynamic filter = sc.addFilter("userFilter", UserFilter.class);
        // 配置Filter的映射信息
        filter.addMappingForUrlPatterns(EnumSet.of(DispatcherType.REQUEST), true, "/*");
    }
}
```



### 使用注解开发Spring mvc

#### pom.xml

在pom文件中, 引入javax.servlet 3.0 和 spring-webmvc

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.atguigu</groupId>
    <artifactId>springmvc-annotation</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>war</packaging>

    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-webmvc</artifactId>
            <version>4.3.11.RELEASE</version>
        </dependency>

        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>servlet-api</artifactId>
            <version>3.0-alpha-1</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-war-plugin</artifactId>
                <version>2.4</version>
                <configuration>
                    <failOnMissingWebXml>false</failOnMissingWebXml>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

#### 利用 ServletContainerInitializer 的方式一

```java
public class MyWebApplicationInitializer implements WebApplicationInitializer {
    @Override
    public void onStartup(ServletContext servletCxt) {

        // Load Spring web application configuration
        AnnotationConfigWebApplicationContext ac = new AnnotationConfigWebApplicationContext();
        ac.register(AppConfig.class);
        ac.refresh();

        // Create and register the DispatcherServlet
        DispatcherServlet servlet = new DispatcherServlet(ac);
        ServletRegistration.Dynamic registration = servletCxt.addServlet("app", servlet);
        registration.setLoadOnStartup(1);
        registration.addMapping("/app/*");
    }
}
```

就类似于原先的xml

```xml
<web-app>
	先利用监听器, 启动Spring容器, 这是父容器.
    <listener>
        <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
    </listener>

    <context-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>/WEB-INF/app-context.xml</param-value>
    </context-param>

    再启动Spring mvc这个子容器
    <servlet>
        <servlet-name>app</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value></param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>

    <servlet-mapping>
        <servlet-name>app</servlet-name>
        <url-pattern>/app/*</url-pattern>
    </servlet-mapping>

</web-app>
```

#### 利用 ServletContainerInitializer 的方式二

利用注解开发, 容器在启动时, 首先从maven依赖中, 找到spring-web的jar依赖, 找到其中的

META-INF/services/javax.servlet.ServletContainerInitializer

```file
org.springframework.web.SpringServletContainerInitializer
```

web容器在启动的时候，会扫描每个jar包下的META-INF/services/javax.servlet.ServletContainerInitializer文件, 并加载文件中的类. 

SpringServletContainerInitializer

```java
@HandlesTypes({WebApplicationInitializer.class})
public class SpringServletContainerInitializer implements ServletContainerInitializer {}

// 说明这个类关心的是WebApplicationInitializer的子类型, 并放在onStartup方法中.
```

然后加载这个文件指定的类SpringServletContainerInitializer, 这个类感兴趣的是(@HandlesTypes({WebApplicationInitializer.class})) WebApplicationInitializer 接口的下的所有组件

然后为WebApplicationInitializer组件的子类型创建对象

总共有三个实现类

```java
1）、AbstractContextLoaderInitializer：
	创建根容器；createRootApplicationContext()；
2）、AbstractDispatcherServletInitializer：
    创建一个web的ioc容器；createServletApplicationContext();
    创建了DispatcherServlet；createDispatcherServlet()；
    将创建的DispatcherServlet添加到ServletContext中；
        getServletMappings();
3）、AbstractAnnotationConfigDispatcherServletInitializer：注解方式配置的DispatcherServlet初始化器, 实际上是重写了父类的方法.
    创建根容器：createRootApplicationContext(). 在创建过程中, 通过getRootConfigClasses();传入一个配置. 这个方法是抽象的, 我们可以重写它.
    创建web的ioc容器： createServletApplicationContext(); 在创建过程中, 通过getServletConfigClasses();获取配置类, 这个方法是抽象的, 我们可以重写它.
```

#### 总结

如果要以配置的方式启动springmvc, 只需要继承AbstractAnnotationConfigDispatcherServletInitializer, 然后实现上述抽象方法指定DispatcherServlet的配置类信息

### 实现

#### MyWebAppInitializer

```java
package com.atguigu;

import org.springframework.web.servlet.support.AbstractAnnotationConfigDispatcherServletInitializer;

import com.atguigu.config.AppConfig;
import com.atguigu.config.RootConfig;

// 在web容器启动的时候创建这个对象(是WebApplicationInitializer的子类型)；
// 然后调用其中的方法来初始化容器和前端控制器
public class MyWebAppInitializer extends AbstractAnnotationConfigDispatcherServletInitializer {

	//获取根容器的配置类；（Spring的配置文件）   父容器；
	@Override
	protected Class<?>[] getRootConfigClasses() {
		return new Class<?>[]{RootConfig.class};
	}

	//获取web容器的配置类（SpringMVC配置文件）  子容器；
	@Override
	protected Class<?>[] getServletConfigClasses() {
		return new Class<?>[]{AppConfig.class};
	}

	// 获取DispatcherServlet的映射信息
	//  /：拦截所有请求（包括静态资源（xx.js,xx.png）），但是不包括*.jsp；
	//  /*：拦截所有请求；连*.jsp页面都拦截；若拦截jsp, 则jsp页面无法显示, 因为jsp页面是tomcat的jsp引擎解析的, 不能被拦截
	@Override
	protected String[] getServletMappings() {
		return new String[]{"/"};
	}
}
```

#### RootConfig

```java
package com.atguigu.config;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.ComponentScan.Filter;
import org.springframework.context.annotation.FilterType;
import org.springframework.stereotype.Controller;

// 配置Spring的容器 不扫描controller;	父容器
@ComponentScan(value="com.atguigu",excludeFilters={
		@Filter(type=FilterType.ANNOTATION,classes={Controller.class})
})
public class RootConfig {
}
```

#### AppConfig

```java
package com.atguigu.config;

import com.atguigu.controller.MyFirstInterceptor;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.ComponentScan.Filter;
import org.springframework.context.annotation.FilterType;
import org.springframework.stereotype.Controller;
import org.springframework.web.servlet.config.annotation.*;

// SpringMVC只扫描Controller；	子容器
// 必须配置useDefaultFilters=false 禁用默认的过滤规则；
@ComponentScan(value="com.atguigu",includeFilters={
		@Filter(type=FilterType.ANNOTATION,classes={Controller.class})
},useDefaultFilters=false)
public class AppConfig {
}
```

然后编写Controller和Service, 即可测试.



### 定制SpringMVC(更加高级的springmvc功能)

1. 在配置类MyWebConfig上加 @EnableWebMvc: 开启SpringMVC定制配置功能；相当于xml中的

   ```xml
   <mvc:annotation-driven />
   ```

2. 配置组件（视图解析器、视图映射、静态资源映射、拦截器。。。）

* **实现方式**: 
  * **MyWebConfig extends WebMvcConfigurerAdapter, 复写方法即可**
  * MyWebConfig implements WebMvcConfigurer, 需要实现方法

3. 示例

```java
package com.atguigu.config;


import com.atguigu.controller.MyFirstInterceptor;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.ComponentScan.Filter;
import org.springframework.context.annotation.FilterType;
import org.springframework.stereotype.Controller;
import org.springframework.web.servlet.config.annotation.*;

// SpringMVC只扫描Controller；	子容器
// 必须配置useDefaultFilters=false 禁用默认的过滤规则；
@ComponentScan(value="com.atguigu",includeFilters={
		@Filter(type=FilterType.ANNOTATION,classes={Controller.class})
},useDefaultFilters=false)
@EnableWebMvc
public class AppConfig  extends WebMvcConfigurerAdapter  {

	// 视图解析器
	@Override
	public void configureViewResolvers(ViewResolverRegistry registry) {
		// 默认所有的页面都从 /WEB-INF/xxx.jsp
		// registry.jsp();
		registry.jsp("/WEB-INF/views/", ".jsp");
	}
	
	// 静态资源访问
    // 如果不配置静态资源访问, 则静态资源的URI会被springmvc当成路径映射处理. 但实际上, 静态资源应该被tomcat来处理. 所以要配置静态资源访问
    // 相当于在xml中配置了
    // <mvc: default-servlet-handler />
	@Override
	public void configureDefaultServletHandling(DefaultServletHandlerConfigurer configurer) {
		configurer.enable();
	}
	
	//拦截器
	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		registry.addInterceptor(new MyFirstInterceptor()).addPathPatterns("/**");
	}
}
```

##### MyFirstInterceptor

在spring中实现的拦截器, 需要实现spring提供的接口HandlerInterceptor

```java
package com.atguigu.controller;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

public class MyFirstInterceptor implements HandlerInterceptor {

	//目标方法运行之前执行
	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
		System.out.println("preHandle..." + request.getRequestURI());
		return true;
	}

	//目标方法执行正确以后执行
	@Override
	public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
		System.out.println("postHandle...");
	}

	//页面响应以后执行
	@Override
	public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
		System.out.println("afterCompletion...");
	}
}
```



### 异步处理

在Servlet 3.0之前，Servlet采用Thread-Per-Request的方式处理请求。即每一次Http请求都由某一个线程从头到尾负责处理。

如果一个请求需要进行IO操作，比如访问数据库、调用第三方服务接口等，那么其所对应的线程将同步地等待IO操作完成， 而IO操作是非常慢的，所以此时的线程并不能及时地释放回线程池以供后续使用，在并发量越来越大的情况下，这将带来严重的性能问题。即便是像Spring、Struts这样的高层框架也脱离不了这样的桎梏，因为他们都是建立在Servlet之上的。

**为了解决这样的问题，Servlet 3.0引入了异步处理，然后在Servlet 3.1中又引入了非阻塞IO来进一步增强异步处理的性能。**

#### 同步请求的示例

```java
package com.atguigu.servlet;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/hello")
public class HelloServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        //super.doGet(req, resp);
        System.out.println(Thread.currentThread() + " start...");
        try {
            sayHello();
        } catch (Exception e) {
            e.printStackTrace();
        }
        resp.getWriter().write("hello...");
        System.out.println(Thread.currentThread() + " end...");
    }

    private void sayHello() throws Exception {
        System.out.println(Thread.currentThread() + " processing...");
        Thread.sleep(3000);
    }
}
```

#### 异步请求的示例

```java
package com.atguigu.servlet;

import java.io.IOException;

import javax.servlet.AsyncContext;
import javax.servlet.ServletException;
import javax.servlet.ServletResponse;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet(value = "/async", asyncSupported = true)
public class HelloAsyncServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        //1、开启支持异步处理的功能: 在@WebServlet中设置属性为: asyncSupported=true
        System.out.println("主线程开始。。。" + Thread.currentThread() + "==>" + System.currentTimeMillis());
        //2、开启异步模式, 返回异步的Context上下文对象
        AsyncContext startAsync = req.startAsync();

        //3、AsyncContext.start(Runnable runnable), 让业务逻辑进行异步处理; 开始异步处理
        startAsync.start(new Runnable() {
            @Override
            public void run() {
                try {
                    System.out.println("副线程开始。。。" + Thread.currentThread() + "==>" + System.currentTimeMillis());
                    sayHello();
                    // 异步处理已经结束
                    startAsync.complete();
                    // 再次获取到异步上下文
                    AsyncContext asyncContext = req.getAsyncContext();
                    // 4. 从异步上下文对象中获取响应
                    ServletResponse response = asyncContext.getResponse();
                    response.getWriter().write("hello async...");
                    System.out.println("副线程结束。。。" + Thread.currentThread() + "==>" + System.currentTimeMillis());
                } catch (Exception e) {
                }
            }
        });
        System.out.println("主线程结束。。。" + Thread.currentThread() + "==>" + System.currentTimeMillis());
    }

    private void sayHello() throws Exception {
        System.out.println(Thread.currentThread() + " processing...");
        Thread.sleep(3000);
    }
}
```

异步流程相当于处了主线程的线程池之外, 还有一个副线程的线程池.

在spring中, spring为我们管理这个副线程, 所以会产生两种异步的spring开发模式

#### 在Controller中返回Callable

```java
package com.atguigu.controller;

import java.util.UUID;
import java.util.concurrent.Callable;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.context.request.async.DeferredResult;

import com.atguigu.service.DeferredResultQueue;


@Controller
public class AsyncController {
	
    /**
     * 1、控制器返回Callable对象
     * 2、Spring异步处理，将 Callable对象 提交到 TaskExecutor接口(extends Excutor接口, 链有excutor方法, 执行Callable任务), 使用一个隔离的线程进行执行
     * 3、DispatcherServlet和所有的Filter退出web容器的线程，但是 response 保持打开状态；还可以给浏览器响应数据
     * 4、Callable返回结果后，SpringMVC将请求重新派发给容器，恢复之前的处理；
     * 5、根据Callable返回的结果。SpringMVC继续进行视图渲染流程等（从收请求-视图渲染）。
     * <p>
     * preHandle.../springmvc-annotation/async01
     * 主线程开始...Thread[http-bio-8081-exec-3,5,main]==>1513932494700
     * 主线程结束...Thread[http-bio-8081-exec-3,5,main]==>1513932494700
     * ========= DispatcherServlet及所有的Filter退出主线程 ============================
     * <p>
     * ================开始副线程中Callable执行==========
     * 副线程开始...Thread[MvcAsync1,5,main]==>1513932494707
     * 副线程开始...Thread[MvcAsync1,5,main]==>1513932496708
     * ================Callable执行完成==========
     * <p>
     * ================主线程再次收到重发过来的初始的请求========
     * preHandle.../springmvc-annotation/async01
     * postHandle...（Callable的之前的返回值就是目标方法的返回值）
     * afterCompletion...
     * <p>
     
     也就是说, 异步情况下, 拦截器是无法拦截到真正的业务逻辑的
     我们需要使用异步拦截器
     
     * 异步的拦截器:
     * 1）、原生API的AsyncListener
     * 2）、SpringMVC：实现AsyncHandlerInterceptor；
     *
     */
    @ResponseBody
    @RequestMapping("/async01")
    public Callable<String> async01() {
        System.out.println("主线程开始..." + Thread.currentThread() + "==>" + System.currentTimeMillis());
		// 创建要返回的Callable<String>对象
        Callable<String> callable = new Callable<String>() {
            @Override
            public String call() throws Exception {
                System.out.println("副线程开始..." + Thread.currentThread() + "==>" + System.currentTimeMillis());
                Thread.sleep(2000);
                System.out.println("副线程开始..." + Thread.currentThread() + "==>" + System.currentTimeMillis());
                return "Callable<String> async01()";
            }
        };

        System.out.println("主线程结束..." + Thread.currentThread() + "==>" + System.currentTimeMillis());
        return callable;
    }
}
```

#### 在Controller中返回DeferredResult

```java
package com.atguigu.controller;

import com.atguigu.service.DeferredResultQueue;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.context.request.async.DeferredResult;

import java.util.UUID;

@Controller
public class AsyncController {

    @ResponseBody
    @RequestMapping("/createOrder")
    public DeferredResult<Object> createOrder() {
        // 本api(线程)的目标是产生一个创建订单的消息放在消息队列中, 同时, 需要另外一个api来监听消息队列, 并真正从创建订单.
        // 因为创建订单的操作比较耗时, 所以无法及时返回结果,
        // 没关系, 先创建DeferredResult对象, 然后把这个对象返回
        // 此时, 本api就在等待响应结果
        // 当在另外一个代码逻辑中, 调用deferredResult.setResult(data);之后, DeferredResult有值了
        // 则本api就可以响应结果了

        // 设置超时时间为3s, 如果超时了, 就返回错误提示消息(第二个参数)
        DeferredResult<Object> deferredResult = new DeferredResult<>((long) 3000, "create fail...");

        // 模拟的消息队列, 这个队列就是存储DeferredResult对象的
        DeferredResultQueue.save(deferredResult);
        return deferredResult;
    }

    @ResponseBody
    @RequestMapping("/create")
    public String create() {
        //真正创建订单的api(线程)
        String order = UUID.randomUUID().toString();
        DeferredResult<Object> deferredResult = DeferredResultQueue.get();
        deferredResult.setResult(order);
        return "success===>" + order;
    }
}
```

DeferredResultQueue

```java
package com.atguigu.service;

import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

import org.springframework.web.context.request.async.DeferredResult;

public class DeferredResultQueue {

	// 模拟的消息队列, 这个消息队列就是存储DeferredResult对象的
	private static Queue<DeferredResult<Object>> queue = new ConcurrentLinkedQueue<DeferredResult<Object>>();
	
	public static void save(DeferredResult<Object> deferredResult){
		queue.add(deferredResult);
	}
	
	public static DeferredResult<Object> get( ){
		return queue.poll();
	}
}
```

