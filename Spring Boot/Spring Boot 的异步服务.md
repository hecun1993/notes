### springboot中的异步任务一

1.首先定义AsyncTask类, 加上@Component注解, 在其中定义几个方法, 分别在方法上加上@Async注解

2.在另外一个类(controller)中, @Autowired这个AsyncTask类, 然后在本类的一个方法中, 调用AsyncTask类中的方法即可.

3.在启动类上加上@EnableAsync, @EnableScheduling

```java
@Component
public class AsyncTask {
	
    @Async
    public void startMonitorSystem(String roundId) {
        MonitorController.threadIdMap.put("SystemThreadId", Thread.currentThread().getId());
        try {
            log.info("Begin monitor system matrix, roundId: {}", roundId);
            monitorService.monitorSystemMatrix(requestNum, roundId, source);
        } catch (Exception e) {
            log.info("System Monitor thread is killed, roundId: {}, {}", roundId, e.getMessage());
        }
    }

    @Async
    public void startMonitorUser(String roundId) {
        MonitorController.threadIdMap.put("UserThreadId", Thread.currentThread().getId());
        try {
            log.info("Begin monitor user matrix, roundId: {}", roundId);
            monitorService.monitorUserMatrix(requestNum, roundId);
        } catch (Exception e) {
            log.info("Custom Monitor thread is killed, roundId: {}, {}", roundId, e.getMessage());
        }
    }
}
```

```java
@RestController
@RequestMapping("/monitor")
@Slf4j
public class MonitorController {
    /**
     * 存储正在运行的线程id
     */
    public static Map<String, Long> threadIdMap = new HashMap<>();

    @Autowired
    private AsyncTask monitorTask;
    
    @GetMapping("/begin")
    public ResponseEntity<GeneralResponse> begin() {
        //开始监控
        monitorTask.startMonitorSystem(roundId);
        monitorTask.startMonitorUser(roundId);
    }
}
```

### 

### Spring Boot 的异步服务二

#### 异步处理的核心

当有http请求来到类似tomcat的中间件时, 中间件的主线程, 调起一个副线程去处理业务逻辑. 当副线程处理结束后, 主线程再把结果返回.

在副线程处理业务请求的过程中, 主线程是空闲的, 可以处理其他请求. 这样, 服务器的吞吐量会增加.

#### 使用Callable实现异步处理

```java
package com.hecun.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.concurrent.Callable;

@RestController
public class AsyncController {

    private Logger logger = LoggerFactory.getLogger(AsyncController.class);
	
    //同步的方式
    @RequestMapping("/order")
    public String order() throws InterruptedException {
        logger.info("主线程开始");

        //模拟下单逻辑, 耗时1s
        Thread.sleep(1000);

        logger.info("主线程返回");

        return "success";
    }

    //异步的方式
    @RequestMapping("/order")
    public Callable<String> orderAsync() throws InterruptedException {
        logger.info("主线程开始");
        
        //spring创建的一个简单的线程池, 不会重用其中的线程, 每次都会创建一个新的线程执行.
        Callable<String> result = new Callable<String>() {
            @Override
            public String call() throws Exception {
                logger.info("副线程开始");

                //模拟下单逻辑, 耗时1s
                Thread.sleep(1000);

                logger.info("副线程返回");
                return "success";
            }
        };

        logger.info("主线程返回");

        return result;
    }
}
```



#### DefferedResult的方式

Callable方式的不足之处在于: 处理业务逻辑的副线程, 必须由中间件的主线程调起, 才可以开始执行.

```java
总共有三个线程
1. 主线程: 接受http请求. (AsyncController)
2. 处理真正的下单逻辑. (MockQueue)
3. 把处理下单逻辑的线程的处理结果返回给前台. (QueueListener)
4. 主线程和返回前台结果线程之间, 通过DeferredResultHolder来交互, 传递DeferredResult对象

上述三个线程互相隔离, 通过消息队列进行通信.
对前台来说, 感知到的仍然是耗时1s的同步任务, 从开发者工具可以看出.
```

##### AsyncController

```java
package com.hecun.controller.async;

import org.apache.commons.lang.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.context.request.async.DeferredResult;

@RestController
public class AsyncController {

    private Logger logger = LoggerFactory.getLogger(AsyncController.class);

    @Autowired
    private MockQueue mockQueue;

    @Autowired
    private DeferredResultHolder deferredResultHolder;

    @RequestMapping("/order")
    public DeferredResult<String> order() throws InterruptedException {
        logger.info("主线程开始");

        //1. 由下单请求到来, 也就是请求了/order这个api
        //2. 生成一个8位随机的订单号
        String orderNumber = RandomStringUtils.randomNumeric(8);
        //3. 把订单号放在消息队列中
        mockQueue.setPlaceOrder(orderNumber);
        //4. 创建DeferredResult, 然后放在专门放置DeferredResult的Map中, 准备传给另外一个监听消息队列的线程中
        DeferredResult<String> result = new DeferredResult<>();
        deferredResultHolder.getMap().put(orderNumber, result);

        logger.info("主线程结束");

        //5. 将DeferredResult对象返回. (tomcat服务器的线程1的任务结束)
        return result;
    }
}
```

##### MockQueue

```java
package com.hecun.controller.async;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * 模拟下单/订单完成的消息队列
 */
@Component
public class MockQueue {

    private Logger logger = LoggerFactory.getLogger(MockQueue.class);


    /**
     * 以下两个属性, 第一个有值代表下单了; 第二个有值代表订单完成
     */
    private String placeOrder;
    private String completeOrder;

    public String getPlaceOrder() {
        return placeOrder;
    }

    /**
     * 接受到下单请求之后的处理
     * @param placeOrder 订单
     * @throws InterruptedException
     */
    public void setPlaceOrder(String placeOrder) throws InterruptedException {
        new Thread(() -> {
            logger.info("接到下单请求, " + placeOrder);
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            this.completeOrder = placeOrder;
            logger.info("下单请求处理完成, " + placeOrder);
        }).start();
    }

    public String getCompleteOrder() {
        return completeOrder;
    }

    public void setCompleteOrder(String completeOrder) {
        this.completeOrder = completeOrder;
    }
}
```

##### QueueListener

```java
package com.hecun.controller.async;

import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.stereotype.Component;

/**
 * 监听队列中completeOrder中是否有值, 如果有值, 则返回给前台
 *
 * ContextRefreshedEvent: 这个事件表示整个spring容器初始化完毕的事件
 */
@Component
public class QueueListener implements ApplicationListener<ContextRefreshedEvent> {

    private Logger logger = LoggerFactory.getLogger(QueueListener.class);

    @Autowired
    private MockQueue mockQueue;

    @Autowired
    private DeferredResultHolder deferredResultHolder;

    /**
     * 当spring容器初始化完毕之后, 要做的事.
     * 也就是监听MockQueue消息队列中的 completeOrder 的值
     * @param contextRefreshedEvent
     */
    @Override
    public void onApplicationEvent(ContextRefreshedEvent contextRefreshedEvent) {

        //监听器需要新开一个线程
        new Thread(() -> {
            while(true) {
                if (StringUtils.isNotBlank(mockQueue.getCompleteOrder())) {
                    String orderNumber = mockQueue.getCompleteOrder();
                    logger.info("返回订单处理结果: " + orderNumber);
                    //调用setResult方法, 把值返回给前台.
                    deferredResultHolder.getMap().get(orderNumber).setResult("place order success");
                    mockQueue.setCompleteOrder(null);
                } else {
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }).start();
    }
}
```

##### DeferredResultHolder

```java
package com.hecun.controller.async;

import org.springframework.stereotype.Component;
import org.springframework.web.context.request.async.DeferredResult;

import java.util.HashMap;
import java.util.Map;

@Component
public class DeferredResultHolder {

    //1. 在Map中, String表示订单号. DeferredResult<String>表示订单的处理结果.
    //2. DeferredResult<String>中的String, 表示订单处理完成后, 在前台显示的是一个字符串.
    //3. 这个类的作用是, 在tomcat服务器的两个线程中, 传递DeferredResult<String>对象.
    private Map<String, DeferredResult<String>> map = new HashMap<>();

    public Map<String, DeferredResult<String>> getMap() {
        return map;
    }

    public void setMap(Map<String, DeferredResult<String>> map) {
        this.map = map;
    }
}
```

##### WebConfig

```java
package com.hecun.controller.async;

import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.AsyncTaskExecutor;
import org.springframework.web.servlet.config.annotation.AsyncSupportConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

import java.util.concurrent.Callable;
import java.util.concurrent.Future;

//异步任务的一些配置(拦截器, 超时时间, spring线程池)
@Configuration
public class WebConfig extends WebMvcConfigurerAdapter {

    @Override
    public void configureAsyncSupport(AsyncSupportConfigurer configurer) {

        //设置异步任务的拦截器
        configurer.registerCallableInterceptors();

        //设置异步任务的拦截器
        configurer.registerDeferredResultInterceptors();

        //设置异步任务的超时时间
        configurer.setDefaultTimeout(1L);

        //自定义spring的线程池
        configurer.setTaskExecutor(new AsyncTaskExecutor() {
            @Override
            public void execute(Runnable runnable, long l) {

            }

            @Override
            public Future<?> submit(Runnable runnable) {
                return null;
            }

            @Override
            public <T> Future<T> submit(Callable<T> callable) {
                return null;
            }

            @Override
            public void execute(Runnable runnable) {

            }
        });
    }
}
```

