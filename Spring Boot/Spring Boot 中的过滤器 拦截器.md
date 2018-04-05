## Spring Boot 中的过滤器 拦截器

### Filter — JavaEE规范

#### 1. 实现Filter接口

```java
// 加上@Component注解,交给Spring管理
@Component
public class TimeFilter implements Filter {
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        System.out.println("my filter init");
    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        System.out.println("my filter start");
        long start = new Date().getTime();
        filterChain.doFilter(servletRequest, servletResponse);
        System.out.println("耗时:" + (new Date().getTime() - start));
        System.out.println("my filter end");
    }

    @Override
    public void destroy() {
        System.out.println("my filter destroy");
    }
}
```

#### 2. 加到过滤器链中

```java
@Configuration
public class WebConfig {
    //注册Bean
    @Bean
    public FilterRegistrationBean timeFilter() {
        FilterRegistrationBean filterRegistrationBean = new FilterRegistrationBean();
        TimeFilter timeFilter = new TimeFilter();
        filterRegistrationBean.setFilter(timeFilter);

        //指定这个filter在哪些url上起作用
        List<String> urls = new ArrayList<>();
        urls.add("/*");
        filterRegistrationBean.setUrlPatterns(urls);

        return filterRegistrationBean;
    }
}
```

#### 3. 特点

filter只能拿到http的请求和响应, 但当前发来的请求是由哪个controller哪个方法处理的, 在filter中并不知道.

整个流程是在一个方法中完成的(doFilter)



### Interceptor — spring提供

#### 1. 特点

整个流程是在两个方法中完成的,所以需要把一些属性值放在request的Attribute中.

优势在于有一个handler参数,可以获得控制器的类和方法

不足在于无法拿到控制器方法的参数的值

#### 2. 创建TimeInterceptor

```java
@Component
public class TimeInterceptor implements HandlerInterceptor {
    //在controller某一方法调用之前,执行
    @Override
    public boolean preHandle(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, Object o) throws Exception {
        System.out.println("preHandler");
        httpServletRequest.setAttribute("startTime", new Date().getTime());

        // 可以获得HandlerMethod 然后获得方法名和类名
        HandlerMethod handlerMethod = (HandlerMethod)o;
        System.out.println(handlerMethod.getBean().getClass().getName());
        System.out.println(handlerMethod.getMethod().getName());
        return true;
    }
    
    //控制器的方法调用之后,执行(如果控制器抛出了异常, 则该方法不会被调用)
    @Override
    public void postHandle(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, Object o, ModelAndView modelAndView) throws Exception {
        System.out.println("postHandle");
        Long startTime = (Long) httpServletRequest.getAttribute("startTime");
        System.out.println("time interceptor 耗时: " + (new Date().getTime() - startTime));
    }
    
    //无论控制器方法是否有异常,都会执行这个方法
    @Override
    public void afterCompletion(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, Object o, Exception e) throws Exception {
        System.out.println("afterCompletion");
        Long startTime = (Long) httpServletRequest.getAttribute("startTime");
        System.out.println("time interceptor 耗时: " + (new Date().getTime() - startTime));
        System.out.println(e);
    }
}
```

#### 3. 配置

```java
@Configuration
public class WebConfig extends WebMvcConfigurerAdapter {

    @Autowired
    private TimeInterceptor timeInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(timeInterceptor);
    }
}
```

### AOP在spring中的应用

```java
@Aspect
@Component
//1. 上面的两个注解就已经搞定了切片(类)
public class TimeAspect {
    //1.1. 什么时候起作用(切入点)
    //    @Before(): 控制器调用之前执行
    //    @After(): 控制器调用之后执行
    //    @AfterThrowing: 控制器调用抛出异常时执行
    //    @Around(): 完全覆盖了前面三个, 一般都用Around

    //1.2. 在哪些方法上起作用(增强), 用表达式
    @Around("execution(* me.hds.web.controller.UserController.*(..))")
    public Object handlerControllerMethod(ProceedingJoinPoint proceedingJoinPoint) throws Throwable {
        System.out.println("time aspect start");

        //拿到控制器方法的参数
        Object[] args = proceedingJoinPoint.getArgs();
        System.out.println(Arrays.asList(args));

        long start = new Date().getTime();
        //执行被拦截的控制器中的方法
        //控制器方法返回值是什么, proceed就是什么
        Object proceed = proceedingJoinPoint.proceed();
        System.out.println("耗时:" + (new Date().getTime() - start));

        System.out.println("time aspect end");
        return proceed;
    }
}
```

> ```
> 起作用的顺序: Filter -> Interceptor -> ControllerAdvice -> Aspect -> Controller
> ```

