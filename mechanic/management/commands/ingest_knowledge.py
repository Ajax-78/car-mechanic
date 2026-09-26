
from pathlib import Path

from django.core.management.base import BaseCommand

from mechanic.models import KnowledgeDocument

from mechanic.services.embedding_service import (
    generate_document_embedding
)


class Command(BaseCommand):
    help = "Ingest mechanic knowledge into PostgreSQL vector database"

    def handle(self, *args, **options):

        # Project root directory
        base_dir = Path("knowledge")

        # Check whether knowledge directory exists
        if not base_dir.exists():

            self.stdout.write(
                self.style.ERROR(
                    "knowledge directory not found."
                )
            )

            self.stdout.write(
                "Create a 'knowledge' folder in the backend directory."
            )

            return

        # Find all .txt files
        files = list(
            base_dir.glob("*.txt")
        )

        if not files:

            self.stdout.write(
                self.style.WARNING(
                    "No .txt knowledge files found."
                )
            )

            return

        self.stdout.write(
            f"Found {len(files)} knowledge file(s)."
        )

        # Process each knowledge file
        for file_path in files:

            self.stdout.write(
                f"Processing: {file_path.name}"
            )

            # Read file
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not content:

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping empty file: {file_path.name}"
                    )
                )

                continue

            # Generate title from filename
            title = (
                file_path.stem
                .replace("_", " ")
                .replace("-", " ")
                .title()
            )

            # Category based on filename
            category = file_path.stem.lower()

            # Generate Gemini embedding
            embedding = generate_document_embedding(
                text=content,
                title=title
            )

            # Save or update document
            document, created = (
                KnowledgeDocument.objects.update_or_create(
                    title=title,
                    defaults={
                        "category": category,
                        "content": content,
                        "source": file_path.name,
                        "embedding": embedding,
                    }
                )
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {title}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated: {title}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Knowledge ingestion completed successfully."
            )
        )
