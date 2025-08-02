"""Core PDF extraction functionality."""

import pymupdf4llm
import pymupdf
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Result of PDF extraction."""
    content: str
    token_estimate: int
    page_count: int
    has_images: bool
    has_tables: bool
    output_path: Optional[Path] = None
    image_paths: List[Path] = None


class PDFExtractor:
    """Extract content from PDFs for LLM consumption."""
    
    def __init__(self, 
                 output_dir: Path = None,
                 image_format: str = "png",
                 dpi: int = 150,
                 page_chunks: bool = True):
        """
        Initialize PDF extractor.
        
        Args:
            output_dir: Base directory for output files
            image_format: Format for extracted images
            dpi: DPI for image extraction
            page_chunks: Whether to preserve page boundaries
        """
        self.output_dir = output_dir or Path("extracted")
        self.image_format = image_format
        self.dpi = dpi
        self.page_chunks = page_chunks
        
    def analyze_structure(self, pdf_path: Path) -> Dict:
        """Analyze PDF structure and content types."""
        doc = pymupdf.open(str(pdf_path))
        
        analysis = {
            "total_pages": len(doc),
            "pages": [],
            "has_images": False,
            "has_tables": False,
            "total_images": 0,
            "total_tables": 0
        }
        
        for page_num, page in enumerate(doc):
            page_info = {
                "page_number": page_num + 1,
                "text_blocks": len(page.get_text("blocks")),
                "images": len(page.get_images()),
                "tables": 0,
                "links": len(page.get_links())
            }
            
            # Check for tables
            table_finder = page.find_tables()
            if table_finder and hasattr(table_finder, 'tables'):
                page_info["tables"] = len(table_finder.tables)
            
            analysis["pages"].append(page_info)
            analysis["total_images"] += page_info["images"]
            analysis["total_tables"] += page_info["tables"]
            
            if page_info["images"] > 0:
                analysis["has_images"] = True
            if page_info["tables"] > 0:
                analysis["has_tables"] = True
        
        doc.close()
        return analysis
    
    def extract(self, 
                pdf_path: Path,
                output_format: str = "markdown",
                analyze_first: bool = True) -> ExtractionResult:
        """
        Extract PDF content.
        
        Args:
            pdf_path: Path to PDF file
            output_format: "markdown" or "text"
            analyze_first: Whether to analyze structure first
            
        Returns:
            ExtractionResult with extracted content and metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Analyze structure if requested
        analysis = None
        if analyze_first:
            analysis = self.analyze_structure(pdf_path)
        
        # Create output directory structure
        pdf_output_dir = self.output_dir / pdf_path.stem
        pdf_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up image directory
        image_dir = pdf_output_dir / "images"
        if analysis and analysis["has_images"]:
            image_dir.mkdir(exist_ok=True)
        
        # Extract content
        if output_format == "markdown":
            content = self._extract_markdown(pdf_path, image_dir)
        else:
            content = self._extract_text(pdf_path)
        
        # Calculate token estimate
        token_estimate = int(len(content.split()) * 1.3)
        
        # Collect image paths if they exist
        image_paths = list(image_dir.glob(f"*.{self.image_format}")) if image_dir.exists() else []
        
        return ExtractionResult(
            content=content,
            token_estimate=token_estimate,
            page_count=analysis["total_pages"] if analysis else 0,
            has_images=bool(image_paths),
            has_tables=analysis["has_tables"] if analysis else False,
            image_paths=image_paths
        )
    
    def _extract_markdown(self, pdf_path: Path, image_dir: Path) -> str:
        """Extract as markdown with images."""
        content = pymupdf4llm.to_markdown(
            str(pdf_path),
            page_chunks=self.page_chunks,
            write_images=True,
            image_path=str(image_dir),
            image_format=self.image_format,
            dpi=self.dpi
        )
        
        # Format with page separators if needed
        if isinstance(content, list):
            formatted_content = []
            for i, page_content in enumerate(content):
                formatted_content.append(f"\n\n<!-- Page {i+1} -->\n")
                formatted_content.append(page_content['text'] if isinstance(page_content, dict) else str(page_content))
            content = "".join(formatted_content)
            
        return content
    
    def _extract_text(self, pdf_path: Path) -> str:
        """Extract as plain text."""
        doc = pymupdf.open(str(pdf_path))
        content = []
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if self.page_chunks:
                content.append(f"--- Page {page_num + 1} ---\n{page_text}")
            else:
                content.append(page_text)
        
        doc.close()
        return "\n\n".join(content) if self.page_chunks else "\n".join(content)
    
    def save_extraction(self, result: ExtractionResult, pdf_path: Path, format_suffix: str = "") -> Path:
        """Save extraction result to file."""
        pdf_output_dir = self.output_dir / pdf_path.stem
        pdf_output_dir.mkdir(parents=True, exist_ok=True)
        
        output_filename = f"content{format_suffix}.md" if format_suffix else "content.md"
        output_path = pdf_output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.content)
        
        result.output_path = output_path
        return output_path
    
    def batch_extract(self, pdf_files: List[Path], **kwargs) -> List[Tuple[Path, ExtractionResult]]:
        """Extract multiple PDFs."""
        results = []
        for pdf_path in pdf_files:
            try:
                result = self.extract(pdf_path, **kwargs)
                results.append((pdf_path, result))
            except Exception as e:
                print(f"Error extracting {pdf_path}: {e}")
                results.append((pdf_path, None))
        return results