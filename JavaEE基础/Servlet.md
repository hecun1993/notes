## Servlet

### 服务器收到客户端Servlet的访问请求后

1. Web服务器首先检查是否已经装载并创建了该Servlet的实例对象。如果是，则直接执行第4步，否则，执行第2步
2. 装载并创建该`Servlet`的一个实例对象
3. 调用Servlet实例对象的`init()`方法
4. 创建一个用于封装HTTP请求消息的`HttpServletRequest`对象和一个代表HTTP响应消息的`HttpServletResponse`对象，然后调用`Servlet`的`service()`方法并将请求和响应对象作为参数传递进去。
5. Web应用程序被停止或重新启动之前，Servlet引擎卸载Servlet，并在卸载之前调用Servlet的destory()方法。



### 以下情况会导致destory()方法调用：

* tomcat重新启动
* reload该Webapp 
* 重新启动电脑



### Servlet生命周期的三个阶段

1. 初始化阶段 调用init()方法

>  Servlet被装载后，Servlet容器创建一个Servlet实例并且调用Servlet的init()方法进行初始化。在Servlet的整个生命周期内，init()方法只被调用一次。

2. 响应客户请求阶段 调用service()方法
3. 终止阶段 调用destroy()方法



### 在下列时刻Servlet容器装载Servlet

1. Servlet容器启动时会自动装载某些Servlet，实现它只需要在web.xml文件中的<Servlet></Servlet>之间添加如下代码：<load-on-startup>1</load-on-startup>
2. 在Servlet容器启动后，客户首次向Servlet发送请求
3. Servlet类文件被更新后，重新装载Servlet



### 工作原理

1. 客户发送一个请求，Servlet是调用service()方法对请求进行响应的. 通过源代码可见，service()方法中对请求的方式进行了匹配，选择调用doGet, doPost等这些方法，然后再进入对应的方法中调用逻辑层的方法，实现对客户的响应。

2. 在Servlet接口和GenericServlet抽象类中是没有doGet, doPost等等这些方法的，HttpServlet抽象类中定义了这些方法，但是都是返回error信息，所以，我们每次定义一个Servlet的时候，都必须实现doGet或doPost等这些方法。

   ```java
   protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
       String protocol = req.getProtocol();
       String msg = lStrings.getString("http.method_get_not_supported");
       if (protocol.endsWith("1.1")) {
           resp.sendError(405, msg);
       } else {
           resp.sendError(400, msg);
       }
   }
   ```

3. 我们定义Servlet的时候只需要继承HttpServlet即可

```java
// 每一个自定义的Servlet都必须实现Servlet的接口，Servlet接口中定义了五个方法，其中比较重要的三个方法涉及到Servlet的生命周期，分别是上文提到的init(),service(),destroy()方法。

// GenericServlet是一个通用的，不特定于任何协议的Servlet, 它实现了Servlet接口, 是一个抽象类。

// HttpServlet继承于GenericServlet，因此HttpServlet也实现了Servlet接口。

// Servlet接口和GenericServlet是不特定于任何协议的，而HttpServlet是特定于HTTP协议的类，所以HttpServlet中实现了service()方法，并将请求ServletRequest,ServletResponse强转为HttpRequest和HttpResponse。
```

4. 一个Servlet的每次访问请求都导致Servlet引擎调用一次servlet的service方法。
5. 对于每次访问请求，Servlet引擎都会创建一个新的HttpServletRequest请求对象和一个新的HttpServletResponse响应对象，service方法再根据请求方式分别调用doXXX方法。

### 响应请求

1. 对于用户到达Servlet的请求，Servlet容器会创建特定于这个请求的`ServletRequest`对象和`ServletResponse`对象，然后调用Servlet的service方法。
2. service方法从ServletRequest对象获得客户请求信息，处理该请求，并通过ServletResponse对象向客户返回响应信息。

> 对于Tomcat来说，它会将传递过来的参数放在一个Hashtable中，该Hashtable的定义是：

```java
private Hashtable<String String[]> paramHashStringArray = new Hashtable<String String[]>();  
```



### Servlet何时被创建

1. 默认情况下，当WEB客户第一次请求访问某个Servlet的时候，WEB容器将创建这个Servlet的实例。
2. 当web.xml文件中如果<servlet>元素中指定了<load-on-startup>子元素时，Servlet容器在启动web服务器时，将按照顺序创建并初始化Servlet对象。

##### 注意事项

* 在web.xml文件中，某些Servlet只有<serlvet>元素，没有<servlet-mapping>元素，这样我们无法通过url的方式访问这些Servlet，这种Servlet通常只要在启动web应用时调用，而不需要外部访问。操作方法是在<servlet>元素中配置一个<load-on-startup>子元素，让容器在启动的时候自动加载这些Servlet并调用init()方法，完成一些全局性的初始化工作。
* 针对客户端的多次Servlet请求，通常情况下，服务器只会创建一个Servlet实例对象**（单例模式）**也就是说Servlet实例一旦创建，它就会驻留在内存中，为后续的其他请求服务，直至web容器退出/或者reload该web运用，servlet实例对象才会销毁。
* **Servlet单例模式存在线程安全问题**，要注意并发处理，比如买票系统，票是所有客户端共享的，那么售票的代码应该使用同步机制。



### Servlet中的两种跳转方式
为了划分模块, 会让不同的Servlet实现不同的功能, 就要保证Servlet之间可以互相跳转
- `forward`: 是服务器端的转向, 客户端浏览器的地址栏不会显示转向后的地址

  >  整个定向的过程用的是同一个Request, 该Request信息会被带到新的Servlet中, 所以,forward是在服务器端的,一次请求中完成的.
- `redirect`: 客户端浏览器会获取到跳转后的地址, 然后重新发起请求, 因此浏览器会显示跳转后的地址. 这种方式比forward多了一次网络请求, 效率低.



### JSP

- JSP页面是嵌入了JAVA代码的HTML文件, 是一个特殊的Servlet, 最终也会被转换为Servlet.
- Servlet没有内置对象, JSP中有内置对象, 但必须通过HttpServletRequest, HttpServletResponse, HttpServlet对象得到.

```java
JSP的九大内置对象:
    pageContext: 对JSP页面的所有对象的访问
    request: 客户端的请求信息被封装到request对象中.getParameter()可以获得用户提交的表单数据
    session
    application: 可以存放全局变量,实现数据共享.其生命周期与服务器一致.服务器启动,对象就被创建,服务器停止,其生命周期结束
    response
    out
    config
    page
    exception	
```



### 开发Servlet

1. 建立一个Web应用myWeb
2. 在myWeb下建立WEB-INF/web.xml文件（可以从ROOT/WEB-INF拷贝）
3. 在myWeb下建立classes目录和lib目录，我们的Servlet就要在classes目录下开发。
4. 开发myFirstServlet.java

#### MyFirstServlet

```java
public class MyFirstServlet implements Servlet {  
    // 该函数用于初始化servlet，即把该servlet装载到内存中  
    // 该函数只会被调用一次  
    public void init(ServletConfig config) throws ServletException {  
    }  

    // 该函数得到ServletConfig对象  
    public ServletConfig getServletConfig(){  
        return null;  
    }  

    // 该函数是服务函数，我们的业务逻辑代码就是写在这里的  
    // 对于浏览器的每次请求，该函数每次都会被调用  
    public void service(ServletRequest req, ServletResponse res) throws ServletException, java.io.IOException {  
        //在控制台输出  
        System.out.println("Hello,World " + new java.util.Date());   
        //在浏览器输出  
        res.getWriter().println("Hello,World " + new java.util.Date().toLocaleString());            
    }  

    // 该函数得到servlet的配置信息  
    public java.lang.String getServletInfo(){  
        return null;  
    }  

    // 销毁该servlet，从内存中清除，该函数和init函数是配对的  
    // 该函数也只会被调用一次  
    public void destroy(){  
    }  
} 
```

#### web.xml

```xml
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"  
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee  
                             http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"  
         version="3.1"  
         metadata-complete="true">  

    <!--根据Servlet规范，需要将Servlet部署到web.xml文件-->  
    <!--每开发一个Servlet，都要在web.xml中部署-->  
    <servlet>  
        <!--servlet-name，指定servlet名称，可自己定义. 不一定和Servlet的类名一致，但习惯上一致-->  
        <servlet-name>myFirstServlet</servlet-name>  
        <!--servlet-class要指明该servlet放在哪个包下的,形式如下：包.类-->  
        <servlet-class>com.gavin.servlet.myFirstServlet</servlet-class>  
    </servlet>  

    <!--servlet-mapping是servlet的映射-->  
    <servlet-mapping>  
        <!--这里要和上面的servlet-name一致,这样才能匹配上-->  
        <servlet-name>myFirstServlet</servlet-name>  
        <!--url-pattern这里就是将来访问该servlet的资源名称，可以自定义-->  
        <!--默认命名规范就是该servlet的名字，前面的斜杠绝对不能丢-->  
        <url-pattern>/myFirstServlet</url-pattern>  
    </servlet-mapping>  
</web-app>
```



            
        
            