"""Milestone 5 - Gradio query interface for The Unofficial Guide.

Run:  .venv/Scripts/python app.py   then open the printed local URL.
Type a question about GT CS courses/professors; the answer is grounded in the
retrieved student reviews, with sources and the raw retrieved chunks shown.
"""
import gradio as gr

from generator import generate_answer

EXAMPLES = [
    "Is CS 1331 a hard class?",
    "Should I take CS 2050 with Ellen Zegura?",
    "Are Mark Riedl's exams in CS 3600 curved?",
    "Which CS professor has the best lectures?",
    "What is the average GPA for CS 1331?",
]


def answer_fn(query):
    if not query or not query.strip():
        return "Type a question about Georgia Tech CS courses or professors.", ""

    res = generate_answer(query)

    if res["sources"]:
        sources_md = "**Sources**\n" + "\n".join(
            f"- [{s['file']}]({s['url']})" for s in res["sources"]
        )
    else:
        sources_md = "_No sources cited (the answer wasn't found in the reviews)._"
    answer_md = res["answer"] + "\n\n---\n" + sources_md

    chunks_md = ""
    for i, h in enumerate(res["hits"], 1):
        chunks_md += (
            f"**[{i}]** distance `{h['distance']:.3f}` · {h['source_file']}\n\n"
            f"> {h['text'].replace(chr(10), ' ')}\n\n"
        )
    return answer_md, chunks_md


with gr.Blocks(title="The Unofficial Guide - GT CS") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about **Georgia Tech CS courses & professors**. Answers come only "
        "from collected student reviews (Rate My Professors, r/gatech, Course "
        "Critique) - not the model's general knowledge."
    )
    query = gr.Textbox(
        label="Your question",
        placeholder="e.g. Should I take CS 2050 with Zegura?",
        autofocus=True,
    )
    ask = gr.Button("Ask", variant="primary")
    answer = gr.Markdown(label="Answer")
    with gr.Accordion("Show the chunks that were retrieved", open=False):
        chunks = gr.Markdown()

    gr.Examples(examples=EXAMPLES, inputs=query)
    ask.click(answer_fn, inputs=query, outputs=[answer, chunks])
    query.submit(answer_fn, inputs=query, outputs=[answer, chunks])


if __name__ == "__main__":
    demo.launch()
