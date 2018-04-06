#### User

```java
package org.spring5.model;

public class User {
	
	private int id;
	private String name;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                '}';
    }
}
```



#### UserRepository

```java
package org.spring5.repository;

import org.spring5.model.User;
import org.springframework.stereotype.Repository;

import java.util.Collection;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

@Repository
public class UserRepository {

    private final ConcurrentHashMap<Integer, User> repository = new ConcurrentHashMap<>();

    //id生成器
    private final static AtomicInteger idGenerator = new AtomicInteger();

    public boolean save(User user) {
        Integer id = idGenerator.getAndIncrement();
        user.setId(id);
        return repository.put(id, user) == null;
    }

    public Collection<User> findAll() {
	    return repository.values();
    }
}
```



#### Routes

```java
package org.spring5.routes;

import org.spring5.model.User;
import org.spring5.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.server.RequestPredicates;
import org.springframework.web.reactive.function.server.RouterFunction;
import org.springframework.web.reactive.function.server.RouterFunctions;
import org.springframework.web.reactive.function.server.ServerResponse;
import reactor.core.publisher.Flux;

import java.util.Collection;

import static org.springframework.web.reactive.function.server.RequestPredicates.accept;

/**
 * 路由函数与原先的controller类似, 相当于定义了@GetMapping等
 */
@Configuration //spring3
public class Routes {

    /**
     * Servlet:
     *  请求接口: ServletRequest, HttpServletRequest
     *  响应接口: ServletResponse, HttpServletResponse
     *
     * Spring 5:
     *  请求接口: ServerRequest
     *  响应接口: ServerResponse
     *
     *  既可以支持Servlet容器, 也可以支持自定义的容器, 比如Netty web Server
     *
     *  用函数式的方式声明EndPoint, 这个EndPoint就是一个rest服务的暴露
     *  Flux是0-N个对象集合
     *  Mono是0-1个对象集合
     *  Reactive中的Flux和Mono是异步处理的(非阻塞)
     *
     *  Flux和Mono都是Publisher, 服务器端的推模式, 把数据源推给请求方, 放在body中
     *
     *  本例中定义get请求, 并返回所有的用户对象: /person/find/all
     */

    @Bean
    @Autowired //方法参数的注入(set/get注入, 字段注入, 方法注入, 构造器注入), UserRepository作为消息的来源
    public RouterFunction<ServerResponse> personFindAll(UserRepository userRepository) {
        //定义映射关系
        return RouterFunctions.route(RequestPredicates.GET("/user/all").and(accept(MediaType.APPLICATION_JSON)),
                request -> {
                    //数据源
                    Collection<User> users = userRepository.findAll();
                    Flux<User> flux = Flux.fromIterable(users);
                    return ServerResponse.ok().body(flux, User.class);
                });
    }
}
```



#### UserController

```java
package org.spring5.controller;

import org.spring5.model.User;
import org.spring5.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.server.ServerResponse;

import reactor.core.publisher.Mono;

@RestController("/user")
public class UserController {

    //使用构造器注入: 不能修改, 可以提早进行初始化
    private final UserRepository userRepository;

    @Autowired
    //是spring传递的这个参数
    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @PostMapping
    public User save(@RequestParam("name") String name) {
        User user = new User();
        user.setName(name);
        if (userRepository.save(user)) {
            System.out.printf("用户对象: %s 保存成功! \n", user);
        }

        return user;
    }

//	@GetMapping("/user")
//	public Mono<ServerResponse> handleGetUsers() {
//		return WebClient.create("http://localhost:9000").get().uri("/api/user")
//				.accept(MediaType.APPLICATION_JSON).exchange().flatMap(resp -> ServerResponse.ok().body(resp.bodyToFlux(User.class), User.class));
//	}
//
//	@GetMapping("/user/{id}")
//	public Mono<ServerResponse> handleGetUserById(@PathVariable String id) {
//		return WebClient.create("http://localhost:9000").get().uri("/api/user/" + id)
//				.accept(MediaType.APPLICATION_JSON).exchange().flatMap(resp -> ServerResponse.ok().body(resp.bodyToMono(User.class), User.class));
//	}
}
```

