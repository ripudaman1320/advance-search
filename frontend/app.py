import gradio as gr
import httpx

from styles import CSS, HEADER_HTML, JS

API_BASE = "http://localhost:8000/api"


class EmailRAGInterface:
    def __init__(self):
        self.client = httpx.Client(timeout=60.0)

    def check_health(self) -> dict:
        """Check API health"""
        try:
            response = self.client.get(f"{API_BASE}/health")
            return response.json()
        except Exception:
            return {"status": "disconnected", "message": "Cannot reach API"}

    def ingest_email(self, docx_file) -> str:
        """Ingest email from uploaded file"""
        try:
            response = self.client.post(
                f"{API_BASE}/ingest",
                params={"docx_path": docx_file.name}
            )
            result = response.json()
            return f"✓ Ingested: {result['subject']}\n✓ Chunks created: {result['chunks_created']}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def chat(self, message: str, top_k: int) -> tuple[str, str]:
        """Chat with RAG system"""
        try:
            response = self.client.post(
                f"{API_BASE}/chat",
                json={
                    "text": message,
                    "top_k": top_k,
                    "return_sources": True,
                },
            )

            if response.status_code != 200:
                return "Error: API request failed", ""

            data = response.json()
            answer = data["answer"]

            sources_text = "**Sources:**\n"
            if data["sources"]:
                for i, source in enumerate(data["sources"], 1):
                    sources_text += f"\n{i}. **From**: {source['sender']} | **Date**: {source['timestamp']}\n"
                    sources_text += f"   *Score*: {source['score']:.3f}\n"
            else:
                sources_text += "No sources retrieved"

            sources_text += f"\n**Confidence**: {data['confidence']:.2%}\n"
            sources_text += f"**Response Time**: {data['execution_time_ms']}ms"

            return answer, sources_text

        except Exception as e:
            return f"Error: {str(e)}", ""

    def list_emails(self) -> str:
        """List ingested emails"""
        try:
            response = self.client.get(f"{API_BASE}/emails")
            data = response.json()

            if not data["emails"]:
                return "No emails ingested yet"

            output = f"**Total Emails**: {data['count']}\n\n"
            for email in data["emails"]:
                output += f"📧 **{email['subject']}**\n"
                output += f"   From: {email['sender_email']}\n"
                output += f"   Date: {email['created_at']}\n"
                output += f"   Words: {email['word_count']}\n\n"

            return output
        except Exception as e:
            return f"Error: {str(e)}"


interface = EmailRAGInterface()

with gr.Blocks(title="Email RAG Chatbot", theme=gr.themes.Base(), css=CSS) as demo:
    gr.HTML(HEADER_HTML)

    with gr.Row():
        message_input = gr.Textbox(
            label="Your Question",
            placeholder="Ask anything about your emails...",
            lines=3,
            elem_id="dr-query",
        )
        chat_button = gr.Button("Investigate", variant="primary", elem_id="dr-run")

    with gr.Row():
        top_k_slider = gr.Slider(
            minimum=1,
            maximum=10,
            value=5,
            step=1,
            label="Number of Sources",
        )

    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            with gr.Row():
                with gr.Column(scale=3):
                    answer_output = gr.Markdown(label="Answer", elem_id="chat-output")
                with gr.Column():
                    sources_output = gr.Markdown(label="Retrieved Sources", elem_id="sources-output")

            chat_button.click(
                fn=interface.chat,
                inputs=[message_input, top_k_slider],
                outputs=[answer_output, sources_output],
            )
            message_input.submit(
                fn=interface.chat,
                inputs=[message_input, top_k_slider],
                outputs=[answer_output, sources_output],
            )

        with gr.TabItem("📤 Ingest Emails"):
            with gr.Column(elem_id="ingest-panel"):
                gr.Markdown("### Upload Email DOCX Files")

                with gr.Row():
                    docx_upload = gr.File(
                        label="Select DOCX File",
                        file_types=[".docx"],
                    )
                    ingest_button = gr.Button("📥 Ingest", variant="primary")

                ingest_output = gr.Textbox(
                    label="Result",
                    interactive=False,
                    lines=5,
                )

                ingest_button.click(
                    fn=interface.ingest_email,
                    inputs=docx_upload,
                    outputs=ingest_output,
                )

        with gr.TabItem("📬 Emails"):
            with gr.Column(elem_id="emails-panel"):
                gr.Markdown("### Ingested Emails")
                emails_button = gr.Button("🔄 Refresh", variant="secondary")
                emails_output = gr.Markdown(label="Email List")

                emails_button.click(
                    fn=interface.list_emails,
                    outputs=emails_output,
                )

        with gr.TabItem("ℹ️ About"):
            with gr.Column(elem_id="about-panel"):
                gr.Markdown(
                    """
                    ## Email RAG Chatbot

                    **What is this?**
                    This is an AI-powered chatbot that understands your personal email history.
                    It uses advanced retrieval techniques to find relevant emails and generates contextual responses.

                    **How does it work?**
                    1. **Ingestion**: Upload your email DOCX files
                    2. **Chunking**: Emails are split into semantic chunks
                    3. **Indexing**: Chunks are indexed using BM25 + vector embeddings
                    4. **Retrieval**: Your question retrieves the most relevant chunks
                    5. **Generation**: An LLM generates an answer using those chunks
                    6. **Citations**: Sources are tracked and displayed

                    **Technologies**:
                    - FastAPI backend
                    - ChromaDB for vector storage
                    - Ollama for local LLM
                    - Gradio for this UI
                    - Hybrid BM25 + Dense retrieval

                    **Privacy**: All data stays on your machine!
                    """
                )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        js=JS,
    )
