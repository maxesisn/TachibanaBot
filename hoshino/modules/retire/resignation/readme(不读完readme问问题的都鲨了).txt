这是一个使用yobot的数据生成离职报告的hoshino插件，仅供娱乐
因插件使用过程中会读取yobot数据库，因程序运行故障导致数据库损坏本人概不负责

安装说明：
此插件试用于hoshino V1，已修复插件版yobot的超时问题
使用前请在yobot的web页面开启API访问（具体操作请阅读yobot文档）
0. 将retire文件夹放到modules文件夹里。确保路径结构是modules/retire/resignationforv1
1. 安装依赖 matplotlib，pillow 如果你成功安装过hoshino，这两个库应该已经装好了，这一步pass
2. 为matplotlib安装中文字体。如果你是Windows系统，这一步应该不需要做。linux系统请先使用 pip show matplotlib找到matplotlib的安装位置，并将msyh.ttf文件复制matplotlib/mpl_data的font目录下
3. 为pillow提供中文字体，将对应字体文件移到resignationforv1里应该就可以
3.在__init__.py里修改yobot的网址
4.在data_source.py里修改yobot的数据库路径，linux系统请确认相关文件的访问权限问题

使用方法：
指令[生成离职报告]：生成一张离职报告
指令[生成会战报告]：生成一张本期会战报告
指令[看看报告@某人]：看某人的会战报告（需要管理权限）

ps：
1.不同设备可能出现显示与预设结果不同，请尝试微调__init__.py里的坐标参数
2.此生成数据与yobotAPI返回数据相关，如希望数据真实，请会战前清除档案
3.修改年月星座在本目录下_init_.py的132-134行

特别鸣谢：
倚栏待月--代码的编写及指导（待月佬tql）
明见--背景图片以及字体提供（明见佬tql）
魔法の書--添加了一点点垃圾代码让显示的好看点（我是憨批）