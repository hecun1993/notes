## Spring Boot 的监控

### 1. spring admin监控平台

- 1. 搭建spring-admin的springboot工程, 引入相关依赖

     ```xml
     <dependency>
        <groupId>de.codecentric</groupId>
        <artifactId>spring-boot-admin-server</artifactId>
        <version>1.3.2</version>
     </dependency>
     <dependency>
        <groupId>de.codecentric</groupId>
        <artifactId>spring-boot-admin-server-ui</artifactId>
        <version>1.3.2</version>
     </dependency>
     ```

- 1. 在启动类上加注解 @EnableAdminServer, 并配置server.port = 9090

  2. 在被监控的项目中引入依赖

     ```xml
     <dependency>
        <groupId>de.codecentric</groupId>
        <artifactId>spring-boot-admin-client</artifactId>
        <version>1.3.2</version>
     </dependency>
     ```

     然后在application.properties中加上以下配置

     ```properties
     spring.boot.admin.url=http://localhost:9090
     ```

- 1. 启动两个项目即可监控应用信息

### 2. spring boot actuator

/info 自定义信息

/health 健康监测

/beans  所有的bean

/autoconfig 所有的自定义配置

/env  系统和应用程序的环境 classpath 操作系统等

/mappings rest信息

/metrics  jvm 内存等信息

/trace  最近访问的快照

/dump 线程信息

/configprops  配置的属性值

/shutdown endpoints.shutdown.enabled = true, 可以关闭应用