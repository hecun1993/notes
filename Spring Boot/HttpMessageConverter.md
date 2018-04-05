## HttpMessageConverter

HttpMessageConverter<T> 是 Spring3.0 新添加的一个接口，负责将请求信息转换为一个对象（类型为 T），将对象（类型为T）输出为响应信息 

（1）**HttpInputMessage **将请求的信息先转为 **InputStream** 对象，InputStream 再由 **HttpMessageConverter** 转换为 SpringMVC 需要的java对象；

（2）SpringMVC 返回一个 java 对象， 并通过 HttpMessageConverter 转为响应信息，接着 **HttpOutputMessage** 将响应的信息转换为 **OutputStream**，接着给出响应。

1.DispatcherServlet 默认加载 HttpMessageConveter的6个实现类

2.加入 jackson jar包后，启动的时候加载7个HttpMessageConverter 的实现类

注意: 当控制器处理方法使用@RequestBody, 或者@ResponseBody时, spring首先根据请求头或响应头中的Accept属性, 选择匹配的HttpMessageConverter, 

自定义自己的消息转换器

```java
@Component
public class CustomJsonHttpMessageConverter implements HttpMessageConverter {

    //Jackson的json映射类
    private ObjectMapper objectMapper = new ObjectMapper();

    //该转换器支持的类型
    private List supportedMediaTypes = Arrays.asList(MediaType.APPLICATION_JSON);

    /**
     * 判断转换器是否可以将输入内容转换成 Java 类型
     *
     * @param clazz     需要转换的 Java 类型
     * @param mediaType 该请求的 MediaType
     * @return
     */
    @Override
    public boolean canRead(Class clazz, MediaType mediaType) {
        if (mediaType == null) {
            return true;
        }

        for (MediaType supportedMediaType : getSupportedMediaTypes()) {
            if (supportedMediaType.includes(mediaType)) {
                return true;
            }
        }

        return false;
    }

    /**
     * 判断转换器是否可以将 Java 类型转换成指定输出内容
     *
     * @param clazz     需要转换的 Java 类型
     * @param mediaType 该请求的 MediaType
     * @return
     */
    @Override
    public boolean canWrite(Class clazz, MediaType mediaType) {
        if (mediaType == null || MediaType.ALL.equals(mediaType)) {
            return true;
        }

        for (MediaType supportedMediaType : getSupportedMediaTypes()) {
            if (supportedMediaType.includes(mediaType)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 获得该转换器支持的 MediaType
     *
     * @return
     */
    @Override
    public List<MediaType> getSupportedMediaTypes() {
        return supportedMediaTypes;
    }

    /**
     * 读取请求内容，将其中的 Json 转换成 Java 对象
     *
     * @param clazz        需要转换的 Java 类型
     * @param inputMessage 请求对象
     * @return
     * @throws IOException
     * @throws HttpMessageNotReadableException
     */
    @Override
    public Object read(Class clazz, HttpInputMessage inputMessage) throws IOException, HttpMessageNotReadableException {
        return objectMapper.readValue(inputMessage.getBody(), clazz);
    }

    /**
     * 将 Java 对象转换成 Json 返回内容
     *
     * @param o             需要转换的对象
     * @param contentType   返回类型
     * @param outputMessage 回执对象
     * @throws IOException
     * @throws HttpMessageNotWritableException
     */
    @Override
    public void write(Object o, MediaType contentType, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException {
        objectMapper.writeValue(outputMessage.getBody(), o);
    }
}

```

```java
@Configuration
public class HttpMessageConverterConfig {

    @Bean
    public MappingJackson2HttpMessageConverter mappingJackson2HttpMessageConverter() {
        return new MappingJackson2HttpMessageConverter() {
            @Override
            protected void writeInternal(Object o, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException {
                ObjectMapper objectMapper = new ObjectMapper();
                String json = objectMapper.writeValueAsString(o);
                //加密
                String result = json + "加密";
                outputMessage.getBody().write(result.getBytes());
            }
        };
    }
}
```

```java
@Configuration
public class MyWebMvcConfigurer extends WebMvcConfigurerAdapter {

    @Autowired
    private MappingJackson2HttpMessageConverter mappingJackson2HttpMessageConverter;

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        converters.add(mappingJackson2HttpMessageConverter);
        super.configureMessageConverters(converters);
    }
}
```

