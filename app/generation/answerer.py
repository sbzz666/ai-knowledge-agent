from __future__ import annotations

from openai import OpenAI

from app.models import Answer, Citation, SearchHit


REFUSAL = "当前知识库中没有找到足够证据回答这个问题。请补充相关资料或换一种问法。"


def answer_question(question: str, hits: list[SearchHit], *, api_key: str = "", base_url: str = "", model: str = "") -> Answer:
    reliable = [hit for hit in hits if hit.score >= 0.08]
    citations = [
        Citation(
            source=hit.chunk.filename,
            page=hit.chunk.page,
            chunk_id=hit.chunk.id,
            quote=hit.chunk.content[:280],
            score=round(hit.score, 4),
        )
        for hit in reliable
    ]
    if not reliable:
        return Answer(REFUSAL, [], False)

    if not api_key:
        lead = reliable[0].chunk.content
        return Answer(
            f"根据知识库检索结果，最相关的资料内容如下：\n\n{lead}\n\n（当前未配置大模型，以上为离线检索结果。）",
            citations,
            True,
        )

    context = "\n\n".join(
        f"[资料{i}] 文件={hit.chunk.filename} 页码={hit.chunk.page or '无'}\n{hit.chunk.content}"
        for i, hit in enumerate(reliable, 1)
    )
    client = OpenAI(api_key=api_key, base_url=base_url or None)
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是严谨的企业知识库助手。只能依据提供的资料回答。"
                    "每个事实后使用[资料1]形式标注来源；证据不足必须明确说不知道，不得补写常识。"
                ),
            },
            {"role": "user", "content": f"问题：{question}\n\n可用资料：\n{context}"},
        ],
    )
    text = response.choices[0].message.content or REFUSAL
    return Answer(text, citations, text != REFUSAL)

