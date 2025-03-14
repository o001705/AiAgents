from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector
import typer
from typing import Optional, List
from phi.assistant import Assistant
from phi.storage.assistant.postgres import PgAssistantStorage

from dotenv import load_dotenv
load_dotenv("agent.env")


db_url = "postgresql://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/thai_recipes.pdf"],
    vector_db=PgVector(
        table_name="recipes",
        db_url=db_url
    )
)

# Load the knowledge base: Comment out after first run
knowledge_base.load(
    storage=PgAssistantStorage(
        table_name="pdf_assistant",
        db_url=db_url
    )
)

def pdf_assistant(
    new: bool = False,
    user: str = "user"
) -> None:
    assistant = Assistant(
        run_id="pdf_assistant",
        user_id=user,
        knowledge_base=knowledge_base,
        storage=PgAssistantStorage(
            table_name="pdf_assistant",
            db_url=db_url
        ),
        show_tool_calls=True,
        search_knowledge=True,
        read_chat_history=True
    )

    if new or not assistant.run_id:
        assistant.run_id = "pdf_assistant"
    
    assistant.start()
    assistant.cli(markdown=True)
    
if __name__ == "__main__":
    import typer
    typer.run(pdf_assistant)