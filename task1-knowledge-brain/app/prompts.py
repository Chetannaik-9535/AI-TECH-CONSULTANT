"""
AI Tech Consultant - Knowledge Brain
Prompt templates for Claude-powered RAG question answering and escalation.
"""
from __future__ import annotations


# ─── System Prompt ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert technical support specialist for Brilliant Directories, \
a website builder platform for creating membership and directory websites.

Your role:
- Answer questions accurately using ONLY the retrieved knowledge base articles provided below.
- Cite specific articles by title and URL when referencing information.
- If an article contains step-by-step instructions, reproduce them clearly.
- If relevant images or screenshots exist, reference them to help the user.
- Be friendly, professional, and concise.

Rules:
1. ONLY use information from the provided context. Never invent features or steps.
2. If the context doesn't contain enough information to fully answer, say so clearly \
   and indicate what's missing.
3. If multiple articles are relevant, synthesize them into a coherent answer.
4. When quoting steps, preserve their order and numbering.
5. Always include source URLs so the user can read the full article.
6. Use markdown formatting for readability (headings, lists, bold for emphasis).
"""


# ─── QA Prompt ───────────────────────────────────────────────────────

QA_PROMPT_TEMPLATE = """Answer the following question using the retrieved knowledge base articles.

## Question
{question}

## Retrieved Articles
{context}

## Instructions
- Provide a clear, accurate answer based solely on the articles above.
- Cite sources with [Article Title](URL) format.
- If the articles don't contain sufficient information, clearly state: \
  "I don't have enough information in the knowledge base to fully answer this."
- Include any relevant step-by-step instructions exactly as documented.
- Reference relevant images/screenshots if mentioned in the articles.
"""


# ─── Confidence Assessment Prompt ────────────────────────────────────

CONFIDENCE_PROMPT = """Evaluate how well the retrieved context answers the user's question.

Question: {question}

Retrieved context (summarized):
{context_summary}

Rate the answer on this scale:
- ANSWERED: The context fully and directly answers the question with clear evidence.
- PARTIAL: The context contains related information but doesn't fully address the question.
- INSUFFICIENT: The context doesn't contain enough relevant information to answer.

Respond with ONLY one of: ANSWERED, PARTIAL, INSUFFICIENT
"""


# ─── Escalation Summary Prompt ───────────────────────────────────────

ESCALATION_SUMMARY_PROMPT = """A user asked a question that the knowledge base couldn't fully answer.

Question: {question}

Retrieved articles (if any):
{context}

Please provide:
1. A brief summary of what information WAS available.
2. What specific information is MISSING to answer the question.
3. Suggested areas where expert knowledge is needed.

Keep the summary concise (under 200 words).
"""


# ─── Chunk Context Enrichment Prompt ─────────────────────────────────

CHUNK_ENRICHMENT_PROMPT = """Given this article chunk, generate a brief contextual summary \
that would help with retrieval. Include the main topic, key concepts, and any \
product features mentioned.

Article Title: {title}
Section: {section}
Content:
{content}

Respond with a 1-2 sentence summary focused on what questions this chunk could answer.
"""


# ─── Image Description Prompt ────────────────────────────────────────

IMAGE_DESCRIPTION_PROMPT = """Describe this screenshot/image from a help-center article in a way \
that would be useful for someone following step-by-step instructions.

Article context: {context}

Focus on:
- What UI elements are visible (buttons, menus, form fields)
- What action the image is demonstrating
- Any highlighted or annotated areas
- Text visible in the image

Keep the description concise but informative (under 100 words).
"""


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string for the QA prompt."""
    if not chunks:
        return "No relevant articles found."

    sections = []
    for i, chunk in enumerate(chunks, 1):
        title = chunk.get("title", "Untitled")
        url = chunk.get("url", "")
        section = chunk.get("section", "")
        content = chunk.get("content", "")
        score = chunk.get("score", 0.0)

        header = f"### Source {i}: {title}"
        if section:
            header += f" — {section}"
        header += f"\n**URL:** {url}"
        header += f"\n**Relevance:** {score:.2f}"

        # Include image descriptions if available
        image_descs = chunk.get("image_descriptions", [])
        image_note = ""
        if image_descs:
            image_note = "\n**Related images:** " + "; ".join(image_descs)

        sections.append(f"{header}{image_note}\n\n{content}")

    return "\n\n---\n\n".join(sections)


def build_qa_prompt(question: str, chunks: list[dict]) -> str:
    """Build the complete QA prompt with context."""
    context = format_context(chunks)
    return QA_PROMPT_TEMPLATE.format(question=question, context=context)


def build_confidence_prompt(question: str, chunks: list[dict]) -> str:
    """Build prompt to assess answer confidence."""
    summaries = []
    for c in chunks[:3]:
        summaries.append(f"- {c.get('title', 'Untitled')}: {c.get('content', '')[:150]}...")
    context_summary = "\n".join(summaries) if summaries else "No context available."
    return CONFIDENCE_PROMPT.format(question=question, context_summary=context_summary)


def build_escalation_prompt(question: str, chunks: list[dict]) -> str:
    """Build prompt for escalation summary."""
    context = format_context(chunks) if chunks else "No relevant articles found."
    return ESCALATION_SUMMARY_PROMPT.format(question=question, context=context)
