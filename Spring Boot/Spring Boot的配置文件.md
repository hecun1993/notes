### application.properties

```properties
### mysql的配置
spring.datasource.driver-class-name=com.mysql.jdbc.Driver
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/security?characterEncoding=utf8&useSSL=false&useUnicode=true
spring.datasource.username=root
spring.activemq.password=root

### 缓存类型和redis的配置
## 配置了jdbc和redis的依赖，就要配置数据库信息，开启redis服务，否则启动报错。还要关闭session集群管理
# 开启session集群管理，存放在redis中 开始时要设置为None, 启动不报错
# spring.session.store-type=hash_map
spring.session.store-type=redis
spring.redis.host=127.0.0.1
spring.redis.port=6379

# 这里默认是秒数, 但springboot默认最小失效时间是1min
server.session.timeout=10

### jpa的配置
spring.jpa.generate-ddl = true
# 自定义数据库中的表的命名策略
spring.jpa.hibernate.naming.implicit-strategy = me.hds.support.HDSNameStrategy
spring.jpa.show-sql = true
spring.jpa.properties.hibernate.format_sql = true

# 取消springboot的默认错误页面的显示, 而用我们自己的错误页面
server.error.whitelabel.enabled=false

# springboot热部署时, 取消对静态资源的监控
spring.devtools.restart.exclude=templates/**,static/**

# 关闭管理接口的安全校验 (ManagementServerProperties)
management.security.enabled = false
# 访问/env, 可以看到application.properties中配置的信息, 还有端口号等.

# 指定端口为0, 是操作系统的可用的随机端口. 每次启动的端口都不一样
server.port = 0
```