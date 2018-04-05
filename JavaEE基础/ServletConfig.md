## ServletConfig

### 每个Servlet都只有一个ServletConfig



### 原理

1. 在Servlet的配置文件中，可以使用一个或多个<init-param>标签为servlet配置一些初始化参数。
2. 当servlet配置了初始化参数后，web容器在创建servlet实例对象时，会自动将这些初始化参数封装到ServletConfig对象传递给servlet。并在调用servlet的init方法时，将ServletConfig对象传递给servlet。进而，程序员通过ServletConfig对象就可以得到当前servlet的初始化参数信息。



### 步骤

```java
* 首先，需要创建私有变量：private ServletConfig config = null;
* 其次，要重写init方法，传入config，令this.config = config;从而获得ServletConfig对象
* 最后，就可以获得<init-parm>中的配置信息了
```
```xml
<servlet>  
    <servlet-name>MyServlet1</servlet-name>  
    <servlet-class>com.gavin.servlet.MyServlet1</servlet-class>  
    <!-- 这里可以给servlet配置信息，这里的配置信息，只能被该servlet读取 -->  
    <init-param>  
        <param-name>encoding</param-name>  
        <param-value>utf-8</param-value>  
    </init-param>  
</servlet>  
```



### 获取到参数的两种方法

1. response.setCharacterEncoding(this.getInitParameter("encoding"));  

2. 如果有多个参数，可以使用getInitParameterNames()方法，该方法返回枚举类型Enumeration，可以通过for循环拿到对应的参数名称，然后通过参数名称再通过上述方法拿到参数，当然也可以一个个拿到。

   > 说明：这里的配置参数方法，只能被该servlet读取，而不能被其他servlet使用



### ServletConfig的作用有如下三个

```java
// 1）获得字符集编码
String charset = this.config.getInitParameter("charset");

// 2）获得数据库连接信息
String url = this.config.getInitParameter("url");
String username = this.config.getInitParameter("username");
String password = this.config.getInitParameter("password");

// 3）获得配置文件
String configFile = this.config.getInitParameter("config");
```

