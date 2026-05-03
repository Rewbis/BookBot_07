import streamlit as st
import markdown
from ebooklib import epub
from pathlib import Path
import re, uuid
import os
import tempfile

def show_phase5():
    st.header("Phase 5: EPUB Builder")
    st.markdown("Compile your finalized manuscript, cover art, and illustrations into a ready-to-publish EPUB file.")
    
    # --- Inputs ---
    md_file = st.file_uploader("Book manuscript (.md)", type=["md"], help="Upload the final compiled markdown file of your book.")
    cover_file = st.file_uploader("Cover image (PNG/JPG)", type=["png", "jpg", "jpeg"], help="Upload your book cover.")
    chapter_imgs = st.file_uploader("Chapter illustrations (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, help="Upload any images referenced in your markdown (e.g. ![alt](my_image.png)).")

    col1, col2, col3 = st.columns(3)
    title = col1.text_input("Book title", "My Book")
    author = col2.text_input("Author name", "Author Name")
    language = col3.text_input("Language code", "en")

    if st.button("Build EPUB", type="primary") and md_file:
        with st.spinner("Building EPUB..."):
            md_text = md_file.read().decode("utf-8")

            book = epub.EpubBook()
            book.set_identifier(str(uuid.uuid4()))
            book.set_title(title)
            book.set_language(language)
            book.add_author(author)

            # --- Cover ---
            if cover_file:
                cover_bytes = cover_file.read()
                ext = Path(cover_file.name).suffix.lstrip(".")
                mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                cover_img = epub.EpubItem(
                    uid="cover-image",
                    file_name=f"images/cover.{ext}",
                    media_type=mime,
                    content=cover_bytes,
                )
                book.add_item(cover_img)
                book.set_cover(f"images/cover.{ext}", cover_bytes)

            # --- Chapter images ---
            img_map = {}  # filename → epub item
            if chapter_imgs:
                for img_file in chapter_imgs:
                    img_bytes = img_file.read()
                    ext = Path(img_file.name).suffix.lstrip(".")
                    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                    fname = f"images/{img_file.name}"
                    item = epub.EpubItem(
                        uid=str(uuid.uuid4()),
                        file_name=fname,
                        media_type=mime,
                        content=img_bytes,
                    )
                    book.add_item(item)
                    img_map[img_file.name] = fname  # so you can reference by filename in MD

            # --- Split MD into chapters on H1 headings ---
            chapters_md = re.split(r'(?=^# )', md_text, flags=re.MULTILINE)
            chapters_md = [c.strip() for c in chapters_md if c.strip()]

            epub_chapters = []
            spine = ["nav"]

            for i, chap_md in enumerate(chapters_md):
                # Extract title from first H1
                lines = chap_md.splitlines()
                chap_title = lines[0].lstrip("# ").strip() if lines else f"Chapter {i+1}"
                chap_html = markdown.markdown(chap_md, extensions=["extra"])

                # Rewrite image references: ![alt](filename.png) → images/filename.png
                for orig_name, epub_path in img_map.items():
                    # Handle standard markdown image syntax that compiled to HTML
                    chap_html = chap_html.replace(f'src="{orig_name}"', f'src="{epub_path}"')

                chap = epub.EpubHtml(
                    title=chap_title,
                    file_name=f"chap_{i+1:02d}.xhtml",
                    lang=language,
                )
                chap.content = f"<html><body>{chap_html}</body></html>"
                book.add_item(chap)
                epub_chapters.append(chap)
                spine.append(chap)

            # --- Navigation ---
            book.toc = [(epub.Section(c.title), [c]) for c in epub_chapters]
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = spine

            # --- Write ---
            temp_dir = tempfile.gettempdir()
            out_path = os.path.join(temp_dir, f"{title.replace(' ', '_')}.epub")
            epub.write_epub(out_path, book)

            with open(out_path, "rb") as f:
                st.download_button("Download EPUB", f, file_name=Path(out_path).name, mime="application/epub+zip")

            st.success("Done! Upload this EPUB to KDP. Submit the cover image separately.")
