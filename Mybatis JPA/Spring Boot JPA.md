## Spring Boot JPA

### Spring Data JPA的配置

#### JPAConfig.java

```java
@Configuration
@EnableJpaRepositories(basePackages = "com.imooc.repository")
@EnableTransactionManagement
public class JPAConfig {
    /**
     * 配置数据源
     */
    @Bean
    //让数据源的属性自动注入
    @ConfigurationProperties(prefix = "spring.datasource")
    public DataSource dataSource() {
        return DataSourceBuilder.create().build();
    }

    /**
     * 配置实体类的管理
     */
    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory() {
        //使用的是Hibernate的ORM，所以要用HibernateJpaVendorAdapter来配置实体类管理
        HibernateJpaVendorAdapter japVendor = new HibernateJpaVendorAdapter();
        //我们自己控制sql的生成
        japVendor.setGenerateDdl(false);

        LocalContainerEntityManagerFactoryBean entityManagerFactory = new LocalContainerEntityManagerFactoryBean();
        //1. 设置数据源
        entityManagerFactory.setDataSource(dataSource());
        //2. 设置ORM框架
        entityManagerFactory.setJpaVendorAdapter(japVendor);
        //3. 设置扫描的实体类的包
        entityManagerFactory.setPackagesToScan("com.imooc.entity");
        return entityManagerFactory;
    }

    /**
     * 配置事务管理器
     */
    @Bean
    public PlatformTransactionManager transactionManager(EntityManagerFactory entityManagerFactory) {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(entityManagerFactory);
        return transactionManager;
    }
}
```

#### WebMvcConfig.java

```java
package com.imooc.config;

import org.modelmapper.ModelMapper;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;
import org.thymeleaf.extras.springsecurity4.dialect.SpringSecurityDialect;
import org.thymeleaf.spring4.SpringTemplateEngine;
import org.thymeleaf.spring4.templateresolver.SpringResourceTemplateResolver;
import org.thymeleaf.spring4.view.ThymeleafViewResolver;

/**
 * 实现ApplicationContextAware接口, 可以获取spring的上下文
 * 1. 实现ApplicationContextAware接口; 
 * 2. 实现其中的setApplicationContext方法;
 * 3. 设置一个属性为ApplicationContext, 然后在实现的方法中设置属性的值为方法的参数.
 */
@Configuration
public class WebMvcConfig extends WebMvcConfigurerAdapter implements ApplicationContextAware {

    @Value("${spring.thymeleaf.cache}")
    private boolean thymeleafCacheEnable = true;

    //这个就是获取的spring上下文，通过set方法注入值
    private ApplicationContext applicationContext;
    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
    }

    /**
     * 把静态资源如js css等加载到thymeleaf中的配置
     * 效果: 只要访问的路径是以static开头的, 那么就会到classpath:/static/下找资源.
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**").addResourceLocations("classpath:/static/");
    }

    /**
     * 1. 模板资源解析器
     */
    @Bean
    //利用spring的自动配置, 获取配置的值
    @ConfigurationProperties(prefix = "spring.thymeleaf")
    public SpringResourceTemplateResolver templateResolver() {
        SpringResourceTemplateResolver templateResolver = new SpringResourceTemplateResolver();
        //模板资源解析器需要指定ApplicationContext
        templateResolver.setApplicationContext(this.applicationContext);
        templateResolver.setCharacterEncoding("UTF-8");
        templateResolver.setCacheable(thymeleafCacheEnable);
        return templateResolver;
    }

    /**
     * 2. Thymeleaf标准方言解释器
     */
    @Bean
    public SpringTemplateEngine templateEngine() {
        SpringTemplateEngine templateEngine = new SpringTemplateEngine();
		// 设置资源解析器
        templateEngine.setTemplateResolver(templateResolver());
        // 支持Spring EL表达式
        templateEngine.setEnableSpringELCompiler(true);
        // 支持SpringSecurity方言(登录成功后,结合thymeleaf模版, 把已经登录的用户的用户名显示出来)
        SpringSecurityDialect securityDialect = new SpringSecurityDialect();
        templateEngine.addDialect(securityDialect);
        return templateEngine;
    }

    /**
     * 3. 视图解析器
     */
    @Bean
    public ThymeleafViewResolver viewResolver() {
        ThymeleafViewResolver viewResolver = new ThymeleafViewResolver();
        //设置模板引擎
        viewResolver.setTemplateEngine(templateEngine());
        return viewResolver;
    }

    /**
     * Bean Util，用于在pojo和dto之间的转化
     * @return
     */
    @Bean
    public ModelMapper modelMapper() {
        return new ModelMapper();
    }
}
```



#### JPA / Hibernate / JDBC

- JPA

  > Sun公司提供的JAVA的ORM规范, 也就是API.
  >
  > 表现形式是一组接口和注解, 目的是整合不同的ORM框架和技术.

- Hibernate

  > 是一种ORM框架.
  >
  > 核心: 用Java对对象的操作, 可以通过Hibernate框架, 转成对数据库表的操作.

- JDBC

  > 用于执行SQL语句的Java的API
  >
  > 打开连接; 生成statement; 执行SQL; 拿到ResultSet; 获取数据;

- Spring Data JPA

  > 封装了JPA接口, 所有对数据库的操作,变成了对Repository接口的操作.

#### QueryByExampleExecutor: 带有查询条件

Example适用于简单的和字符串有关的查询: 不能实现复杂的条件查询.

```java
// 根据某个例子来查询.
Book book = new Book();
book.setName("战争与和平");
Example<Book> example = Example.of(book);
bookRepository.findAll(example); // where name = ? (查询出书名和作为查询例子的书名相同的书)
```



```java
//模糊查询: 查出书名中包含(ExampleMatcher.StringMatcher.CONTAINING)着"战争"的书
Book book_like = new Book();
book.setName("战争");
ExampleMatcher exampleMatcher = ExampleMatcher.matching()
        .withStringMatcher(ExampleMatcher.StringMatcher.CONTAINING);
Example<Book> example_like = Example.of(book_like, exampleMatcher); // where name like ?
bookRepository.findAll(example_like);

//方法名查询: 只能查询, 无法新增或者修改
findByNameLikeOrderByNameDesc("%战争%");
```



##### 静态查询

```java
// JPQL: 本来可以通过方法名查询, 不用写JPQL语句, 但是方法名太长, 所以有下面这些JPQL语句	
// JPA查询语言: 针对的是对象的名字Book和对象的属性book.name, 而不是针对表名(hds_book)和字段名
@Query("from Book b where b.name like ?1 and b.category.name = ?2 order by b.name desc")
@Query("from Book b left join b.category c where b.name like ?1 and c.name = ?2 order by b.name desc")
@Query("select b from Book b left join b.category c where b.name like ?1 and c.name = ?2 order by b.name desc")
@Query("select count(b.id) from Book b left join b.category c where b.name like ?1 and c.name = ?2 order by b.name desc")
Page<Book> findBooks(String bookName, String categoryName, Pageable pageable, Sort sort);

@Query("update Book b set b.name = ?1 and b.id = ?2")
@Modifying  //更新语句时要多加的注解
int updateBook(String bookName, Long bookId);

// 也支持原生sql, 但要多加一个属性nativeQuery
@Query(value = "select * from hds_book where hds_id = ?1", nativeQuery = true)
@Modifying  //更新语句时要多加的注解
int updateBook(String bookName, Long bookId);
```



##### 动态查询

> 有时需要where语句,有时又不需要,需要动态拼装

```java
// BookRepository 要单独继承 JpaSpecificationExecutor<Book>: 用来做动态查询
Specification<Book> specification = new Specification<Book>() {
    public Predicate toPredicate(Root<Book> root, CriteriaQuery<?> criteriaQuery, CriteriaBuilder criteriaBuilder) {
        //组合设计模式, 自身既是容器也是实体
        Predicate predicate1 = criteriaBuilder.equal(root.get("name"), "战争与和平");
        Predicate predicate2 = criteriaBuilder.equal(root.get("category").get("name"), "世界名著");
        Predicate predicate3 = criteriaBuilder.and(predicate1, predicate2);
        //指定左外连接
        //这样就可以一次把书和类目的信息全部查出
        root.fetch("category", JoinType.LEFT);
        return predicate3;
    }
};

bookRepository.findOne(specification);
```

##### JpaRepository

```java
// getOne(): 不执行sql, 直接返回
// findOne(): 执行sql的select查询出来
// 将类似findAll()等方法的返回值由Iterator变成List
// 提供了一个flush()方法
```

##### PagingAndSortingRepository

> 提供了分页查询
>
> 每个方法都可以接受Sort sort, Pageable pageable这两个参数

```java
bookRepository.findAll(new Sort(Sort.Direction.DESC, "name", "id"));
bookRepository.findAll(new Sort(new Order(Direction.DESC, "name"), new Order(Direction.ASC, "id")));

Pageable(接口) pageable = new PageRequest(实现类)(page, size, sort);
Page<Book> books = bookRepository.findAll(pageable);

//Page对象的内置方法
books.getContent(): 一页中的所有数据
books.getNumber(): 当前页数
books.getNumberOfElements(): 当前页有多少个元素
books.getSize(): 每页多少条
books.getTotalElements(): 总记录数
books.getTotalPages(): 总页数
```

##### CrudRepository

> 提供了基本的增删改查方法

```java
// save: 创建和修改一个对象或者一个集合(根据id属性是否有值来判断是新增还是更新);
// 有个注解是@NoRepositoryBean, 就是告诉Spring不要为CrudRepository生成代理, 因为他不具体的去操作数据库
```

##### Repository

```java
// 没有任何方法, 只是一个标记接口, spring启动时, 会为继承他的类(BookRepository)生成代理, spring注入的是代理对象
```

##### 自定义Repository

```java
/**
 * 第一步,创建这个类(不再是接口了!), 继承SimpleJpaRepository, 重写save等方法, 加上记录日志等业务代码
 * 第二步: 在启动类上加注解
    @EnableJpaRepositories(repositoryBaseClass = BookShopRepositoryImpl.class)
    public class BookShopApplication {}
 */
public class BookShopRepositoryImpl<T> extends SimpleJpaRepository<T, Long> {
    public BookShopRepositoryImpl(JpaEntityInformation<T, ?> entityInformation, EntityManager entityManager) {
        super(entityInformation, entityManager);
    }

    @Override
    public <S extends T> S save(S entity) {
        System.out.println("记录了日志" + entity.getClass().getSimpleName());
        return super.save(entity);
    }
}
```

##### properties文件的配置

```properties
spring.datasource.driver-class-name = com.mysql.jdbc.Driver
spring.datasource.url = jdbc:mysql://127.0.0.1:3306/bookshop?useUnicode=yes&characterEncoding=UTF-8&useSSL=false
spring.datasource.username = root
spring.datasource.password = root
spring.jpa.generate-ddl = true
spring.jpa.hibernate;naming;implicit-strategy = me.hds.support.HDSNameStrategy
spring.jpa.show-sql = true
spring.jpa.properties.hibernate.format_sql = true
```



### 表结构与java对象的映射

```java
java: Long -> BIGINT
java: String -> VARCHAR
java: int -> INT
java: Date -> DATETIME(默认)
```

> 封装查询条件时, 数字类型要用包装类Integer. 因为包装类型可以取null值, 表示该查询条件不存在. 如果是int类型, 则默认值是0, 用户年龄是0岁不合理.



### 主键产生策略

通过GenerationType来指定。GenerationType是一个枚举，它定义了主键产生策略的类型。

- AUTO　自动选择一个最适合底层数据库的主键生成策略。如MySQL会自动对应auto increment。这个是默认选项，即如果只写@GeneratedValue，等价于@GeneratedValue(strategy=GenerationType.AUTO)。
- IDENTITY　表自增长字段，Oracle不支持这种方式。
- SEQUENCE　通过序列产生主键，MySQL不支持这种方式。
- TABLE　通过表产生主键，框架借由表模拟序列产生主键，使用该策略可以使应用更易于数据库移植。不同的JPA实现商生成的表名是不同的，如 OpenJPA生成openjpa_sequence_table表，Hibernate生成一个hibernate_sequences表，而TopLink则生成sequence表。这些表都具有一个序列名和对应值两个字段，如SEQ_NAME和SEQ_COUNT。

> 在我们的应用中，一般选用@GeneratedValue(strategy=GenerationType.AUTO)这种方式，自动选择主键生成策略，以适应不同的数据库移植。
>
> ```java
> @Id
> @GeneratedValue(strategy = GenerationType.IDENTITY)
> private Long id;
> ```



#### 统一给表名加前缀

```java
package me.hds.support;

import org.hibernate.boot.model.naming.Identifier;
import org.hibernate.boot.model.naming.ImplicitNamingStrategyJpaCompliantImpl;
import org.hibernate.boot.spi.MetadataBuildingContext;

/**
 * 1.统一给表名和字段名前加前缀, 需要自己config
 * 2.在application.yml中配置使用自己的生成表名策略
 *  spring.jpa.hibernate.naming.implicit-strategy = me.hds.support.HDSNameStrategy
 */
public class HDSNameStrategy extends ImplicitNamingStrategyJpaCompliantImpl {

    //command + shift + i
    private static final long serialVersionUID = 7978773882210242492L;

    //control + o ==> 重写父类方法
    //生成表名和字段名的方法
    //有的数据库表名需要加前缀, 但是jpa不能默认统一加前缀, 就需要重写这个方法, 在第一个参数(最终生成的表名)前加上前缀即可
    @Override
    protected Identifier toIdentifier(String stringForm, MetadataBuildingContext buildingContext) {
        return super.toIdentifier("hds_" + stringForm, buildingContext);
    }
}
```