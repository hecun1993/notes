## Redis

### 综述

采用单进程模型, 处理客户端请求. 同一时刻, 只能处理一个命令.

Redis是单线程的, 不适合保存内容大的数据。

#### 缺点

速度问题. 虽然13年公布说可以处理60w的并发量

#### 优点

所有的内存服务器是没有事务支持的. 但redis的单进程可以帮助我们完成类似事务的功能, 保障一组操作是按照顺去执行.

Memcached只支持一种数据类型: key-value

redis可以支持六种数据类型(多了一种地图坐标)

redis加Lua可以实现类似存储过程的功能, 可以减少网络IO



### 安装

>  解压包中如果有MakeFile文件, 则不需要./configure, 只需要make make install

#### 下载redis.tar.gz

#### tar -zxvf redis.tar.gz

#### 进入根目录

#### make

#### make install PREFIX=/opt/install/redis 指定安装目录

#### cd /opt/install/redis/bin

#### cp /opt/software/redis/redis.conf /opt/install/redis 复制配置文件到启动目录

#### 启动 nohup redis-server &



### 事务 MULTI EXEC

Redis事务的实现需要用到 MULTI 和 EXEC 两个命令，事务开始的时候先向Redis服务器发送 MULTI 命令，然后依次发送需要在本次事务中处理的命令，最后再发送 EXEC 命令表示事务命令结束。



### 集群

所有的服务器之间都互相连通.客户端只要连接其中一个服务器,

各个节点的数据不同, 为了安全, 每个节点都需要加一个备份机;

#### 架构细节

1. 所有的redis节点彼此互联(PING-PONG机制),内部使用二进制协议优化传输速度和带宽.

2. 节点的fail是通过集群中超过半数的节点检测失效时才生效.(所以集群中至少有三个节点, 6台服务器)


3. Redis集群没有特定的入口。客户端与redis节点直连,不需要中间proxy层.客户端不需要连接集群所有节点,连接集群中任何一个可用节点，就相当于连接了所有的服务器.
4. 如何把所有存储的数据都分散到不同的节点上去呢?

> redis-cluster把所有的物理节点映射到[0-16383]个slot（槽）上, cluster 负责维护node<->slot<->value。
>
> redis 集群中内置了 16384 个哈希槽，当需要在 Redis 集群中放置一个 key-value 时，redis 先对 key 使用 crc16 算法算出一个结果，然后把结果对 16384 求余数，这样每个 key 都会对应一个编号在 0-16383 之间的哈希槽，redis 会根据节点数量大致均等的将哈希槽映射到不同的节点
>
> Hello这个key,经过上面的算法算出了余数是500,然后500就是槽,找到槽对应的服务器,把key放在对应的服务器中.

因此, 搭redis集群,集群中最多有16384个节点,每个服务器代表一个槽



### 五种数据类型

**Redis中所有的数据都是字符串。命令不区分大小写，key是区分大小写的。**

#### String: key 		

验证码，缓存，PV

#### Hash: key-fields-values		

一个key对应一个map，map中有key-value

```properties
hset person name jack
hset person age 20
hset person sex famale
hkeys person
hgetall person
hvals person
```

#### List: 有顺序可重复	

最新列表，关注列表

#### Set: 无顺序不可重复	

点赞点踩，抽奖，共同好友，已读

#### Zset: 有顺序不能重复

排行榜



### 其他命令	

flushdb 清除redis数据库

Key的命令: 

* expire key second	(设置key的过期时间)
	 ttl key 			(查看key的有效期)
	 persist key 		(清除key的过期时间，key持久化)

 monitor 监听redis的日志命令



### redis持久化方案

> redis所有数据都存在内存中。所以才需要持久化

#### RDB

快照形式，定期把内存中当前时刻的数据保存到磁盘。Redis默认支持的持久化方案。

#### AOF

append only file。把所有对redis数据库操作的命令，增删改操作的命令。保存到文件中。数据库恢复时把所有的命令执行一遍即可。

#### 注意

* 默认是RDB，如果想开启AOF，在redis.conf中搜索"aof"，appendonly no --> appendonly yes
* 两种持久化方案同时开启使用aof文件来恢复数据库。
* redis在强行终止服务的时候, 不会持久化, 只有在./redis-cli shutdown的时候才会持久化. 也可以人为触发save命令, 来持久化

### redis的性能

#### 基于内存 单进程单线程模型; 

##### 优势

* 代码更清晰，处理逻辑更简单
* 不用去考虑各种锁的问题，不存在加锁释放锁操作，没有因为可能出现死锁而导致的性能消耗
* 不存在多进程或者多线程导致的切换而消耗CPU
* 但是, 无法发挥多核CPU性能，不过可以通过在单机开多个Redis实例来完善；

> 完全基于内存
>
> 数据结构简单，对数据操作也简单
>
> 使用多路 I/O 复用模型



### redis一致性算法

将数据和用来缓存的机器进行相同的hash操作, 然后放在同一个hash环形空间中.

当移除或者添加用来缓存的机器时, 数据的重新分配很少

#### 问题

会有ip倾斜性, 也就是用来缓存的机器都集中在环形空间的一侧, 这样导致很多数据会集中在一个缓存机器上

#### 解决

增加很多个虚拟节点, 对每个虚拟节点进行hash操作, 来映射到真实的节点上(用虚拟节点对真实节点进行放大)



### redis.conf配置文件

#### 增加密码

改绑定的可以访问本redis的ip, 由127.0.0.1改成0.0.0.0

改允许后台执行 daemonize yes

改redis的密码, requirepass 123456

重新启动redis-server ./redis.conf

此时需要先auth 123456, 然后再get key1

#### 主从同步

在6380里

slaveof 127.0.0.1 6379

只能读, 不能写