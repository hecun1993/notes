## Spring Security

### Spring Security的配置

#### SecurityConfig

```java
package me.hds.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.security.oauth2.client.EnableOAuth2Sso;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.authentication.rememberme.JdbcTokenRepositoryImpl;
import org.springframework.security.web.authentication.rememberme.PersistentTokenRepository;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;

/**
 * 过滤器链, 放置在api前
 * SecurityPersistenceFilter: 检查session信息, 创建SecurityContext, 包含登录用户的信息的对象 -- 在过滤器链的最前面
 * 是否登录 == SecurityContext中是否有值(无值, 就会跳页面填登录名密码, 有值, 就可以访问)
 *
 * FilterSecurityInterceptor: 最后的拦截器, 判断SecurityContext中是否有值, 来决定如何响应
 *
 * 如果登录成功, 就会把SecurityContext放在session中了
 *
 */
@EnableWebSecurity //1
@Component
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true) //利用注解为方法授权
public class SecurityConfig extends WebSecurityConfigurerAdapter { //2

    @Autowired
    private MyUserDetailsService myUserDetailsService;

    @Autowired
    private BookShopAuthenticationSuccessHandler bookShopAuthenticationSuccessHandler;

    @Autowired
    private BookShopAuthenticationFailureHandler bookShopAuthenticationFailureHandler;

    @Autowired
    @Qualifier("dataSource")
    private DataSource dataSource;

    //7 记住我
    @Bean
    public PersistentTokenRepository persistentTokenRepository() {
        JdbcTokenRepositoryImpl tokenRepository = new JdbcTokenRepositoryImpl();
        //系统启动时就创建表, 第一次使用为true
        //tokenRepository.setCreateTableOnStartup(true);
        //设置数据源
        tokenRepository.setDataSource(dataSource);
        return tokenRepository;
    }

    //4 自定义UserDetailsService(用户名 密码 加密密码)
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth
            .userDetailsService(myUserDetailsService)
            .passwordEncoder(new BCryptPasswordEncoder());
    }

    //3
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
                //.httpBasic() //把用户名密码经过base64加密后, 放在header中
                //.and()

                .formLogin()
                    //5.自定义登录的页面, 参数等
                    .loginPage("/login.html")
                    .loginProcessingUrl("/auth")
                    .usernameParameter("username")
                    .passwordParameter("password")
                    //6.登录成功/失败后的处理(默认是跳转回原来请求的接口)
                    .successHandler(bookShopAuthenticationSuccessHandler)
                    .failureHandler(bookShopAuthenticationFailureHandler)
                .and()

                //跨站请求伪造
                //正常应用是可以转账的网站
                //张三点击钓鱼网站, 钓鱼网站会往正常应用发一个转账的请求, 转给钓鱼网站100元
                //这个请求是从张三的浏览器发出的, 带着张三浏览器上的cookie信息
                //如果正常应用只是通过浏览器携带的cookie判断张三是否登录, 而且此时cookie还没有过期, 那么正常应用就会给张三(钓鱼网站)转100元

                //解决: 每次浏览器访问登录页时, 服务器会发给浏览器一个_csrf的Token
                //浏览器用js从cookie中读取到这个信息, 把它放在表单的hidden中, 与用户名密码一起提交
                //因为钓鱼网站不能跨站读取cookie信息, 所以它拿不到存在浏览器cookie中的_csrf的token, 用来向服务器发起请求
                //可以避免csrf攻击
                .csrf()
                    //自动往浏览器的header中加token信息
                    //.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())

                //去除csrf
                    .disable()

                //.and()

                //7.记住我: 勾选之后, 登录成功后服务器会往cookie中写一个Token, 同时服务器会在数据库中记下该token和用户信息的一一对应关系
                .rememberMe()
                    //记住我功能, 就需要配置记录token和用户信息的数据表
                    .tokenRepository(persistentTokenRepository())
                    //设置token有效期
                    .tokenValiditySeconds(600)
                .and()

                //session管理
                //.sessionManagement()
                    //防止session固定攻击:
                    //钓鱼网站先访问目标网站, 获得一个JSESSIONID
                    //张三访问了钓鱼网站, 钓鱼网站给张三的浏览器在目标网站域下设置一个相同的JSESSIONID的cookie
                    //张三登录, 则session建立关联
                    //钓鱼网站和张三有相同的JSESSIONID, 则钓鱼网站也可以登录
                    //.sessionFixation().changeSessionId()
                    //1. session过期时间: application.yml: session.server.timeout = 600(s)
                    //.invalidSessionUrl("/session.html")
                    //2. 在当前系统中, session数量最多是1个
                    //A浏览器登录的情况下, B浏览器登录后, A浏览器会被踢下
                    //.maximumSessions(1)
                    //3. A浏览器登录后, B浏览器就无法登录
                    //.maxSessionsPreventsLogin(true)

                //.and()
                //.and()

                //开始授权
                .authorizeRequests()
                //antMatchers的第一种参数
                //.antMatchers(HttpMethod.GET).permitAll()

                //antMatchers的第二种参数
                .antMatchers("/book", "/login.html", "/auth", "/session.html").permitAll()
                .anyRequest()
                //.authenticated();

                //自己指定访问权限(使用配置控制url访问权限)
                .access("hasAuthority('admin')");

                //自定义授权模式
                //.access("@bookSecurity.check(authentication, request)");

    }
}
```

#### MyUserDetailsService

```java
package me.hds.config;

import org.apache.commons.lang.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.ArrayList;

/**
 * GrantedAuthority 用户被授予的权限
 */
@Component
public class MyUserDetailsService implements UserDetailsService {

    //实际情况中, 通过数据库来查询用户信息
    //@Autowired
    //private UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        if (StringUtils.equals(username, "huadeshui")) {
            String passwordFromDatabase = new BCryptPasswordEncoder().encode("123");
            return new User(
                    "huadeshui",
                    passwordFromDatabase,
                    AuthorityUtils.createAuthorityList("admin")
            );
        }
        return null;
    }
}
```

#### BookShopAuthenticationSuccessHandler

```java
package me.hds.config;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.security.web.authentication.SavedRequestAwareAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;

/**
 * 登录成功后的自定义处理逻辑
 * 比如可以记日志等
 */
@Component
//public class BookShopAuthenticationSuccessHandler implements AuthenticationSuccessHandler {
public class BookShopAuthenticationSuccessHandler extends SavedRequestAwareAuthenticationSuccessHandler {

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException, ServletException {
        //第三个参数: 获取到用户信息后的封装类Authentication
        System.out.println((UserDetails)authentication.getPrincipal()); //getPrincipal后, 得到的是UserDetails接口的实现
        //调用父类的方法, 登录成功后, 之前一句记录了日志, 现在是跳转回原来的页面
        super.onAuthenticationSuccess(request, response, authentication);
        new ArrayList<>().forEach(System.out::println);
    }
}
```

#### BookShopAuthenticationFailureHandler

```java
package me.hds.config;

import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.stereotype.Component;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * 登录失败之后的处理
 */
@Component
public class BookShopAuthenticationFailureHandler implements AuthenticationFailureHandler {

    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response, AuthenticationException exception) throws IOException, ServletException {
        response.getWriter().write(exception.getMessage());
    }
}
```



### 基本原理

1. 请求和响应是在一个线程中完成的
2. 请求 -> UsernamePasswordAuthenticationFilter(表单登录) -> BasicAuthenticationFilter(原始登录) -> ... -> ExceptionTranslationFilter(捕获后一个拦截器产生的异常, 决定后续的步骤) -> FilterSecurityInterceptor(根据配置查看这个用户需要经过哪些验证, 看session中是否有用户信息, 有则可以访问rest api, 否则就抛出异常) -> rest api

```java
1. 登录请求发来后, 首先来到UsernamePasswordAuthenticationFilter(是过滤器链上的一个过滤器, 负责处理登录请求).
    
2. 然后用拿到的登录名和密码, 构建一个UsernamePasswordAuthenticationToken的对象, 它是Authentication接口的实现. 然后把请求的相关信息也放在UsernamePasswordAuthenticationToken对象中

3. 使用AuthenticationManager,这个类本身不包含认证的逻辑,它的作用是用来收集和管理一组AuthenticationProvider(不同的登录方式, 认证逻辑不同). 首先拿到一组AuthenticationProviders, 然后for循环, 调用supports方法判断是否支持传入的Authentication的类型.
return this.getAuthenticationManager().authenticate(usernamePasswordAuthenticationToken)

4. 找出Provider之后, 执行验证. 过程中调用提供的UserDetailsService的实现, 根据用户名获得用户信息UserDetails. 然后进行预检查,密码检查和后检查. 如果检查都通过, 则重新创建UsernamePasswordAuthenticationToken对象, 把权限信息设置进去.
    
5. 登录成功, 调用onAuthenticationSuccess方法, 登录成功的处理器. 
```

### 认证结果如何在多个请求间共享

1. 最初的想法: 放在session中.
2. 把认证成功后构建的UsernamePasswordAuthenticationToken对象封装在SecurityContext中, 然后放在SecirutyContextHolder中.
3. SecirutyContextHolder是ThreadLocal的一个封装. 它是与线程绑定的map. 在同一个线程中, 这个方法里放的变量, 另外一个方法中可以读出. 可以理解为线程级别的变量.
4. SecurityContextPersistenceFilter在整个过滤器链的最前面.
  作用是检查session中是否有SecurityContext, 如果有, 就拿到线程变量中. 在返回时, 如果有, 就放到session中.
  SecurityContextHolder.getContext().getAuthentication();	

### OAuth协议:

#### 目标

让第三方应用可以在不知道用户的用户名密码的情况下, 访问用户存在应用服务器上的(自拍)数据

#### 当(自拍)数据变成了用户信息就变成了Spring social框架:

##### Spring social

把下面的流程封装到了SocialAuthenticationFilter中, 当请求来时, 在这个过滤器里实现了第三方登陆

##### 步骤

0. 用户访问client
1. 将用户导向认证服务器(访问服务器的url, 与第三步的url是一样的)
2. 用户同意授权
3. 服务提供商携带授权码返回client(返回的url地址就是回调地址, 在申请qq登录时, 需要填写一个回调域)
4. client向服务提供商申请令牌
5. 服务提供商发放令牌
6. client拿着令牌向服务提供商获取用户信息
7. 与服务提供商无关, client根据用户信息, 构建Authentication, 并放入SecurityContext中. 实际上就是完成了登录

##### 综述

1. 开发ServiceProvider, 需要getUserInfo()的Api类和OAuth2Template(封装前五步)
2. 用ConnectionFactory创建Connection类, 来封装社交登录后获得的用户信息, 
3. 期间需要调用ApiAdaptor,把不同应用在第六步获得的数据结构不同的用户信息适配转化成相同的Connection类封装用户信息, 然后存在数据库UserConnection表中
4. 构建出Authentication对象, 实现登录.

		Spring social框架: 封装的是client的行为

#### Spring security OAuth

封装的是服务提供商的行为, 来发令牌等

- 认证服务器(通过4种标准授权模式确认用户身份和权限(提供了默认实现),或者使自定义的认证方式(手机号, 社交账号等), 然后调用Token生成机制发给client,来实现Token的生成和存储(提供了默认的实现))
- 资源服务器(保护rest服务, 做法是在spring security过滤器链上加了一个`OAuth2AuthenticationProcessingFilter`, 作用是从请求中拿出token, 根据token的存储策略, 根据Token找到用户信息, 进行判断, 然后访问rest服务)
- ​

### JWT(json web token)

自包含: 令牌中包含有意义信息, 不需要到数据库等中读取令牌拿到有意义的信息

密签: 虽然大家都看得到JWT, 所以不要放敏感信息, 但是发出的令牌可以签名, 防止篡改

可扩展: 有意义的信息是可以扩展的		

#### 三种用户认证的方式

1. 借助于传统的Servlet容器的cookie-session机制
2. 借助外部存储redis实现的token机制, 但要依赖外部redis, 可以实现单点登录
3. 借助JWT, 将用户信息直接存在JWT中, 避免对外部存储设备redis的依赖

#### JWT的组成 (引入java-jwt的依赖)

skxal1231@!.sdjai02321@!.sdjaioxmsioadjoa#$

- Header JWT的类型(JWT类型 + 编码格式, 然后用Base64加密)
- PayLoad JWT的相关信息, 比如过期时间, 唯一标识, 服务器信息等, 构成的Json对象, 然后再进行Base64加密
- Signature 随机码加上前两部分的字符串

> JWT的缺陷, 一开始创建时就定死了有效期, 但用户的登出是随机的, 所以还是需要借助redis, 修改其有效时间

#### 示例一

1. 设计一个服务端的/auth接口, 用来让客户端向服务端申请钥匙 (将来是放在Header中, 如下)

   ```properties
   Authorization: Bearer skxal1231@!.sdjai02321@!.sdjaioxmsioadjoa#$
   ```

   获得的钥匙如下

   ```json
   {
       randomKey: "csahi79",
       token: "skxal1231@!.sdjai02321@!.sdjaioxmsioadjoa#$"
   }
   // 上面的token就是服务端给客户端的钥匙(客户端一般都是app)
   // randomKey是盐/随机字符串, 用来签名
   ```

2. 模拟客户端的操作

   ```java
   package com.stylefeng.guns.jwt;

   import com.alibaba.fastjson.JSON;
   import com.stylefeng.guns.core.util.MD5Util;
   import com.stylefeng.guns.rest.common.SimpleObject;
   import com.stylefeng.guns.rest.modular.auth.converter.BaseTransferEntity;
   import com.stylefeng.guns.rest.modular.auth.security.impl.Base64SecurityAction;

   /**
    * jwt测试
    */
   public class DecryptTest {

       public static void main(String[] args) {

           String key = "mySecret";
   		// 就是第一步中的token
           String compactJws = "eyJhbGciOiJIUzUxMiJ9.eyJyYW5kb21LZXkiOiJxczV4ZjciLCJzdWIiOiJhZG1pbiIsImV4cCI6MTUwNjM0Mzk4NywiaWF0IjoxNTA1NzM5MTg3fQ.N5_npknF-w_pq_3bi-cRp0HkjQqOVlK_dTh5QPIDYcWYCujp4uQ5-QrHDB86azHhsNKVgwpvh1_0ZkxmmEFsEQ";
           // 就是第一步中的randomKey
           String salt = "qs5xf7";

           // 执行业务逻辑, 比如插入一条数据, SimpleObject就是这条数据实体
           SimpleObject simpleObject = new SimpleObject();
           simpleObject.setUser("stylefeng");
           simpleObject.setAge(12);
           simpleObject.setName("ffff");
           simpleObject.setTips("code");

           // 把数据实体转成Json字符串
           String jsonString = JSON.toJSONString(simpleObject);
           // 然后进行Base64和md5加密, 得到新的加密后的字符串
           String encode = new Base64SecurityAction().doAction(jsonString);
           String md5 = MD5Util.encrypt(encode + salt);

           // 把上一步得到的字符串封装在一个实体类中
           // 这个实体类将来在请求服务端的业务接口(新增数据接口)时, 会让在body中
           // body中的请求参数包含 两个部分
           // 1. 插入的数据的本身(经过base64加密后的字符串) 
           // 2. 签名(经过base64加密后的字符串 + 盐(randomKey))
           // 然后请求服务端的真正业务接口, 就可以正常的返回数据了.
           BaseTransferEntity baseTransferEntity = new BaseTransferEntity();
           baseTransferEntity.setObject(encode);
           baseTransferEntity.setSign(md5);

           System.out.println(JSON.toJSONString(baseTransferEntity));

           //System.out.println("body = " + Jwts.parser().setSigningKey(key).parseClaimsJws(compactJws).getBody());
           //System.out.println("header = " + Jwts.parser().setSigningKey(key).parseClaimsJws(compactJws).getHeader());
           //System.out.println("signature = " + Jwts.parser().setSigningKey(key).parseClaimsJws(compactJws).getSignature());
       }
   }

   ```

   ​

#### 示例二

##### JwtHelper

```java
public class JwtHelper {

    private static final String SECRET = "session_secret";

    //发布者, 可以一起校验
    private static final String ISSUER = "mooc_user";

    public static String genToken(Map<String, String> claims) {
        try {
            Algorithm algorithm = Algorithm.HMAC256(SECRET);
            JWTCreator.Builder builder = JWT.create().withIssuer(ISSUER)
                    //过期时间
                    .withExpiresAt(DateUtils.addDays(new Date(), 1));
            //将参数claims, 也就是要存入jwt token的那些属性, 存入token中
            claims.forEach((k, v) -> builder.withClaim(k, v));
            //做一个签名算法
            return builder.sign(algorithm).toString();
        } catch (IllegalArgumentException | UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    public static Map<String, String> verifyToken(String token) {
        Algorithm algorithm = null;
        try {
            algorithm = Algorithm.HMAC256(SECRET);
        } catch (IllegalArgumentException | UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
        JWTVerifier verifier = JWT.require(algorithm).withIssuer(ISSUER).build();
        DecodedJWT jwt = verifier.verify(token);
        Map<String, Claim> map = jwt.getClaims();
        Map<String, String> resultMap = Maps.newHashMap();
        map.forEach((k, v) -> resultMap.put(k, v.asString()));
        return resultMap;
    }
}
```

##### UserService

```java
public class UserService {
    public User auth(String email, String passwd) {
	if (StringUtils.isBlank(email) || StringUtils.isBlank(passwd)) {
		throw new UserException(Type.USER_AUTH_FAIL, "User Auth Fail");
	}
	//先构造一个用户对象, 作为查询条件
	User user = new User();
	user.setEmail(email);
	user.setPasswd(HashUtils.encryPassword(passwd));
	user.setEnable(1);
	//开始查询用户
	List<User> list = getUserByQuery(user);
	if (!list.isEmpty()) {
		User retUser = list.get(0);
		//查到登录的用户后, 生成token, 存JWT
		onLogin(retUser);
		return retUser;
	}
	throw new UserException(Type.USER_AUTH_FAIL, "User Auth Fail");
}

	private void onLogin(User user) {
        String token = JwtHelper.genToken(ImmutableMap.of("email", user.getEmail(), "name", user.getName(), "ts", Instant.now().getEpochSecond() + ""));
        renewToken(token, user.getEmail());
        user.setToken(token);
    }
}
```

