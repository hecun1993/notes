### Log4j

Log4j 是目前最为流行的Java 日志框架之一，虽然已经停滞发展，并逐步被Logback和Log4j2 等日志框架所替代，可是无法掩饰光辉历程，以及优良的设计理念。

```properties
Log4j API

日志对象（org.apache.log4j.Logger）
日志级别（org.apache.log4j.Level）
日志管理器（org.apache.log4j.LogManager）
日志仓储（org.apache.log4j.spi.LoggerRepository）
日志附加器（org.apache.log4j.Appender）
日志过滤器（org.apache.log4j.spi.Filter）
日志格式布局（org.apache.log4j.Layout）
日志事件（org.apache.log4j.LoggingEvent）
日志配置器（org.apache.log4j.spi.Configurator） xml / properties
日志诊断上下文（org.apache.log4j.NDC(嵌套)、org.apache.log4j.MDC(映射)）
```

1. 因为在starter-web中, 本身引入了slf4j, 所以, 要看到Log4j的特性, 就必须排除slf4j的包

```xml
<dependency>
    <groupId>log4j</groupId>
    <artifactId>log4j</artifactId>
    <version>1.2.17</version>
</dependency>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>log4j-over-slf4j</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

2. 把 `log4j.properties` 放在classpath下, 由于`LogManager`类的作用, 会自动读取这个propeties文件

```properties
log4j.rootLogger=DEBUG, com
log4j.appender.com=org.apache.log4j.ConsoleAppender
log4j.appender.com.layout=org.apache.log4j.PatternLayout
log4j.appender.com.layout.conversionPattern=[%t] %-5p %c - %m%n
```

3. 使用

```java
Logger logger = Logger.getLogger(Log4jTest.class.getName());
logger.info("Hello,World");
```

> * WARN的级别比INFO高, 所以, 如果设置的日志级别是WARN, 那么, logger.info()的内容就不会输出了
> * log4j是最开始有的日志框架, 在2015年不再维护了. 新出来的logback和log4j2(logging)框架.
> * 整合两者, 会有slf4j框架和apache的common-logging框架
> * 但所有的框架设计思想都是基于log4j的
> * logback是springboot默认支持的
> * log4j2性能更好, 适合高并发



### log4j2的使用

#### 1. pom文件

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-log4j2</artifactId>
</dependency>

<!--帮助实现高性能日志输出的功能的依赖-->
<dependency>
    <groupId>com.lmax</groupId>
    <artifactId>disruptor</artifactId>
    <version>3.3.6</version>
</dependency>
```

#### 2. 添加log4j2.xml文件配置日志输出信息



### Spring中logback的配置

#### /resources/logback-spring.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration debug="true">

	<!--只在非生产环境往控制台打印日志 -->
	<springProfile name="pro">
		<property name="TO_CONSOLE" value="false" />
	</springProfile>
	<springProfile name="!pro">
		<property name="TO_CONSOLE" value="true" />
	</springProfile>

	<!-- 控制台输出 -->
	<appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
		<encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
			<!--格式化输出：%d表示日期，%thread表示线程名，%-5level：级别从左显示5个字符宽度%msg：日志消息，%n是换行符 -->
			<pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50}:%line - %msg%n</pattern>
			<charset>UTF-8</charset>
		</encoder>
	</appender>

	<!-- 按照每天生成日志文件 -->
	<appender name="FILE"
		class="ch.qos.logback.core.rolling.RollingFileAppender">
		<file>${LOG_PATH}/${LOG_FILE}.log</file>
		<rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
			<!-- rollover daily -->
			<fileNamePattern>${LOG_PATH}/${LOG_FILE}-%d{yyyy-MM-dd}.%i.log
			</fileNamePattern>
			<timeBasedFileNamingAndTriggeringPolicy
				class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
				<!-- or whenever the file size reaches 100MB -->
				<maxFileSize>100MB</maxFileSize>
			</timeBasedFileNamingAndTriggeringPolicy>
		</rollingPolicy>
		<encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
			<!--格式化输出：%d表示日期，%thread表示线程名，%-5level：级别从左显示5个字符宽度%msg：日志消息，%n是换行符 -->
			<pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50}:%line - %msg%n</pattern>
			<charset>UTF-8</charset>
		</encoder>
	</appender>

	<!-- 日志输出级别 -->
	<root level="INFO">
		<appender-ref ref="STDOUT" />
	</root>

	<!--com开头的包的日志存在哪里-->
	<logger name="com" level="INFO" additivity="${TO_CONSOLE}">
		<appender-ref ref="FILE"/>
	</logger>
	
	<logger name="org" level="INFO" additivity="${TO_CONSOLE}">
		<appender-ref ref="FILE"/>
	</logger>

</configuration>
```

#### DemoApplication

```java
package me.hds;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ImportResource;

@SpringBootApplication
@ImportResource("resources/logback-spring.xml")
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

}
```

