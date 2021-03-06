## Guava Cache

### 说明

是一个全内存的本地缓存实现，它提供了线程安全的实现机制。

缓存中存放的数据总量不会超出内存容量。

### 令牌桶和漏桶的机制

* RateLimiter.create() 
* RateLimiter.acquire()

#### 1. 规定每秒可以发requestNum个请求

```java
RateLimiter rateLimiter = RateLimiter.create(requestNum, 1, TimeUnit.SECONDS);
```

#### 2. 进行循环

```java
while (flag) {
  //执行下句之后,saveRecord才可以执行,相当于控制速度(每秒只能执行requestNum次)
  rateLimiter.acquire();
  //业务逻辑
}
```

### 使用方法

#### 定义本地缓存localCache

```java
private static LoadingCache<String, String> localCache = CacheBuilder.newBuilder()
        .initialCapacity(1000)
        .maximumSize(10000)
        .expireAfterAccess(12, TimeUnit.HOURS)
        .build(new CacheLoader<String, String>() {
            //当调用get取guava缓存中的值时,如果键名key没有对应的键值,就调用这个方法进行返回值
            //这里是说,如果没有值的话,就返回"null"这个字符串
            @Override
            public String load(String s) throws Exception {
                return "null";
            }
        });
```

#### 使用缓存

```java
public static String getKey(String key) {
    String value;
    try {
        value = localCache.get(key);
        //如果执行了if,也就是返回了null,就说明,之前没有向缓存中添加键值对,现在却要取值,所以会返回"null"这个字符串
        //最终的结果是,从缓存中取值,获得了null
        if ("null".equals(value)) {
            return null;
        }
        return value;
    } catch (Exception e) {
        logger.error("localCache get error", e);
    }
    return null;
}
```



### 漏桶算法

```java
@Override
public void monitorUserMatrix(int requestNum, String roundId) {
    List<Mapping> mappings = mappingService.getAllCustomMapping();

    //1. 规定每秒可以发requestNum个请求
    RateLimiter rateLimiter = RateLimiter.create(requestNum, 1, TimeUnit.SECONDS);
	
    //不断循环
    while (!Thread.currentThread().isInterrupted()) {
        for (Mapping mapping : mappings) {
            //2. 获得执行的权限, 从而实现每秒可以发多少个请求
            rateLimiter.acquire();
            log.info("Custom monitor, matrix is {}, source is {}", mapping.getMatrix(), mapping.getSource());
            recordService.saveUserMatrix(mapping.getMatrix(), mapping.getSource(), roundId);
        }
    }
}
```

### 