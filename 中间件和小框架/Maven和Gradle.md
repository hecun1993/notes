## Maven

### maven中的scope属性

#### compile：编译依赖范围。如果没有指定，默认使用该依赖范围。

> 使用此依赖范围时，对于编译、测试、运行都有效。例如：spring-core，编译、测试、运行时都需要使用该依赖。

#### test：测试依赖范围。只对测试classpath有效。

> JUnit，它只在编译测试代码以及运行测试的时候才需要，编译和运行classpath时无法使用此依赖。

#### provided：已提供依赖范围。对于编译和测试时有效，但在运行时无效。

> servlet-api，编译和测试项目的时候需要该依赖，但运行时，由于容器已经提供，就不需要Maven重复的引入。

#### runtime：运行时依赖。编译时无效，对于测试和运行有效。

> JDBC驱动实现，编译时只需要JDK提供的JDBC接口，只有在执行测试和运行时才需要实现上述接口的具体JDBC驱动。

#### system：系统依赖范围。同provided。

> 使用该依赖时必须通过systemPath元素显式地指定依赖文件路径。主要用于依赖本地的、且Maven仓库之外的类库文件。



### maven环境隔离

#### 1. 在pom.xml中增加配置

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/resources.${deploy.type}</directory>
            <excludes>
                <exclude>*.jsp</exclude>
            </excludes>
        </resource>
        <resource>
            <directory>src/main/resources</directory>
        </resource>
    </resources>

    <plugins>
    	...
    </plugins>
</build>

<profiles>
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <deploy.type>dev</deploy.type>
        </properties>
    </profile>
    <profile>
        <id>beta</id>
        <properties>
            <deploy.type>beta</deploy.type>
        </properties>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <deploy.type>prod</deploy.type>
        </properties>
    </profile>
</profiles>
```

#### 2. 配置resources目录

在resources下建立resources.beta/dev/prod, 把各自环境中的配置信息文件放入各自文件夹之中. 

比如 datasource.properties, logback.xml, mmall.properties, zfbinfo.properties

#### 3. 启动

`mvn clean package -Dmaven.skip.test=true -Pdev`

打包一个dev环境的war包



### 引入依赖时排除某些jar依赖

```xml
<dependency>
    <groupId>com.101tec</groupId>
    <artifactId>zkclient</artifactId>
    <version>0.8</version>
    <exclusions>
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```



### 在打包时排除某些资源

```xml
<build>
    <resources>
        <resource>
            <directory>${basedir}/src/main/resources</directory>
            <excludes>
                <exclude>*.properties</exclude>
            </excludes>
        </resource>
    </resources>
    <plugins>
    	...
    </plugins>
</build>
```



### 引入大数据cloudera依赖

```xml
<repositories>
    <repository>
        <id>cloudera</id>
        <url>https://repository.cloudera.com/artifactory/cloudera-repos/</url>
    </repository>
</repositories>
```


### dependency的元素标签optional的作用

假如Project A的某个依赖D添加了<optional>true</optional>，当别人通过pom依赖Project A的时候，D不会被传递依赖进来

当你依赖某各工程很庞大或很可能与其他工程的jar包冲突的时候建议加上该选项，可以节省开销，同时减少依赖冲突

> 当我们依赖一个a.jar时，如果a.jar依赖b.jar，那么只需要早pom中声明对a.jar的依赖即可，b.jar会被Maven自动加载进来。

## Gradle

### 配置模板

```gradle
// buildscript 代码块中脚本优先执行
buildscript {

	// ext 用于定义动态属性
	ext {
		springBootVersion = '2.0.0.M4'
	}

	// 使用了Maven的中央仓库及Spring自己的仓库（也可以指定其他仓库）
	repositories {
		// mavenCentral()
		// 非稳定版spring boot， 所以要用spring提供的仓库
		maven { url "https://repo.spring.io/snapshot" }
		maven { url "https://repo.spring.io/milestone" }
		maven { url "http://maven.aliyun.com/nexus/content/groups/public/" }
	}

	// 依赖关系
	dependencies {
		// classpath 声明了在执行其余的脚本时，ClassLoader 可以使用这些依赖项
		classpath("org.springframework.boot:spring-boot-gradle-plugin:${springBootVersion}")
	}
}

// 使用插件
apply plugin: 'java'
apply plugin: 'eclipse'
apply plugin: 'org.springframework.boot'
apply plugin: 'io.spring.dependency-management'

// 指定了生成的编译文件的版本，默认是打成了 jar 包
group = 'com.waylau.spring.cloud'
version = '0.0.1-SNAPSHOT'

// 指定编译 .java 文件的 JDK 版本
sourceCompatibility = 1.8

// 依赖关系
dependencies {

	// 该依赖用于编译阶段
	compile('org.springframework.boot:spring-boot-starter-web')

	// 该依赖用于测试阶段
	testCompile('org.springframework.boot:spring-boot-starter-test')
}
```

### 编译整个工程，生成jar包，位置在/build/libs中：

* gradle build

### 运行项目：

* gradle bootRun