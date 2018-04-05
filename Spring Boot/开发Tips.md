### 分页操作

#### 第一种方式

1. 定义PageModel<T> 

```java
//PageModel对象, 有pageNo和pageSize两个默认值, 总共有四个属性, 还有一个方法
Data
@NoArgsConstructor
@AllArgsConstructor
public class PageModel<T> {
    //分页查询得到的结果集
    private List<T> datas;
    //总记录数
    private int rowCount;
    //每页显示条数
    private int pageSize = 10;
    //第几页
    private int pageNo = 1;

    //总页数
    public int getTotalPage() {
        return (rowCount + pageSize - 1) / pageSize;
    }
}
```

2. 在controller中, 将PageModel当成controller方法的参数, 传入service层. 此时, 传入service层的PageModel, 要么是只有pageNo和pageSize默认值, 其他属性都为空; 要么就是通过postman等工具添加了pageNo和pageSize请求参数, 其他属性都为空的PageModel.
3. repository层的代码, 相当于为PageModel添加了rowCount属性和datas属性. 总页数就可以计算出来. 然后返回经过**填充**的PageModel<Result>

```java
//repository
public PageModel<Result> findResultsByPageModel(Date start, Date end, PageModel<Result> pageModel) {
    Query query = new Query();
query.addCriteria(Criteria.where(Constants.START).gte(start).and("end").lte(end).and(Constants.STORY).is(Constants.PERFTEST));
    
    //总记录数
    int rowCount = (int) mongoTemplate.count(query, Result.class);
    pageModel.setRowCount(rowCount);

    //倒序查询得到结果
    query.with(new Sort(Sort.Direction.DESC, Constants.START));

    //验证需要跳过的数据条数
    int skip = (pageModel.getPageNo() - 1 >= 0) ? pageModel.getPageNo() - 1 : 0;
    query.skip(skip * pageModel.getPageSize()).limit(pageModel.getPageSize());

    List<Result> resultList = mongoTemplate.find(query, Result.class);
    pageModel.setDatas(resultList);

    return pageModel;
}

//service
public PageModel<Result> findForewarningByPageModel(Date start, Date end, PageModel<Result> pageModel) {
    return resultRepository.findResultsByPageModel(start, end, pageModel);
}

//controller
@GetMapping("/test")
public ResponseEntity<GeneralResponse> getForewarning(PageModel<Result> pageModel,
                                                      @RequestParam(value = "start", required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm") Date start,
                                                      @RequestParam(value = "end", required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm") Date end) {
    PageModel<Result> pageModelResult = resultService.findForewarningByPageModel(start, end, pageModel);
    GeneralResponse generalResponse = new GeneralResponse(ResponseStatus.SUCCESS, "get forewarning results success", pageModelResult);
    return new ResponseEntity<>(generalResponse, HttpStatus.OK);
}
```



### 枚举值的配置

```java
/**
 * Enum类型只能用getter
 */
public enum SnackExceptionEnum {

    THEME_NOT_EXIST(10, "该专题不存在"),
    PRODUCT_NOT_EXIST(11, "该商品不存在"),
    ;

    private Integer code;

    private String message;

    SnackExceptionEnum(Integer code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public Integer getCode() {
        return code;
    }
}
```



### 项目的请求返回类集合

#### 第一种方式

```java
public class GeneralResponse {
    private ResponseStatus status;
    private String message;
    private Object data;
}

public enum ResponseStatus {
    SUCCESS,
    ERROR,
    INVALID_REQUEST
}

@GetMapping("/isfinished")
public ResponseEntity<GeneralResponse> isFinished(@RequestParam("roundId") String roundId) {
    Result result = resultService.getResultByRoundId(roundId);
    GeneralResponse generalResponse = new GeneralResponse(ResponseStatus.SUCCESS, "get result success", result);
    return new ResponseEntity<>(generalResponse, HttpStatus.OK);
}
```



### InfluxDB的操作

```yaml
spring:  
  influxdb:
    url: http://adco-esm-relay-1.vm.elenet.me:6666
    username: root
    password: root
    database: esm
    retention-policy: autogen
```

```java
@Autowired
private InfluxDBTemplate<?> influxDBTemplate;

Query query = new Query(expression, database);
QueryResult queryResult = influxDBTemplate.query(query);
List<QueryResult.Result> results = queryResult.getResults();
if (results != null) {
    for (QueryResult.Result result : results) {
        List<QueryResult.Series> resultSeries = result.getSeries();
        if (resultSeries != null) {
            Map<String, String> tags = resultSeries.get(i).getTags();
            List<List<Object>> values = resultSeries.get(i).getValues();
        }
    }
}
```

### SpecialBeanUtils

```java
public class SpecificBeanUtils extends BeanUtils {

    private SpecificBeanUtils() {
    }

    /**
     * Override copyProperties method
     * in order not to copy the field when its value is null
     *
     * @param source
     * @param target
     * @throws BeansException
     */
    public static void copyProperties(Object source, Object target) {
        Class<?> actualEditable = target.getClass();
        PropertyDescriptor[] targetPds = getPropertyDescriptors(actualEditable);
        for (PropertyDescriptor targetPd : targetPds) {
            if (targetPd.getWriteMethod() != null) {
                PropertyDescriptor sourcePd = getPropertyDescriptor(
                        source.getClass(), targetPd.getName());
                if (sourcePd != null && sourcePd.getReadMethod() != null) {
                    try {
                        Method readMethod = sourcePd.getReadMethod();
                        if (!Modifier.isPublic(readMethod.getDeclaringClass().getModifiers())) {
                            readMethod.setAccessible(true);
                        }
                        Object value = readMethod.invoke(source);

                        if (value != null) {
                            Method writeMethod = targetPd.getWriteMethod();
                            if (!Modifier.isPublic(writeMethod.getDeclaringClass().getModifiers())) {
                                writeMethod.setAccessible(true);
                            }
                            writeMethod.invoke(target, value);
                        }
                    } catch (Exception ex) {
                        throw new FatalBeanException(
                                "Could not copy properties from source to target", ex);
                    }
                }
            }
        }
    }
}
```

### 通过线程id获取某一线程

```java
public class ThreadUtil {
	//对工具类, 要给这个类加上私有的构造函数
    private ThreadUtil() {
    }

    /**
     * 根据线程id获取某一线程
     * @param threadId
     * @return
     */
    public static Thread findThread(long threadId) {
        ThreadGroup group = Thread.currentThread().getThreadGroup();
        while(group != null) {
            Thread[] threads = new Thread[(int)(group.activeCount() * 1.2)];
            int count = group.enumerate(threads, true);
            for(int i = 0; i < count; i++) {
                if(threadId == threads[i].getId()) {
                    return threads[i];
                }
            }
            group = group.getParent();
        }
        return null;
    }
}
```

### UUIDUtils

```java
public class UuidUtil {

    private UuidUtil() {
    }

    private static final String[] CHARS = new String[]{
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C",
            "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
            "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"};

    /**
     * like 550E8400-E29B-11D4-A716-446655440000
     *
     * @return
     */
    public static String genTypicalUuid() {
        return UUID.randomUUID().toString();
    }

    private static String genUuid(int length, int radix) {
        StringBuilder buffer = new StringBuilder();
        String uuid = UUID.randomUUID().toString().replace("-", "");
        IntStream.range(0, length).forEach(i -> {
            String str = uuid.substring(i * 4, i * 4 + 4);
            int x = Integer.parseInt(str, radix);
            buffer.append(CHARS[x % 0x3E]);
        });
        return buffer.toString();
    }

    /**
     * like 5Ts8MFp3
     *
     * @return
     */
    public static String genShortUuid() {
        return genUuid(8, 16);
    }

}
```

或者可以使用commons-lang中提供的方法

```java
RandomStringUtils.randomAlphabetic(10);
```



### 生成订单号的方法

```java
public static synchronized String createOrderId() {
    char[] chars = new char[]{'A', 'B', 'C', 'D', 'E', 'F'};

    //获得当前年份
    Calendar calendar = Calendar.getInstance();
    int year = calendar.get(Calendar.YEAR);

    //产生六位随机数
    Random random = new Random();
    Integer number = random.nextInt(900000) + 100000;

    return chars[year - 2017] + String.valueOf(System.currentTimeMillis()) + String.valueOf(number);
}
```



### 注册用户为密码md5加密的工具类

```java
//需要借助Guava
public class HashUtils {
    private static final HashFunction FUNCTION = Hashing.md5();
    private static final HashFunction MURMUR_FUNC = Hashing.murmur3_128();
    private static final String SALT = "mooc.com";

    //为密码加盐并加密
    public static String encryPassword(String password) {
        HashCode code = FUNCTION.hashString(password + SALT, Charset.forName("UTF-8"));
        return code.toString();
    }

    //加密的方法
    public static String hashString(String input) {
        HashCode code = null;
        try {
            code = MURMUR_FUNC.hashBytes(input.getBytes("utf-8"));
        } catch (UnsupportedEncodingException e) {
            Throwables.propagate(e);
        }
        return code.toString();
    }
}
```



### 自动更新数据库的插入和更新时间

```java
public class BeanHelper {
    private static final String updateTimeKey = "updateTime";
    private static final String createTimeKey = "createTime";

    public static <T> void setDefaultProp(T target, Class<T> clazz) {
        PropertyDescriptor[] descriptors = PropertyUtils.getPropertyDescriptors(clazz);
        for (PropertyDescriptor propertyDescriptor : descriptors) {
            String fieldName = propertyDescriptor.getName();
            Object value;
            try {
                value = PropertyUtils.getProperty(target, fieldName);
            } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
                throw new RuntimeException("can not set property  when get for " + target + " and clazz " + clazz + " field " + fieldName);
            }
            if (String.class.isAssignableFrom(propertyDescriptor.getPropertyType()) && value == null) {
                try {
                    PropertyUtils.setProperty(target, fieldName, "");
                } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
                    throw new RuntimeException("can not set property when set for " + target + " and clazz " + clazz + " field " + fieldName);
                }
            } else if (Number.class.isAssignableFrom(propertyDescriptor.getPropertyType()) && value == null) {
                try {
                    BeanUtils.setProperty(target, fieldName, "0");
                } catch (Exception e) {
                    throw new RuntimeException("can not set property when set for " + target + " and clazz " + clazz + " field " + fieldName);
                }
            }
        }
    }

    public static <T> void onUpdate(T target) {
        try {
            PropertyUtils.setProperty(target, updateTimeKey, System.currentTimeMillis());
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
            return;
        }
    }

    public static <T> void onInsert(T target) {
        long time = System.currentTimeMillis();
        Date date = new Date(time);
        try {
            PropertyUtils.setProperty(target, updateTimeKey, date);
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
        }
        try {
            PropertyUtils.setProperty(target, createTimeKey, date);
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
        }
    }
}

//调用时
BeanHelper.onInsert(user);
```





### Thread.sleep的新方法

#### 1. Thread.sleep() 

一个静态方法，暂停线程时它不会释放锁，该方法会抛出InterrupttedException异常（如果有线程中断了当前线程）

Thread.sleep()是一个重载方法，可以接收长整型毫秒和长整型的纳秒参数，这样对程序员造成的一个问题就是很难知道到底当前线程是睡眠了多少秒、分、小时或者天.

#### 2. TimeUnit

```java
TimeUnit.MINUTES.sleep(4);
```

> 1. TimeUnit.sleep()内部调用的Thread.sleep()也会抛出InterruptException
>
> 2. 除了sleep的功能外，TimeUnit还提供了便捷方法用于把时间转换成不同单位，例如，如果你想把秒转换成毫秒，你可以使用下面代码：
>
>    ```java
>    // 44000
>    TimeUnit.SECONDS.toMillis(44)
>    ```



### 高级的toString方法

```java
ReflectionToStringBuilder.toString(userCondition, ToStringStyle.MULTI_LINE_STYLE)
```



### 其他

- web包里放controller，dto，form
- 异常拦截器包括两个部分，页面异常拦截器和Api异常拦截器
- 在做单元测试的时候，可以把springboot默认生成的主类当成父类，其他单测都继承这个类即可
- 尽量不要用外键, 而是用逻辑上的外键. 否则将来数据庞大之后, 要进行分库分表, 外键就是一种束缚.
- @Async注解加载A类的a方法上, 则A类的b方法调用a方法, 该注解无效, 必须在非A类中调用a方法才有效.

