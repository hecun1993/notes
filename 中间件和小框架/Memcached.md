## Memcached

一款高性能, 分布式的内存对象缓存**系统**

基于libevent事件处理实现无阻塞通信

Memcached是C语言编写的

Memcached提供了诸多主流语言的客户端

​	java_memcached[官方] 传统IO

​	spymemcached

​	xmemcached

### 安装

#### libevent

http://libevent.org/ 

- 1、解压缩

- 2、./configure --prefix=/opt/install/libevent

- 3、make

- 4、make install


#### memcached

http://memcached.org/

- 1、解压缩

- 2、./configure --prefix=/opt/install/memcached --with-libevent=/opt/install/libevent

- 3、make

- 4、make install


#### 启动参数

bin/memcached -d -u root -l 192.168.1.18 -p 2222 -c 128 -m 100 -P myPid

#### 操作

安装命令行工具 yum install -y telnet

telnet 192.168.1.18 2222

**telnet   ip地址   端口号**

然后输入命令即可



### XMemcached: 操作Memcached的工具

#### pom.xml

```xml
<dependency>
    <groupId>com.googlecode.xmemcached</groupId>
    <artifactId>xmemcached</artifactId>
    <version>2.4.0</version>
</dependency>
```

#### ConnectionHelper

1. 连接配置
2. 创建与服务端之间的连接[ip地址，端口号，用户名和密码]
3. 获取操作业务的对象(一般就是第二步中获取到的连接对象)
4. 操作业务
5. 关闭与服务器的连接

```java
public class ConnectionHelper {
    public static void main(String[] args) throws Exception {
        // 连接配置
        // 创建与服务端之间的连接[ip地址，端口号，用户名和密码]
        // 获取操作业务对象
        MemcachedClient memcachedClient = new XMemcachedClient("192.168.1.18", 2222);

        // 操作业务
        String str = "Hello Imooc!";
        boolean isSuccess = memcachedClient.set("k1", 3600, str);

        String value = memcachedClient.get("k1");
        System.out.println("value=" + value);

        // 关闭与服务端连接
        memcachedClient.shutdown();
    }
}
```

#### ShowApi: Java操作Memcached的API

##### UserModel: 必须实现Serializable接口(可以直接操作实体类)

```java
package com.imooc.jiangzh.user.vo;

import java.io.Serializable;

public class UserModel implements Serializable {

    private int uuid;
    private String userName;
    private int age;

    // 如果自己创建带参数的构造函数, 一定要写上空参的构造函数
    public UserModel() {
    }

    public UserModel(int uuid, String userName, int age) {
        this.uuid = uuid;
        this.userName = userName;
        this.age = age;
    }

    public int getUuid() {
        return uuid;
    }

    public void setUuid(int uuid) {
        this.uuid = uuid;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    @Override
    public String toString() {
        return "UserModel{" +
                "uuid=" + uuid +
                ", userName='" + userName + '\'' +
                ", age=" + age +
                '}';
    }
}
```

##### showApi

```java
// 新增【set,add】
// set 无论什么情况，都可以插入
// set  key  flags   exTime  length(value的字符串长度) -> value

// add 只有当key不存在的情况下，才可以插入
// add  key  flags   exTime  length -> value
public static void showAdd(UserModel um) throws Exception {
    MemcachedClient memcachedClient = ConnectonHelper.getClient();

    memcachedClient.set("set-user:" + um.getUuid(), 3600, um);
    memcachedClient.add("add-user:" + um.getUuid(), 3600, um);
}

// 修改【replace,append,prepend】
// replace 只修改已存在key的value值 如果key不存在，则不会进行操作
// replace  key  flags   exTime  length -> value

// append 追加后面内容
// append  key  flags   exTime  length -> value

// prepend 追加前面内容
// prepend  key  flags   exTime  length -> value

// length表示追加的长度而不是总长度
// 如果key不存在，则不会进行操作
public static void showUpdate(UserModel um) throws Exception {
    MemcachedClient memcachedClient = ConnectonHelper.getClient();

    memcachedClient.replace("set-user:" + um.getUuid(), 3600, um);
    // Hi! imooc jiangzh
    memcachedClient.prepend("k1", "Hi! ");
    memcachedClient.append("k1", " jiangzh");
}

// 查询【get/gets】
// get key
// gets key
// delete key
public static void showQuery(String key) throws Exception {
    MemcachedClient memcachedClient = ConnectonHelper.getClient();

    UserModel um = memcachedClient.get(key);
    System.out.println("get方法获取的值 = " + um);
}

// CAS操作, 检查更新, 包含以下两个方法, showGets和showCAS

// 1. gets方法返回的是带有版本号(long cas)和实体对象的封装类GetsResponse
public static GetsResponse<UserModel> showGets(String key) throws Exception {
    MemcachedClient memcachedClient = ConnectonHelper.getClient();

    GetsResponse<UserModel> gets = memcachedClient.gets(key);
    return gets;
}

// 2. 检查更新【cas】
// Check And Set
// 输入待修改的数据+版本号 Memcached检测版本号是否正确 如果正确，则修改数据
// cas  key  flags  exTime  length  version  -> value
public static void showCAS(UserModel um) throws Exception {
    MemcachedClient memcachedClient = ConnectonHelper.getClient();

    String key = "set-user:" + um.getUuid();

    // 1. 先获取版本号
    GetsResponse<UserModel> userModelGetsResponse = showGets(key);
    long cas = userModelGetsResponse.getCas();

    // 2. 将版本号当成参数, 传入memcachedClient的cas方法, 进行更新操作
    boolean isSuccess = memcachedClient.cas(key, 3600, um, cas);
}

// 3. 验证如果更新时, 版本号cas有变化(有别的update操作, 比如append prepend repalce, 则无法进行cas的更新

// 检查更新【cas】
public static void showCAS(UserModel um) throws Exception {
    MemcachedClient memcachedClient = ConnectonHelper.getClient();

    String key = "set-user:" + um.getUuid();

    // 1. 先获取版本号
    GetsResponse<UserModel> userModelGetsResponse = showGets(key);
    long cas = userModelGetsResponse.getCas();

    // 2. 先用别的别的update操作, 比如append prepend repalce 更新, 再在第三步使用cas更新
    UserModel um1 = new UserModel(1, "imooc admin", 20);
    showUpdate(um1);

    // 3. 将初始的版本号(61行的cas)当成参数(此时真实的cas已经变化了), 传入memcachedClient的cas方法, 进行更新操作
    boolean isSuccess = memcachedClient.cas(key, 3600, um, cas);
    
    // 最终的结果, 第三步中的更新无效, 结果还是第二步中的更新值.

    // 问题：
    /*
            背景： 订单来了【10个电脑】， 检查库存【11个电脑】，修改库存数量，发货
            -> order
            ->  int num = checkWareHouse(...) -> 11  select
              -> 时间差 会造成多扣库存
            ->  update
            
            解决办法是, 去除select语句, 直接在update中查出, 比如只update库存大于购买数量的商品
            相当于利用了数据库的行级锁解决高并发问题
         */
}

// 数值操作【incr/decr】用于统计访问次数, 购买次数等操作.
// incr  key  增加偏移量
// decr  key  减少偏移量
// incr和decr只能操作能转换为数字的Value
// desr不能将数字减少至0以下
public static void showNumChange() throws Exception {

    MemcachedClient memcachedClient = ConnectonHelper.getClient();
    
    long result = memcachedClient.incr("k5", 5, 10);
    // 返回的是 result1 = 10  -> API【如果key不存在，则第三个参数为key的初始值】

    result = memcachedClient.incr("k5", 40, 10);
    // 返回的是 result2 = 50  -> 如果key存在，则进行递增或递减操作

    result = memcachedClient.decr("k5", 25, 10);
    // 返回的是 result3 = 25  -> 如果key存在，则进行递增或递减操作

    result = memcachedClient.decr("k5", 30, 10);
    // 返回的是 result4 = 0   -> decr是不能减出负数
}

// touch命令修改过期时间
public void showTouch() throws Exception {
    // 更新数据过期时间
    // 没有touch命令时的操作方法
    /*
        1、先存入一条数据 【设置过过期时间 10个小时】
        2、先获取待更新过期时间的数据
        3、再通过 replace | set 方法，将数据修改回去，同时设置过期时间
        */

    //使用touch命令
    /*
        1、先存入一条数据 【设置过过期时间 10个小时】
        2、直接使用touch进行更新过期时间
        */
    client.set("k1", 3600, "Hello imooc");
    client.touch("k1", 10);
}

// 操作XMemcached提供的CAS操作
public void showXMCAS() throws Exception {
    client.cas("k1", new CASOperation<String>() {
        // 重试次数
        public int getMaxTries() {
            return Integer.MAX_VALUE;
        }

        // 修改内容
        public String getNewValue(long cas, String currentValue) {
            // 返回值就是修改的内容
            // return "Hello imooc!";
            return "Hi ! " + currentValue + "！！！！！";
        }
    });
}

// XMemcached获取所有的key列表, 效率低
public void showKeyIterator() throws Exception {
    KeyIterator keyIterator = client.getKeyIterator(AddrUtil.getOneAddress("192.168.1.18:2222"));
    while (keyIterator.hasNext()) {
        System.out.println("keys=" + keyIterator.next());
    }
}

// XMemcached提供的计数器
public void showCounter() throws Exception {
    // 第三个参数是初始值
    Counter counter = new Counter(client, "k5", 10);
    // 加一
    long c1 = counter.incrementAndGet();
    // 减一
    long c2 = counter.decrementAndGet();
    // 加或减某一值
    long c3 = counter.addAndGet(88);
    long c4 = counter.addAndGet(-10000);
    long c5 = counter.get();
    String key = counter.getKey();
}

// memcached的命名空间
// 1. 设置命名空间为ns1
// 2. memcached会以 namespace:ns1 作为key, 生成的一长串数字作为value 存入memcached中
// 3. 然后再以这一长串数字 213712893719:key10 作为key, value作为value 存入memcached中
public void showNameSpace() throws Exception {
    // 定义两个namespace
    String ns1 = "ns1";
    String ns2 = "ns2";
    
    // 赋值操作
    client.withNamespace(ns1, new MemcachedClientCallable<String>() {
        public String call(MemcachedClient memcachedClient) throws MemcachedException, InterruptedException, TimeoutException {
            memcachedClient.set("k10", 0, " Hello jiangzh!! ");
            return null;
        }
    });

    // 获取不到key为k10的value
    String str = client.get("k10");

    // 加上命名空间来获取才可以
    String k10 = client.withNamespace(ns1, new MemcachedClientCallable<String>() {
        public String call(MemcachedClient memcachedClient) throws MemcachedException, InterruptedException, TimeoutException {
            return memcachedClient.get("k10");
        }
    });

    // 有值
    System.out.println("k10=" + k10);

    // 命名空间错误, 无值
    String k102 = client.withNamespace(ns2, new MemcachedClientCallable<String>() {
        public String call(MemcachedClient memcachedClient) throws MemcachedException, InterruptedException, TimeoutException {
            return memcachedClient.get("k10");
        }
    });

    // 无值
    System.out.println("k102=" + k102);
}

// flush_all 清空数据库
```

#### 生成Memcached客户端

```java
public static MemcachedClient getClient() {
    // Memcached支持文本协议和二进制协议. 通过Builder方式创建的MemcachedClient可以支持二进制协议
    MemcachedClientBuilder memcachedClientBuilder = new XMemcachedClientBuilder(AddrUtil.getAddresses("192.168.1.18:2222"));
    MemcachedClient memcachedClient = null;
    try {
        memcachedClient = memcachedClientBuilder.build();
    } catch (IOException e) {
        e.printStackTrace();
    }

    return memcachedClient;
}
```



### Memcached组成原理

#### Slab Allocator

##### Slab 内存容器

##### Page 小版的内存容器

##### Chunk "保险箱" 具体存放数据的地方

#### 注意

- Chunk是预分配大小的, 大小是80Byte

- 不同Slab的Chunk大小不一样

- 相同Slab的Chunk大小固定

- 宁可内存不整除被浪费，Chunk大小也不会变



- 自增长因子是1.25, 随着slab的变化, chunk的大小会增加为原来的1.25倍
- Slab Class Slab的一些元数据目录

#### 寻找Chunk的经历

##### Slot【垃圾桶】

* delete后，将Chunk标识放入Slot
* 数据过期，将Chunk标识放入Slot

##### 流程

- 在Slot中寻找不用的Chunk

- 使用空闲的Chunk

- 触发LRU流程



### Memcached分布式原理(集群)

#### 客户端分布式

客户端连接 XMemcached, XMemcached 连接多个Memcached服务器, 也会记录服务器列表(M1, M2, M3). 服务器的信息只有XMemcached知道, 每个服务器之间不互相通信. 通过算法保证数据的唯一性 (也就是记住每一个key到底存放在了哪台服务器上, 后续只到这个服务器上去取. 不管其他服务器上的值到底是多少.)

1、自身通过算法保障数据唯一性

2、集群形式对用户和Memcached都是透明的

3、Memcached的集群是通过客户端实现的

4、Memcached服务端相互不认识

#### 使用

只需要修改MemcachedClient的获取方式, API没有变化. 因为只有XMemcached知道是集群.

```java
public static MemcachedClient getClient() {
    // Memcached支持文本协议和二进制协议. 通过Builder方式创建的MemcachedClient可以支持二进制协议
    // 不同服务器之间是空格
    MemcachedClientBuilder memcachedClientBuilder = new XMemcachedClientBuilder(AddrUtil.getAddresses("192.168.1.18:2222 192.168.1.18:6666"));
    MemcachedClient memcachedClient = null;
    try {
        memcachedClient = memcachedClientBuilder.build();
    } catch (IOException e) {
        e.printStackTrace();
    }

    return memcachedClient;
}
```

#### 分布式算法

##### 余数Hash

- 将传入的key转成hash值
- 获取集群中服务器的数量
- 将hash值除以服务器数量, 取余数, 然后把数据放在对应的服务器上.
- 无论是查询还是存入, 算法不变. 则一个key会永远在一个服务器中

##### 优点: 简便易理解

##### 缺点: 如果服务器数量变化, 则所有存储数据的位置都会变化

##### 一致性Hash

将真实节点和虚拟节点映射在2的32次方的一个圆上. 如果数据命中虚拟节点, 则按顺时针方向, 存在对应的物理节点上.

##### Memcached的两段Hash

1. 是将数据**存储/查询**某个具体Memcached节点的时候, 选择余数Hash或者一致性Hash
2. 选择好Memcached节点后, 通过Hash算法, 找到具体的Chunk来存放数据.



### 与Spring Boot的整合

#### XMemcachedConfig

```java
package me.hds.memcached.config;

import net.rubyeye.xmemcached.KeyProvider;
import net.rubyeye.xmemcached.MemcachedClient;
import net.rubyeye.xmemcached.MemcachedClientBuilder;
import net.rubyeye.xmemcached.XMemcachedClientBuilder;
import net.rubyeye.xmemcached.command.BinaryCommandFactory;
import net.rubyeye.xmemcached.impl.KetamaMemcachedSessionLocator;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class XMemcachedConfig {

    @Autowired
    private XMemcachedProperties xMemcachedProperties;

    @Bean
    public MemcachedClientBuilder memcachedClientBuilder() {
        MemcachedClientBuilder memcachedClientBuilder;

        try {
            // String servers = "192.168.1.18:2222 192.168.1.18:6666";
            String servers = xMemcachedProperties.getServers();
            memcachedClientBuilder = new XMemcachedClientBuilder(servers);
            // XMemcached的配置
            // 1. 开启或关闭failure模式
            // 如果开启, 则遇到失败的节点, 直接返回错误.
            // 如果关闭, 则遇到失败的节点, 会寻找下一个
            memcachedClientBuilder.setFailureMode(false);

            // 2. 对key进行加密操作, 修改key的值
            memcachedClientBuilder.setKeyProvider(new KeyProvider() {
                @Override
                public String process(String key) {
                    return key + "_secret";
                }
            });

            // 3. 是否对将URL作为key的key进行编码
            // memcachedClientBuilder.setSanitizeKeys(false);
            memcachedClientBuilder.setSanitizeKeys(xMemcachedProperties.isSanitizeKeys());

            // 4. NIO处理, 所以10是很大的值了(连接池)
            // memcachedClientBuilder.setConnectionPoolSize(10);
            memcachedClientBuilder.setConnectionPoolSize(xMemcachedProperties.getPoolSize());

            // 5. 在服务器上, 建议配置成二进制的形式, 速度更快
            memcachedClientBuilder.setCommandFactory(new BinaryCommandFactory());

            // 6. 设置默认操作超时时间(默认的key的数据的超时时间)
            memcachedClientBuilder.setOpTimeout(3000);

            // 7. 设置客户端的Hash方式(默认是余数Hash, 可以配置成一致性Hash)
            memcachedClientBuilder.setSessionLocator(new KetamaMemcachedSessionLocator());

            return memcachedClientBuilder;
        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }

    @Bean
    public MemcachedClient memcachedClient(MemcachedClientBuilder memcachedClientBuilder) {
        MemcachedClient memcachedClient;

        try {
            memcachedClient = memcachedClientBuilder.build();
            return memcachedClient;
        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }
}
```

#### XMemcachedProperties

```java
package me.hds.memcached.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "memcached")
public class XMemcachedProperties {

    private String servers;
    private int poolSize;
    private boolean sanitizeKeys;

    public String getServers() {
        return servers;
    }

    public void setServers(String servers) {
        this.servers = servers;
    }

    public int getPoolSize() {
        return poolSize;
    }

    public void setPoolSize(int poolSize) {
        this.poolSize = poolSize;
    }

    public boolean isSanitizeKeys() {
        return sanitizeKeys;
    }

    public void setSanitizeKeys(boolean sanitizeKeys) {
        this.sanitizeKeys = sanitizeKeys;
    }
}
```

#### application.properties

```properties
memcached.servers = 192.168.1.18:2222 192.168.1.18:6666
memcached.poolSize = 10
memcached.sanitizeKeys = false
```



### Memcached的服务器调优

#### 调优思路

##### 提高内存的命中率 (能够从内存中读取到想要读取到的数据)

##### 减少内存浪费 (一个Chunk就是一个数据, 本来分配给一个Chunk是200B, 但可能只使用了130B)

##### 增加内存的重复利用率

#### 辅助调优命令

##### Stats

查看服务器的运行状态和内部数据

##### Stats settings

查看服务器的设置

##### Stats items/slabs

数据项统计 / 区块统计

