from .utils import TextDeduplicator

def calculate_fingerprint(text: str) -> int:
    deduplicator = TextDeduplicator(
        similarity_threshold=10,  # 较严格的阈值
        char_ngram_range=(3, 6),  # 字符3-6gram，提高精度
        word_ngram_range=(1, 3),  # 词1-3gram
        min_text_length=0,  # 过滤过短文本
        use_tfidf_weight=False  # 使用TF-IDF权重
    )

    return deduplicator.compute_simhash(text)

def compare_fingerprint(fp1: int, fp2: int) -> int:
    return bin(fp1 ^ fp2).count('1')