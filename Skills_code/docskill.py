# import json
# from pathlib import Path
# from agent_framework import Skill

# document_skill = Skill(
#     name="document-skill",
#     description="save text as a document",
#     content="Use the save_text_as_doc script to save text content to a document file.",
# )

# @document_skill.script(name="save_text_as_doc", description="Save text content to a document file")
# def save_text_as_doc(text: str, filename: str) -> str:
#     """Save text to a .doc file in saved_docs/"""

#     if not filename.endswith(".doc"):
#         filename += ".doc"

#     save_dir = Path("saved_docs")
#     save_dir.mkdir(exist_ok=True)

#     file_path = save_dir / filename
#     file_path.write_text(text, encoding="utf-8")

#     return json.dumps({
#         "filepath": str(file_path.resolve()),
#         "saved": True,
#         "characters": len(text)
#     })

import json
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


from agent_framework import Skill
document_skill = Skill(
    name="document-skill",
    description="save text as a pdf",
    content="Use the save_text_as_pdf script to save text content to a pdf file.",
)


@document_skill.script(name="save_text_as_pdf", description="Save text content to a PDF file")
def save_text_as_pdf(text: str, filename: str) -> str:
    """Save text to a PDF file in saved_docs/"""

    if not filename.endswith(".pdf"):
        filename += ".pdf"

    save_dir = Path("saved_docs")
    save_dir.mkdir(exist_ok=True)

    file_path = save_dir / filename

    doc = SimpleDocTemplate(str(file_path))
    styles = getSampleStyleSheet()
    story = [Paragraph(text.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)
    print(str(file_path.resolve()))
    return json.dumps({
        "filepath": str(file_path.resolve().as_uri()),
        "download_url": "http://localhost:8000/saved_docs/" + filename ,
        "saved": True,
        "characters": len(text)
    })