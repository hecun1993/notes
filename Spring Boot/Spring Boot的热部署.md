### Java热部署与热加载的联系

1. 不重启服务器实现编译 / 部署
2. 都基于Java类加载器来实现



### Java热部署与热加载的区别

1. 热部署在服务器运行时**重新部署项目**. 热部署直接重新加载整个应用, 会耗费时间, 更彻底. 更多用在生产环境.
2. 热加载在运行时**重新加载class文件**. 依赖Java的类加载机制. 在容器启动时, 启动一个后台线程, 定时检测类文件的时间戳变化. 如果类的时间戳有变化, 就把类重新载入. 也就是通过改变类的信息, 改变类的行为. 更多用在开发环境. (不安全, 无法记录修改class文件的日志信息, 难以控制)



### Java类的加载过程

Java文件 => 编译 => Java字节码文件 => 序列化为类似于字符串的串 => 编译成源码对象 => 编译成.class文件 => 由类加载器加载到JVM中运行.

初始化JVM => 产生启动类加载器 => 标准扩展类加载器 => 系统类加载器 => 加载class文件(交给父类加载)



### Java类加载的五个阶段

加载 => 找到类的静态存储结构, 加载到JVM中, 转化成方法区的运行时数据结构, 生成class对象. 用户可以自定义类加载器参与其中.

验证 => 确保字节码文件是安全的, 不会危害JVM. 可以通过JVM参数禁用验证.

准备 => 确定内存布局, 初始化类变量. 赋初始值, 不是程序的赋值操作.

解析 => 将符号引用变成直接引用.

初始化 => 调用程序自定义的代码赋值



### Java类的热部署的实现

#### 1. 通过类的热加载实现

```java
// 通过集成ClassLoader, 重写findClass方法
@override
protected Class<?> findClass(String name) throws ClassNotFoundException {
    System.out.println("加载类: " + name);
    byte[] data = loadClassData(name);
    return this.defineClass(name, data, 0, data.length);
}
```

##### MyClassLoader

```java
package com.imooc.classloader;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

/**
 * 自定义Java类加载器来实现Java类的热加载
 */
public class MyClassLoader extends ClassLoader {
	//要加载的Java类的classpath路径
	private String classpath;
	
	public MyClassLoader(String classpath) {
		//调用父类的得到系统类加载器的方法
		super(ClassLoader.getSystemClassLoader());
		this.classpath = classpath;
	}
	
	@Override
	protected Class<?> findClass(String name) throws ClassNotFoundException {
		byte[] data = new byte[0];
		try {
			data = this.loadClassData(name);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return this.defineClass(name, data, 0, data.length);
	}

	/**
	 * 加载class文件中的内容
	 * @param name
	 * @return
	 */
	private byte[] loadClassData(String name) throws IOException {
		//传入的是com.imooc.classloader, 要把.转成/
		name = name.replace(".", "/");
		File file = new File(classpath + name + ".class");
		if (file.exists()) {
			FileInputStream fileInputStream = new FileInputStream(file);
			ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
			int b;
			while ((b = fileInputStream.read()) != -1) {
				byteArrayOutputStream.write(b);
			}
			fileInputStream.close();
			return byteArrayOutputStream.toByteArray();
		} else {
			return "111".getBytes();
		}
	}		
}
```

##### BaseManager

```java
package com.imooc.classloader;

/**
 * 实现这个接口的子类需要动态更新(热加载)
 */
public interface BaseManager {
	void logic();
}
```

##### MyManager

```java
package com.imooc.classloader;

/**
 * BaseManager的子类，此类需要实现java类的热加载功能
 */
public class MyManager implements BaseManager {

	@Override
	public void logic() {
		System.out.println("我在慕课网学习呢，我在慕课网上学习了Spring Boot热部署这门课程");
		System.out.println("慕课网学习资源很丰富，师资很强大，学习的人很多111222333222");
	}
}
```

##### ManagerFactory

```Java
package com.imooc.classloader;

import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

/**
 * 加载manager的工厂
 */
public class ManagerFactory {

	//记录热加载类的加载信息
	private static final Map<String, LoadInfo> loadTimeMap = new HashMap<String, LoadInfo>();

	//要加载的类的classpath
	public static final String CLASS_PATH = Class.class.getClass().getResource("/").getPath();

	//实现热加载的类的全名称(包名+类名)
	public static final String MY_MANAGER = "com.imooc.classloader.MyManager";
	
	public static BaseManager getManager(String className){
		File loadFile = new File(CLASS_PATH + className.replaceAll("\\.", File.separator) + ".class");
		//最后一次的修改时间
		long lastModified = loadFile.lastModified();
		//loadTimeMap不包含className为key的LoadInfo信息。证明这个类没有被加载，那么需要加载这个类到JVM
		if(loadTimeMap.get(className) == null){
			load(className, lastModified);
		}
		//加载类的时间戳变化了，我们同样要重新加载这个类到JVM
		else if(loadTimeMap.get(className).getLoadTime() != lastModified){	
			load(className, lastModified);
		}
		return loadTimeMap.get(className).getManager();
	}

	private static void load(String className, long lastModified) {
		MyClassLoader myClassLoader = new MyClassLoader(CLASS_PATH);
		Class<?> loadClass = null;
		try {
			loadClass = myClassLoader.findClass(className);
			if (loadClass != null) {
				BaseManager manager = newInstance(loadClass);
				LoadInfo loadInfo = new LoadInfo(myClassLoader, lastModified);
				loadInfo.setManager(manager);
				loadTimeMap.put(className, loadInfo);
			}
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		}
	}

	//以反射的方式创建BaseManager子类对象
	private static BaseManager newInstance(Class<?> loadClass) {
		try {
			return (BaseManager)loadClass.getConstructor(new Class[]{}).newInstance(new Object[]{});
		} catch (InstantiationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IllegalAccessException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IllegalArgumentException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InvocationTargetException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NoSuchMethodException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (SecurityException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
	}
}
```

##### LoadInfo

```java
package com.imooc.classloader;

/**
 * 封装加载类的信息
 */
public class LoadInfo {
	//自定义的类加载
	private MyClassLoader myLoader;
	//记录要加载的类的时间戳-->加载的时间
	private long loadTime;
	private BaseManager manager;
	
	public LoadInfo(MyClassLoader myLoader, long loadTime) {
		super();
		this.myLoader = myLoader;
		this.loadTime = loadTime;
	}

	public MyClassLoader getMyLoader() {
		return myLoader;
	}

	public void setMyLoader(MyClassLoader myLoader) {
		this.myLoader = myLoader;
	}

	public long getLoadTime() {
		return loadTime;
	}

	public void setLoadTime(long loadTime) {
		this.loadTime = loadTime;
	}

	public BaseManager getManager() {
		return manager;
	}

	public void setManager(BaseManager manager) {
		this.manager = manager;
	}
}
```

##### MessageHandler

```java
package com.imooc.classloader;

/**
 * 后台启动一条线程不断刷新重新加载实现了热加载的类
 */
public class MsgHandler implements Runnable {

	@Override
	public void run() {
		while (true) {
			BaseManager manager = ManagerFactory.getManager(ManagerFactory.MY_MANAGER);
			manager.logic();
			try {
				Thread.sleep(3000);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
}
```

##### ClassloaderTest

```java
package com.imooc.classloader;

import java.io.*;

/**
 * 测试Java类的热加载
 */
public class ClassLoaderTest {
	public static void main(String[] args) throws IOException {
		new Thread(new MsgHandler()).start();
//		System.out.println(Class.class.getClass().getResource("/").getPath());
	}
}
```

> 1. 使用debug方式启动
> 2. 修改代码后, 要重新编译项目. Command + F9

#### 2. 通过配置tomcat实现

##### 1. 直接启动tomcat后再把项目放进webapp

##### 2. 修改servlet.xml中, 在<host></host>中加入context标签中实现

```xml
<Context debug="0" docBase="D:/Imooc/web" path="/hot" privileged="true" reloadable="true"/>
```

> 要把原始项目中的META-INF/WEB-INF文件夹复制到D:/Imooc/web目录下, 然后访问: localhost:8080/hot/原始项目名. 观察tomcat日志, 发现已经热部署.

##### 3. 编写hot.xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<Context docBase = "D:/Imooc/web" reloadable = "true" />
```

然后把hot.xml复制到conf/catalina/locahost下
然后把原始项目中的META-INF/WEB-INF文件夹复制到D:/Imooc/web目录下, 然后访问: localhost:8080/hot/原始项目名. 观察tomcat日志, 发现已经热部署.



### Spring Boot热部署的方式

#### IDEA的两项配置

1. File->Settings->Build,Execution,Deployment->Compiler,选中Build project automatically 
2. 快捷键 Shift+Ctrl+Alt+/ ，点击 Registry，根据首字母找到compiler.automake.allow.when.app.running，选中即可。

#### Chrome的一项配置

1. F12（或Ctrl+Shift+J或Ctrl+Shift+I）--> NetWork --> Disable Cache(while DevTools is open) 

#### 方式一: springloaded

##### 修改pom.xml

```xml
<plugins>
	<plugin>
    	<groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>springloaded</artifactId>
            <version>1.2.8.RELEASE</version>
        </dependency>
    </plugin>
</plugins>
```

##### 执行 mvn spring-boot:run

#### 方式二: dev-tools

##### 引入依赖

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <optional>true</optional>
</dependency>

<build>  
    <plugins>  
        <plugin>  
            <groupId>org.springframework.boot</groupId>  
            <artifactId>spring-boot-maven-plugin</artifactId>  
            <configuration>  
                <fork>true</fork>  
            </configuration>  
        </plugin>  
    </plugins>  
</build>  
```

> 将依赖标记为`optional`可选是一种最佳做法，可以防止将devtools依赖传递到其他模块中。
>
> 运行打包的应用程序时，开发人员工具会自动禁用。如果你通过 `java -jar`或者其他特殊的类加载器进行启动时，都会被认为是“生产环境的应用”。

##### 1. 自动禁用了缓存

Spring Boot 支持的一些库中会使用缓存来提高性能。例如模版引擎将缓存编译后的模板，以避免重复解析模板文件。 此外，Spring MVC可以在服务静态资源时向响应中添加HTTP缓存头。

虽然缓存在生产中非常有益，但它在开发过程中可能会产生反效果，它会阻止你看到刚刚在应用程序中进行的更改。 因此，spring-boot-devtools将默认禁用这些缓存选项。

缓存选项通常在`application.properties`文件中配置。 例如，Thymeleaf提供了`spring.thymeleaf.cache`属性。`spring-boot-devtools`模块不需要手动设置这些属性，而是自动应用合理的开发时配置。

##### 2. 自动重启

`spring-boot-devtools`会在类路径上的文件发生更改时自动重启。 这在IDE中工作时可能是一个有用的功能，因为它为代码更改提供了非常快的反馈循环。 默认情况下会监视类路径上的所有变动，但请注意，某些资源（如静态资源和视图模板）不需要重启应用程序。

> **触发重启**
>
> 当DevTools监视类路径资源时，触发重启的唯一方法是更新类路径。 导致类路径更新的方式取决于你正在使用的IDE。在Eclipse中，保存修改的文件将导致类路径被更新并触发重启。 在IntelliJ IDEA中，构建项目（ `Build -> Make Project` ）将具有相同的效果。
>
> **重新启动和重新加载**
>
> Spring Boot提供的重新启动技术使用了两个类加载器。 不改变的类（例如，来自第三方jar的）被加载到 *base* 类加载器中。 你正在开发的类被加载到 *restart* 类加载器中。 当应用程序*重启*时， *restart*加载器将被丢弃，并创建一个新的类加载器。 这种方法意味着应用程序重启通常比“冷启动”快得多，因为 *base* 加载器已经已加载并且可用。

##### 3. 排除资源

某些资源在更改时不一定需要触发重启。 例如，可以直接编辑Thymeleaf模板。 **默认情况下**，更改`/META-INF/maven` ， `/META-INF/resources` ， `/resources` ， `/static` ， `/public`或`/templates`中的资源不会触发重启，但会触发实时重新加载。 如果要自定义这些排除项，可以使用`spring.devtools.restart.exclude`属性。 例如，要**仅排除**`/static`和`/public`你将设置以下内容：

```
spring.devtools.restart.exclude = static/**, public/** 1
```

> 如果你想保留上面**的默认（情况下的）值**并添加其他的排除项，你可以使用
>
> `spring.devtools.restart.additional-exclude` 属性。

##### 4. 监控额外的路径

当你对不在类路径中的文件进行更改时，可能需要重启或重新加载应用程序。 为此，请使用`spring.devtools.restart.additional-paths`属性来配置监视其他路径的更改。 你可以使用上述的`spring.devtools.restart.exclude`属性来控制附加路径下的更改是否会触发完全重启或只是实时重新加载 。

##### 5. 禁用重启

如果不想使用重启功能，可以使用`spring.devtools.restart.enabled`属性来禁用它。 在大多数情况下，你可以在`application.properties`中设置此项（这仍将初始化重启类加载器，但不会监视文件更改）。

例如，如果你需要**完全**禁用重启支持，因为它不适用于特定库，则需要在调用`SpringApplication.run(…)`之前设置`System`属性。 例如：

```java
public static void main(String[] args) {
    System.setProperty("spring.devtools.restart.enabled", "false");
    SpringApplication.run(MyApp.class, args);
} 
```

#### 方式三 使用jar包

##### 在VM options中, 添加启动参数

```java
-javaagent:E:\DEV\springloaded-1.2.6.RELEASE.jar -noverify
```



