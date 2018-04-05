### HTTP和Websocket协议的区别

- http协议, 客户端和服务端传递数据, 在同一时刻, 数据传递方向只能有一个, 要么发送数据, 要么接收数据.
- websocket协议, 在同一个连接, 同一个时刻, 可以既发送数据, 也接收数据. 
- websocket是一个长连接协议, 不需要每次传输数据前都建立连接. 所以延迟低, 而且不需要每次携带一些连接信息, 传递的数据少.



### get和post的区别

- 不在于携带数据的多少, 那是浏览器厂商规定的.
- get是**幂等性**的, 从服务端获取数据, 无论获取多少次, 得到的结果是一样的
- post不是**幂等性**的. 向服务端提交数据, 目的是让服务端数据发生变化. 如果让服务端的数据产生变化, 那么就应该用post而不是get



### HTTP&HTTPS

- http是超文本传输协议，信息是明文传输（如果攻击者截取了在浏览器和服务器之间的传输报文，就可以读懂其中的信息），是无状态的。
- https是由具有安全性的**ssl加密传输协议**和HTTP协议一同构建的，需要到CA申请证书来验证服务器的身份，因此可进行加密传输和身份认证。  
- http和https使用的端口不一样，前者是80，后者是443。
- http请求建立在一次tcp连接的基础上; 一次tcp连接至少会产生一次或多次http请求



### URL（统一资源定位符）和URI（统一资源标识符）

- URI可以分为URL（具有位置信息）和URN（统一资源命名符，具有名字）或同时具备locators和names特性。URN作用就好像一个人的名字，URL就像一个人的地址。
- 换句话说：URN确定了东西的身份，URL提供了找到它的方式。  
- URI是以一种抽象的，高层次概念定义统一资源标识，而URL和URN则是具体的资源标识的方式。URL和URN都是URI的一种



### HTTP协议

- HTTP是超文本传输协议, 建立在TCP/IP协议基础上, 主要实现客户端与服务器端之间的通信
- 包含两类报文：请求报文和响应报文。
- HTTP请求报文: 由请求头, 请求行、空行和请求数据4个部分组成
- 是半双工的, 一次单向通讯
- 请求头和响应头会造成不必要的通讯负载

> 修正:
>
> 1. Ajax 仍然采用拉的模式, 无法避免头负载的问题. 但页面修改无需整体刷新.
> 2. Polling 接近于实时, 用Ajax模拟实时通讯, 浏览器不停的规律的发送请求

#### 请求报文

##### 1. 请求行 GET /index.html HTTP/1.1

```
* get方式不适合传输私密数据; 不适合传输大量数据; 
* 如果数据是英文字母/数字，原样发送;
* 如果是空格，转换为+;
* 如果是中文/其他字符，则直接把字符串用BASE64加密，得出如：%E4%BD%A0%E5%A5%BD; 其中％XX中的XX为该符号以16进制表示的ASCII。

* post方法将请求参数封装在HTTP请求数据中, 以名称/值的形式出现，可以传输大量数据，不会显示在URL中。
```

##### 2. 请求头

- 请求头部由关键字/值对组成，每行一对.
- 关键字和值用英文冒号“:”分隔。请求头部通知服务器有关于客户端请求的信息
```
User-Agent：产生请求的浏览器类型。
Accept：客户端可识别的内容类型列表。
Host：请求的主机名，允许多个域名同处一个IP地址，即虚拟主机。
```

##### 3. 空行

- 最后一个请求头之后是一个空行，发送回车符和换行符，通知服务器以下不再有请求头

##### 4. 请求数据

#### 响应报文
```
1xx：指示信息--表示请求已接收，继续处理。
2xx：成功--表示请求已被成功接收、理解、接受。
3xx：重定向--要完成请求必须进行更进一步的操作。
4xx：客户端错误--请求有语法错误或请求无法实现。
5xx：服务器端错误--服务器未能实现合法的请求。
```


### Websocket

#### 现实要求

当前的web需要的是可靠的, 近乎零延迟的实时通讯. 不仅需要广播, 还需要双向通讯. **(类似于消息系统中的点对点模式和发布订阅模式.)**

> * **单工 双工 半双工**
>
> ```java
> * 单工数据传输只支持数据在一个方向上传输；
> * 半双工数据传输允许数据在两个方向上传输，但是，在某一时刻，只允许数据在一个方向上传输，它实际上是一种切换方向的单工通信；
> * 全双工数据通信允许数据同时在两个方向上传输，因此，全双工通信是两个单工通信方式的结合，它要求发送设备和接收设备都有独立的接收和发送能力。 
> ```

#### Comet

是个整体的术语. 是一种长期持有HTTP请求的Web应用模型, 允许Web服务器向浏览器推送数据.

#### Demo

##### ChatServlet

```java
package comet;

import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.concurrent.BlockingDeque;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.LinkedBlockingDeque;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.catalina.comet.CometEvent;
import org.apache.catalina.comet.CometProcessor;

@WebServlet("/chat")
public class ChatServlet extends HttpServlet implements CometProcessor {

	private static final long serialVersionUID = 1L;

	protected MessageSender messageSender = null;

	public void init() throws ServletException {
		messageSender = new MessageSender();
		Thread messageSenderThread = new Thread(messageSender, "MessageSender[" + getServletContext().getContextPath() + "]");
		messageSenderThread.setDaemon(true);
		messageSenderThread.start();
	}

	public void destroy() {
		messageSender.stop();
		messageSender = null;
	}

	/**
	 * Process the given Comet event.
	 *
	 * @param event
	 *            The Comet event that will be processed
	 * @throws IOException
	 * @throws ServletException
	 */
	public void event(CometEvent event) throws IOException, ServletException {
		HttpServletRequest request = event.getHttpServletRequest();
		HttpServletResponse response = event.getHttpServletResponse();
		response.setCharacterEncoding("UTF-8");
		String sessionId = request.getSession(true).getId();

		if (event.getEventType() == CometEvent.EventType.BEGIN) {
			log("Begin for session: " + sessionId);
			messageSender.openSession(request, response);
			messageSender.send(sessionId, "<!DOCTYPE html>");
			messageSender.send(sessionId, "<head><title>JSP Chat</title></head><body>");
		} else if (event.getEventType() == CometEvent.EventType.ERROR) {
			log("Error for session: " + request.getSession(true).getId() + " , sub type :" + event.getEventSubType());
			messageSender.removeSession(request);
			event.close();
		} else if (event.getEventType() == CometEvent.EventType.END) {
			log("End for session: " + request.getSession(true).getId());
			messageSender.removeSession(request);
			PrintWriter writer = response.getWriter();
			writer.println("</body></html>");
			event.close();
		} else if (event.getEventType() == CometEvent.EventType.READ) {
			InputStream is = request.getInputStream();
			byte[] buf = new byte[512];
			do {
				int n = is.read(buf); // can throw an IOException
				if (n > 0) {
					String content = new String(buf, 0, n);
					log("Read " + n + " bytes: " + content + " for session: " + sessionId);
					messageSender.send(sessionId, content);
				} else if (n < 0) {
					error(event, request, response);
					return;
				}
			} while (is.available() > 0);
		}
	}

	private void error(CometEvent event, HttpServletRequest request, HttpServletResponse response) {
	}

	public static class Message {
		private final String sessionId;
		private final String value;

		public Message(String sessionId, String value) {
			this.sessionId = sessionId;
			this.value = value;
		}

		public String getSessionId() {
			return sessionId;
		}

		public String getValue() {
			return value;
		}

		public String toString() {
			return "Session [id :" + sessionId + "] : " + value;
		}
	}

	public class MessageSender implements Runnable {

		protected volatile boolean running = true;
		private ConcurrentMap<String, HttpServletResponse> responsesMap = new ConcurrentHashMap<String, HttpServletResponse>();
		private final BlockingDeque<Message> messagesQueue = new LinkedBlockingDeque<Message>();

		public void removeSession(HttpServletRequest request) {
			String sessionId = getSessionId(request);
			if (sessionId != null) {
				responsesMap.remove(sessionId);
			}
		}

		public void openSession(HttpServletRequest request, HttpServletResponse response) {
			String sessionId = getSessionId(request);
			if (sessionId != null) {
				responsesMap.putIfAbsent(sessionId, response);
			}
		}

		private String getSessionId(HttpServletRequest request) {
			String sessionId = null;
			HttpSession session = request.getSession(false);
			if (session != null) {
				sessionId = session.getId();
			}
			return sessionId;
		}

		public MessageSender() {
		}

		public void stop() {
			running = false;
		}

		public void send(String sessionId, String data) {
			Message message = new Message(sessionId, data);
			messagesQueue.add(message);
		}

		public void run() {
			while (running) {
				try {
					Message message = messagesQueue.take();
					String sessionId = message.getSessionId();
					HttpServletResponse response = responsesMap.get(sessionId);
					PrintWriter writer = response.getWriter();
					System.out.println("Thread " + Thread.currentThread().getName() + " , message : " + message.toString());
					writer.println(message.toString());
					writer.flush();
				} catch (Exception e) {
					log("IOExeption sending message", e);
				}
			}
		}
	}
}
```

##### URLClient

```java
URLClientpackage client;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.TimeUnit;

import org.apache.tomcat.util.http.fileupload.IOUtils;

public class URLClient {

	public static void main(String[] args) throws Exception {

		URL url = new URL("http://127.0.0.1:8080/chat");

		HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
		urlConnection.setDoOutput(true);
		urlConnection.setDoInput(true);

     	// 把消息发给服务端
		OutputStream outputStream = urlConnection.getOutputStream();

		outputStream.write("消息测试-1".getBytes("UTF-8"));
		outputStream.flush();
		outputStream.write("消息测试-2".getBytes("UTF-8"));
		outputStream.write("消息测试-3".getBytes("UTF-8"));
		outputStream.flush();

        // 读取服务端发来的内容
		InputStream inputStream = urlConnection.getInputStream();
		ByteArrayOutputStream bufferStream = new ByteArrayOutputStream(64);
		IOUtils.copyLarge(inputStream, bufferStream);
		
		System.out.println(bufferStream.toString("UTF-8"));
		outputStream.close();
		inputStream.close();
		urlConnection.disconnect();
	}
}
```



#### Websocket术语

端点(EndPoint) 连接(Connection) 对点(Peer) 会话(Session)

##### 端点的生命周期

###### 打开

>  EndPoint#onOpen(Session, EndPointConfig) — @OnOpen

###### 关闭

> EndPoint#onClose(Session, CloseReason) — @OnClose

###### 错误

> EndPoint#onError(Session, Throwable) — @OnError

#### 聊天室Demo

##### ChatApplication

```java
package me.hds.chat;

import me.hds.chat.websocket.ChatRoomServerEndpoint;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.socket.server.standard.ServerEndpointExporter;

@SpringBootApplication
public class ChatApplication {

	public static void main(String[] args) {
		SpringApplication.run(ChatApplication.class, args);
	}

	// 暴露ServerEndPoint
	@Bean
	public ServerEndpointExporter serverEndpointExporter() {
		return new ServerEndpointExporter();
	}

	@Bean
	public ChatRoomServerEndpoint chatRoomServerEndpoint() {
		return new ChatRoomServerEndpoint();
	}
}
```

##### ChatRoomServerEndpoint

```java
package me.hds.chat.websocket;

import javax.websocket.*;
import javax.websocket.server.PathParam;
import javax.websocket.server.ServerEndpoint;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 聊天室 {@link ServerEndpoint}
 */
@ServerEndpoint("/chat-room/{username}")
public class ChatRoomServerEndpoint {

    // 存储连接的Session信息
    private static Map<String, Session> livingSessions = new ConcurrentHashMap<String, Session>();

    /**
     * 刚刚打开连接的时候
     * @param username
     * @param session
     */
    @OnOpen
    public void openSession(@PathParam("username") String username, Session session) {
        String sessionId = session.getId();
        livingSessions.put(sessionId, session);
        // 服务端发给用户
        sendTextAll("欢迎用户[" + username + "] 来到聊天室！");
    }

    /**
     * 接收到消息的时候, 需要广播, 给所有的人都发送一遍这个消息
     * @param username
     * @param message
     */
    @OnMessage
    public void onMessage(@PathParam("username") String username, String message) {
        // 广播消息
        sendTextAll("用户[" + username + "] : " + message);
    }

    private void sendTextAll(String message) {
        livingSessions.forEach((sessionId, session) -> {
            sendText(session,message);
        });
    }

    private void sendText(Session session, String message) {
        // 从Websocket的Session中获得远程的客户端端点, 然后发送消息
        RemoteEndpoint.Basic basic = session.getBasicRemote();
        try {
            basic.sendText(message);
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    @OnClose
    public void onClose(@PathParam("username") String username, Session session) {
        String sessionId = session.getId();
        //当前的Session 移除
        livingSessions.remove(sessionId);
        //并且通知其他人当前用户已经离开聊天室了
        sendTextAll("用户[" + username + "] 已经离开聊天室了！");
    }
}
```

##### chat.html

```Html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">

    <title>聊天室</title>
    <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>

</head>

<body>

聊天消息内容：

<br/>

<textarea id="text_chat_content" readonly="readonly" cols="100" rows="9"></textarea>

<br/>

用户：<input id="in_user_name" value=""/>
<button id="btn_join">加入聊天室</button>
<button id="btn_exit">离开聊天室</button>

<br/>

输入框：<input id="in_msg" value=""/>
<button id="btn_send">发送消息</button>

<script type="text/javascript">
    $(document).ready(function () {
        // 链接前缀
        var urlPrefix = 'ws://127.0.0.1:8080/chat-room/';
        // js中的websocket对象
        var ws = null;
        // 点击加入聊天室之后的操作
        $('#btn_join').click(function () {
            // 从输入框中获得用户名
            var username = $('#in_user_name').val();
            // 拼成前缀+用户名, 得到完整的url
            var url = urlPrefix + username;
            // 创建Websocket对象
            ws = new WebSocket(url);

            // onmessage表示接收到来自服务器的消息, 实际上参数是一个事件event, 里面的数据是data属性
            ws.onmessage = function (event) {
                // 服务端发送的消息
                // 显示在聊天框中
                $('#text_chat_content').append(event.data + '\n');
            };

            // 关闭的时候, 要发送信息到聊天框中
            ws.onclose = function (event) {
                $('#text_chat_content').append('用户[' + username + '] 已经离开聊天室!');
            }

        });

        //客户端发送消息到服务器
        $('#btn_send').click(function () {
            var msg = $('#in_msg').val();
            if (ws) {
                ws.send(msg);
            }
        });

        //离开聊天室
        $('#btn_exit').click(function () {
            if (ws) {
                ws.close();
            }
        });
    })
</script>
</body>
</html>
```

