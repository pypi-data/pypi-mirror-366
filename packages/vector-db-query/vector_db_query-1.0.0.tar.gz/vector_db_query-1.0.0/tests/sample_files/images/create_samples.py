#!/usr/bin/env python3
"""Create sample images for OCR testing."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random


def create_text_document():
    """Create a document-like image with text."""
    width, height = 1200, 1600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Draw title
    title = "Vector Database Query System"
    draw.text((100, 100), title, fill='black', font=title_font)
    
    # Draw subtitle
    subtitle = "Technical Documentation"
    draw.text((100, 180), subtitle, fill='gray', font=body_font)
    
    # Draw body text
    body_text = """
Introduction

The Vector Database Query System is a powerful tool for semantic search
and document retrieval. It leverages state-of-the-art embedding models
to convert text into high-dimensional vectors, enabling similarity-based
searches across large document collections.

Key Features:
• Multi-format document support
• Semantic search capabilities
• Real-time indexing
• Scalable architecture
• RESTful API interface

Technical Specifications:
- Embedding Model: text-embedding-ada-002
- Vector Dimensions: 1536
- Database: Qdrant
- Supported Formats: PDF, DOCX, TXT, HTML, and more

Getting Started:
1. Install dependencies
2. Configure the database connection
3. Index your documents
4. Start querying!

For more information, visit our documentation at:
https://github.com/example/vector-db-query
"""
    
    y_offset = 300
    for line in body_text.strip().split('\n'):
        draw.text((100, y_offset), line, fill='black', font=body_font)
        y_offset += 35
    
    image.save('document.png')
    print("Created: document.png")


def create_invoice_image():
    """Create an invoice-like image."""
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except:
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # Header
    draw.text((50, 50), "INVOICE", fill='black', font=header_font)
    draw.text((600, 50), "#INV-2025-001", fill='black', font=normal_font)
    
    # Company info
    draw.text((50, 120), "Acme Corporation", fill='black', font=normal_font)
    draw.text((50, 145), "123 Business St", fill='black', font=normal_font)
    draw.text((50, 170), "Tech City, TC 12345", fill='black', font=normal_font)
    
    # Date
    draw.text((600, 120), "Date: 2025-01-30", fill='black', font=normal_font)
    
    # Draw line
    draw.line((50, 220, 750, 220), fill='black', width=2)
    
    # Table headers
    draw.text((50, 240), "Description", fill='black', font=normal_font)
    draw.text((400, 240), "Quantity", fill='black', font=normal_font)
    draw.text((550, 240), "Price", fill='black', font=normal_font)
    draw.text((650, 240), "Total", fill='black', font=normal_font)
    
    # Table items
    items = [
        ("Software License", "1", "$999.00", "$999.00"),
        ("Support Package", "1", "$199.00", "$199.00"),
        ("Training Hours", "8", "$150.00", "$1,200.00"),
        ("Implementation", "1", "$2,500.00", "$2,500.00")
    ]
    
    y = 280
    for item, qty, price, total in items:
        draw.text((50, y), item, fill='black', font=normal_font)
        draw.text((400, y), qty, fill='black', font=normal_font)
        draw.text((550, y), price, fill='black', font=normal_font)
        draw.text((650, y), total, fill='black', font=normal_font)
        y += 30
    
    # Total
    draw.line((50, y + 20, 750, y + 20), fill='black', width=1)
    draw.text((550, y + 40), "Total:", fill='black', font=header_font)
    draw.text((650, y + 40), "$4,898.00", fill='black', font=header_font)
    
    image.save('invoice.jpg')
    print("Created: invoice.jpg")


def create_handwritten_note():
    """Create a handwritten-style note image."""
    width, height = 600, 400
    # Create slightly off-white background
    image = Image.new('RGB', (width, height), color=(250, 250, 245))
    draw = ImageDraw.Draw(image)
    
    # Draw lines like notebook paper
    for y in range(50, height - 20, 30):
        draw.line((20, y, width - 20, y), fill=(200, 200, 250), width=1)
    
    # Simulate handwritten text (using regular font with slight variations)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Noteworthy.ttc", 20)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()
    
    notes = [
        "Meeting Notes - Jan 30",
        "",
        "- Discuss Q1 roadmap",
        "- Review vector DB performance",
        "- Plan scaling strategy",
        "",
        "Action items:",
        "• Benchmark query speeds",
        "• Test with 1M documents",
        "• Deploy to staging env",
        "",
        "Next meeting: Feb 6 @ 2pm"
    ]
    
    y = 60
    for line in notes:
        # Add slight random offset to simulate handwriting
        x_offset = 30 + random.randint(-2, 2)
        draw.text((x_offset, y), line, fill=(30, 30, 100), font=font)
        y += 28
    
    image.save('handwritten_note.png')
    print("Created: handwritten_note.png")


def create_screenshot():
    """Create a screenshot-like image."""
    width, height = 1024, 768
    image = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttc", 14)
    except:
        font = ImageFont.load_default()
    
    # Window title bar
    draw.rectangle((0, 0, width, 30), fill=(50, 50, 50))
    draw.text((10, 8), "Terminal - vector-db-query", fill='white', font=font)
    
    # Terminal content
    terminal_text = """$ python -m vector_db_query process /path/to/documents
[2025-01-30 10:15:32] INFO: Starting document processing...
[2025-01-30 10:15:33] INFO: Found 42 documents to process
[2025-01-30 10:15:33] INFO: Initializing vector database connection...
[2025-01-30 10:15:34] INFO: Connected to Qdrant at localhost:6333

Processing documents:
  document1.pdf     [################] 100% - Indexed successfully
  report.docx       [################] 100% - Indexed successfully
  data.xlsx         [################] 100% - Indexed successfully
  
[2025-01-30 10:16:45] INFO: Processing complete!
[2025-01-30 10:16:45] INFO: Total documents processed: 42
[2025-01-30 10:16:45] INFO: Total chunks created: 1,337
[2025-01-30 10:16:45] INFO: Average processing time: 1.54s per document

$ python -m vector_db_query search "machine learning applications"
[2025-01-30 10:17:02] INFO: Searching for: machine learning applications
[2025-01-30 10:17:03] INFO: Found 5 relevant documents:

1. [Score: 0.92] ml_whitepaper.pdf - "Machine Learning in Production"
2. [Score: 0.87] research_notes.docx - "Applications of ML in Industry"
3. [Score: 0.85] tech_report.pdf - "Deep Learning Applications"

$"""
    
    y = 40
    for line in terminal_text.strip().split('\n'):
        # Terminal green text for some lines
        if line.startswith('$'):
            color = (0, 255, 0)
        elif 'INFO' in line:
            color = (100, 150, 255)
        elif '[####' in line:
            color = (255, 200, 0)
        else:
            color = (200, 200, 200)
            
        draw.text((10, y), line, fill=color, font=font)
        y += 18
    
    image.save('screenshot.png')
    print("Created: screenshot.png")


def create_low_quality_scan():
    """Create a low quality scanned document."""
    width, height = 800, 1100
    # Create slightly yellowed background
    image = Image.new('RGB', (width, height), color=(245, 240, 220))
    
    # Add noise
    pixels = image.load()
    for i in range(width):
        for j in range(height):
            # Add random noise
            if random.random() < 0.02:
                pixels[i, j] = (
                    random.randint(100, 150),
                    random.randint(100, 150),
                    random.randint(100, 150)
                )
    
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 18)
    except:
        font = ImageFont.load_default()
    
    # Slightly rotated text to simulate scan skew
    text_content = """
                           MEMORANDUM
    
    TO:      All Staff
    FROM:    Management
    DATE:    January 30, 2025
    RE:      New Document Processing System
    
    
    This memo is to inform all staff that we will be implementing
    a new document processing system based on vector database
    technology. This system will improve our ability to search
    and retrieve documents across all departments.
    
    Key Benefits:
    
    • Faster document retrieval
    • More accurate search results  
    • Support for multiple file formats
    • Automated document classification
    
    Implementation Timeline:
    
    Phase 1 (Feb 1-15):    System setup and configuration
    Phase 2 (Feb 16-28):   Department pilot programs
    Phase 3 (March 1):     Full rollout
    
    Training sessions will be scheduled for all staff during
    the week of February 12-16. Attendance is mandatory.
    
    Please direct any questions to the IT department.
    """
    
    y = 100
    for line in text_content.strip().split('\n'):
        # Add slight variation to simulate scan imperfections
        x = 80 + random.randint(-2, 2)
        draw.text((x, y), line, fill=(40, 40, 40), font=font)
        y += 25
    
    # Add some "scan artifacts" - dark edges
    for i in range(10):
        draw.line((i, 0, i, height), fill=(150-i*10, 150-i*10, 150-i*10))
        draw.line((width-i, 0, width-i, height), fill=(150-i*10, 150-i*10, 150-i*10))
    
    image.save('scanned_memo.jpg', quality=70)
    print("Created: scanned_memo.jpg")


def create_multi_page_tiff():
    """Create a multi-page TIFF document."""
    pages = []
    
    for page_num in range(1, 4):
        image = Image.new('RGB', (800, 1100), color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
        
        # Page header
        draw.text((50, 50), f"Technical Report - Page {page_num} of 3", fill='black', font=font)
        draw.line((50, 90, 750, 90), fill='black', width=2)
        
        # Page content
        if page_num == 1:
            content = """
Executive Summary

This technical report presents the findings from our evaluation of the
Vector Database Query System. The system demonstrates excellent performance
characteristics and meets all specified requirements.

Key Findings:
• Query latency: < 100ms for 95% of queries
• Indexing speed: 1000 documents/minute
• Accuracy: 94% precision on test dataset
• Scalability: Linear up to 10M documents

The system is ready for production deployment.
"""
        elif page_num == 2:
            content = """
Performance Analysis

Detailed benchmarking was conducted across various document types and
query patterns. Results show consistent performance across all scenarios.

Test Environment:
- CPU: 8-core Intel Xeon
- RAM: 32GB DDR4
- Storage: NVMe SSD
- Network: 10Gbps

Query Performance by Document Type:
- PDF files: 89ms average
- Word documents: 92ms average
- Text files: 45ms average
- HTML pages: 67ms average
"""
        else:
            content = """
Recommendations

Based on our analysis, we recommend:

1. Immediate deployment to production environment
2. Implement automated scaling policies
3. Set up continuous monitoring
4. Plan for quarterly performance reviews

Next Steps:
- Schedule deployment window
- Prepare rollback procedures
- Train operations team
- Document best practices

For questions, contact: tech-team@example.com
"""
        
        y = 120
        for line in content.strip().split('\n'):
            draw.text((50, y), line, fill='black', font=font)
            y += 30
        
        # Page number at bottom
        draw.text((400, 1000), f"Page {page_num}", fill='gray', font=font)
        
        pages.append(image)
    
    # Save as multi-page TIFF
    pages[0].save(
        'multipage_report.tiff',
        save_all=True,
        append_images=pages[1:],
        compression='tiff_lzw'
    )
    print("Created: multipage_report.tiff")


def main():
    """Create all sample images."""
    print("Creating sample images for OCR testing...")
    
    # Change to the images directory
    images_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        import os
        os.chdir(images_dir)
        
        create_text_document()
        create_invoice_image()
        create_handwritten_note()
        create_screenshot()
        create_low_quality_scan()
        create_multi_page_tiff()
        
        print("\nAll sample images created successfully!")
        print(f"Files created in: {images_dir}")
        
    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()