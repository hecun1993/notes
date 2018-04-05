## HttpClient

### RestAutoConfig

```java
@Configuration
public class RestAutoConfig {

	public static class RestTemplateConfig {

		//支持负载均衡的RestTemplate
		@Bean
		@LoadBalanced //spring 对restTemplate bean进行定制，加入loadbalance拦截器, 进行ip:port的替换, 替换成服务名. (因为在微服务调用时, 使用服务名调用)
		RestTemplate lbRestTemplate(HttpClient httpclient) {
			RestTemplate template = new RestTemplate(new HttpComponentsClientHttpRequestFactory(httpclient));
		    template.getMessageConverters().add(0, new StringHttpMessageConverter(Charset.forName("utf-8")));
		    template.getMessageConverters().add(1, new FastJsonHttpMessageConvert5());
		    return template;
		}
		
		@Bean
		RestTemplate directRestTemplate(HttpClient httpclient) {
			RestTemplate template = new RestTemplate(new HttpComponentsClientHttpRequestFactory(httpclient));
		    template.getMessageConverters().add(0, new StringHttpMessageConverter(Charset.forName("utf-8")));
		    template.getMessageConverters().add(1, new FastJsonHttpMessageConvert5());
		    return template;
		}
		
		//阿里的fastjson, 要加入pom依赖
		//一个问题, 默认支持MediaType.All, spring会使用字节流来处理, 而不是识别成json
		public static class FastJsonHttpMessageConvert5 extends FastJsonHttpMessageConverter4 {
			
			static final Charset DEFAULT_CHARSET = Charset.forName("UTF-8");
			
			public FastJsonHttpMessageConvert5() {
				setDefaultCharset(DEFAULT_CHARSET);
				setSupportedMediaTypes(Arrays.asList(MediaType.APPLICATION_JSON, new MediaType("application","*+json")));
			}
		}
	}
}
```

### HttpClientProperties

```java
@ConfigurationProperties(prefix="spring.httpclient")
public class HttpClientProperties {
	
	private Integer connectTimeOut = 1000;
	private Integer socketTimeOut = 1000000;
	private String agent = "agent";
	private Integer maxConnPerRoute = 10;
	private Integer maxConnTotaol   = 50;

	public Integer getConnectTimeOut() {
		return connectTimeOut;
	}
	public void setConnectTimeOut(Integer connectTimeOut) {
		this.connectTimeOut = connectTimeOut;
	}
	public Integer getSocketTimeOut() {
		return socketTimeOut;
	}
	public void setSocketTimeOut(Integer socketTimeOut) {
		this.socketTimeOut = socketTimeOut;
	}
	public String getAgent() {
		return agent;
	}
	public void setAgent(String agent) {
		this.agent = agent;
	}
	public Integer getMaxConnPerRoute() {
		return maxConnPerRoute;
	}
	public void setMaxConnPerRoute(Integer maxConnPerRoute) {
		this.maxConnPerRoute = maxConnPerRoute;
	}
	public Integer getMaxConnTotaol() {
		return maxConnTotaol;
	}
	public void setMaxConnTotaol(Integer maxConnTotaol) {
		this.maxConnTotaol = maxConnTotaol;
	}
}
```

### HttpClientAutoConfiguration

```java
@Configuration
@ConditionalOnClass({HttpClient.class})
@EnableConfigurationProperties(HttpClientProperties.class)
public class HttpClientAutoConfiguration {

	private final HttpClientProperties properties;
	public HttpClientAutoConfiguration(HttpClientProperties properties){
		this.properties = properties;
	}
	
	@Autowired
	private LogbookHttpRequestInterceptor logbookHttpRequestInterceptor;
	
	@Autowired
	private LogbookHttpResponseInterceptor logbookHttpResponseInterceptor;
	
	/**
	 * httpclient bean 的定义
	 * @return
	 */
	@Bean
	@ConditionalOnMissingBean(HttpClient.class)
	public HttpClient httpClient() {
		RequestConfig requestConfig = RequestConfig.custom()
				.setConnectTimeout(properties.getConnectTimeOut())
				.setSocketTimeout(properties.getSocketTimeOut()).build();// 构建requestConfig
		
		HttpClient client = HttpClientBuilder.create().setDefaultRequestConfig(requestConfig)
				.setUserAgent(properties.getAgent())
				.setMaxConnPerRoute(properties.getMaxConnPerRoute()) //每个应用的最大连接数
				.setMaxConnTotal(properties.getMaxConnTotaol()) //总的连接数
				.addInterceptorFirst(logbookHttpRequestInterceptor)
				.addInterceptorFirst(logbookHttpResponseInterceptor)
				.build();
		
		return client;
	}
}
```

### GenericRest

```java
/**
 * 既支持直连又支持服务发现的调用
 * 封装两种模式的RestTemplate
 */
@Service
public class GenericRest {
	
	@Autowired
	private RestTemplate lbRestTemplate;
	
	@Autowired
	private RestTemplate directRestTemplate;
	
	//区分调用直连还是负载均衡的请求
	private static final String directFlag = "direct://";
	
	public <T> ResponseEntity<T> post(String url, Object reqBody, ParameterizedTypeReference<T> responseType) {
		RestTemplate template = getRestTemplate(url);
		url = url.replace(directFlag, "");
		return template.exchange(url, HttpMethod.POST, new HttpEntity(reqBody), responseType);
	}
	
	public <T> ResponseEntity<T> get(String url, ParameterizedTypeReference<T> responseType) {
		RestTemplate template = getRestTemplate(url);
		url = url.replace(directFlag, "");
		return template.exchange(url, HttpMethod.GET, HttpEntity.EMPTY, responseType);
	}

	private RestTemplate getRestTemplate(String url) {
		if (url.contains(directFlag)) {
			return directRestTemplate;
		}else {
			return lbRestTemplate;
		}
	}
}
```

### RestCode

```java
public enum RestCode {

    OK(0, "OK"),
    UNKNOWN_ERROR(1, "用户服务异常"),
    WRONG_PAGE(10100, "页码不合法"),
    USER_NOT_FOUND(10101, "用户未找到"),
    ILLEGAL_PARAMS(10102, "参数不合法");

    public final int code;
    public final String msg;

    private RestCode(int code, String msg) {
        this.code = code;
        this.msg = msg;
    }
}
```

### RestResponse

```java
//所有的rest响应结果
@JsonInclude(Include.NON_NULL)
public class RestResponse<T> {

    private int code;
    private String msg;
    private T result;

    public static <T> RestResponse<T> success() {
        return new RestResponse<T>();
    }

    public static <T> RestResponse<T> success(T result) {
        RestResponse<T> response = new RestResponse<T>();
        response.setResult(result);
        return response;
    }

    public static <T> RestResponse<T> error(RestCode code) {
        return new RestResponse<T>(code.code, code.msg);
    }

    public RestResponse() {
        this(RestCode.OK.code, RestCode.OK.msg);
    }

    public RestResponse(int code, String msg) {
        this.code = code;
        this.msg = msg;
    }

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public T getResult() {
        return result;
    }

    public void setResult(T result) {
        this.result = result;
    }

    @Override
    public String toString() {
        return "RestResponse [code=" + code + ", msg=" + msg + ", result=" + result + "]";
    }
}
```

### 服务提供方

在服务提供方user中增加一个controller包

```java
@RestController
public class TestUserController {

    private static final Logger logger = LoggerFactory.getLogger(TestUserController.class);

    @RequestMapping("getUsername")
    public RestResponse<String> getUsername(Long id) {
        logger.info("Incoming Request...");
        return RestResponse.success("test httpclient...");
    }
}
```

### 服务的消费方

在服务的消费方api-gateway中定义dao service controller

```java
@Repository
public class TestUserDao {

    @Autowired
    private GenericRest rest;

    public String getUsername(Long id) {
        String url = "http://user/getUsername?id=" + id;
        RestResponse<String> response = rest.get(url, new ParameterizedTypeReference<RestResponse<String>>() {}).getBody();
        return response.getResult();
    }
}

@Service
public class TestUserService {

    @Autowired
    private TestUserDao testUserDao;

    public String getUsername(Long id) {
        return testUserDao.getUsername(id);
    }
}

@RestController
public class ApiTestUserController {

    @Autowired
    private TestUserService testUserService;

    @RequestMapping("test/getUsername")
    public RestResponse<String> getUsername(Long id) {
        return RestResponse.success(testUserService.getUsername(id));
    }
}
```

同时启动 eureka server, user, api-gateway, 分别访问user和api-gateway中的接口, 结果相同