## MongoDB

### 综述

1. 基于分布式文件存储的数据库。由C++语言编写
2. 是一个高性能，开源，无模式的文档型数据库，是一个介于关系数据库和非关系数据库之间的产品
3. 支持的数据结构非常松散，是类似json的bjson格式
4. MongoDB的适合对大量或者无固定格式的数据进行存储，比如：日志、缓存等。
5. 对事务支持较弱，不适用复杂的多文档（多表）的级联查询。
6. database -> collection -> document

### 在windows中使用

#### 1. 创建这样两个文件夹:

D:\Program Files (x86)\MongoDB\data

D:\Program Files (x86)\MongoDB\data\db

#### 2. 在cmd中

mongod --dbpath D:\Program Files (x86)\MongoDB\data\db

在D:\Program Files (x86)\MongoDB\bin下打开cmd

输入mongo。即可操作数据库

>  每个文档都有一个属性，为_id，用来保证每个文档的唯一性。可以自己设置，也可以mongodb自己生成。



### 对数据库和表的操作

db.persons.drop() -- 删除collection

db.dropDatabase() -- 删除database

db.persons.count() -- document的数量

db.persons.remove({}) -- 删除全部数据, 但索引会保留

db.persons.remove({name: "hds"}) -- 删除指定条件的数据



### \$lt, \$gt, \$gte, \$ne

db.stu.find({age: {$gte: 20}})

db.stu.find({age: {$gte:20}}, {gender: 1})

db.stu.find({$or: [{age: {$gte:20}}, {gender: 1}], name: 'mj'})

db.stu.find({age: {$in: [18, 28]}})

db.stu.find().limit(获取的文档条数).skip(跳过的记录数)

### 投影

只显示一个文档中的部分字段，值为1表示显示，值为0表示不显示。_id默认是显示的。

db.stu.find({}, {_id: 0, name: 1, gender: 0})

### 排序 sort 

1为升序，-1为降序。

db.stu.find().sort({gender: -1, age: 1})

### 统计个数 count

db.stu.count({age: {$gte: 20}, gender: 1})

db.stu.find({gender: 1}).count()

### 去重 distinct

查找年龄大于18的性别

db.stu.distinct('gender', {age: {$gt: 18}})

### 聚合 aggregate

主要用于计算数据，sum(), avg()

db.t.aggregate([管道1: {表达式1}, 管道2: {表达式2}])

##### $group:分组查询

db.stu.aggregate([
	{$group:
		{
			_id: '\$gender', (表示分组依据，$+某个字段)
			counter: {$sum: 1} (代表求和)
		}
	}
])

db.stu.aggregate([
	{$group:
		{
			_id: null, 表示分组的依据，目前是不分组，查询全部。
			counter: {$sum: 1},
			avgAge: {\$avg: '$age'}
		}
	}
])

##### $match: 过滤数据，只输出符合条件的文档

db.stu.aggregate([
	{$match: {age: {$gt: 20}}},
		{$group: 
			{
				_id: '$gender', 
				counter: {$sum: 1}
			}
		}
	}
])

##### $project: 表示输出哪些查询结果，1表示输出，0不输出。

db.stu.aggregate([
	{$group: {_id: '$gender', counter: {$sum: 1}}},
	{$project: {_id: 0, counter: 1}}
])

##### \$sort, \$skip, $limit:

db.stu.aggregate([
	{$group: {_id: '$gender', counter: {$sum: 1}}},
	{$sort: {counter: 1}},
	{$skip: 1},
	{$limit: 1}

]}

### 创建超级管理用户

db.createUser({
	user: 'admin',
	pwd: '123',
	roles: [{role: 'root', db: 'admin'}]
})

### upsert方法说明

MongoDB的update方法的第三个参数是upsert，这个参数是个布尔类型，默认是false

当它为true的时候，update方法会首先查找与第一个参数匹配的记录，在用第二个参数更新之，如果找不到与第一个参数匹配的的记录，就插入一条。

#### 举例

db.post.update({count:100},{"$inc":{count:10}},true);

> 在找不到count=100这条记录的时候，自动插入一条count=100，然后再加10，最后得到一条 count=110的记录



### 其他

1. db.eval() -- 把字符串当成js代码
2. mongo不支持类似: db.persons.insert([{}, {}, {})

> 要想批量插入, 必须用for循环
>
> for(var i = 0; i < 10; i++) {
> 	db.persons.insert({name: i})
> }

3. save/insert: 当遇到_id相同的情况

> save: 保存, 同时更新 
>
> insert: 报错

4. 批量更新操作

   * 默认情况当查询器查询出多条数据的时候默认就修改第一条数据
   * 如何实现批量修改

   >  db.[documentName].update({name: 3}, {$set: {name: 33}}, false, true)

