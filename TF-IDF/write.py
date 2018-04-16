#!/user/bin/python
# coding:utf-8

import nltk
import numpy
import jieba
import codecs
import os

class SummaryTxt:
    def __init__(self,stopwordspath):
        # 单词数量
        self.N = 100
        # 单词间的距离
        self.CLUSTER_THRESHOLD = 5
        # 返回的top n句子
        self.TOP_SENTENCES = 5
        self.stopwrods = {}
        #加载停用词
        if os.path.exists(stopwordspath):
            stoplist = [line.strip() for line in codecs.open(stopwordspath, 'r', encoding='utf8').readlines()]
            self.stopwrods = {}.fromkeys(stoplist)


    def _split_sentences(self,texts):
        '''
        把texts拆分成单个句子，保存在列表里面，以（.!?。！？）这些标点作为拆分的意见，
        :param texts: 文本信息
        :return:
        '''
        splitstr = '.!?。！？'
        start = 0
        index = 0  # 每个字符的位置
        sentences = []
        for text in texts:
            if text in splitstr:  # 检查标点符号下一个字符是否还是标点
                sentences.append(texts[start:index + 1])  # 当前标点符号位置
                start = index + 1  # start标记到下一句的开头
            index += 1
        if start < len(texts):
            sentences.append(texts[start:])  # 这是为了处理文本末尾没有标

        return sentences

    def _score_sentences(self,sentences, topn_words):
        '''
        利用前N个关键字给句子打分
        :param sentences: 句子列表
        :param topn_words: 关键字列表
        :return:
        '''
        scores = []
        sentence_idx = -1
        for s in [list(jieba.cut(s)) for s in sentences]:
            sentence_idx += 1
            word_idx = []
            for w in topn_words:
                try:
                    word_idx.append(s.index(w))  # 关键词出现在该句子中的索引位置
                except ValueError:  # w不在句子中
                    pass
            word_idx.sort()
            if len(word_idx) == 0:
                continue
            # 对于两个连续的单词，利用单词位置索引，通过距离阀值计算族
            clusters = []
            cluster = [word_idx[0]]
            i = 1
            while i < len(word_idx):
                if word_idx[i] - word_idx[i - 1] < self.CLUSTER_THRESHOLD:
                    cluster.append(word_idx[i])
                else:
                    clusters.append(cluster[:])
                    cluster = [word_idx[i]]
                i += 1
            clusters.append(cluster)
            # 对每个族打分，每个族类的最大分数是对句子的打分
            max_cluster_score = 0
            for c in clusters:
                significant_words_in_cluster = len(c)
                total_words_in_cluster = c[-1] - c[0] + 1
                score = 1.0 * significant_words_in_cluster * significant_words_in_cluster / total_words_in_cluster
                if score > max_cluster_score:
                    max_cluster_score = score
            scores.append((sentence_idx, max_cluster_score))
        return scores

    def summaryScoredtxt(self,text):
        # 将文章分成句子
        sentences = self._split_sentences(text)

        # 生成分词
        words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in self.stopwrods if
                 len(w) > 1 and w != '\t']
        # words = []
        # for sentence in sentences:
        #     for w in jieba.cut(sentence):
        #         if w not in stopwords and len(w) > 1 and w != '\t':
        #             words.append(w)

        # 统计词频
        wordfre = nltk.FreqDist(words)

        # 获取词频最高的前N个词
        topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:self.N]

        # 根据最高的n个关键词，给句子打分
        scored_sentences = self._score_sentences(sentences, topn_words)

        # 利用均值和标准差过滤非重要句子
        avg = numpy.mean([s[1] for s in scored_sentences])  # 均值
        std = numpy.std([s[1] for s in scored_sentences])  # 标准差
        summarySentences = []
        for (sent_idx, score) in scored_sentences:
            if score > (avg + 0.5 * std):
                summarySentences.append(sentences[sent_idx])
                print (sentences[sent_idx])
        return summarySentences

    def summaryTopNtxt(self,text):
        # 将文章分成句子
        sentences = self._split_sentences(text)

        # 根据句子列表生成分词列表
        words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in self.stopwrods if
                 len(w) > 1 and w != '\t']
        # words = []
        # for sentence in sentences:
        #     for w in jieba.cut(sentence):
        #         if w not in stopwords and len(w) > 1 and w != '\t':
        #             words.append(w)

        # 统计词频
        wordfre = nltk.FreqDist(words)

        # 获取词频最高的前N个词
        topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:self.N]

        # 根据最高的n个关键词，给句子打分
        scored_sentences = self._score_sentences(sentences, topn_words)

        top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-self.TOP_SENTENCES:]
        top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
        summarySentences = []
        for (idx, score) in top_n_scored:
            print (sentences[idx])
            summarySentences.append(sentences[idx])

        return sentences



if __name__=='__main__':
    obj =SummaryTxt('D:\work\Solr\solr-python\CNstopwords.txt')

    with open("/home/tianbao/Desktop/news.txt", "r") as f:  
        txt = f.read() 
    
    with open("/home/tianbao/Desktop/a.txt","r") as book:
        R = book.read()

    print (R)
 
    # print (txt)
    print ("--")
    obj.summaryScoredtxt(txt)

    print ("----")
    #obj.summaryTopNtxt(txt)
