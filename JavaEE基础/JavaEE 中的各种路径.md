### JavaEE 中的各种路径

#### 项目的classpath

```java
// /Users/bytedance/IdeaProjects/chat/target/classes/
Class.class.getClass().getResource("/").getPath();
```

#### 汇总

```java
String path = request.getContextPath();  
String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+path+"/";  
```

- request.getSchema()，返回的是当前连接使用的协议，一般应用返回的是http、SSL返回的是https；
- request.getServerName()，返回当前页面所在的服务器的名字；
- request.getServerPort()，返回当前页面所在的服务器使用的端口，80；
- request.getContextPath()，返回当前页面所在的应用的名字。

以访问的jsp为：http://localhost:8080/dmsd-itoo-exam-log-web/course/index.jsp，工程名为/dmsd-itoo-exam-log-web为例：**request.getContextPath()，得到工程名：/dmsd-itoo-exam-log-web；**

> 请求重定向，这样的好处可以让获取的路径更加灵活。不用考虑项目名是否发生了变化。  
> response.sendRedirect(context.getContextPath()+"/index.jsp");  

- request.getServletPath()，返回当前页面所在目录下全名称：/course/index.jsp；

- request.getRequestURL()，返回IE地址栏地址：http://localhost:8080/dmsd-itoo-exam-log-web/course/index.jsp；

- request.getRequestURI() ，返回包含工程名的当前页面全路径：/dmsd-itoo-exam-log-web/course/index.jsp。

  > **URI = contextPath + servletPath**

- request.getRealPath(); 获取当前web应用的某一个文件的真实路径(绝对路径)--是获取的服务器上的物理路径

- request.getResourceAsStream(String path); 获得当前web应用的某一个文件对应的输入流 path的/为当前web应用的根目录