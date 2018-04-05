## Mybatis

### Mybatis的使用步骤(C3P0连接池)

#### 1. mybatis-config.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <!-- 1. 配置全局属性 -->
    <settings>
        <!-- 使用jdbc的getGeneratedKeys获取数据库自增主键值 -->
        <!-- 当insert一条数据时, 这个方法会返回自增的主键值 -->
        <setting name="useGeneratedKeys" value="true"/>
        
        <!-- 关闭缓存  -->
        <setting name="cacheEnabled" value="false"/>
        
        <!-- 提高性能 -->
        <setting name="defaultExecutorType" value="REUSE"/>
        
        <!-- 事务超时时间 -->
        <setting name="defaultStatementTimeout" value="600"/>

        <!-- 使用列标签替换列别名 默认:true -->
        <setting name="useColumnLabel" value="true"/>

        <!-- 开启驼峰命名转换:Table{create_time} -> Entity{createTime} -->
        <setting name="mapUnderscoreToCamelCase" value="true"/>
    </settings>
    
    <!--
        2. 批量设置别名
        作用：
        在mapper.xml文件中的select insert update delete等语句中,写ParameterType时,
        直接写别名(默认是类名首字母小写)，不用写全路径名。
    -->
    <typeAliases>
        <package name="me.hds.mmall.pojo" />
    </typeAliases>

    <!--

        单独设置某一个pojo类的别名
        <typeAliases>
            <typeAlias type="me.hds.mmall.pojo.Cart" alias="cart" />
        </typeAliases>

    -->

    <!-- 3. 配置mybatis的分页插件PageHelper -->
    <plugins>
        <!-- com.github.pagehelper为PageHelper类所在包名 -->
        <plugin interceptor="com.github.pagehelper.PageHelper">
            <!-- 设置数据库类型Oracle,Mysql,MariaDB,SQLite,Hsqldb,PostgreSQL六种数据库 -->
            <property name="dialect" value="mysql"/>
        </plugin>
    </plugins>

    <!-- 
		4. 在springboot中, 以下这个可以不配置, 直接使用
		mybatis-mapper-locations: classpath:mappers/*.xml
	-->
    <mappers>
        <mapper resource="me/hds/mmall/dao/mappers/CartMapper.xml"/>
    </mappers>

</configuration>
```

> 配置PageHelper分页插件时, 还可以通过Java配置
>
> ```java
> //在任意一个加了@Configuration注解的类中即可
> @Bean
> public PageHelper pageHelper() {
>     PageHelper pageHelper = new PageHelper();
>
>     Properties properties = new Properties();
>     properties.setProperty("offsetAsPageNum", "true");
>     properties.setProperty("rowBoundsWithCount", "true");
>     properties.setProperty("reasonable", "true");
>
>     //配置mysql数据库的方言
>     properties.setProperty("dialect", "mysql");
>
>     pageHelper.setProperties(properties);
>     return pageHelper;
> }
> ```
>
> 

#### 2. 配置数据源 DataSource

```java
package com.imooc.demo.config.dao;

import java.beans.PropertyVetoException;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import com.mchange.v2.c3p0.ComboPooledDataSource;

/**
 * 配置datasource到ioc容器里面
 */
@Configuration
public class DataSourceConfiguration {

	@Value("${jdbc.driver}")
	private String jdbcDriver;

	@Value("${jdbc.url}")
	private String jdbcUrl;

	@Value("${jdbc.username}")
	private String jdbcUsername;

	@Value("${jdbc.password}")
	private String jdbcPassword;

	/**
	 * 生成与spring-dao.xml对应的bean dataSource
	 */
	@Bean(name = "dataSource")
	public ComboPooledDataSource createDataSource() throws PropertyVetoException {
		// 生成datasource实例
		ComboPooledDataSource dataSource = new ComboPooledDataSource();
		// 跟配置文件一样设置以下信息
		// 驱动
		dataSource.setDriverClass(jdbcDriver);
		// 数据库连接URL
		dataSource.setJdbcUrl(jdbcUrl);
		// 设置用户名
		dataSource.setUser(jdbcUsername);
		// 设置用户密码
		dataSource.setPassword(jdbcPassword);

		// 配置c3p0连接池的私有属性
        <dependency>
			<groupId>com.mchange</groupId>
			<artifactId>c3p0</artifactId>
			<version>0.9.5.2</version>
		</dependency>
            
		// 连接池最大线程数
		dataSource.setMaxPoolSize(30);
		// 连接池最小线程数
		dataSource.setMinPoolSize(10);
		// 关闭连接后不自动commit(关闭连接之后, 不自动提交. 便于通过事务进行控制)
		dataSource.setAutoCommitOnClose(false);
		// 连接超时时间
		dataSource.setCheckoutTimeout(10000);
		// 连接失败重试次数
		dataSource.setAcquireRetryAttempts(2);
        
		return dataSource;
	}
}
```

#### 3. 配置SessionFactory

```java
package com.imooc.demo.config.dao;

import java.io.IOException;

import javax.sql.DataSource;

import org.mybatis.spring.SqlSessionFactoryBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.core.io.support.ResourcePatternResolver;

@Configuration
// 1. 配置mybatis mapper接口的扫描路径
@MapperScan("com.imooc.demo.dao")
//@Import注解支持导入普通的java类,并将其声明成一个bean
//@Import(value = {DataSource.class})
public class SessionFactoryConfiguration {

	// mybatis-config.xml配置文件的路径
	private static String mybatisConfigFile;

	@Value("${mybatis_config_file}")
	public void setMybatisConfigFile(String mybatisConfigFile) {
		SessionFactoryConfiguration.mybatisConfigFile = mybatisConfigFile;
	}

	// mybatis mapper文件所在路径
	private static String mapperPath;

	@Value("${mapper_path}")
	public void setMapperPath(String mapperPath) {
		SessionFactoryConfiguration.mapperPath = mapperPath;
	}

	// 实体类所在的package
	@Value("${type_alias_package}")
	private String typeAliasPackage;

	@Autowired
	@Qualifier("dataSource")
	// 按照名字进行加载
	private DataSource dataSource;

	/**
	 * 创建sqlSessionFactoryBean 实例 并且设置 configuration 设置mapper 映射路径 设置datasource数据源
	 */
	@Bean(name = "sqlSessionFactory")
	public SqlSessionFactoryBean createSqlSessionFactoryBean() throws IOException {

		SqlSessionFactoryBean sqlSessionFactoryBean = new SqlSessionFactoryBean();

		// 设置 mybatis configuration 文件的扫描路径
		// 1. 设置mybatis的配置文件的扫描路径
		sqlSessionFactoryBean.setConfigLocation(new ClassPathResource(mybatisConfigFile));

		// 添加 mapper xml文件的扫描路径
		// 2. Mapper xml文件. ORM框架, 将前台发来的请求转换成数据库可以识别的语言, 去操作数据库, 再将结果映射到实体类中.
		// 针对数据文件流的处理, 需要用到 PathMatchingResourcePatternResolver
		PathMatchingResourcePatternResolver pathMatchingResourcePatternResolver = new PathMatchingResourcePatternResolver();
		String packageSearchPath = ResourcePatternResolver.CLASSPATH_ALL_URL_PREFIX + mapperPath;
		sqlSessionFactoryBean.setMapperLocations(pathMatchingResourcePatternResolver.getResources(packageSearchPath));
        
        //(另外一种方法 Configuration)
        Configuration configuration = new Configuration();
        // 扫描对应的mapper文件
        factoryBean.setMapperLocations(new Resource[]{new ClassPathResource("mapper/UserMapper.xml")});

		// 3. 设置dataSource
		sqlSessionFactoryBean.setDataSource(dataSource);

		// 4. 设置typeAlias 包扫描路径
		sqlSessionFactoryBean.setTypeAliasesPackage(typeAliasPackage);

		return sqlSessionFactoryBean;
	}
}
```

#### 4. 事务管理器的配置

```java
package com.imooc.demo.config.service;

import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.transaction.annotation.TransactionManagementConfigurer;

/**
 * 对标spring-service里面的transactionManager
 * 继承 TransactionManagementConfigurer 是因为开启 annotation-driven
 */
@Configuration
// 首先使用注解 @EnableTransactionManagement 开启事务支持后
// 在Service方法上添加注解 @Transactional 便可
@EnableTransactionManagement
public class TransactionManagementConfiguration implements TransactionManagementConfigurer {

	@Autowired
	// 注入DataSourceConfiguration里边的dataSource,通过createDataSource()获取
	private DataSource dataSource;

	@Override
	/*
	 * 关于事务管理，需要返回PlatformTransactionManager的实现
	 */
	public PlatformTransactionManager annotationDrivenTransactionManager() {
		return new DataSourceTransactionManager(dataSource);
	}
}
```

#### 5. 配置mapper.xml文件

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<!-- namespace 指的是 要对哪个Dao进行配置 -->
<mapper namespace="com.imooc.demo.dao.AreaDao">
    <select id="queryArea" resultType="com.imooc.demo.entity.Area">
        SELECT area_id, area_name,
        priority, create_time, update_time
        FROM tb_area
        ORDER BY priority
        DESC
    </select>
    <select id="queryAreaById" resultType="com.imooc.demo.entity.Area">
        SELECT area_id, area_name,
        priority, create_time, update_time
        FROM tb_area
        WHERE
        area_id=#{areaId}
    </select>
    <insert id="insertArea" useGeneratedKeys="true" keyProperty="areaId"
            keyColumn="area_id" parameterType="com.imooc.demo.entity.Area">
        INSERT INTO
        tb_area(area_name,priority,
        create_time,update_time)
        VALUES
        (#{areaName},#{priority},
        #{createTime},#{updateTime})
    </insert>
    <update id="updateArea" parameterType="com.imooc.demo.entity.Area">
        update tb_area
        <set>
            <if test="areaName != null">area_name=#{areaName},</if>
            <if test="priority != null">priority=#{priority},</if>
            <if test="updateTime != null">update_time=#{updateTime}</if>
        </set>
        where area_id=#{areaId}
    </update>
    <delete id="deleteArea">
        DELETE FROM
        tb_area
        WHERE
        area_id =
        #{areaId}
    </delete>
</mapper>
```

#### 6. 配置文件

```properties
### DataSource
#数据库驱动
jdbc.driver=com.mysql.jdbc.Driver
#数据库链接
jdbc.url=jdbc:mysql://localhost:3306/wx?useUnicode=true&characterEncoding=utf8&useSSL=false
#数据库用户名
jdbc.username=root
#数据库密码
jdbc.password=12345678

### Mybatis
mybatis_config_file=mybatis-config.xml
mapper_path=/mapper/**.xml
type_alias_package=com.imooc.demo.entity

#============

spring.datasource.url=jdbc:mysql://localhost:3306/user?characterEncoding=UTF-8
spring.datasource.username=root
spring.datasource.password=123456
spring.datasource.driver-class-name=com.mysql.jdbc.Driver

# mybatis的配置
mybatis.config-location=classpath:/mybatis/mybatis-config.xml
```

> 可以将Mybatis的配置放在yml文件中
>
> ```yml
> mybatis:
>   mapper-locations: classpath:mappers/*.xml
>   #type-aliases-package: me.hds.mmall.pojo
>   #config-location: classpath:mybatis-config.xml
> ```

#### 7. UserMapper.java

```java
@Mapper
public interface UserMapper {
  public List<User>  selectUsers();
  public int insert(User account);
  public int delete(String email);
  public int update(User updateUser);
  public List<User> selectUsersByQuery(User user);
}
```



### 使用Druid连接池

druid连接池的优势在于:

1. 内置监控统计
2. 数据库密码加密
3. 防止SQL注入

已经有了 druid-spring-boot-starter的maven依赖

引入mysql依赖, 就需要引入spring-jdbc的依赖, 以及druid的依赖

会自动创建DataSource, 通过DataSourceBuilder的build方法

DruidConfig.java

```java
@Configuration
public class DruidConfig {
    /**
     * 使用druid连接池, 就需要配置新的数据源, 而不是使用springboot默认提供的jdbc数据源
     */
  @ConfigurationProperties(prefix = "spring.druid")
  @Bean(initMethod = "init",destroyMethod = "close")
  public DruidDataSource dataSource() {
    DruidDataSource dataSource = new DruidDataSource();
    dataSource.setProxyFilters(Lists.newArrayList(statFilter()));
    return dataSource;
  }
  
    //配置监控的Filter
  @Bean
  public Filter statFilter() {
    StatFilter filter = new StatFilter();
    //打印sql的慢日志
    filter.setSlowSqlMillis(5000);
    filter.setLogSlowSql(true);
    filter.setMergeSql(true);
    return filter;
  }

    /**
     * 把监控功能的Filter配置到Servlet中, 启动后访问/druid接口, 就可以看到监控的信息
     */
  @Bean
  public ServletRegistrationBean servletRegistrationBean() {
    return new ServletRegistrationBean(new StatViewServlet(), "/druid/*");
  }
}
```

application.properties

```properties
spring.druid.driverClassName=com.mysql.jdbc.Driver
spring.druid.url=jdbc:mysql://127.0.0.1:3306/houses?useUnicode=true&amp;amp;characterEncoding=UTF-8&amp;amp;zeroDateTimeBehavior=convertToNull
spring.druid.username=root
spring.druid.password=123456
spring.druid.maxActive=30
spring.druid.minIdle=5
spring.druid.maxWait=10000
spring.druid.validationQuery=SELECT 'x'
```





### sqlMapConfig.xml

mybatis的全局配置文件，配置了数据源、事务管理.

### mapper.xml

sql映射文件，文件中配置了操作数据库的sql语句。需要在sqlMapConfig.xml中加载。

通过mybatis环境等配置信息构造SqlSessionFactory会话工厂, 由会话工厂创建sqlSession会话，操作数据库需要通过sqlSession进行

- mybatis底层自定义了Executor执行器接口, 用来操作数据库;
- Mapped Statement是mybatis一个底层封装对象，它包装了mybatis配置信息及sql映射信息等。mapper.xml文件中一个sql对应一个Mapped Statement对象，sql的id即是Mapped statement的id。
- Excutor通过Mapper Statement对象实现输入参数/输出结果与java对象的映射.

###{}和${}
#### {} 参数占位符

- Mybatis会将sql中的#{}替换为?号，在sql执行前会使用PreparedStatement的参数设置方法，按序给sql的?号占位符设置参数值。会自动为其中的值添加’’，其中的值可以任意写，比如写成v


- {}可以有效防止sql注入


- 自动进行java类型和jdbc类型转换

#### ${} 字符串拼接

- 静态文本替换。不会自动为其中的值添加’’，而且其中的值必须写成value


- 不进行jdbc类型转换
- Select * from user where id = #{v}
- Select * from user where username like “%${value}%”



### 注意事项

1. mybatis和hibernate的区别

    - Mybatis不完全是一个ORM框架，需要自己编写Sql语句。mybatis可以通过XML或注解方式灵活配置要运行的sql语句，并将java对象和sql语句映射生成最终执行的sql，最后将sql执行的结果再映射生成java对象。


    - Mybatis可以编写原生态sql，可严格控制sql执行性能，灵活度高，但是灵活的前提是mybatis无法做到数据库无关性，如果需要实现支持多种数据库的软件则需要自定义多套sql映射文件，工作量大。

2. Mapper接口开发 --- 取代传统的Dao开发模式

    1、  Mapper.xml文件中的namespace与mapper接口的类路径相同。

    2、  Mapper接口方法名和Mapper.xml中定义的每个statement的id相同 

    3、  Mapper接口方法的输入参数类型和mapper.xml中定义的每个sql的parameterType的类型相同

    4、  Mapper接口方法的输出参数类型和mapper.xml中定义的每个sql的resultType的类型相同

    Dao接口，就是人们常说的Mapper接口，接口的全限名，就是映射文件中的namespace的值，接口的方法名，就是映射文件中MappedStatement的id值，接口方法内的参数，就是传递给sql的参数。

    Mapper接口是没有实现类的，当调用接口方法时，接口全限名+方法名拼接字符串作为key值，可唯一定位一个MappedStatement，在Mybatis中，每一个<select>、<insert>、<update>、<delete>标签，都会被解析为一个MappedStatement对象。

    **Dao接口的工作原理是JDK动态代理，Mybatis运行时会使用JDK动态代理为Dao接口生成代理proxy对象，代理对象proxy会拦截接口方法，转而执行MappedStatement所代表的sql，然后将sql执行结果返回。**




### 通过xml配置mybatis

1. 配置DataSource(指定username, password, url等)
2. 配置SqlSessionFactory

    需要注入DataSource和mybatis-config.xml全局配置文件
3. 配置MapperScannerConfigurer

    需要注入basePackages和sqlSessionFactory
4. 创建mybatis-config.xml, mapper接口类, sql映射文件



### 通过springboot

1. 引入mybatis starter

2. 在application.properties中加入DataSource的配置

    ```properties
    spring.datasource.url=jdbc:mysql://localhost:3306/user?characterEncoding=UTF-8
    spring.datasource.username=root
    spring.datasource.password=123456
    spring.datasource.driver-class-name=com.mysql.jdbc.Driver
    mybatis.config-location=classpath:/mybatis/mybatis-config.xml
    # 这样的配置, 默认启用的是tomcat提供的数据库连接池
    ```

3. 创建mybatis-config.xml, mapper接口类, sql映射文件
