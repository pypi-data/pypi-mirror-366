from typing import List, Tuple, Set, Dict
import re
import jieba
import numpy as np
from collections import defaultdict, Counter
from simhash import Simhash


class TextDeduplicator:
    def __init__(self,
                 similarity_threshold: int = 3,
                 char_ngram_range: Tuple[int, int] = (3, 5),
                 word_ngram_range: Tuple[int, int] = (1, 3),
                 min_text_length: int = 50,
                 use_tfidf_weight: bool = True):
        """
        纯文本去重器

        Args:
            similarity_threshold: SimHash汉明距离阈值(0-64)，越小越严格
            char_ngram_range: 字符级n-gram范围
            word_ngram_range: 词级n-gram范围
            min_text_length: 最小文本长度过滤
            use_tfidf_weight: 是否使用TF-IDF权重
        """
        self.similarity_threshold = similarity_threshold
        self.char_ngram_range = char_ngram_range
        self.word_ngram_range = word_ngram_range
        self.min_text_length = min_text_length
        self.use_tfidf_weight = use_tfidf_weight

        self.fingerprints = {}  # url -> simhash值
        self.text_cache = {}  # url -> 清理后的文本
        self.feature_cache = {}  # 缓存所有文本的特征用于TF-IDF计算

        # 停用词（可根据需要扩展）
        self.stopwords = {'的', '了', '在', '是', '我', '有', '和', '就',
                          'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

    def normalize_text(self, text: str) -> str:
        """标准化文本"""
        if not text:
            return ""

        # 转小写
        text = text.lower()

        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)

        # 移除特殊字符，保留中英文、数字、基本标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff\.\,\!\?\;\:]', ' ', text)

        # 移除过短的数字串和单字符
        text = re.sub(r'\b\w{1}\b', ' ', text)
        text = re.sub(r'\b\d{1,2}\b', ' ', text)

        return text.strip()

    def extract_char_ngrams(self, text: str) -> List[str]:
        """提取字符级n-gram特征"""
        char_ngrams = []

        # 去除空格的纯字符序列用于字符级n-gram
        clean_text = re.sub(r'\s+', '', text)

        for n in range(self.char_ngram_range[0], self.char_ngram_range[1] + 1):
            for i in range(len(clean_text) - n + 1):
                ngram = clean_text[i:i + n]
                # 过滤纯数字和纯标点的n-gram
                if not re.match(r'^[\d\W]+$', ngram):
                    char_ngrams.append(f"char_{n}_{ngram}")

        return char_ngrams

    def extract_word_ngrams(self, text: str) -> List[str]:
        """提取词级n-gram特征"""
        word_ngrams = []

        # 中文分词
        chinese_words = [w for w in jieba.cut(text) if len(w.strip()) > 1 and w not in self.stopwords]

        # 英文分词
        english_words = [w for w in re.findall(r'\b[a-zA-Z]{2,}\b', text) if w.lower() not in self.stopwords]

        # 合并词汇
        all_words = chinese_words + english_words

        # 生成词级n-gram
        for n in range(self.word_ngram_range[0], min(self.word_ngram_range[1] + 1, len(all_words) + 1)):
            for i in range(len(all_words) - n + 1):
                ngram = '_'.join(all_words[i:i + n])
                word_ngrams.append(f"word_{n}_{ngram}")

        return word_ngrams

    def extract_semantic_features(self, text: str) -> List[str]:
        """提取语义特征"""
        features = []

        # 1. 文本长度特征（分桶）
        text_len = len(text)
        if text_len < 200:
            features.append("length_short")
        elif text_len < 1000:
            features.append("length_medium")
        else:
            features.append("length_long")

        # 2. 数字密度特征
        digit_ratio = len(re.findall(r'\d', text)) / max(len(text), 1)
        if digit_ratio > 0.1:
            features.append("digit_heavy")
        elif digit_ratio > 0.05:
            features.append("digit_medium")
        else:
            features.append("digit_light")

        # 3. 标点密度特征
        punct_ratio = len(re.findall(r'[^\w\s\u4e00-\u9fff]', text)) / max(len(text), 1)
        if punct_ratio > 0.1:
            features.append("punct_heavy")

        # 4. 中英文比例特征
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = chinese_chars + english_chars

        if total_chars > 0:
            chinese_ratio = chinese_chars / total_chars
            if chinese_ratio > 0.8:
                features.append("lang_chinese")
            elif chinese_ratio < 0.2:
                features.append("lang_english")
            else:
                features.append("lang_mixed")

        return features

    def extract_all_features(self, text: str) -> List[str]:
        """提取所有特征"""
        normalized_text = self.normalize_text(text)

        if len(normalized_text) < self.min_text_length:
            return []

        features = []

        # 字符级特征
        char_features = self.extract_char_ngrams(normalized_text)
        features.extend(char_features)

        # 词级特征
        word_features = self.extract_word_ngrams(normalized_text)
        features.extend(word_features)

        # 语义特征
        semantic_features = self.extract_semantic_features(normalized_text)
        features.extend(semantic_features)

        return features

    def compute_tfidf_weights(self, all_features: List[List[str]]) -> Dict[str, float]:
        """计算TF-IDF权重"""
        if not self.use_tfidf_weight or len(all_features) < 2:
            return {}

        # 统计文档频率
        doc_freq = defaultdict(int)
        total_docs = len(all_features)

        for features in all_features:
            unique_features = set(features)
            for feature in unique_features:
                doc_freq[feature] += 1

        # 计算IDF权重
        idf_weights = {}
        for feature, df in doc_freq.items():
            idf = np.log(total_docs / (df + 1))
            idf_weights[feature] = idf

        return idf_weights

    def compute_simhash(self, text: str, idf_weights: Dict[str, float] = None) -> int:
        """计算文本的SimHash指纹"""
        features = self.extract_all_features(text)

        if not features:
            return 0

        # 如果有TF-IDF权重，应用权重
        if idf_weights and self.use_tfidf_weight:
            weighted_features = []
            feature_counts = Counter(features)

            for feature, count in feature_counts.items():
                weight = idf_weights.get(feature, 1.0)
                # 根据TF-IDF权重重复添加特征
                repeat_count = max(1, int(count * weight * 2))
                weighted_features.extend([feature] * min(repeat_count, 10))  # 限制最大重复次数

            features = weighted_features

        return Simhash(features).value

    def batch_deduplicate(self, url_content_pairs: List[Tuple[str, str]]) -> dict:
        """批量去重"""
        # 第一遍：提取所有特征，计算TF-IDF权重
        all_features = []
        valid_pairs = []

        print('extracting ngram features')
        for url, content in url_content_pairs.items():
            features = self.extract_all_features(content)
            if features:  # 过滤掉太短的文本
                all_features.append(features)
                valid_pairs.append((url, content))
                self.text_cache[url] = self.normalize_text(content)

        # pdb.set_trace()
        # 计算TF-IDF权重
        print('extracting tfidf features')
        idf_weights = self.compute_tfidf_weights(all_features)

        # 第二遍：计算SimHash指纹并去重
        print('extracting simhash features')
        fingerprint_to_urls = defaultdict(list)
        url_to_fingerprint = {}

        for url, content in valid_pairs:
            fingerprint = self.compute_simhash(content, idf_weights)
            self.fingerprints[url] = fingerprint
            url_to_fingerprint[url] = fingerprint

        # pdb.set_trace()
        # 使用汉明距离进行聚类
        print('clustering')
        processed_urls = set()
        duplicate_groups = []
        unique_urls = []

        for url, fingerprint in url_to_fingerprint.items():
            if url in processed_urls:
                continue

            # 找到所有相似的URL
            similar_urls = [url]
            processed_urls.add(url)

            for other_url, other_fingerprint in url_to_fingerprint.items():
                if other_url != url and other_url not in processed_urls:
                    distance = bin(fingerprint ^ other_fingerprint).count('1')
                    if distance <= self.similarity_threshold:
                        similar_urls.append(other_url)
                        processed_urls.add(other_url)

            if len(similar_urls) == 1:
                unique_urls.append(url)
            else:
                duplicate_groups.append(similar_urls)

        # 统计信息
        stats = {
            'total_input': len(url_content_pairs),
            'valid_input': len(valid_pairs),
            'unique_count': len(unique_urls),
            'duplicate_groups': len(duplicate_groups),
            'duplicate_total': sum(len(group) for group in duplicate_groups),
            'filtered_short': len(url_content_pairs) - len(valid_pairs)
        }

        return {
            'unique_urls': unique_urls,
            'duplicate_groups': duplicate_groups,
            'stats': stats
        }

    def find_similar_content(self, query_content: str, max_distance: int = None) -> List[Tuple[str, int]]:
        """查找与查询内容相似的已存储内容"""
        if max_distance is None:
            max_distance = self.similarity_threshold

        # 计算查询内容的指纹
        query_features = self.extract_all_features(query_content)
        if not query_features:
            return []

        # 这里简化处理，不重新计算TF-IDF权重
        query_hash = Simhash(query_features).value

        similar_content = []
        for url, fingerprint in self.fingerprints.items():
            distance = bin(query_hash ^ fingerprint).count('1')
            if distance <= max_distance:
                similar_content.append((url, distance))

        return sorted(similar_content, key=lambda x: x[1])
