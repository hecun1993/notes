# SpringBoot与数据访问

## 1、JDBC

### 1. 示例

#### pom.xml

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <scope>runtime</scope>
</dependency>
```

#### application.yml

```yaml
spring:
  datasource:
    username: root
    password: 123456
    url: jdbc:mysql://192.168.15.22:3306/jdbc
    driver-class-name: com.mysql.jdbc.Driver
```

#### Test

有上述两个配置, 即可进行测试

在测试的时候, 发现可以获得数据源和连接信息

```java
package com.atguigu.springboot;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;

@RunWith(SpringRunner.class)
@SpringBootTest
public class SpringBoot06DataJdbcApplicationTests {

	@Autowired
	DataSource dataSource;

	@Test
	public void contextLoads() throws SQLException {
		//org.apache.tomcat.jdbc.pool.DataSource
		System.out.println(dataSource.getClass());

		Connection connection = dataSource.getConnection();
		System.out.println(connection);
		connection.close();
	}
}
```

​默认是用org.apache.tomcat.jdbc.pool.DataSource作为数据源

数据源的相关配置都在DataSourceProperties里面

### 2. 自动配置原理：

org.springframework.boot.autoconfigure.jdbc：

#### 1、参考DataSourceConfiguration

根据配置创建数据源，默认使用Tomcat连接池；可以使用spring.datasource.type指定自定义的数据源类型；

```java
// @ConditionalOnProperty 即使没有配置 spring.datasource.type 也会使用tomcat的配置
@ConditionalOnClass(org.apache.tomcat.jdbc.pool.DataSource.class)
@ConditionalOnProperty(name = "spring.datasource.type", havingValue = "org.apache.tomcat.jdbc.pool.DataSource", matchIfMissing = true)
static class Tomcat extends DataSourceConfiguration {

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.tomcat")
    public org.apache.tomcat.jdbc.pool.DataSource dataSource(
        DataSourceProperties properties) {
        org.apache.tomcat.jdbc.pool.DataSource dataSource = createDataSource(
            properties, org.apache.tomcat.jdbc.pool.DataSource.class);
        DatabaseDriver databaseDriver = DatabaseDriver
            .fromJdbcUrl(properties.determineUrl());
        String validationQuery = databaseDriver.getValidationQuery();
        if (validationQuery != null) {
            dataSource.setTestOnBorrow(true);
            dataSource.setValidationQuery(validationQuery);
        }
        return dataSource;
    }
}
```

#### 2、SpringBoot默认可以支持的数据源

```
org.apache.tomcat.jdbc.pool.DataSource、HikariDataSource、BasicDataSource、
```

我们通常可以使用druid数据源

#### 3、自定义数据源类型

```java
/**
 * Generic DataSource configuration.
 */
@ConditionalOnMissingBean(DataSource.class)
@ConditionalOnProperty(name = "spring.datasource.type")
static class Generic {

   @Bean
   public DataSource dataSource(DataSourceProperties properties) {
       //使用DataSourceBuilder创建数据源，利用反射创建响应type的数据源，并且绑定相关属性
      return properties.initializeDataSourceBuilder().build();
   }

}
```

#### 4、**DataSourceInitializer：**

DataSourceInitializer本身是一个ApplicationListener. 它的作用：

1）runSchemaScripts(); 运行建表语句；

2）runDataScripts(); 运行插入数据的sql语句；

默认只需要将文件命名为：

```properties
schema-*.sql
data-*.sql
默认规则：schema.sql，schema-all.sql
把这些名字的文件放在类路径下, 启动应用, 即可执行

如果需要自定义sql文件的位置, 则这样定义: 
spring: 	
	schema: 
      - classpath:department.sql
```

#### 5、操作数据库

JdbcTemplateAutoConfiguration

自动配置了JdbcTemplate操作数据库

我们可以在项目的任意位置, 注入JdbcTemplate

```java
package com.atguigu.springboot.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;
import java.util.Map;

@Controller
public class HelloController {

    @Autowired
    JdbcTemplate jdbcTemplate;

    @ResponseBody
    @GetMapping("/query")
    public Map<String,Object> map(){
        List<Map<String, Object>> list = jdbcTemplate.queryForList("select * FROM department");
        return list.get(0);
    }
}
```



## 2、整合Druid数据源

### application.yml

```yaml
spring:
  datasource:
    username: root
    password: 123456
    url: jdbc:mysql://192.168.15.22:3306/jdbc
    driver-class-name: com.mysql.jdbc.Driver
    type: com.alibaba.druid.pool.DruidDataSource

    initialSize: 5
    minIdle: 5
    maxActive: 20
    maxWait: 60000
    timeBetweenEvictionRunsMillis: 60000
    minEvictableIdleTimeMillis: 300000
    validationQuery: SELECT 1 FROM DUAL
    testWhileIdle: true
    testOnBorrow: false
    testOnReturn: false
    poolPreparedStatements: true
#   配置监控统计拦截的filters，去掉后监控界面sql无法统计，'wall'用于防火墙
    filters: stat,wall,log4j
    maxPoolPreparedStatementPerConnectionSize: 20
    useGlobalDataSourceStat: true
    connectionProperties: druid.stat.mergeSql=true;druid.stat.slowSqlMillis=500
#    schema:
#      - classpath:department.sql
```

### DruidConfig

```java
// 导入druid数据源
@Configuration
public class DruidConfig {

    // 自己来创建数据源Druid
    // 同时要把配置属性和这个创建的数据源绑定起来
    // 所以要加上@ConfigurationProperties注解, 获取全局配置文件中的属性
    @ConfigurationProperties(prefix = "spring.datasource")
    @Bean
    public DataSource druid(){
       return  new DruidDataSource();
    }

    // 配置Druid的监控
    // 1、配置一个管理后台的Servlet ServletRegistrationBean
    @Bean
    public ServletRegistrationBean statViewServlet() {
        ServletRegistrationBean bean = new ServletRegistrationBean(new StatViewServlet(), "/druid/*");
        Map<String,String> initParams = new HashMap<>();

        initParams.put("loginUsername", "admin");
        initParams.put("loginPassword", "123456");
        initParams.put("allow", "");//默认就是允许所有访问
        initParams.put("deny", "192.168.15.21");

        bean.setInitParameters(initParams);
        return bean;
    }


    // 2、配置一个web监控的filter FilterRegistrationBean
    @Bean
    public FilterRegistrationBean webStatFilter(){
        FilterRegistrationBean bean = new FilterRegistrationBean();
        bean.setFilter(new WebStatFilter());

        Map<String,String> initParams = new HashMap<>();
        initParams.put("exclusions", "*.js,*.css,/druid/*");

        bean.setInitParameters(initParams);
        // 拦截所有请求
        bean.setUrlPatterns(Arrays.asList("/*"));

        return  bean;
    }
}
```

### 访问 localhost:8080/druid 

进入管理后台

## 3、整合MyBatis

#### mybatis自己适配spring boot, 写的starter如下

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>1.3.1</version>
</dependency>
```

![](/Users/bytedance/Documents/Spring%20Boot%20%E7%AC%94%E8%AE%B0/images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180305194443.png)

### 步骤：

#### 1. 配置数据源相关属性（见上一节Druid）

> 引入druid依赖, 创建yml全局配置文件, 编写DruidConfig配置类

#### 2. 给数据库建表

把sql文件放在类路径下的sql/a.sql; sql/b.sql

然后在yml中设置spring.datasource.schema = classpath:sql/a.sql

注意: 创建表之后, 把这个创建表的配置注释掉, 防止下次启动又建表

#### ​3. 创建JavaBean

#### 4. 注解版

##### DepartmentMapper

只需要写@Mapper注解, 编写Mapper文件(DAO)即可, 无需做任何配置

```java
//指定这是一个操作数据库的mapper
@Mapper
public interface DepartmentMapper {

    @Select("select * from department where id=#{id}")
    public Department getDeptById(Integer id);

    @Delete("delete from department where id=#{id}")
    public int deleteDeptById(Integer id);

    @Options(useGeneratedKeys = true, keyProperty = "id") // 插入数据时, 设置主键自增
    @Insert("insert into department(departmentName) values(#{departmentName})")
    public int insertDept(Department department);

    @Update("update department set departmentName=#{departmentName} where id=#{id}")
    public int updateDept(Department department);
}
```

问题：无任何配置的情况下, 无法开启驼峰转换的功能. 所以需要我们再添加一个配置类, 用来做一些配置.

##### 自定义MyBatis的配置规则；给容器中添加一个ConfigurationCustomizer；

```java
@org.springframework.context.annotation.Configuration
public class MyBatisConfig {

	// 给容器中新增一个ConfigurationCustomizer接口的实现类
    @Bean
    public ConfigurationCustomizer configurationCustomizer(){
        return new ConfigurationCustomizer(){
            @Override
            public void customize(Configuration configuration) {
            	// 开启驼峰法
                configuration.setMapUnderscoreToCamelCase(true);
            }
        };
    }
}
```

##### 如果Mapper类太多, 可以使用批量扫描功能 这样就不需要给每个Mapper类都加@Mapper了

只需要在主配置类上加 @MapperScan(value = "com.atguigu.springboot.mapper")

```java
@MapperScan(value = "com.atguigu.springboot.mapper")
@SpringBootApplication
public class SpringBoot06DataMybatisApplication {

	public static void main(String[] args) {
		SpringApplication.run(SpringBoot06DataMybatisApplication.class, args);
	}
}
```

### 5）配置文件版

无论是注解还是配置文件, 对Mapper文件, 都需要用@Mapper或者@MapperScan的方式扫描Mapper文件, 装配到容器中

#### mybatis-config.xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <settings>
        <setting name="mapUnderscoreToCamelCase" value="true"/>
    </settings>
</configuration>
```

#### EmployeeMapper.xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.atguigu.springboot.mapper.EmployeeMapper">
   <!--    public Employee getEmpById(Integer id);

    public void insertEmp(Employee employee);-->
    <select id="getEmpById" resultType="com.atguigu.springboot.bean.Employee">
        SELECT * FROM employee WHERE id=#{id}
    </select>

    <insert id="insertEmp">
        INSERT INTO employee(lastName,email,gender,d_id) VALUES (#{lastName},#{email},#{gender},#{dId})
    </insert>
</mapper>
```

#### application.yml

```yaml
mybatis:
  config-location: classpath:mybatis/mybatis-config.xml 指定全局配置文件的位置
  mapper-locations: classpath:mybatis/mapper/*.xml  指定sql映射文件的位置
```

更多使用参照

http://www.mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/



## 4、整合SpringData JPA

### 1）Spring Data简介

- Spring Data是spring的一个子项目, 里面有针对不同数据库的各种模块, 是Spring boot在数据访问上使用的框架
- spring data提供统一的api访问数据库, 提供了很多Repository接口, 这些接口具有基本的增删改查, 分页的功能
- 我们只需要继承这些接口, 不用关心实现, 就可以使用CRUD功能
- spring data提供了统一的模板类xxxTemplate
- spring data jpa使用了JPA规范, 有很多实现, 其中一个是Hibernate
- spring data jpa默认就是用Hibernate实现

![](/Users/bytedance/Documents/Spring%20Boot%20%E7%AC%94%E8%AE%B0/images/%E6%90%9C%E7%8B%97%E6%88%AA%E5%9B%BE20180306105412.png)

### 2）整合SpringData JPA

JPA:ORM（Object Relational Mapping）；

1）编写一个实体类（bean）和数据表进行映射，并且配置好映射关系；

```java
//使用JPA注解配置映射关系
@Entity //告诉JPA这是一个实体类（和数据表映射的类）
@Table(name = "tbl_user") //@Table来指定和哪个数据表对应;如果省略默认表名就是user；
public class User {

    @Id //这是一个主键
    @GeneratedValue(strategy = GenerationType.IDENTITY)//自增主键
    private Integer id;

    @Column(name = "last_name",length = 50) //这是和数据表对应的一个列
    private String lastName;
    @Column //省略默认列名就是属性名
    private String email;
}
```

2）编写一个Dao接口来操作实体类对应的数据表（Repository）

```java
//继承JpaRepository来完成对数据库的操作
public interface UserRepository extends JpaRepository<User,Integer> {
}
```

3）基本的配置 JpaProperties

```yaml
spring:  
 jpa:
    hibernate:
#     更新或者创建数据表结构
      ddl-auto: update
#    控制台显示SQL
    show-sql: true
```

