# Spring Cloud Hystrix 源码分析

## Spring Cloud Hystrix 源码解读

### `@EnableCircuitBreaker`

职责：

* 激活 Circuit Breaker

* ```java
  @Order(Ordered.LOWEST_PRECEDENCE - 100)
  public class EnableCircuitBreakerImportSelector extends
  		SpringFactoryImportSelector<EnableCircuitBreaker> {

  	@Override
  	protected boolean isEnabled() {
  		return new RelaxedPropertyResolver(getEnvironment()).getProperty(
  				"spring.cloud.circuit.breaker.enabled", Boolean.class, Boolean.TRUE);
  	}

  }
  ```

* 但是, 如果我们在配置项中, 设置spring.cloud.circuit.breaker.enabled为false, 则即使加了上述注解, 也无法激活hystrix, 具体测试可以通过访问endpoint来检测. /hystrix.stream

  ```properties
  ## 应用名称
  spring.application.name = hystrix-source-code

  ## Circuit Breaker 开关（默认值：true）
  spring.cloud.circuit.breaker.enabled = true

  ## Hystrix Stream Endpoint 开关（默认值：true）
  hystrix.stream.endpoint.enabled = true

  ## 关闭 Endpoint 安全
  management.security.enabled = false

  ## endpoints.env.sensitive = false

  ## 动态配置 Hystrix Command 超时时间
  dynamic.hystrix.command.timeout = 100
  ```

  ​



#### 初始化顺序

* `@EnableCircuitBreaker `
  * `EnableCircuitBreakerImportSelector`

    * SpringFactoryImportSelector<EnableCircuitBreaker>

    * ```java
      protected SpringFactoryImportSelector() {
          this.annotationClass = (Class<T>) GenericTypeResolver
              .resolveTypeArgument(this.getClass(), SpringFactoryImportSelector.class);
      }
      //在构造方法中拿到泛型类, 也就是注解本身
      //然后在
      @Override
      public String[] selectImports(AnnotationMetadata metadata) {
          if (!isEnabled()) {
              return new String[0];
          }
          AnnotationAttributes attributes = AnnotationAttributes.fromMap(
              metadata.getAnnotationAttributes(this.annotationClass.getName(), true));

          Assert.notNull(attributes, "No " + getSimpleName() + " attributes found. Is "
                         + metadata.getClassName() + " annotated with @" + getSimpleName() + "?");

          // Find all possible auto configuration classes, filtering duplicates
          List<String> factories = new ArrayList<>(new LinkedHashSet<>(SpringFactoriesLoader
                                                                       .loadFactoryNames(this.annotationClass, this.beanClassLoader)));

          if (factories.isEmpty() && !hasDefaultFactory()) {
              throw new IllegalStateException("Annotation @" + getSimpleName()
                                              + " found, but there are no implementations. Did you forget to include a starter?");
          }

          if (factories.size() > 1) {
              // there should only ever be one DiscoveryClient, but there might be more than
              // one factory
              log.warn("More than one implementation " + "of @" + getSimpleName()
                       + " (now relying on @Conditionals to pick one): " + factories);
          }

          return factories.toArray(new String[factories.size()]);
      }
      //这个方法中, 通过从spring.factories文件中找到上述注解为键名的键值, 来自动配置HystrixCircuitBreakerConfiguration类
      //关键代码如下:
      SpringFactoriesLoader
                                                                    .loadFactoryNames(this.annotationClass, this.beanClassLoader));
      ```

      * `HystrixCircuitBreakerConfiguration`



### HystrixCircuitBreakerConfiguration

#### 初始化组件

* `HystrixCommandAspect`: 切面的配置, 把@HystrixCommand转变成一个java类

* `HystrixShutdownHook`:

  ```java
  //利用spring的方式来销毁
  private class HystrixShutdownHook implements DisposableBean {
      @Override
      public void destroy() throws Exception {
          // Just call Hystrix to reset thread pool etc.
          Hystrix.reset();
      }
  }
  ```

  ​

* `HystrixStreamEndpoint` ： 继承了Servlet API 的Web组件

* `HystrixMetricsPollerConfiguration`




## Netflix Hystrix 源码解读

### `HystrixCommandAspect`

#### 依赖组件

* `MetaHolderFactory`
* `HystrixCommandFactory`: 生成`HystrixInvokable`
* `HystrixInvokable`
  * `CommandCollapser`
  * `GenericObservableCommand`
  * `GenericCommand`




###  Future 实现 服务熔断

```java
package com.segumentfault.springcloudlesson9.future;

import java.util.Random;
import java.util.concurrent.*;

/**
 * 通过 {@link Future} 实现 服务熔断
 *
 * @author <a href="mailto:mercyblitz@gmail.com">Mercy</a>
 */
public class FutureCircuitBreakerDemo {
    
    public static void main(String[] args) throws InterruptedException, ExecutionException {
        // 初始化线程池
        ExecutorService executorService = Executors.newSingleThreadExecutor();
        RandomCommand command = new RandomCommand();
        Future<String> future = executorService.submit(command::run);
        String result = null;
        // 100 毫秒超时时间
        try {
            //future 如果超过100ms, 则不等待, 就抛出异常
            //用来模拟@HystrixCommand中设置的100ms的超时时间
            result = future.get(100, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            // fallback 方法调用
            result = command.fallback();
        }
        System.out.println(result);
        executorService.shutdown();
    }
    
    /**
     * 随机对象
     */
    private static final Random random = new Random();

    /**
     * 随机的时间执行命令
     */
    public static class RandomCommand implements Command<String> {
        @Override
        public String run() throws InterruptedException {
            long executeTime = random.nextInt(200);
            // 通过休眠来模拟执行时间
            System.out.println("Execute Time : " + executeTime + " ms");
            Thread.sleep(executeTime);
            return "Hello,World";
        }

        @Override
        public String fallback() {
            return "Fallback";
        }
    }

    public interface Command<T> {
        /**
         * 正常执行，并且返回结果
         */
        T run() throws Exception;

        /**
         * 错误时，返回容错结果
         */
        T fallback();
    }
}
```



## RxJava 基础

```java
/**
 * RxJava 1.x 示例
 */
public class RxJavaDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("主线程：" + Thread.currentThread().getName());
        demoStandardReactive();
    }

    private static void demoStandardReactive() throws InterruptedException {
        List<Integer> values = Arrays.asList(1, 2, 3);
        Observable.from(values) //发布多个数据
                .subscribeOn(Schedulers.newThread()) // 在 newThread 线程执行
                .subscribe(value -> {
                    if (value > 2)
                        throw new IllegalStateException("数据不应许大于 2");
                    //消费数据
                    println("消费数据：" + value);
                }, e -> {
                    // 当异常情况，中断执行
                    println("发生异常 , " + e.getMessage());
                }, () -> {
                    // 当整体流程完成时
                    println("流程执行完成");
                })
        ;
        // 等待线程执行完毕
        Thread.sleep(100);
    }

    private static void demoObservable() throws InterruptedException {
        List<Integer> values = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
        Observable.from(values) //发布多个数据
                .subscribeOn(Schedulers.computation()) // 在 computation 线程执行
                .subscribe(RxJavaDemo::println) // 订阅并且消费数据
        ;
        // 等待线程执行完毕
        Thread.sleep(100);
    }

    private static void demoSingle() {
        Single.just("Hello,World") // 仅能发布单个数据
                .subscribeOn(Schedulers.io()) // 在 I/O 线程执行
                .subscribe(RxJavaDemo::println) // 订阅并且消费数据
        ;
    }

    private static void println(Object value) {
        System.out.printf("[线程: %s] %s\n", Thread.currentThread().getName(), value);
    }
}
```



### 单数据：Single

```java
//just方法用来发送数据
//发送数据之后, 就要设置订阅者, 也就是subscribe方法
//在RxJava2.0之后, 才有Flowable.just()方法

Single.just("Hello,World") // Single仅能发布单个数据
        .subscribeOn(Schedulers.io()) // 在 I/O 线程执行, 如果不加这一句, 则默认会挂在主线程执行, 加了这一句, 就变成多线程的执行了
        .subscribe(RxJavaDemo::println) // 订阅并且消费数据
;
```

### 多数据：Observable

```java
List<Integer> values = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);

Observable.from(values) //发布多个数据
        .subscribeOn(Schedulers.io()) // 在 I/O 线程执行
        .subscribe(RxJavaDemo::println) // 订阅并且消费数据
;

// 等待线程执行完毕
Thread.sleep(100);
```

### 使用标准 Reactive 模式

不需要用传统的try catch方式处理代码逻辑

```java
List<Integer> values = Arrays.asList(1, 2, 3);

Observable.from(values) //发布多个数据
    .subscribeOn(Schedulers.newThread()) // 在 newThread 线程执行
    .subscribe(value -> {
        //1. onNext()
        if (value > 2)
            throw new IllegalStateException("数据不应许大于 2");
        //消费数据
        println("消费数据：" + value);
    }, e -> { //2. onError
        // 当异常情况，中断执行
        println("发生异常 , " + e.getMessage());
    }, () -> { //3. onCompleted
        // 当整体流程完成时
        println("流程执行完成");
    })
;

// 等待线程执行完毕
Thread.sleep(100);
```



## Java 9 Flow API

Flow实现了reactive-streams规定的api

```java
package concurrent.java9;

import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;

public class SubmissionPublisherDemo {

    public static void main(String[] args) throws InterruptedException {
        try (SubmissionPublisher<Integer> publisher =
                     new SubmissionPublisher<>()) {
            //Publisher(100) => A -> B -> C => Done
            publisher.subscribe(new IntegerSubscriber("A"));
            publisher.subscribe(new IntegerSubscriber("B"));
            publisher.subscribe(new IntegerSubscriber("C"));

            // 提交数据到各个订阅器
            publisher.submit(100);
        }
        Thread.currentThread().join(1000L);
    }

    //Flow API: 订阅者需要实现的接口
    private static class IntegerSubscriber implements
            Flow.Subscriber<Integer> {

        private final String name;
        private Flow.Subscription subscription;

        private IntegerSubscriber(String name) {
            this.name = name;
        }

        @Override
        public void onSubscribe(Flow.Subscription subscription) {
            System.out.printf(
                    "Thread[%s] Current Subscriber[%s] " +
                            "subscribes subscription[%s]\n",
                    Thread.currentThread().getName(),
                    name,
                    subscription);
            this.subscription = subscription;
            subscription.request(1);
        }

        @Override
        public void onNext(Integer item) {
            System.out.printf(
                    "Thread[%s] Current Subscriber[%s] " +
                            "receives item[%d]\n",
                    Thread.currentThread().getName(),
                    name,
                    item);
            subscription.request(1);
        }

        @Override
        public void onError(Throwable throwable) {
            throwable.printStackTrace();
        }

        @Override
        public void onComplete() {
            System.out.printf(
                    "Thread[%s] Current Subscriber[%s] " +
                            "is completed!\n",
                    Thread.currentThread().getName(),
                    name);
        }
    }
}
```

