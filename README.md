# HMM_Postags
Chinese Postagging Based on HMM

使用Python实现的词性标注程序。

## 一、训练语料

考虑到实验的效率，只采用了30M新闻带标注语料作为训练语料。

![pos1](https://github.com/asura1995/HMM_Postags/blob/master/pos1.png)
 
## 二、	测试语料

测试语料是从网络上选择的随机一则新闻。如下图所示。

![pos2](https://github.com/asura1995/HMM_Postags/blob/master/pos2.png)

## 三、	测试结果

使用词性标注程序标注后，结果如下：

![pos3](https://github.com/asura1995/HMM_Postags/blob/master/pos3.png)

可以看到，受限于实验语料的大小，标注结果仍不太理想。主要有以下几点：

1. 对于未在训练语料中出现的词或字，只是标注为“DNF”（“Does Not Found”），并且在训练时对其进行了平滑处理。因此不具备新词发现能力，也不具备命名实体识别能力；

2. 部分分词结果出现错误，需要进行消歧处理。
