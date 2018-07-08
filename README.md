<font face ="微软雅黑">
 
# <center/>今日头条街拍美图爬取(2018.7)
## 1.查看网站跳转规则，了解网站运行机制
<font size = 3>①进入头条网站：www.taotiao.com;
 ![www.taotiao.com](https://i.imgur.com/YiAbBXl.jpg)
②在右上方的搜索框输入“街拍”，点击搜索，观察地址栏变化：
![https://www.toutiao.com/search/?keyword=街拍](https://i.imgur.com/aZm8YJE.jpg)
地址栏多了一个keyword参数，抓取网页的时候可以把keyword作为参数；打开调试器NetWork的Headers,可以发现真实的请求地址：真实的地址中还包含了若干请求参数：
![Real Request Url](https://i.imgur.com/1WgrHjp.jpg)
每个offset的查询参数如下：
![quey parameters](https://i.imgur.com/bmC5wMN.jpg)
③切换到“图集”选项块，地址栏没有变化；
![offset](https://i.imgur.com/lgaEnEY.jpg)
分别点击“综合，视频，图集，用户”几个选项卡，发现地址栏均没有变化，按F12打开调试器,查看后台的变化：选中NetWork,XHR,(XHR就是 XMLHttpRequest 对象,也就是ajax功能实现所依赖的对象)可以发现地址的from部分其实是有变化的，“综合，视频，图集，用户”几个选项卡分别对应“search_tab,video,gallery,media”,选中"from=gallery"，打开Preview查看其内容,在Preview中的data字段的内容中可以发现title字段和页面中的文字有对用的地方：
![from=gallery](https://i.imgur.com/lJCrGMa.jpg)
并且Preview中有一个article\_url字段，内容是一个网址：
![article_url](https://i.imgur.com/NAFc1fO.jpg)
打开看看其内容:![open article_url](https://i.imgur.com/oBc54hq.jpg)发现图集的照片和标题可以与原网页的内容对应，说明article\_url就是每个图集的地址，因为要抓取多个图集，我们在图集页面（from=gallery）向拉动，观察调试器的变化：
![offset change](https://i.imgur.com/2hSfvjz.jpg)

随着向下滑动，加载的图集增多，offset字段的值以10为单位递增，所以，爬取网页的时候，需要设置offset参数，查看每个offset的Response内容会发现，其中的data字段中包含了0~19个内容，每个内容有一个article\_url，表示一个图集：![data](https://i.imgur.com/5JSNzkl.jpg)，同时每个offset都包含了查询参数。
到此为止，我们已经找到了每个图集的网址，剩下就是从每个图集中抓取照片了；
##2.随机选择一个图集的地址，查看网页代码，寻找图片地址
<font size = 3>①例如，选取地址：http://toutiao.com/group/6575073049085739533/
![http://toutiao.com/group/6575073049085739533/](https://i.imgur.com/k3tEIkz.jpg)
②用requests.get("http://toutiao.com/group/6575073049085739533/"), 抓取网页，结果发现返回的结果为None,这种方法无法抓到图片，为什么已经找到了网页的地址，在浏览器打开正常，却抓不到结果呐？仔细观察可以发现，在浏览器地址栏输入http://toutiao.com/group/6575073049085739533/ 后，地址栏会自动变成https://www.toutiao.com/a6575073049085739533/ ，应该是在输入地址后，服务器进行了转发，此时有两种方法：

1. 方法一：把抓取到的图集网址进行转化把“group/”替换为“a”,然后使用requests.get()进行抓取就可以抓到返回的response的内容了。
2. 方法二：使用selenium库，使用自动化测试方法，这种方法不用转换地址，也可以抓取到response的内容；

③分析图集的response内容，获取图片的保存地址：
![response text](https://i.imgur.com/m52PMx5.jpg)
可以看到图片的url保存在JSON文件中，只需要对其进行解析，就可以拿到图片的url了，然后就可以进行下载保存了。
3.ToutiaoSpider source code:
经过上面的分析，要获取图片,至少要经过一下几个步骤：

1. 爬取“https://www.toutiao.com/search/?keyword=街拍” 页面的内容，同时要传入查询参数：本步骤response的内容为offset=0的20个图集的图集地址为JSON格式，进行JSON解析后，得到每个图集的地址；
2. 对于每一个图集地址进行转化，得到真正的图集地址；
3. 爬取图集地址的内容，对内容进行JSON解析，获取20个图集的每个图集的若干张照片的url地址；若要获取更多就需要在步骤1中，将offset设为参数，这样获取的照片数就是 N个offset*20*每个图集的照片数；
4. 通过照片的url地址经图片下载并保存到数据库中。

Version1.0:抓取一个offset的多个图集的照片;
</font>





