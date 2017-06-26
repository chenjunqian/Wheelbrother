# Wheelbrother


Wheelbrothe是基于朴素贝叶斯算法来模拟知乎[轮子哥](https://www.zhihu.com/people/excited-vczh/answers)的轮带逛。
通过爬取轮子哥主页的动态和[轮子哥带你逛知乎](https://www.zhihu.com/collection/61913303)的收藏夹的动态作为数据集进行算法处理。

因为[轮子哥带你逛知乎](https://www.zhihu.com/collection/61913303) 收藏夹是知乎用户[水见](https://www.zhihu.com/people/shui-jian/answers)通过轮子哥赞的内容进行手动收藏的，目前有1108条数据，可以当做是已经分类好的训练集，所以爬虫的主要工作就是爬取[轮子哥](https://www.zhihu.com/people/excited-vczh/answers)   主页的动态，[轮子哥带你逛知乎](https://www.zhihu.com/collection/61913303)的动态和关注轮子哥所有关注的用户。

爬取完成后，首先使用[结巴分词](https://github.com/fxsjy/jieba)分别对轮子哥主页的内容和收藏夹的内容进行分词，提取出出现频率前5000的词汇作为训练材料，通过朴素贝叶斯分类器训练函数:输出属于带逛每个词汇的出现概率，不属于带逛的每个词汇的出现概率，和内容属于带逛的概率。然后基于这个结果对于新的内容进行分类，判断是否属于轮带逛的答案。

所有关于知乎爬虫的代码在[crawler](https://github.com/chenjunqian/Wheelbrother/tree/master/crawler)中。

所有关于朴素贝叶斯算法的代码在[bayes.py](https://github.com/chenjunqian/Wheelbrother/blob/master/bayes.py)中。

执行测试和运行的入口在[test.py](https://github.com/chenjunqian/Wheelbrother/blob/master/test.py)中。
