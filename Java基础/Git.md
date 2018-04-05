### .gitignore文件

```properties
*.class

#package file
*.war
*.ear

#kdiff3 ignore
*.orig

#maven ignore
target/

#eclipse ignore
.settings/
.project
.classpath

#idea
.idea/
/idea/
*.ipr
*.iml
*.iws

# temp file
*.log
*.cache
*.diff
*.patch
*.tmp

# system ignore
.DS_Store
Thumbs.db
```



### git初始化项目

#### 1. 安装git并配置用户名和邮箱

https://github.com/git/git/releases?after=v2.9.1
homebrew: brew install git

配置用户名和密码, 在提交代码的记录上会展示

注意git config命令的--global参数，用了这个参数，表示你这台机器上所有的Git仓库都会使用这个配置

```properties
git config --global user.name "hecun93"
git config --global user.email "hecun93@gmail.com"

git config --global core.autocrlf false
git config --global core.quotepath off
```

#### 2. 建立电脑和远程仓库的访问通道

```properties
ssh-keygen -t rsa -C "hecun93@163.com"
ssh-add ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub
```

#### 3. 把.ssh文件夹中的id_rsa.pub复制到github中. 

登录到GitHub页面，Account Settings->SSH Public Keys->Add another key

#### 4. 在github中创建项目, 复制在github中的项目路径.

#### 5. 在电脑上创建项目文件夹, 执行以下命令

```properties
git init 创建版本库，多一个.git的目录
git status 查看哪些文件发生了变化
git add .
git commit -am ""
```

#### 6. 与远程仓库进行关联

```properties
git remote add origin https://xxx.git
```



### git操作

#### git clone xxx.git

一份origin的代码到本地，准备进行开发

#### fork

复制一份代码到自己的账号，作为自己的远程仓库

#### git remote add self git@git.elenet.me:cun.he/esmart.git 

给自己的远程仓库起名字为self，并建立起本地仓库和self仓库的联系。

#### git checkout -b etrace

在本地创建创建一个etrace分支，并切换到etrace分支上。

#### git remote 

查看远程库的信息

#### git add .

#### git commit -m "commit to etrace"

把代码提交到本地的etrace分支

>  更新本地develop分支上的代码，因为在这段时间，别人可能进行提交，所以要把最新的代码同步到本地的develop分支。

#### git checkout develop

先切换分支

#### git pull --rebase origin develop

再拉下代码来

>  git pull 是 git fetch + git merge FETCH_HEAD 的缩写。所以，默认情况下，git pull就是先fetch，然后执行merge 操作，如果加 *—rebase* 参数，就是使用git rebase 代替git merge	

#### git checkout etrace

切换回etrace分支

#### git rebase develop

在etrace分支上，把etrace分支上的代码合并到develop上

#### 解决冲突

#### git add .

#### git rebase --continue

#### git push self etrace

把本地etrace分支上的代码提交到self远程仓库中

#### 在网页上进行pull request请求，提交到origin的develop分支上

#### 或者git push origin develop

#### git clone -b dev https://xxx.git

克隆制定分支

#### git branch

查看本地分支

#### git branch -a

查看远程分支