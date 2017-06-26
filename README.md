# Wheelbrother

##*主要思路*

Wheelbrothe是基于朴素贝叶斯算法来模拟知乎[轮子哥](https://www.zhihu.com/people/excited-vczh/answers)的轮带逛。
通过爬取轮子哥主页的动态和[轮子哥带你逛知乎](https://www.zhihu.com/collection/61913303)的收藏夹的动态作为数据集进行算法处理。

因为[轮子哥带你逛知乎](https://www.zhihu.com/collection/61913303) 收藏夹是知乎用户[水见](https://www.zhihu.com/people/shui-jian/answers)通过轮子哥赞的内容进行手动收藏的，目前有1108条数据，可以当做是已经分类好的训练集，所以爬虫的主要工作就是爬取[轮子哥](https://www.zhihu.com/people/excited-vczh/answers)主页的动态，和[轮子哥带你逛知乎](https://www.zhihu.com/collection/61913303)的动态。

爬取完成后，首先使用[结巴分词](https://github.com/fxsjy/jieba)分别对轮子哥主页的内容和收藏夹的内容进行分词，提取出出现频率前5000的词汇。