## 观察Thread的特点

### 1. 主线程和两个新线程同时执行

```java
public static void main(String[] args) throws Exception {
    //主线程
    System.out.println(System.currentTimeMillis() + "1xxx");

    //新线程1
    Thread thread1 = new Thread(new Runnable() {
        @Override
        public void run() {
            try {
                Thread.sleep(1000);
                System.out.println(System.currentTimeMillis() + Thread.currentThread().getName());
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    });
    thread1.start();

	//新线程2
    Thread thread2 = new Thread(() -> {
        try {
            Thread.sleep(2000);
            System.out.println(System.currentTimeMillis() + "lambada: " + Thread.currentThread().getName());
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    });
    thread2.start();

    //主线程
    System.out.println(System.currentTimeMillis() + "2xxx");
}
```

执行结果如下:

> 15190927966421 xxx
> 15190927967482 xxx
> 1519092797650 Thread-0
> 1519092798749 lambada: Thread-1

可以从执行时间上看到, 三个线程是分别执行的.

### 2. ExcutorService的使用

```java
/**
 * 使用Executor执行线程:
 * 一些已有的执行器可以帮我们管理Thread对象。
 * 你无需自己创建与控制Thread对象。比如，你不用在代码中编写new Thread或者thread1.start()也一样可以使用多线程。
 * <p>
 * Executors相当于执行器的工厂类，包含各种常用执行器的工厂方法，可以直接创建常用的执行器。
 * 几种常用的执行器如下：
 * Executors.newCachedThreadPool,
 * 根据需要可以创建新线程的线程池。线程池中曾经创建的线程，在完成某个任务后也许会被用来完成另外一项任务。
 * Executors.newFixedThreadPool(int nThreads) ,
 * 创建一个可重用固定线程数的线程池。这个线程池里最多包含nThread个线程。
 * Executors.newSingleThreadExecutor() ,
 * 创建一个使用单个 worker 线程的 Executor。即使任务再多，也只用1个线程完成任务。
 * Executors.newSingleThreadScheduledExecutor() ,
 * 创建一个单线程执行程序，它可安排在给定延迟后运行命令或者定期执行。
 * <p>
 * 最佳实践：我们应该使用现有Executor或ExecutorService实现类。
 * 比如前面说的newCachedThreadPool可以使用线程池帮我们降低开销（创建一个新的线程是有一定代价的），
 * 而newFixedThreadPool则可以限制并发线程数。即，我们一般使用Executors的工厂方法来创建我们需要的执行器。
 */
@Test
public void test2() {
    /*
    从输出我们可以看到，exec使用了线程池1中的5个线程做了这几个任务。
    这个例子中exec这个Executor负责管理任务，所谓的任务在这里就是实现了Runnable接口的匿名内部类。
    至于要使用几个线程，什么时候启动这些线程，是用线程池还是用单个线程来完成这些任务，我们无需操心。完全由exec这个执行器来负责。
     */
    ExecutorService executorService = Executors.newCachedThreadPool();
    for (int i = 0; i < 5; i++) {
        executorService.submit(() -> {
            System.out.println(Thread.currentThread().getName());
        });
    }
    //使用线程池结束之后, 必须shutdown()
    executorService.shutdown();

    //虽然有5个任务(5个new Runnable)，但是只由1个线程来完成。
    ExecutorService executorService2 = Executors.newSingleThreadExecutor();
    for (int i = 0; i < 5; i++) {
        executorService2.submit(() -> {
            System.out.println(Thread.currentThread().getName());
        });
    }
    executorService2.shutdown();
}
```

### 3. ExcutorService / Excutor 都是接口

```java
/**
 * public interface ExecutorService extends Executor {}
 * ExecutorService 和 Executor 都是接口
 * Executor与ExecutorService的常用方法:
 * executor.execute(new RunnableTask1());
 * <p>
 * Future<?> submit(Runnable task);  <T> Future<T> submit(Callable<T> task)
 * <p>
 * <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks);  <T> T invokeAny(Collection<? extends Callable<T>> tasks)
 * 批量执行一组Callable任务。其中invokeAll是等所有任务完成后返回代表结果的Future列表。而invokeAny是等这一批任务中的任何一个任务完成后就返回。
 * <p>
 * shutdown()
 * 执行此方法后，线程池等待任务结束后就关闭，同时不再接收新的任务。
 */
@Test
public void test3() {
    /*
      exec执行器执行了一个Callable类型的任务列表然后得到了Future类型的结果列表resultList。
     */
    ExecutorService executorService = Executors.newCachedThreadPool();
    //往任务列表中添加5个任务
    List<Callable<String>> taskList = new ArrayList<>();
    for (int i = 0; i < 5; i++) {
        taskList.add(() -> Thread.currentThread().getName());
    }

    //结果列表, 存放完成任务的返回值
    List<Future<String>> resultList = new ArrayList<>();
    try {
        /*invokeAll批量运行所有任务, submit提交单个任务*/
        resultList = executorService.invokeAll(taskList);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }

    try {
        /*从future中输出每个任务的返回值*/
        for (Future<String> future : resultList) {
            System.out.println(future.get()); //get方法会阻塞直到结果返回
        }
    } catch (InterruptedException | ExecutionException e) {
        e.printStackTrace();
    }
}
```

### 4. Callable<Integer>的例子

```java
@Test
public void test4() throws InterruptedException, ExecutionException {

    /*新建一个Callable任务*/
    Callable<Integer> callableTask = () -> {
        System.out.println("正在计算1 + 1");
        TimeUnit.SECONDS.sleep(2);
        return 2;
    };

    ExecutorService executorService = Executors.newCachedThreadPool();
    Future<Integer> future = executorService.submit(callableTask);

    //关闭!!
    executorService.shutdown();

    if (!future.isDone()) {
        System.out.println("还没结束");
    }

    //这就是主线程正在做的事, 可以不受耗时任务(Future)的影响, 只要判断Future是否做完, 做完返回即可
    while (!future.isDone()) {
        System.out.println("正在计算");
        TimeUnit.SECONDS.sleep(1);
    }

    Integer result = future.get();
    System.out.println("计算结果是: " + result);
}
```

### 5. FutureTask的使用

```java
/**
 * FutureTask
 * <p>
 * FutureTask类是 Future 接口的一个实现。
 * FutureTask的构造函数只能在传入Callable接口的实现类
 * <p>
 * 注意:
 * 1. FutureTask<Integer> futureTask = new FutureTask<>(new Callable...)
 * 相当于把Callable任务转换为Runnable任务，就可以使用线程来执行该任务。
 * <p>
 * 也就是说, new FutureTask()传入的参数是Callable对象, 就可以把Callable任务转变为Runnable任务.
 * <p>
 * 2. futureTask.get()相当于将Callable转化为Future，从而得到异步运算的结果。
 */
@Test
public void test5() throws ExecutionException, InterruptedException {
    FutureTask<Integer> futureTask = new FutureTask<>(new Callable<Integer>() {
        @Override
        public Integer call() throws Exception {
            System.out.println("futureTask is working 1 + 1!");
            TimeUnit.SECONDS.sleep(2);
            return 2;
        }
    });

    Thread thread = new Thread(futureTask);
    thread.start();

    System.out.println(futureTask.get());
}

//===========================================================================

/**
 * ExecutorService执行器除了接收Runnable与Callable类型的入参，也可以接收FutureTask类型，
 */
@Test
public void test6() throws InterruptedException, ExecutionException {
    FutureTask<Integer> futureTask = new FutureTask<>(() -> {
        System.out.println("futureTask is working 1 + 1!");
        TimeUnit.SECONDS.sleep(2);
        return 2;
    });

    ExecutorService executorService = Executors.newCachedThreadPool();
    executorService.submit(futureTask);
    executorService.shutdown();

    while (!futureTask.isDone()) {
        System.out.println("子线程还没做完，我再睡会");
        TimeUnit.SECONDS.sleep(1);
    }

    System.out.println("子线程运行的结果：" + futureTask.get());
}
```



## jdk8中的并行流

### 1. 并行流, 串行流, 迭代

```java
//并行流: 649ms
public static long parallelSumV1(long n) {
    return Stream.iterate(1L, i -> i + 1)
        .limit(n)
        .parallel()
        .reduce(0L, Long::sum);
}

//串行流: 286ms
public static long sequenceSumV1(long n) {
    return Stream.iterate(1L, i -> i + 1)
        .limit(n)
        .reduce(0L, Long::sum);
}

//迭代: 12ms
public static long iterativeSum(long n) {
    long result = 0;
    for (int i = 1; i <= n; i++) {
        result = +i;
    }
    return result;
}

//使用Function<T, T>函数式接口, 声明一个执行时长的函数
//Function接口适用于只有一个入参, 只有一个输出结果的那些函数, 泛型就是参数类型和返回值类型
private static long test(Function<Long, Long> computer, long n) {
    long fastest = Long.MAX_VALUE;
    for (int i = 0; i < 10; i++) {
        long start = System.currentTimeMillis();
        System.out.println("result is :" + computer.apply(n));
        long cost = System.currentTimeMillis() - start;
        if (cost < fastest) {
            fastest = cost;
        }
    }
    return fastest;
}

public static void main(String[] args) {
    long n = 20_000_000;
    System.out.println("顺行流:" + test(ParallelStreamDemo::sequenceSum, n));
    System.out.println("并行流:" + test(ParallelStreamDemo::parallelSum, n));
    System.out.println("迭代:" + test(ParallelStreamDemo::iterativeSum, n));
}
```

原因: 

> 1. Stream.iterator(1L, i -> i + 1) ==> 生成的是装箱对象Long, 必须拆箱之后才能相加; 
> 2. iterator很难分成独立的块, 并行执行. 因为其数据结构是一个链表而不是ArrayList, 后者不需要全部遍历就可以拆分到不同线程中, 但链表不行. 
> 3. 由于是依靠lambda表达式生成全部的数, 在并行的时刻, 数据还没有准备好. 
> 4. 总之, **某些流比其他流更容易并行化**

* 解决方案

```java
//用LongStream.rangeClosed(0, n)方法
//2ms
public static long parallelSum(long n) {
    return LongStream.rangeClosed(0, n).parallel().reduce(0L, Long::sum);
}

//10ms
public static long sequenceSum(long n) {
    return LongStream.rangeClosed(0, n).reduce(0L, Long::sum);
}
```

> 该方法生成的不是装箱对象Long, 而且在parallel()方法之前, 已经将数据全部生成

### 2. 使用并行流容易出现线程安全问题

```java
public class Counter {
	public long total = 0;
	public void add(long value) {
		total += value;
	}
}
```

在另外一个类中

```java
private static long wrongSum(long n) {
    Counter counter = new Counter();
    LongStream.rangeClosed(0, n).parallel().forEach(counter::add);
    return counter.total;
}

private static long test(Function<Long, Long> computer, long n) {
    long fastest = Long.MAX_VALUE;
    for (int i = 0; i < 10; i++) {
        long start = System.currentTimeMillis();
        System.out.println("result is :" + computer.apply(n));
        long cost = System.currentTimeMillis() - start;
        if (cost < fastest) {
            fastest = cost;
        }
    }
    return fastest;
}
```

在test方法中, 执行10次, 每次算出的结果(总和)都不相同. 说明出现了线程安全问题.



## jdk8中的Future

### Future Demo

```java
public class FutureDemo {
    public static void main(String[] args) throws Exception {

        ExecutorService executorService = Executors.newCachedThreadPool();
        System.out.println(System.currentTimeMillis() + " start"); //1

        Future<String> futute = executorService.submit(FutureDemo::doSomeLongOperation);//2
        System.out.println(System.currentTimeMillis() + " : xxxx"); //3

        String result = futute.get(1, TimeUnit.SECONDS);
        System.out.println(System.currentTimeMillis() + " " + result); //4 比3处晚1s
    }

    public static String doSomeLongOperation() throws InterruptedException {
        Thread.sleep(1000);
        return "123";
    }
}

//=====================================================================

public class FutureDemo {
    public static void main(String[] args) throws Exception {

        ExecutorService executorService = Executors.newCachedThreadPool();
        System.out.println(System.currentTimeMillis() + " start"); //1

        Future<String> future = executorService.submit(FutureDemo::doSomeLongOperation);//2
        System.out.println(System.currentTimeMillis() + " : xxxx"); 
        Thread.sleep(1000); 
        System.out.println(System.currentTimeMillis() + "yyyyyyy"); //3

        String result = future.get(1, TimeUnit.SECONDS);
        System.out.println(System.currentTimeMillis() + " " + result); //4 和3处时间一致. 说明在主线程执行sleep1s的过程中, 执行耗时任务的新线程已经执行结束了, get方法可以立即返回了.
    }

    public static String doSomeLongOperation() throws InterruptedException {
        Thread.sleep(1000);
        return "123";
    }
}
```

1. 所谓的Future, 是用在那些需要调用一个很耗时的任务的场景中的, 比如本例中的`doSomeLongOperation`.
2. 在主线程执行的过程中, 通过线程池新创建了一个线程, 用Future的方法执行那个耗时的任务. 也就是2处, 通过submit提交了这个Callable线程. 
3. 本来, 这个耗时线程不执行完, 主线程也不能做其他的事, 但使用Future之后, 主线程可以立即返回, 执行其他的任务. 比如3处, 打印了一段话.
4. 直到主线程不得不依赖Future所返回的结果时, 我们再通过future.get方法, 拿到让新线程执行的耗时任务的返回结果. (在主线程执行过程中, 很可能future那个耗时任务已经完成了. 所以再次调用get方法获取值的时候, 会直接返回.
5. 可以在get方法中指定, 等待多长时间, 如果还没有返回, 会抛出一个`TimeoutException`


## jdk8中的CompletableFuture

Future的Demo无法描述不同Future结果之间的依赖关系.

CompletableFuture 类实现了 Future 接口.

```java
class CompletableFuture<T> implements Future<T>, CompletionStage<T>
```

> 使用场景:
>
> 查询10个商店的商品价格, 异步的返回.
>
> 如果是循环查询, 也就是商店1查到后返回, 查询商店2, 商店2查到之后返回, 查询商店3...
>
> 但这样容易产生问题, 如果商店3一直不返回, 则阻塞了

`CompletableFuture`适用于上述场景. 不过, 它不是循环的等待, 而是只要有一个查到(比如第九个商店最先查到价格, 则立即返回, 更新价格表)就返回.

### 1. 第一个例子

```java
public class Shop {

    private String name;

    public Shop(String name) {
        this.name = name;
    }

    private Random random = new Random();
	
    //模拟远程调用的延时
    private void delay() {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    //同步获取商品价格的方法
    private Double getPrice(String product) {
        delay();
        return random.nextDouble() * 100;
    }

    //异步获取商品价格的方法(所谓异步, 是指返回的是一个异步的包装对象Future<Double>)
    public Future<Double> getPriceAsync(String product) {
        CompletableFuture<Double> futurePrice = new CompletableFuture<>();
        //futurePrice.complete()方法, 是对耗时操作的一个包装, 包装成异步方法.
        //start()就是开了一个新线程来执行
        new Thread(() -> futurePrice.complete(getPrice(product))).start();
        return futurePrice;
    }

    public static void main(String[] args) throws Exception {
        Shop shop = new Shop("bestShop");
        long start = System.currentTimeMillis();
        Future<Double> futurePrice = shop.getPriceAsync("some product");
        System.out.println("调用返回,耗时:" + (System.currentTimeMillis() - start)); //97
        //这里可以让主线程做一些其他的操作
        double price = futurePrice.get();
        System.out.println("价格返回,耗时:" + (System.currentTimeMillis() - start)); //1098
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
```

#### 改进一: getPriceAsync 

```java
public Future<Double> getPriceAsync(String product) {
    //supplyAsync方法接收一个Supplier对象, 把一个同步方法转成异步方法, 返回一个Future对象.
    //supplyAsync方法如果只有一个参数, 则默认使用的线程池的大小是电脑的核数.
    //supplyAsync方法也可以指定第二个参数, 也就是自定义线程池
    //supplyAsync方法内部会对异常进行处理, 所以一定要这样写而不是自己new CompletableFuture. 否则会因为产生异常而导致线程阻塞.
    return CompletableFuture.supplyAsync(() -> getPrice(product));
}
```

#### 改进二: 提供查询服务(循环方式)

上述的Shop类是不同商店提供的查询价格的方法getPrice(), 我们需要写一个findPrices方法, 去不同商店查询价格, 并返回给用户.

```java
public class PriceDemo {
    private List<Shop> shops = Arrays.asList(
            new Shop("shop1"),
            new Shop("shop2"),
            new Shop("shop3"),
            new Shop("shop4"),
            new Shop("shop5"),
            new Shop("shop6"),
            new Shop("shop7"),
            new Shop("shop8"));

    //把Shop类, 当成流, 循环每个流, 然后把shop类转成字符串, 显示不同商店的商品价格
    public List<String> findPrices(String product) {
        return shops.stream().map(
                shop -> String.format("%s price is %.2f", shop.getName(), shop.getPrice(product)))
                .collect(Collectors.toList());
    }

    public static void main(String[] args) {
		System.out.println(Runtime.getRuntime().availableProcessors());
        PriceDemo priceDemo = new PriceDemo();
        long start = System.currentTimeMillis();
		System.out.println(priceDemo.findPrices("iPhone7"));
        System.out.println("服务耗时:" + (System.currentTimeMillis() - start));
    }
}
```

> 如果是8核的cpu, 因为是循环查询8个店, 每个店都延时1s(delay方法中定义的), 则共耗时8s.

#### 改进三: 把findPrices方法改成parallel并行流

```java
public List<String> findPrices(String product) {
    return shops.stream().parallel().map(
        shop -> String.format("%s price is %.2f", shop.getName(), shop.getPrice(product)))
            .collect(Collectors.toList());
}
```

> 这样, 会把8个循环分到8个线程中执行, 每个都延时1s, 所以总共耗时也是1s

#### 改进四: 使用CompletableFuture

```java
public List<String> findPricesByCompletableFuture(String product) {
    List<CompletableFuture<String>> priceFuture = shops.stream().map(
            shop -> CompletableFuture.supplyAsync(() -> String.format("%s price is %.2f", shop.getName(), shop.getPrice(product)))
    ).collect(Collectors.toList());

    //这里的join方法和get方法相同, 都是拿到Future的返回结果.
    //只是join方法不会抛出异常. 所以使用join方法
    return priceFuture.stream().map(CompletableFuture::join).collect(Collectors.toList());
}
```

> 耗时为2s

四与三相比, 结果令人失望. 因为代码复杂了, 耗时却增加了.

但是, 如果当商店数量为17个的时候, parallel方式, 会耗时3s, CompletableFuture也会耗时3s, 这是因为当我们不指定CompletableFuture的线程池的时候, 默认会和parallel一样使用cpu本身的核数作为线程池的大小.

但对于远程调用这种场景, 我们可以自定义一个拥有多个线程的线程池来加快速度. 而这种自定义, 只能在CompletableFuture中实现. parallel是无法实现的. 这就是改进五.

#### 改进五: 增加自定义线程池

```java
public List<String> findPricesByCompletableFuture(String product) {
	//自定义线程池
    Executor executor = Executors.newFixedThreadPool(Math.min(shops.size(), 100));

    List<CompletableFuture<String>> priceFuture = shops.stream().map(
            shop -> CompletableFuture.supplyAsync(() -> String.format("%s price is %.2f", shop.getName(), shop.getPrice(product)), executor)
    ).collect(Collectors.toList());

    //这里的join方法和get方法相同, 都是拿到Future的返回结果.
    //只是join方法不会抛出异常. 所以使用join方法
    return priceFuture.stream().map(CompletableFuture::join).collect(Collectors.toList());
}
```

> 耗时只有1s.
>
> 也就是说, 在大量的异步调用场景下, CompletableFuture + 自定义线程池是效率最高的方式.

* 如何计算线程池的线程数量

  ```java
  T = N * U * (1 + W / C)
  N: CPU的核数: Runtime.getRuntime().availableProcessors()
  U: 期望的CPU的利用率(0 ~ 1)
  W: 等待时间
  C: 计算时间
  ```

### 2. 增加打折服务

```java
//折扣的枚举类
public enum Discount {

    NONE(0), SILVER(5), GOLD(10), PLATINUM(15), DIAMOND(20);

    private final int percent;

    Discount(int percent) {
        this.percent = percent;
    }

    public int getPercent() {
        return percent;
    }
}

//封装返回给比价服务的实体类(包括商店名, 价格, 折扣)
public class Quote {

    private final String shop;
    private final double price;
    private final Discount discount;

    public Quote(String shop, double price, Discount discount) {
        this.shop = shop;
        this.price = price;
        this.discount = discount;
    }

    public static Quote parse(String content) {
        String[] items = StringUtils.splitByWholeSeparatorPreserveAllTokens(content, ":");
        return new Quote(items[0], Double.parseDouble(items[1]), Discount.valueOf(items[2]));
    }

    public String getShop() {
        return shop;
    }

    public double getPrice() {
        return price;
    }

    public Discount getDiscount() {
        return discount;
    }
}

//Shop
public class Shop {

    private String name;

    public Shop(String name) {
        this.name = name;
    }

    private Random random = new Random();

    private void delay() {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    public Quote getPrice(String product) {
        delay();
        double price = random.nextDouble() * 100;
        Discount discount = Discount.values()[random.nextInt(Discount.values().length)];
        return String.format("%s:%.2f:%s", getName(), price, discount);
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
```

修改findPrices方法

```java
public List<String> findPricesByTwoCompletableFuture(String product) {

    Executor executor = Executors.newFixedThreadPool(Math.min(shops.size(), 100));

    List<CompletableFuture<String>> futurePrices = shops.stream()
        .map(shop -> CompletableFuture.supplyAsync(() -> shop.getPrice(product), executor))
        .map(future -> future.thenApply(Quote::parse)) //getPrice方法返回字符串, 作为这里的输入参数, thenApply执行的是同步操作, 进行parse, 变成Quote对象
        //进行下一个异步操作, 也就是折扣服务, 传入quote对象, 进行applyDiscount服务, 要用CompletableFuture转成异步执行
        //thenCompose方法是连接两个异步操作的方法
        //thenCompose方法连接的这两个异步操作必须有先后顺序, 也就是上一个异步方法结束后, 才会执行下一个异步方法/
        .map(future -> future.thenCompose(quote ->
                                          CompletableFuture.supplyAsync(() -> DiscountDemo.applyDiscount(quote))))
        .collect(Collectors.toList());
}
```

> 总共耗时2s, 因为执行了查价格, 查折扣两个异步操作

### 3. 增加一个查询汇率的服务

这个查询汇率的服务和查询价格查询折扣之间没有依赖关系. 这时要用thenCombine, 只要结合这两个异步操作的结果即可. 查询汇率的异步操作不需要等待查询价格的异步操作完成之后再操作(thenCombine). 而查询折扣的异步操作需要等到查询价格的异步操作结束后才能执行.(thenCompose)

```java
public List<String> findPrices(String product) {
    Executor executor = Executors.newFixedThreadPool(100);

    List<CompletableFuture<String>> priceFuture = shops.stream()
        .map(shop ->
             //第一个异步操作: 查询价格
             CompletableFuture
             .supplyAsync(() -> shop.getPrice(product), executor)
             //第二个异步操作: 查询汇率(与第一个操作同时执行, 要开两个线程)
             .thenCombine(
                 CompletableFuture.supplyAsync(
                     () -> ExchangeDemo.getRate("USD", "CNY"), executor
                 ),
                 //两个异步操作完成之后, 进行的操作
                 (quote, rate) -> new Quote(quote.getShop(), quote.getPrice() * rate, quote.getDiscount())
             )
            )
        //第三个异步操作
        .map(future -> future.thenCompose(quote -> CompletableFuture.supplyAsync(() -> DiscountDemo.applyDiscount(quote), executor)))
        .collect(Collectors.toList());

    return priceFuture.stream().map(CompletableFuture::join).collect(Collectors.toList());
}
```

### 4. 不等所有商店全部返回, 只要有一个返回就显示

* 修改延时方法, 变成随机延时

  ```java
  //随机延时
  public void delay() {
      int delay = 500 + random.nextInt(2000);
      try {
          Thread.sleep(delay);
      } catch (Exception e) {
          throw new RuntimeException(e);
      }
  }
  ```

* 修改findPrices方法

  ```java
  public void findPrices(String product) {
      long start = System.currentTimeMillis();
      Executor executor = Executors.newFixedThreadPool(100);

      CompletableFuture<?>[] priceFuture =
          shops.stream()
          .map(shop ->
               CompletableFuture
               .supplyAsync(() -> shop.getPrice(product), executor)
               .thenCombine(
                   CompletableFuture.supplyAsync(
                       () -> ExchangeDemo.getRate("USD", "CNY"), executor
                   ),
                   (quote, rate) -> new Quote(quote.getShop(), quote.getPrice() * rate, quote.getDiscount())
               )
              )
          .map(future -> future.thenCompose(quote -> CompletableFuture.supplyAsync(() -> DiscountDemo.applyDiscount(quote), executor)))

          //thenAccept方法定义了如何处理CompletableFuture最终返回的结果
          .map(future -> future.thenAccept(content ->
                                           System.out.println(content + " (done in " + (System.currentTimeMillis() - start ) + " msecs)")))
          .toArray(size -> new CompletableFuture[size]);
      
      //所有都执行完毕后的处理
      CompletableFuture.allOf(priceFuture).thenAccept((obj) -> System.out.println("all done" + obj));
      
      //所有都执行完毕后的处理
      CompletableFuture.anyOf(priceFuture).thenAccept((obj) -> System.out.println("fastest done" + obj));
  }
  ```

  ​

## 线程池的创建规则

线程池不允许使用Executors创建, 而是通过ThreadPoolExecutor的方式. 这样的处理方式让写的同学更加明确线程池的运行规则, 规避资源耗尽的风险.

说明： Executors 返回的线程池对象的弊端如下
1） FixedThreadPool 和 SingleThreadPool :
允许的请求队列长度为 Integer.MAX_VALUE ，可能会堆积大量的请求，从而导致 OOM 。
2） CachedThreadPool 和 ScheduledThreadPool :
允许的创建线程数量为 Integer.MAX_VALUE ，可能会创建大量的线程，从而导致 OOM 。

```java
public class Demo {
    public static void main(String[] args) {

        ThreadFactory namedThreadFactory = new ThreadFactoryBuilder()
                .setNameFormat("demo-pool-%d").build();

        ExecutorService pool = new ThreadPoolExecutor(
                5,
                200,
                0L,
                TimeUnit.MILLISECONDS,
                new LinkedBlockingQueue<Runnable>(1024),
                namedThreadFactory,
                new ThreadPoolExecutor.AbortPolicy()
        );

        pool.execute(() -> System.out.println(Thread.currentThread().getName()));
        pool.shutdown();
        
        //==================================================
        //引入org.apache.commons.lang3包
        ScheduledExecutorService executorService = new ScheduledThreadPoolExecutor(
                1,
                new BasicThreadFactory.Builder().namingPattern("example-schedule-pool-%d")
                .daemon(true)
                .build()
        );
    }
}

ThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue) 构造方法: 
		corePoolSize
			核心线程数，默认情况下核心线程会一直存活，即使处于闲置状态也不会受存keepAliveTime限制。除非将allowCoreThreadTimeOut设置为true。
		maximumPoolSize
			线程池所能容纳的最大线程数。超过这个数的线程将被阻塞。当任务队列为没有设置大小的LinkedBlockingDeque时，这个值无效。	
		keepAliveTime
			非核心线程的闲置超时时间，超过这个时间就会被回收。
		unit
			指定keepAliveTime的单位，如TimeUnit.SECONDS。当将allowCoreThreadTimeOut设置为true时对corePoolSize生效。
		workQueue
			线程池中的任务队列.
			常用的有三种队列，SynchronousQueue, LinkedBlockingDeque, ArrayBlockingQueue。
		threadFactory
			线程工厂，提供创建新线程的功能。ThreadFactory是一个接口，只有一个方法
		RejectedExecutionHandler
			当线程池中的资源已经全部使用，添加新线程被拒绝时，会调用RejectedExecutionHandler的rejectedExecution方法

	如果线程数量 <= 核心线程数量，那么直接启动一个核心线程来执行任务，不会放入队列中。
	如果线程数量 > 核心线程数，但 <= 最大线程数，并且任务队列是LinkedBlockingDeque的时候，超过核心线程数量的任务会放在任务队列中排队。
	如果线程数量 > 核心线程数，但 <= 最大线程数，并且任务队列是SynchronousQueue的时候，线程池会创建新线程执行任务，这些任务也不会被放在任务队列中。这些线程属于非核心线程，在任务完成后，闲置时间达到了超时时间就会被清除。
	如果线程数量 > 核心线程数，并且 > 最大线程数，当任务队列是LinkedBlockingDeque，会将超过核心线程的任务放在任务队列中排队。也就是当任务队列是LinkedBlockingDeque并且没有大小限制时，线程池的最大线程数设置是无效的，他的线程数最多不会超过核心线程数。
	如果线程数量 > 核心线程数，并且 > 最大线程数，当任务队列是SynchronousQueue的时候，会因为线程池拒绝添加任务而抛出异常。
```

