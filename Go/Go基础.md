## Go基础

#### 安装Go

##### 解压go的tar包

##### 配置环境变量

```properties
# go压缩包解压后的位置
export GOROOT=/opt/install/go 
# 和go有关的程序运行时的位置(环境)
export GOPATH=/opt/install/go_path/codis 

export PATH=$PAHT:$GOROOT/bin
```

#### 安装glibc

解压glibc的tar包

cd glibc

mkdir build

cd build

../configure —prefix=/usr

make -j2

make install

#### 安装zookeeper

#### 安装codis

解压codis的tar包, 解压到安装go时配置的go_path中

然后创建config/redis.conf文件, 修改配置文件后, 启动codis-server即可