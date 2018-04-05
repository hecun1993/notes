## Spring Boot 与 MongoDB

### 单数据源

引入pom依赖: spring-boot-starter-data-mongodb

```properties
spring.data.mongodb.uri=mongodb://name:pass@localhost:27017/test
# 多集群配置
spring.data.mongodb.uri=mongodb://user:pwd@ip1:port1,ip2:port2/database
```

单数据源可以不配置MongoDBFactory, 直接在DAO类中用@Autowired注入MongoTemplate

```java
@Autowired
private MongoTemplate mongoTemplate;

//MongoTemplate的API
//1. 查询操作
Query query = new Query();
query.addCriteria(Criteria.where("email").is(email).and("_id").is(new ObjectId(id)));
//分页, 排序查询
query.with(new Sort(Sort.Direction.DESC, Constants.START));
int skip = (pageModel.getPageNo() - 1 > 0) ? pageModel.getPageNo() - 1 : 0;
query.skip(skip * pageModel.getPageSize()).limit(pageModel.getPageSize());

//2. 更新操作
Query query = new Query(Criteria.where("id").is(user.getId()));
Update update = new Update();
update.set("userName", user.getUserName()).set("passWord", user.getPassWord());

UserEntity user = mongoTemplate.findOne(query, UserEntity.class);
//更新查询返回结果集的第一条
mongoTemplate.updateFirst(query, update, UserEntity.class);
//更新查询返回结果集的所有
mongoTemplate.updateMulti(query, update, UserEntity.class);
```

> ```
> MongoDB中存储的是标准时间，而通过System.currentTimeMillis()获得的是当前时区的时间，快8个小时.
> ```



- 配置文件的写法

```java
@Configuration
public class MultipleMongoConfig {

    @Autowired
    private MongoProperties mongoProperties;

    @Bean
    public MongoTemplate mongoTemplate() throws Exception {
        return new MongoTemplate(primaryFactory(mongoProperties));
    }

    @Bean
    public MongoDbFactory mongoDbFactory(MongoProperties mongoProperties) throws Exception {
        return new SimpleMongoDbFactory(new MongoClient(mongo.getHost(), mongo.getPort()), mongo.getDatabase());
    }
}
```



### 多数据源

1. yml文件

   ```yaml
   mongodb:
     primary:
       host: 192.168.9.60
       port: 20000
       database: test
     secondary:
       host: 192.168.9.60
       port: 20000
       database: test1
   ```

2. 读取不同的配置文件 && 不同包使用不同的数据源

   ```java
   @Data
   @ConfigurationProperties(prefix = "mongodb")
   public class MultipleMongoProperties {
       private MongoProperties primary = new MongoProperties();
       private MongoProperties secondary = new MongoProperties();
   }

   //不同数据源对应不同的包
   @Configuration
   @EnableMongoRepositories(basePackages = "com.neo.model.repository.primary",
           mongoTemplateRef = PrimaryMongoConfig.MONGO_TEMPLATE)
   public class PrimaryMongoConfig {
       protected static final String MONGO_TEMPLATE = "primaryMongoTemplate";
   }

   @Configuration
   @EnableMongoRepositories(basePackages = "com.neo.model.repository.secondary",
           mongoTemplateRef = SecondaryMongoConfig.MONGO_TEMPLATE)
   public class SecondaryMongoConfig {
       protected static final String MONGO_TEMPLATE = "secondaryMongoTemplate";
   }
   ```

3. 配置文件

   ```java
   @Configuration
   public class MultipleMongoConfig {
       
       @Autowired
       private MultipleMongoProperties mongoProperties;

       @Primary
       @Bean(name = PrimaryMongoConfig.MONGO_TEMPLATE)
       public MongoTemplate primaryMongoTemplate() throws Exception {
           return new MongoTemplate(primaryFactory(this.mongoProperties.getPrimary()));
       }

       @Bean
       @Qualifier(SecondaryMongoConfig.MONGO_TEMPLATE)
       public MongoTemplate secondaryMongoTemplate() throws Exception {
           return new MongoTemplate(secondaryFactory(this.mongoProperties.getSecondary()));
       }

       @Bean
       @Primary
       public MongoDbFactory primaryFactory(MongoProperties mongo) throws Exception {
           return new SimpleMongoDbFactory(new MongoClient(mongo.getHost(), mongo.getPort()),
                   mongo.getDatabase());
       }

       @Bean
       public MongoDbFactory secondaryFactory(MongoProperties mongo) throws Exception {
           return new SimpleMongoDbFactory(new MongoClient(mongo.getHost(), mongo.getPort()),
                   mongo.getDatabase());
       }
   }
   ```