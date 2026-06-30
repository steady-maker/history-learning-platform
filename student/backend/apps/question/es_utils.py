# question/es_utils.py
from elasticsearch import Elasticsearch
from django.conf import settings

from question.models import Question

# 初始化 ES 客户端（和 views.py 保持一致）
es = Elasticsearch(settings.ELASTICSEARCH_URL)


def init_question_index():
    """初始化 ES 索引（只需要执行一次）"""
    index_name = "questions"  # 索引名，和 views.py 里的 index 一致

    # 如果索引已存在，先删除（避免重复）
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print("旧索引已删除")

    # 定义映射：只对 content 字段用 IK 分词
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},  # 题目 ID（和数据库一致）
                "content": {"type": "text", "analyzer": "ik_max_word"}  # IK 细粒度分词
            }
        }
    }

    # 创建索引
    es.indices.create(index=index_name, body=mapping)
    print("✅ ES 索引创建成功！")


def sync_questions_to_es():
    """同步数据库所有题目到 ES"""
    index_name = "questions"
    # 清空旧数据（避免重复同步）
    es.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
    print("📦 正在同步数据库题目到 ES...")

    # 遍历数据库所有题目，逐条同步
    total = 0
    for question in Question.objects.all():
        # 只同步 id 和 content 字段（搜索需要的）
        doc = {
            "id": question.id,
            "content": question.content
        }
        # 写入 ES
        es.index(index=index_name, id=question.id, document=doc)
        total += 1

    print(f"✅ 同步完成！共同步 {total} 道题目到 ES")


# 一键执行：初始化 + 同步（方便测试）
if __name__ == "__main__":
    # 先配置 Django 环境（如果直接运行这个文件需要加）
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "history_web_backend.settings")  # 替换成你的项目 settings 路径
    django.setup()

    init_question_index()
    sync_questions_to_es()