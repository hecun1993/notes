## Spring Boot 缓存

### 先查缓存再查数据库

```java
//直接引入spring-redis依赖即可, 不用做java配置, 可以添加properties中的连接池配置

@Autowired
private StringRedisTemplate redisTemplate;

/**
     * 1.首先通过缓存获取
     * 2.不存在将从通过数据库获取用户对象
     * 3.将用户对象写入缓存，设置缓存时间5分钟
     * 4.返回对象
     *
     * @param id
     * @return
 */
public User getUserById(Long id) {
    String key = "user:" + id;
    String json = redisTemplate.opsForValue().get(key);
    User user = null;
    if (Strings.isNullOrEmpty(json)) {
        user = userMapper.selectById(id);
        String string = JSON.toJSONString(user);
        redisTemplate.opsForValue().set(key, string);
        redisTemplate.expire(key, 5, TimeUnit.MINUTES);
    } else {
        user = JSON.parseObject(json, User.class);
    }
    return user;
}
```

```properties
# spring为redis提供了默认的连接池
# 定义最大连接数
spring.redis.pool.max-active=3
spring.redis.host=localhost
spring.redis.port=6379
spring.redis.timeout=6000
```



### 主页的缓存方法

比如要缓存房屋的列表, 则应该使用两个缓存

#### 1. houseIndexs: 存储所有的id到缓存中, 而不是存储数据对象本身的List到缓存.

key => houseIndexs 

value => 1, 2, 3, 4, 5...

#### 2. houseItem:

key => 1

value => JSON形式的字符串, 是House实体类转成的字符串.

#### 优势

在添加缓存的时候可以直接对houseIndexs进行操作, 不用关心具体的houseItem, 节省网络传输的数据量.



#### 当添加/修改商品时service层.

首先修改数据库

如果修改成功, 则修改缓存.

首先判断indexUuids对应的value是否存在, 如果不存在, 则初始化一个indexUuids. 如果存在, 则修改indexUuids对应的value, 也就是加上一个", House.getId()". 然后再把房屋对象设置到缓存中, 以房屋id为key, 房屋对象的json数据为value.

#### 当删除商品时service层.

首先修改数据库

然后修改indexUuids. 有两种方式, 一种是将indexUuids字符串转成数字的集合, 循环寻找匹配值, 然后删除该缓存,再将indexUuids结果重新放入缓存中.

另一种方案是将indexUuids当成字符串处理, 如果传入的要删除的id匹配在了首位或者末尾(uuids.startWith(uuid + ",")), 则截取字符串来删除这个id即可; 否则, 则通过replace, ",uuid," => ","