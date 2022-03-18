# 数据库课程设计 后端
# requirement
* python 3.8+
* PostgreSQL 14

## 安装库
在项目根目录下
```powershell
pip install -r requirements.txt
```
## 创建表
在项目根目录下
```powershell
createdb.exe tb
psql.exe -U postgres -d tb -f "src\sql\1_create_table.sql" 
psql.exe -U postgres -d tb -f "src\sql\3_create_table.sql" 
```
或者
```shell
createdb tb
psql -U postgres -d tb -f "src/sql/1_create_table.sql" 
psql -U postgres -d tb -f "src/sql/3_create_table.sql" 
```

# 启动server
在项目根目录下
```powershell
uvicorn src.main:app --reload 
```

# TODO List


| 大项                       | 小项                                                         | 完成情况              |
| -------------------------- | ------------------------------------------------------------ | --------------------- |
| 登录界面                   |                                                              | 1                     |
|                            | 登录                                                         | 1                     |
|                            | 注册                                                         | 1                     |
| 用户管理                   |                                                              |                       |
|                            | 激活用户                                                     | 1                     |
|                            | 添加/删除用户                                                |                       |
|                            | 查看用户信息                                                 | 1                     |
|                            | 可以查看数据库连接、后台数据库服务器<br/>及数据库的配置信息，可以设置、修改数据库连接时长、数据库缓冲区大小等参数。 |                       |
| 批量导入                   |                                                              |                       |
|                            | 输入文件分组                                                 | 1                     |
|                            | 范围检查                                                     |                       |
|                            | 批量导入命令                                                 | 1                     |
|                            | 触发器                                                       |                       |
| 数据导出                   |                                                              | 1                     |
|                            | 数据导出                                                     | 1                     |
| 索引设计                   |                                                              |                       |
|                            | 主键聚集索引                                                 |                       |
|                            | 非聚集索引设计                                               |                       |
|                            | 比较结果                                                     |                       |
| 数据库文件                 |                                                              |                       |
|                            | 观察数据库主文件、辅文<br/>件、日志文件、数据库文件<br/>组，列出文件、文件组名称 |                       |
|                            | Create Database 定义语句、<br/>所在磁盘分区；                |                       |
| 查询                       |                                                              | 1                     |
|                            | 小区配置信息查询                                             | 1                     |
|                            | 基站 eNodeB 信息查询                                         | 1                     |
|                            | 小区 KPI 指标信息查询                                        | 1 此处KPI表未完全建完 |
|                            | PRB 信息统计与查询                                           | 1                     |
| 主邻小区 C2I 干扰分析      |                                                              |                       |
|                            | 生成新表 tbC2Inew                                            |                       |
|                            | 函数实现：计算主邻小区RSRP 差值的均值、标准差。              |                       |
| 重叠覆盖干扰小区三元组分析 |                                                              |                       |
|                            | 根据表 tbC2Inew，找出所有的小区三元组<a, b, c>，             |                       |
| MRO/MRE 测量数据解析       |                                                              |                       |
|                            | 暂时没看到数据包                                             |                       |
|                            | MRO 数据入库，XML 数据<br/>解析，表结构和索引设计            |                       |
| 网络干扰结构分析           |                                                              |                       |
|                            | 干扰数据预处理                                               |                       |
|                            | 网络可视化                                                   |                       |

