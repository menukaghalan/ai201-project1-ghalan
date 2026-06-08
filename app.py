import sys
from pathlib import Path

import gradio as gr

# Allow importing from src/ when running python app.py from project root.
sys.path.append(str(Path(__file__).parent / "src"))
from query import ask  # noqa: E402


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", "", ""

    result = ask(question)
    source_text = "\n".join(f"- {source}" for source in result["sources"])
    retrieved_text = "\n\n".join(
        f"Source: {chunk['source']} | Chunk: {chunk['chunk_index']} | Distance: {chunk['distance']}\n{chunk['text']}"
        for chunk in result["retrieved_chunks"]
    )
    return result["answer"], source_text, retrieved_text


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown("# The Unofficial Guide")
    gr.Markdown("Ask a question about WMU student-life discussion documents. Answers should cite source files.")

    question = gr.Textbox(label="Your question", placeholder="Example: What do students say about parking at WMU?")
    ask_button = gr.Button("Ask")

    answer = gr.Textbox(label="Grounded answer", lines=8)
    sources = gr.Textbox(label="Retrieved source files", lines=4)
    retrieved_chunks = gr.Textbox(label="Retrieved chunks for debugging/evaluation", lines=12)

    ask_button.click(handle_query, inputs=question, outputs=[answer, sources, retrieved_chunks])
    question.submit(handle_query, inputs=question, outputs=[answer, sources, retrieved_chunks])


if __name__ == "__main__":
    demo.launch()
