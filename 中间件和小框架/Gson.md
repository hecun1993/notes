## Gson

### JsonToMap.java

```java
public class JsonToMap {

    /**
     * 获取JsonObject
     *
     * @param json
     * @return
     */
    public static JsonObject parseJson(String json) {
        JsonParser parser = new JsonParser();
        JsonObject jsonObj = parser.parse(json).getAsJsonObject();
        return jsonObj;
    }

    /**
     * 根据json字符串返回Map对象
     *
     * @param json
     * @return
     */
    public static Map<String, Object> toMap(String json) {
        return JsonToMap.toMap(JsonToMap.parseJson(json));
    }

    /**
     * 将JSONObject对象转换成Map-List集合
     *
     * @param json
     * @return
     */
    public static Map<String, Object> toMap(JsonObject json) {
        Map<String, Object> map = new HashMap<>();
        Set<Map.Entry<String, JsonElement>> entrySet = json.entrySet();
        for (Iterator<Map.Entry<String, JsonElement>> iter = entrySet.iterator(); iter.hasNext(); ) {
            Map.Entry<String, JsonElement> entry = iter.next();
            String key = entry.getKey();
            Object value = entry.getValue();
            if (value instanceof JsonArray)
                map.put(key, toList((JsonArray) value));
            else if (value instanceof JsonObject)
                map.put(key, toMap((JsonObject) value));
            else
                map.put(key, value);
        }
        return map;
    }

    /**
     * 将JSONArray对象转换成List集合
     *
     * @param json
     * @return
     */
    public static List<Object> toList(JsonArray json) {
        List<Object> list = new ArrayList<>();
        for (int i = 0; i < json.size(); i++) {
            Object value = json.get(i);
            if (value instanceof JsonArray) {
                list.add(toList((JsonArray) value));
            } else if (value instanceof JsonObject) {
                list.add(toMap((JsonObject) value));
            } else {
                list.add(value);
            }
        }
        return list;
    }
}
```

### Gson的基本使用(5个文件)

#### User.java

```java
@Data
@AllArgsConstructor
public class User {
    //省略其它
    public String name;
    public int age;

    @SerializedName(value = "emailAddress", alternate = {"email", "email_address"})
    //当上面的三个属性(email_address、email、emailAddress)都中出现任意一个时均可以得到正确的结果。
    //注：当多种情况同时出时，以最后一个出现的值为准。
    public String emailAddress;

    User(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

#### Result.java

```java
@Data
@AllArgsConstructor
public class Result<T> {
    public int code;
    public String message;
    public T data;
}
```

#### ParameterizedType.java

```java
/**
 Map<String, User>

 public interface ParameterizedType extends Type {
     // 返回Map<String, User>里的String和User，所以这里返回[String.class, User.class]
     Type[] getActualTypeArguments();

     // Map<String, User>里的Map,所以返回值是Map.class
     Type getRawType();

     // 用于这个泛型上中包含了内部类的情况,一般返回null
     Type getOwnerType();
 }

 */
public class ParameterizedTypeImpl implements ParameterizedType {

    private final Class raw;
    private final Type[] args;

    public ParameterizedTypeImpl(Class raw, Type[] args) {
        this.raw = raw;
        this.args = args != null ? args : new Type[0];
    }

    @Override
    public Type[] getActualTypeArguments() {
        return args;
    }

    @Override
    public Type getRawType() {
        return raw;
    }

    @Override
    public Type getOwnerType() {
        return null;
    }
}
```

#### GsonDemo.java

```java
public class GsonDemo {

    @Test
    public void test() {
        Gson gson = new Gson();

        //1. 基本数据类型的解析
        int i = gson.fromJson("100", int.class);              //100
        double d = gson.fromJson("\"99.99\"", double.class);  //99.99 (容错机制, 把String转成double类型)
        boolean b = gson.fromJson("true", boolean.class);     // true
        String str = gson.fromJson("String", String.class);   // String

        //2. 基本数据类型的生成
        String jsonNumber = gson.toJson(100);       // 100
        String jsonBoolean = gson.toJson(false);    // false
        String jsonString = gson.toJson("String"); //"String"

        //3. pojo类转成json
        User user = new User("怪盗kidou", 24);
        String jsonObject = gson.toJson(user); // {"name":"怪盗kidou","age":24}
        System.out.println(jsonObject);

        //4. json转成对应的pojo类
        String jsonString2 = "{\"name\":\"怪盗kidou\",\"age\":24}";
        User newUser = gson.fromJson(jsonString, User.class);
        System.out.println(newUser);
    }

    @Test
    public void test02() {
        //5. 属性重命名 @SerializedName 注解的使用
        /*
            Gson在序列化和反序列化时需要使用反射，说到反射就不得不想到注解.
            现在的目的是, 把json字符串转成pojo类, 但是pojo类的属性名, 可能与json中的键名不一致, 这时就需要用这个注解
         */
        Gson gson = new Gson();
        String json = "{\"name\":\"怪盗kidou\",\"age\":24,\"emailAddress\":\"ikidou_1@example.com\",\"email\":\"ikidou_2@example.com\",\"email_address\":\"ikidou_3@example.com\"}";
        User user = gson.fromJson(json, User.class);
        System.out.println(user.emailAddress); // ikidou_3@example.com
    }

    /**
     * Gson中使用泛型
     */
    @Test
    public void test03() {
        Gson gson = new Gson();
        String jsonArray = "[\"Android\",\"Java\",\"PHP\"]";
        //json字符串转成数组
        String[] strings = gson.fromJson(jsonArray, String[].class);
        /*
            json字符串转成List
            不能把String[].class转成List<String>.class
            因为: 对于Java来说List<String> 和List<User> 这俩个的字节码文件只一个那就是List.class，这是Java泛型使用时要注意的问题 泛型擦除。
            解决: 用TypeToken来存储泛型信息
                new TypeToken<List<String>>() {}.getType()

            TypeToken的构造方法是protected修饰的,所以上面才会写成new TypeToken<List<String>>() {}.getType() 而不是  new TypeToken<List<String>>().getType()
                原因: 匿名内部类, 这里其实是new了一个继承TypeToken的子类,
         */
        List<String> stringList = gson.fromJson(jsonArray, new TypeToken<List<String>>() {}.getType());
    }

    @Test
    public void test04() {
        /*
            要解析这样的json数据:
            {"code":"0","message":"success","data":{}}
            {"code":"0","message":"success","data":[]}

            原始做法:
                //=========
                public class UserResult {
                    public int code;
                    public String message;
                    public User data;
                }
                //=========
                public class UserListResult {
                    public int code;
                    public String message;
                    public List<User> data;
                }
                //=========
                String json = "{..........}";
                Gson gson = new Gson();
                UserResult userResult = gson.fromJson(json,UserResult.class);
                User user = userResult.data;

                UserListResult userListResult = gson.fromJson(json,UserListResult.class);
                List<User> users = userListResult.data;
                //=========
                但是重复定义了字段

                这时就要用TypeToken
         */

        String json = "{\"code\":\"0\",\"message\":\"success\",\"data\":{}}";

        Gson gson = new Gson();
        Type userType = new TypeToken<Result<User>>(){}.getType();
        Result<User> userResult = gson.fromJson(json, userType);
        User user = userResult.data;

        Type userListType = new TypeToken<List<User>>(){}.getType();
        Result<List<User>> userListResult = gson.fromJson(json, userListType);
        List<User> users = userListResult.data;
    }

    /**
     * 自定义的gson带泛型的解析
     */
    public void test05() {
        String json = "{\"code\":\"0\",\"message\":\"success\",\"data\":{}}";
        Result<User> userResult = GenerateTypeForGson.fromJsonObject(json, User.class);
        Result<List<User>> listResult = GenerateTypeForGson.fromJsonArray(json, User.class);
    }

    /**
     * 使用工具类生成泛型信息
     */
    public void test06() {
        String json = "{\"code\":\"0\",\"message\":\"success\",\"data\":{}}";
        Result<User> userResult = GenerateTypeForGson.fromJsonObject2(json, User.class);
        Result<List<User>> listResult = GenerateTypeForGson.fromJsonArray2(json, User.class);
    }

    /**
     * Gson提供了fromJson()和toJson() 两个直接用于解析和生成的方法，前者实现反序列化，后者实现了序列化。同时每个方法都提供了重载方法，我常用的总共有5个。
         Gson.toJson(Object);
         Gson.fromJson(Reader,Class);
         Gson.fromJson(String,Class);
         Gson.fromJson(Reader,Type);
         Gson.fromJson(String,Type);
     */
    public void test07() {

    }
}
```

#### GenerateTypeForGson.java

```java
public class GenerateTypeForGson {

    public static Gson gson = new Gson();

    public static <T> Result<T> fromJsonObject(String json, Class<T> clazz) {
        Type type = new ParameterizedTypeImpl(Result.class, new Class[]{clazz});
        return gson.fromJson(json, type);
    }

    public static <T> Result<List<T>> fromJsonArray(String json, Class<T> clazz) {
        // 生成List<T> 中的 List<T>
        Type listType = new ParameterizedTypeImpl(List.class, new Class[]{clazz});
        // 根据List<T>生成完整的Result<List<T>>
        Type type = new ParameterizedTypeImpl(Result.class, new Type[]{listType});
        return gson.fromJson(json, type);
    }

    public static <T> Result<T> fromJsonObject2(String json, Class<T> clazz) {
        Type type = TypeBuilder
                .newInstance(Result.class)
                .addTypeParam(clazz)
                .build();
        return gson.fromJson(json, type);
    }

    public static <T> Result<List<T>> fromJsonArray2(String json, Class<T> clazz) {
        Type type = TypeBuilder
                .newInstance(Result.class)
                .beginSubType(List.class)
                .addTypeParam(clazz)
                .endSubType()
                .build();
        return gson.fromJson(json, type);
    }

```

