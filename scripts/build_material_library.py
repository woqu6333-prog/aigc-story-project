#!/usr/bin/env python
"""构建作业5素材库并运行三组检索评估。"""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from material_library import MaterialLibrary, build_library  # noqa: E402


EVALUATION_CASES = [
    {"query": "女孩乘火箭去太空冒险", "expected": ["太空", "火箭", "星球"]},
    {"query": "森林里的小鸟友谊故事", "expected": ["森林", "小鸟", "友谊"]},
    {"query": "海底鲸鱼保护珊瑚", "expected": ["海底", "鲸鱼", "珊瑚", "环保"]},
]


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs" / "library" / "homework5"
    index_path = build_library(output_dir)
    library = MaterialLibrary(index_path)
    evaluations = []
    for case in EVALUATION_CASES:
        result = library.recommend(case["query"])
        top = result["materials"]["images"][:5]
        hit_count = sum(
            bool(set(item["tags"]) & set(case["expected"])) for item in top
        )
        evaluations.append(
            {
                **case,
                "top_image_ids": [item["id"] for item in top],
                "precision_at_5": round(hit_count / 5, 2),
                "recommendation": result,
            }
        )
    report = {
        "metric": "相关标签命中率 Precision@5",
        "backend": library.data["image_search_backend"],
        "cases": evaluations,
        "average_precision_at_5": round(sum(item["precision_at_5"] for item in evaluations) / len(evaluations), 2),
    }
    (output_dir / "evaluation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"素材库已生成：{index_path}")
    print(f"素材数量：{library.data['counts']}")
    print(f"3组查询平均 Precision@5：{report['average_precision_at_5']:.2f}")


if __name__ == "__main__":
    main()
