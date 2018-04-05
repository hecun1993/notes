## ServletContext

一个全局的储存信息的空间，服务器开始，其就存在，服务器关闭，其才释放。

request，一个用户可有多个；

session，一个用户一个；

servletContext，所有用户共用一个。

所以，为了节省空间，提高效率，ServletContext中，要放必须的、重要的、所有用户需要共享的线程又是安全的一些信息。



### 主要用途

ServletContext被Servlet程序用来与Web容器通信, 不同Servlet之间也可利用ServletContext通信。例如写日志，转发请求。

ServletContext 的最大应用是Web缓存----把不经常更改的内容读入内存，所以服务器响应请求的时候就不需要进行慢速的磁盘I/O了。

```java
// 1. Servlet引擎为每个Web应用程序都创建一个对应的ServletContext对象, ServletContext对象被包含在ServletConfig对象中, 调用ServletConfig.getServletContext方法可以返回ServletContext对象的引用.

// 2. 由于一个WEB应用程序中的所有Servlet都共享同一个ServletContext对象, 所以ServletContext对象被称之为application对象(Web应用程序对象).

// 3. 当web应用关闭、Tomcat关闭或者Web应用reload的时候，ServletContext对象会被销毁
```



### 使用方式

```xml
<context-param>
    <param-name></param-name>
    <param-value></param-value>
</context-param>
```

```java
// 获得servletcontext对象
ServletContext servletContext = servletConfig.getServletContext();
ServletContext servletContext = request.getServletContext();
ServletContext servletContext = this.getServletContext();

// 通过key获得value
servletContext.getInitParameter("MMM")
Enumeration<String> emn = servletContext.getInitParameterNames();  

// 获取项目的路径 /demo  
String path = servletContext.getContextPath();  

// 请求重定向，这样的好处可以让获取的路径更加灵活。不用考虑项目名是否发生了变化。 /demo/index.jsp  
response.sendRedirect(context.getContextPath() + "/index.jsp");  
```



