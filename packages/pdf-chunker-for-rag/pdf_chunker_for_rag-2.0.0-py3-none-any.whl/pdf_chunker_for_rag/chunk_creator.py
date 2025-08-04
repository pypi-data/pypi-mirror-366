#!/usr/bin/env python3
"""
Clean Hybrid PDF Chunking Approach
1. Use PyMuPDF to identify headers based on font size (25-30pt range)
2. Create exactly one chunk per header with its content only
3. No LLM topic combining - strict header-based boundaries
"""

import os
import json
import re
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import logging
from pypdf import PdfReader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CleanHybridPDFChunker:
    """Clean hybrid chunker: one chunk per header, no combining"""
    
    def __init__(self):
        self.detected_headers = []
        self.full_text = ""
        self.full_text_words = []
    
    def detect_headers_by_font_size(self, pdf_path: str, min_size: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Step 1: Use PyMuPDF to detect headers based on font size
        If min_size is not provided, automatically determine it based on the document's font distribution
        
        Args:
            pdf_path: Path to the PDF file
            min_size: Minimum font size for headers (if None, automatically determined)
            
        Returns:
            List of detected headers with their properties
        """
        # If min_size is not provided, analyze the document to determine it
        if min_size is None:
            # Extract all font sizes to determine the normal text size
            doc = fitz.open(pdf_path)
            all_font_sizes = []
            font_size_counts = {}
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" not in block:
                        continue
                        
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(text) > 2:  # Skip very short text
                                font_size = span["size"]
                                all_font_sizes.append(font_size)
                                font_size_counts[font_size] = font_size_counts.get(font_size, 0) + 1
            
            doc.close()
            
            if not all_font_sizes:
                logger.warning("No text found in document")
                return []
            
            # Find the most common font size (likely the normal text)
            normal_font_size = max(font_size_counts.items(), key=lambda x: x[1])[0]
            
            # Set the minimum header size to be 1.2x the normal text size
            min_size = normal_font_size * 1.2
            
            logger.info(f"Automatically determined normal text size: {normal_font_size:.1f}pt")
            logger.info(f"Setting minimum header size to: {min_size:.1f}pt (1.2x normal text size)")
        
        logger.info(f"Detecting headers with font size > {min_size}pt")
        
        doc = fitz.open(pdf_path)
        all_text_elements = []
        all_font_sizes = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            font_size = span["size"]
                            all_font_sizes.append(font_size)
                            
                            bbox = span.get("bbox", [0, 0, 0, 0])
                            all_text_elements.append({
                                "text": text,
                                "font_size": font_size,
                                "font_name": span["font"],
                                "is_bold": span["flags"] & 16,
                                "page": page_num + 1,
                                "bbox": bbox,
                                "x": bbox[0],
                                "y": bbox[1]
                            })
        
        doc.close()
        
        # Group text elements by Y position (same line across blocks)
        grouped_elements = self._group_by_y_position(all_text_elements)
        
        # Debug: Look for "Executive Summary" specifically
        # Filter for headers based on font size
        headers = []
        for group in grouped_elements:
            max_font_size = max(elem["font_size"] for elem in group)
            
            # Combine text from all elements in the group
            combined_text = " ".join(elem["text"] for elem in sorted(group, key=lambda x: x["x"]))
            
            if max_font_size > min_size:
                # Check length criteria
                if 3 < len(combined_text) < 200:
                    # Use properties from the element with max font size
                    main_element = max(group, key=lambda x: x["font_size"])
                    
                    headers.append({
                        "text": combined_text,
                        "font_size": max_font_size,
                        "font_name": main_element["font_name"],
                        "is_bold": any(elem["is_bold"] for elem in group),
                        "page": main_element["page"],
                        "bbox": [min(e["x"] for e in group), 
                                main_element["y"], 
                                max(e["bbox"][2] for e in group), 
                                main_element["bbox"][3]],
                        "spans_count": len(group)
                    })
        
        # Remove duplicates (same text appearing multiple times)
        unique_headers = []
        seen_texts = set()
        
        for header in headers:
            if header["text"] not in seen_texts:
                unique_headers.append(header)
                seen_texts.add(header["text"])
        
        # Sort by page order
        unique_headers.sort(key=lambda x: (x["page"], x["bbox"][1]))
        
        logger.info(f"Found {len(unique_headers)} unique headers with font size > {min_size}pt")
        
        for i, header in enumerate(unique_headers):
            logger.info(f"  {i+1}. Page {header['page']}: '{header['text']}' ({header['font_size']:.1f}pt)")
        
        self.detected_headers = unique_headers
        return unique_headers
    
    def _group_by_y_position(self, elements: List[Dict[str, Any]], tolerance: float = 1.0) -> List[List[Dict[str, Any]]]:
        """Group text elements that are on the same Y position (same line) and same page"""
        
        if not elements:
            return []
        
        # Group by page first, then by Y position within each page
        pages = {}
        for element in elements:
            page_num = element["page"]
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(element)
        
        all_groups = []
        
        for page_num, page_elements in pages.items():
            # Sort by Y position within the page
            sorted_elements = sorted(page_elements, key=lambda x: x["y"])
            
            if not sorted_elements:
                continue
                
            page_groups = []
            current_group = [sorted_elements[0]]
            current_y = sorted_elements[0]["y"]
            
            for element in sorted_elements[1:]:
                if abs(element["y"] - current_y) <= tolerance:
                    # Same line - add to current group
                    current_group.append(element)
                else:
                    # Different line - start new group
                    if current_group:
                        page_groups.append(current_group)
                    current_group = [element]
                    current_y = element["y"]
            
            # Don't forget the last group
            if current_group:
                page_groups.append(current_group)
                
            all_groups.extend(page_groups)
        
        return all_groups
    
    def extract_full_text_with_structure(self, pdf_path: str) -> str:
        """
        Step 2: Extract full text while preserving some structure
        """
        logger.info("Extracting full text with structure preservation")
        
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            # Add page markers for context
            full_text += f"\n\n--- PAGE {page_num + 1} ---\n"
            full_text += page_text
        
        doc.close()
        
        self.full_text = full_text
        self.full_text_words = full_text.split()
        return full_text
    
    def find_header_positions_in_text(self, headers: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """
        Find the position of each header in the full text to create boundaries
        Uses both text matching and page/Y coordinates to ensure correct order
        """
        logger.info("Finding header positions in text for boundary creation")
        
        header_positions = []
        words = full_text.split()
        
        # Headers are already sorted by page and Y position from detect_headers_by_font_size
        # We need to find them in the text in this order
        for i, header in enumerate(headers):
            header_text = header["text"]
            header_words = header_text.split()
            
            # Find the position of this header in the text
            found_position = None
            
            # Start search from after the previous header if we found one
            search_start = 0
            if header_positions:
                search_start = header_positions[-1]["end_position"]
            
            for word_idx in range(search_start, len(words) - len(header_words) + 1):
                # Check if header words match at this position
                match = True
                for j, header_word in enumerate(header_words):
                    if word_idx + j >= len(words):
                        match = False
                        break
                    # Fuzzy matching for headers (case insensitive, remove punctuation)
                    text_word = words[word_idx + j].lower().strip(".,!?;:()")
                    header_word_clean = header_word.lower().strip(".,!?;:()")
                    if text_word != header_word_clean:
                        match = False
                        break
                
                if match:
                    found_position = word_idx
                    break
            
            if found_position is not None:
                header_positions.append({
                    **header,
                    "start_position": found_position,
                    "end_position": found_position + len(header_words),
                    "document_order": i  # Track original document order
                })
                logger.info(f"  Found header '{header_text}' at position {found_position} (page {header['page']})")
            else:
                logger.warning(f"  Could not find header '{header_text}' in text (page {header['page']})")
        
        # Headers should already be in document order, but verify
        # Sort by document order (which follows page and Y position)
        header_positions.sort(key=lambda x: x["document_order"])
        
        # Validate that positions are sequential
        for i in range(1, len(header_positions)):
            if header_positions[i]["start_position"] <= header_positions[i-1]["start_position"]:
                logger.warning(f"Header position order issue: '{header_positions[i]['text']}' at {header_positions[i]['start_position']} should be after '{header_positions[i-1]['text']}' at {header_positions[i-1]['start_position']}")
        
        return header_positions
    
    def extract_text_with_positions(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text with detailed position information for better header-content association
        """
        logger.info("Extracting text with detailed position information")
        
        doc = fitz.open(pdf_path)
        text_elements = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    line_text = ""
                    line_bbox = None
                    max_font_size = 0
                    
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            line_text += text + " "
                            max_font_size = max(max_font_size, span["size"])
                            
                            if line_bbox is None:
                                line_bbox = list(span["bbox"])
                            else:
                                # Extend bbox to include this span
                                line_bbox[2] = max(line_bbox[2], span["bbox"][2])
                    
                    line_text = line_text.strip()
                    if line_text and line_bbox:
                        text_elements.append({
                            "text": line_text,
                            "page": page_num + 1,
                            "y": line_bbox[1],
                            "x": line_bbox[0],
                            "font_size": max_font_size,
                            "bbox": line_bbox
                        })
        
        doc.close()
        
        # Sort by page, then by Y position (top to bottom)
        text_elements.sort(key=lambda x: (x["page"], x["y"]))
        
        return text_elements
    
    def merge_font_sizes_with_tolerance(self, font_sizes: List[float], tolerance: float = 2.0) -> Dict[float, List[float]]:
        """
        Merge nearby font sizes with configurable tolerance
        
        Args:
            font_sizes: List of font sizes to merge
            tolerance: Maximum difference between sizes to consider them the same (default: 2.0pt)
            
        Returns:
            Dictionary mapping representative size to list of sizes in that group
        """
        if not font_sizes:
            return {}
        
        # Remove duplicates and sort
        unique_sizes = sorted(set(font_sizes))
        
        # Start with the first size
        groups = {}
        current_group = [unique_sizes[0]]
        representative_size = unique_sizes[0]
        
        for size in unique_sizes[1:]:
            # Check if this size is within tolerance of any size in current group
            if any(abs(size - group_size) <= tolerance for group_size in current_group):
                current_group.append(size)
            else:
                # Start a new group
                groups[representative_size] = current_group
                current_group = [size]
                representative_size = size
        
        # Don't forget the last group
        if current_group:
            groups[representative_size] = current_group
        
        return groups
    
    def has_meaningful_sentence_structure(self, text: str) -> bool:
        """
        Simplified meaning detection using generic sentence structure analysis.
        This approach focuses on basic sentence patterns rather than document-specific metadata.
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if text has meaningful sentence structure, False otherwise
        """
        import re
        
        if not text or len(text.strip()) < 20:
            return False
        
        text = text.strip()
        content_lower = text.lower()
        
        # FIRST: Check for obvious formatting patterns (immediate rejection)
        metadata_patterns = [
            r'---\s*page\s+\d+\s*---',          # Page markers like "--- PAGE 2 ---"
            r'[A-Z]\s+[A-Z]\s+[A-Z]\s+[A-Z]',   # Spaced titles like "U N I V E R S A L"
            r'---.*---',                        # Any dashed headers
        ]
        
        for pattern in metadata_patterns:
            if re.search(pattern, content_lower):
                return False
        
        # Check if content is mostly metadata words (keep it simple)
        words = text.split()
        metadata_words = ['page', 'version', 'confidential', 'copyright', 'internal', 'draft']
        
        metadata_word_count = sum(1 for word in words if word.lower() in metadata_words)
        metadata_ratio = metadata_word_count / len(words) if words else 0
        
        if metadata_ratio > 0.3:
            return False
        
        # Check for spaced-out words (like "U N I V E R S A L")
        single_letter_words = sum(1 for word in words if len(word) == 1 and word.isalpha())
        single_letter_ratio = single_letter_words / len(words) if words else 0
        
        if single_letter_ratio > 0.4:
            return False
        
        # Simple meaningful content check based on sentence structure
        has_verbs = any(word in text.lower() for word in ['is', 'are', 'was', 'were', 'will', 'can', 'should', 'would', 'has', 'have', 'had', 'enables', 'provides', 'supports', 'creates', 'allows'])
        has_articles = any(word in text.lower() for word in ['the', 'a', 'an', 'this', 'that', 'these', 'those'])
        has_complete_sentences = '.' in text or '!' in text or '?' in text
        word_count_ok = len(words) >= 5
        
        # Need at least 2 of 4 criteria for meaningful content (flexible scoring)
        meaningful_criteria = sum([has_verbs, has_articles, has_complete_sentences, word_count_ok])
        
        return meaningful_criteria >= 2
    
    def is_meaningless_content(self, content: str, topic: str = "") -> bool:
        """
        Detect if content is meaningless for chunking purposes using conservative criteria
        
        Args:
            content: The text content to analyze
            topic: The associated topic/header (optional)
            
        Returns:
            True if content is meaningless, False if it's valuable
        """
        if not content or not content.strip():
            return True
        
        content_lower = content.lower().strip()
        words = content.split()
        
        # For very short content, use strict NLP analysis
        if len(words) < 30:
            if not self.has_meaningful_sentence_structure(content):
                return True
        
        # Pattern 1: Version/Date/Administrative patterns (conservative)
        metadata_patterns = [
            r'version\s+\d+\.\d+',
            r'september\s+\d+,?\s+\d{4}',  # Specific date patterns
            r'september\s+\d+,?\s+\d{4}',
            r'page\s+\d+',
            r'confidential',
            r'copyright',
            r'proprietary',
            r'internal\s+use\s+only'
        ]
        
        import re
        for pattern in metadata_patterns:
            if re.search(pattern, content_lower):
                return True
        
        # Pattern 2: Formatting artifacts and page markers
        formatting_artifacts = [
            '---',
            'PAGE',
            'U N I V E R S A L',  # Spaced out titles
            '- - -',
            '___'
        ]
        
        for artifact in formatting_artifacts:
            if artifact.lower() in content_lower:
                return True
        
        # Pattern 3: Low word-to-symbol ratio (too much metadata)
        if len(words) > 0:
            # Count actual meaningful words vs numbers/symbols
            meaningful_words = 0
            for word in words:
                # Skip pure numbers, single letters, and common artifacts
                cleaned_word = re.sub(r'[^\w]', '', word)
                if (len(cleaned_word) > 2 and 
                    not cleaned_word.isdigit() and 
                    not re.match(r'^[A-Z]{1,3}$', cleaned_word)):
                    meaningful_words += 1
            
            meaningful_ratio = meaningful_words / len(words)
            if meaningful_ratio < 0.3:  # Less than 30% meaningful words
                return True
        
        # Pattern 4: Incomplete sentences (ending with prepositions/conjunctions)
        if topic and len(topic.split()) > 1:
            topic_words = topic.lower().split()
            incomplete_endings = ['with', 'and', 'or', 'of', 'for', 'to', 'in', 'on', 'at', 'by']
            if topic_words[-1] in incomplete_endings:
                return True
        
        # Pattern 5: Too short and mostly numbers/dates
        if len(words) < 10:
            number_like_words = sum(1 for word in words if re.search(r'\d', word))
            if number_like_words > len(words) * 0.5:  # More than 50% contain numbers
                return True
        
        # Pattern 6: Repetitive or garbled text
        if len(set(words)) < len(words) * 0.3:  # Too many repeated words
            return True
        
        # Pattern 7: All caps (likely headers/titles, not content)
        caps_words = sum(1 for word in words if word.isupper() and len(word) > 2)
        if caps_words > len(words) * 0.7:  # More than 70% all caps
            return True
        
        return False
    
    def merge_short_meaningful_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge short but meaningful chunks with adjacent chunks (forward direction by default)
        
        Args:
            chunks: List of chunks to process
            
        Returns:
            List of chunks with short meaningful chunks merged
        """
        if len(chunks) <= 1:
            return chunks
        
        merged_chunks = []
        i = 0
        merge_count = 0
        
        logger.info("Processing short meaningful chunks for merging...")
        
        while i < len(chunks):
            current_chunk = chunks[i]
            content = current_chunk.get('content', '')
            topic = current_chunk.get('topic', '')
            word_count = current_chunk.get('word_count', 0)
            
            # Check if current chunk is short but meaningful
            if (word_count < 50 and 
                self.has_meaningful_sentence_structure(content) and 
                not self.is_meaningless_content(content, topic)):
                
                # Try to merge forward (with next chunk)
                if i + 1 < len(chunks):
                    next_chunk = chunks[i + 1]
                    
                    # Merge current chunk with next chunk
                    merged_content = f"{content}\n\n{next_chunk['content']}"
                    merged_topic = f"{topic} - {next_chunk['topic']}" if topic != next_chunk['topic'] else topic
                    merged_word_count = word_count + next_chunk['word_count']
                    
                    merged_chunk = {
                        "chunk_id": len(merged_chunks) + 1,
                        "topic": merged_topic,
                        "associated_header": next_chunk.get('associated_header', next_chunk['topic']),  # Use the main chunk's header
                        "content": merged_content,
                        "word_count": merged_word_count,
                        "page": current_chunk['page'],  # Keep original page
                        "font_size": max(current_chunk.get('font_size', 0), next_chunk.get('font_size', 0)),
                        "method": current_chunk.get('method', 'unknown') + "_merged",
                        "validation_notes": f"Merged short meaningful chunk '{topic}' ({word_count} words) with '{next_chunk['topic']}' ({next_chunk['word_count']} words)"
                    }
                    
                    merged_chunks.append(merged_chunk)
                    merge_count += 1
                    
                    logger.info(f"  Merged '{topic}' ({word_count} words) → '{next_chunk['topic']}' ({next_chunk['word_count']} words)")
                    logger.info(f"    Result: '{merged_topic}' ({merged_word_count} words)")
                    
                    # Skip the next chunk since we merged it
                    i += 2
                else:
                    # Last chunk and it's short - keep it as is (nowhere to merge)
                    merged_chunks.append(current_chunk)
                    logger.info(f"  Keeping last short chunk '{topic}' ({word_count} words) - nowhere to merge")
                    i += 1
            else:
                # Normal chunk or meaningless short chunk - keep as is
                merged_chunks.append(current_chunk)
                i += 1
        
        # Renumber the chunks
        for i, chunk in enumerate(merged_chunks, 1):
            chunk['chunk_id'] = i
        
        logger.info(f"Chunk merging results:")
        logger.info(f"  Original chunks: {len(chunks)}")
        logger.info(f"  Merged operations: {merge_count}")
        logger.info(f"  Final chunks: {len(merged_chunks)}")
        
        return merged_chunks

    def process_undersized_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Smart handling of undersized chunks:
        1. Identify chunks with < 50 words
        2. Test if text has meaning 
        3. If no meaning → remove
        4. If meaningful → merge with earlier or later chunk
        
        Args:
            chunks: List of chunks to process
            
        Returns:
            List of chunks with undersized chunks processed
        """
        logger.info("=== PROCESSING UNDERSIZED CHUNKS ===")
        logger.info("Logic: <50 words → test meaning → remove if meaningless, merge if meaningful")
        
        if not chunks:
            return chunks
        
        # Step 1: Identify undersized chunks (< 50 words)
        undersized_chunks = []
        normal_chunks = []
        
        for chunk in chunks:
            word_count = chunk.get("word_count", 0)
            if word_count < 50:
                undersized_chunks.append(chunk)
            else:
                normal_chunks.append(chunk)
        
        logger.info(f"Found {len(undersized_chunks)} undersized chunks (< 50 words)")
        logger.info(f"Found {len(normal_chunks)} normal chunks (≥ 50 words)")
        
        if not undersized_chunks:
            logger.info("No undersized chunks to process")
            return chunks
        
        # Step 2: Process each undersized chunk
        processed_chunks = []
        removed_count = 0
        merged_count = 0
        
        # Work with the original chunk order
        for i, chunk in enumerate(chunks):
            word_count = chunk.get("word_count", 0)
            
            if word_count >= 50:
                # Normal chunk - keep as is
                processed_chunks.append(chunk)
            else:
                # Undersized chunk - test for meaning
                content = chunk.get("content", "")
                topic = chunk.get("topic", "")
                
                logger.info(f"Processing undersized chunk {chunk['chunk_id']}: '{topic}' ({word_count} words)")
                
                # Step 3: Test if content has meaning
                has_meaning = self.has_meaningful_sentence_structure(content)
                
                if not has_meaning:
                    # No meaning - remove the chunk
                    logger.info(f"  → REMOVING: No meaningful content detected")
                    logger.info(f"  → REMOVED CONTENT: '{content}'")
                    removed_count += 1
                else:
                    # Has meaning - merge with adjacent chunk
                    logger.info(f"  → MEANINGFUL: Will merge with adjacent chunk")
                    
                    # Decide whether to merge with previous or next chunk
                    merge_target = self._find_best_merge_target(chunks, i)
                    
                    if merge_target == "previous" and processed_chunks:
                        # Merge with previous chunk
                        prev_chunk = processed_chunks[-1]
                        merged_chunk = self._merge_chunks(prev_chunk, chunk, direction="forward")
                        processed_chunks[-1] = merged_chunk
                        logger.info(f"  → MERGED with previous chunk: '{prev_chunk['topic']}'")
                        merged_count += 1
                    elif merge_target == "next" and i + 1 < len(chunks):
                        # Find next non-undersized chunk to merge with
                        next_chunk = None
                        for j in range(i + 1, len(chunks)):
                            if chunks[j].get("word_count", 0) >= 50:
                                next_chunk = chunks[j]
                                break
                        
                        if next_chunk:
                            # We'll handle this when we reach the next chunk
                            # For now, store it as pending merge
                            chunk["_pending_merge"] = "next"
                            processed_chunks.append(chunk)
                        else:
                            # No next chunk available, merge with previous if possible
                            if processed_chunks:
                                prev_chunk = processed_chunks[-1]
                                merged_chunk = self._merge_chunks(prev_chunk, chunk, direction="forward")
                                processed_chunks[-1] = merged_chunk
                                logger.info(f"  → MERGED with previous chunk (fallback): '{prev_chunk['topic']}'")
                                merged_count += 1
                            else:
                                # Edge case: keep the chunk
                                processed_chunks.append(chunk)
                    else:
                        # Fallback: keep the chunk if no merge possible
                        processed_chunks.append(chunk)
        
        # Step 4: Handle pending merges
        final_chunks = []
        for chunk in processed_chunks:
            if chunk.get("_pending_merge") == "next":
                # This chunk should be merged with the next normal chunk
                if final_chunks and final_chunks[-1].get("word_count", 0) >= 50:
                    # Previous chunk is normal, merge backward
                    prev_chunk = final_chunks[-1]
                    merged_chunk = self._merge_chunks(chunk, prev_chunk, direction="backward")
                    final_chunks[-1] = merged_chunk
                    logger.info(f"  → MERGED pending chunk '{chunk['topic']}' with '{prev_chunk['topic']}'")
                    merged_count += 1
                else:
                    # Remove the pending merge flag and keep
                    del chunk["_pending_merge"]
                    final_chunks.append(chunk)
            else:
                final_chunks.append(chunk)
        
        # Step 5: Renumber chunks
        for i, chunk in enumerate(final_chunks, 1):
            chunk["chunk_id"] = i
        
        logger.info(f"Undersized chunk processing results:")
        logger.info(f"  Original chunks: {len(chunks)}")
        logger.info(f"  Chunks removed: {removed_count}")
        logger.info(f"  Chunks merged: {merged_count}")
        logger.info(f"  Final chunks: {len(final_chunks)}")
        
        return final_chunks
    
    def _find_best_merge_target(self, chunks: List[Dict[str, Any]], current_index: int) -> str:
        """
        Determine whether to merge undersized chunk with previous or next chunk.
        
        Args:
            chunks: All chunks
            current_index: Index of current undersized chunk
            
        Returns:
            "previous" or "next" indicating merge direction
        """
        has_previous = current_index > 0
        has_next = current_index < len(chunks) - 1
        
        if has_previous and not has_next:
            return "previous"
        elif has_next and not has_previous:
            return "next"
        elif has_previous and has_next:
            # Choose based on size - merge with smaller chunk to balance sizes
            prev_size = chunks[current_index - 1].get("word_count", 0)
            next_size = chunks[current_index + 1].get("word_count", 0)
            
            if prev_size <= next_size:
                return "previous"
            else:
                return "next"
        else:
            # Edge case: no adjacent chunks
            return "previous"
    
    def _merge_chunks(self, chunk1: Dict[str, Any], chunk2: Dict[str, Any], direction: str) -> Dict[str, Any]:
        """
        Merge two chunks together.
        
        Args:
            chunk1: First chunk
            chunk2: Second chunk  
            direction: "forward" (chunk1 + chunk2) or "backward" (chunk2 + chunk1)
            
        Returns:
            Merged chunk
        """
        if direction == "forward":
            primary_chunk = chunk1
            secondary_chunk = chunk2
        else:
            primary_chunk = chunk2
            secondary_chunk = chunk1
        
        # Combine content
        combined_content = f"{primary_chunk.get('content', '')} {secondary_chunk.get('content', '')}".strip()
        
        # Combine topics
        primary_topic = primary_chunk.get("topic", "")
        secondary_topic = secondary_chunk.get("topic", "")
        
        if len(secondary_topic) < len(primary_topic):
            combined_topic = f"{primary_topic} + {secondary_topic}"
        else:
            combined_topic = f"{primary_topic} + {secondary_topic}"
        
        # Create merged chunk
        merged_chunk = {
            **primary_chunk,  # Keep primary chunk's metadata
            "topic": combined_topic,
            "content": combined_content,
            "word_count": len(combined_content.split()),
            "method": f"{primary_chunk.get('method', '')} + merged_undersized",
            "merged_from": [primary_chunk.get("chunk_id"), secondary_chunk.get("chunk_id")],
            "is_merged": True
        }
        
        return merged_chunk

    def filter_and_merge_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combined filtering and merging: remove meaningless chunks, merge short meaningful ones
        
        Args:
            chunks: List of chunks to filter and merge
            
        Returns:
            Processed list of chunks
        """
        logger.info("Starting combined filtering and merging process...")
        
        # Step 1: Remove meaningless chunks
        filtered_chunks = []
        removed_count = 0
        
        logger.info("Step 1: Filtering out meaningless chunks...")
        
        for chunk in chunks:
            content = chunk.get('content', '')
            topic = chunk.get('topic', '')
            word_count = chunk.get('word_count', 0)
            
            # Check multiple criteria for meaningless content
            is_meaningless = False
            removal_reason = []
            
            # Criterion 1: Use our meaningless content detector
            if self.is_meaningless_content(content, topic):
                is_meaningless = True
                removal_reason.append("meaningless_content")
            
            # Criterion 2: Too short with no substantial content (and also meaningless)
            if word_count < 50 and self.is_meaningless_content(content, topic):
                is_meaningless = True
                removal_reason.append("short_and_meaningless")
            
            # Criterion 3: Incomplete topic titles
            if topic and topic.endswith((' with', ' and', ' or', ' of', ' for', ' to', ' in', ' on', ' at')):
                is_meaningless = True
                removal_reason.append("incomplete_title")
            
            if is_meaningless:
                removed_count += 1
                logger.info(f"  Removing chunk {chunk['chunk_id']}: '{topic}' ({word_count} words) - {', '.join(removal_reason)}")
                logger.info(f"    Content preview: {content[:100]}...")
            else:
                filtered_chunks.append(chunk)
        
        logger.info(f"Filtering results: {len(chunks)} → {len(filtered_chunks)} chunks ({removed_count} removed)")
        
        # Step 2: Merge short meaningful chunks
        final_chunks = self.merge_short_meaningful_chunks(filtered_chunks)
        
        logger.info(f"Combined processing results:")
        logger.info(f"  Original chunks: {len(chunks)}")
        logger.info(f"  After filtering: {len(filtered_chunks)}")
        logger.info(f"  After merging: {len(final_chunks)}")
        logger.info(f"  Total removed: {removed_count}")
        logger.info(f"  Net reduction: {len(chunks) - len(final_chunks)} chunks")
        
        return final_chunks

    def find_optimal_header_level_by_frequency(self, size_counts: Dict[float, int], min_occurrences: int = 3) -> Optional[float]:
        """
        Find the largest font size that has multiple occurrences (skip rare headers like titles)
        
        Args:
            size_counts: Dictionary mapping font sizes to their occurrence counts
            min_occurrences: Minimum number of occurrences required (default: 3)
            
        Returns:
            The optimal font size, or None if no suitable size found
        """
        # Filter out rare headers (titles, one-offs)
        candidate_sizes = {size: count for size, count in size_counts.items() 
                          if count >= min_occurrences}
        
        if not candidate_sizes:
            # Fallback: if filtering removes everything, lower the threshold
            candidate_sizes = {size: count for size, count in size_counts.items() 
                              if count >= 2}
        
        if not candidate_sizes:
            # Last resort: use the most common size
            return max(size_counts.items(), key=lambda x: x[1])[0] if size_counts else None
        
        # Pick the LARGEST font size among candidates (highest semantic level)
        optimal_size = max(candidate_sizes.keys())
        
        logger.info(f"Font size selection logic:")
        logger.info(f"  Candidates with ≥{min_occurrences} occurrences: {len(candidate_sizes)}")
        for size, count in sorted(candidate_sizes.items(), reverse=True):
            marker = " ← SELECTED" if size == optimal_size else ""
            logger.info(f"    {size:.1f}pt: {count} headers{marker}")
        
        return optimal_size
    
    def strategic_header_chunking(self, pdf_path: str, target_words_per_chunk: int = 200) -> List[Dict[str, Any]]:
        """
        Implements the 5-step strategy for determining optimal header size and creating chunks:
        1. Identify header sizes and merge nearby sizes (e.g., 20, 21, 22 into one category)
        2. Count headers of each size category
        3. Calculate the total number of words in the PDF
        4. Skip rare header sizes (≤2 occurrences), pick largest font size with multiple occurrences
        5. Create chunks using the finalized header size (chunk is text from header to next header)
        
        This approach prioritizes semantic meaning by using larger headers while avoiding
        document titles and one-off headers that would create poor chunking.
        
        Args:
            pdf_path: Path to the PDF file
            target_words_per_chunk: Target words per chunk (used for reference only)
            
        Returns:
            Tuple of (chunks, headers) created using the optimal header size
        """
        logger.info(f"Implementing 5-step strategic header chunking (target: {target_words_per_chunk} words/chunk)")
        logger.info("Strategy: Skip rare headers, use largest font size with multiple occurrences")
        
        # Step 1: Extract all font sizes from the document
        doc = fitz.open(pdf_path)
        all_font_sizes = []
        total_word_count = 0
        all_text_elements = []
        font_size_counts = {}
        
        # Extract all text elements with font sizes and count total words
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            total_word_count += len(page_text.split())
            
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text and len(text) > 2:  # Skip very short text
                            font_size = span["size"]
                            all_font_sizes.append(font_size)
                            font_size_counts[font_size] = font_size_counts.get(font_size, 0) + 1
                            
                            bbox = span.get("bbox", [0, 0, 0, 0])
                            all_text_elements.append({
                                "text": text,
                                "font_size": font_size,
                                "page": page_num + 1,
                                "bbox": bbox,
                                "x": bbox[0],
                                "y": bbox[1]
                            })
        
        doc.close()
        
        # Identify the normal text font size (most common font size)
        if not font_size_counts:
            logger.error("No text found in document")
            return [], []
            
        normal_font_size = max(font_size_counts.items(), key=lambda x: x[1])[0]
        logger.info(f"Identified normal text font size: {normal_font_size:.1f}pt")
        
        # Calculate minimum header size threshold based on normal text size
        min_header_threshold = normal_font_size * 1.2
        logger.info(f"Setting minimum header threshold to {min_header_threshold:.1f}pt (1.2x normal text)")
        
        # Step 1 (continued): Merge nearby font sizes with tolerance
        merged_sizes = self.merge_font_sizes_with_tolerance(all_font_sizes, tolerance=2.0)
        logger.info(f"Merged {len(all_font_sizes)} font sizes into {len(merged_sizes)} categories")
        
        # Step 3: Calculate total words in PDF
        logger.info(f"Total words in PDF: {total_word_count}")
        target_chunk_count = max(1, total_word_count // target_words_per_chunk)
        logger.info(f"Target number of chunks (words/{target_words_per_chunk}): {target_chunk_count}")
        
        # Group text elements by Y position to identify complete headers
        grouped_elements = self._group_by_y_position(all_text_elements)
        
        # Extract potential headers from grouped elements
        potential_headers = []
        for group in grouped_elements:
            max_font_size = max(elem["font_size"] for elem in group)
            
            # Sort by x position if available
            if all("x" in elem for elem in group):
                sorted_group = sorted(group, key=lambda x: x["x"])
                combined_text = " ".join(elem["text"] for elem in sorted_group)
            else:
                combined_text = " ".join(elem["text"] for elem in group)
            
            # Basic filtering - avoid obvious non-headers
            if len(combined_text) <= 200:
                main_element = max(group, key=lambda x: x["font_size"])
                potential_headers.append({
                    "text": combined_text,
                    "font_size": max_font_size,
                    "page": main_element["page"],
                    "bbox": main_element["bbox"],
                    "y": main_element["y"]
                })
        
        # Step 2: Count headers of each merged size
        size_counts = {}
        for representative_size, size_group in merged_sizes.items():
            # Only consider font sizes that are above our minimum header threshold
            if min(size_group) >= min_header_threshold:
                # Count headers that fall within this size group
                count = sum(1 for h in potential_headers 
                          if any(abs(h["font_size"] - size) <= 2.0 for size in size_group))
                size_counts[representative_size] = count
        
        # Log size counts
        logger.info("Font size categories and header counts:")
        for size, count in sorted(size_counts.items(), reverse=True):
            size_range = merged_sizes[size]
            logger.info(f"  {min(size_range):.1f}-{max(size_range):.1f}pt: {count} headers")
        
        # Save header size information to temp folder
        import tempfile
        import os
        from datetime import datetime
        
        temp_dir = tempfile.gettempdir()
        
        # Prepare detailed header size information
        header_size_info = {
            "total_words": total_word_count,
            "target_chunks": target_chunk_count,
            "normal_text_font_size": normal_font_size,
            "min_header_threshold": min_header_threshold,
            "font_size_categories": {
                str(size): {
                    "size_range": [min(group), max(group)],
                    "count": size_counts.get(size, 0),
                    "all_sizes_in_group": sorted(group),
                    "is_header_size": min(group) >= min_header_threshold
                }
                for size, group in merged_sizes.items()
            }
        }
        
        # Save all raw font sizes to a separate file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_sizes_file = os.path.join(temp_dir, f"all_font_sizes_{timestamp}.json")
        
        # Calculate font size statistics
        sorted_font_sizes = sorted(all_font_sizes)
        
        all_sizes_data = {
            "all_font_sizes": sorted_font_sizes,
            "font_size_count": len(all_font_sizes),
            "unique_font_sizes": sorted(set(all_font_sizes)),
            "unique_font_size_count": len(set(all_font_sizes)),
            "min_font_size": min(all_font_sizes) if all_font_sizes else 0,
            "max_font_size": max(all_font_sizes) if all_font_sizes else 0,
            "normal_text_font_size": normal_font_size,
            "min_header_threshold": min_header_threshold,
            "font_size_frequency": {str(size): count for size, count in sorted(font_size_counts.items(), key=lambda x: x[0])},
            "potential_header_sizes": [size for size in sorted(set(all_font_sizes)) if size >= min_header_threshold],
            "histogram": {
                f"{i}-{i+1}": sum(1 for size in all_font_sizes if i <= size < i+1)
                for i in range(int(min(all_font_sizes)) if all_font_sizes else 0, 
                              int(max(all_font_sizes))+2 if all_font_sizes else 1)
            }
        }
        
        with open(all_sizes_file, "w", encoding="utf-8") as f:
            json.dump(all_sizes_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved all font sizes information to {all_sizes_file}")
        
        
        # Also save the headers for each size category
        headers_by_size = {}
        for size, group in merged_sizes.items():
            size_key = f"{min(group):.1f}-{max(group):.1f}pt"
            headers_in_group = [
                {
                    "text": h["text"],
                    "font_size": h["font_size"],
                    "page": h["page"]
                }
                for h in potential_headers
                if any(abs(h["font_size"] - s) <= 2.0 for s in group)
            ]
            headers_by_size[size_key] = headers_in_group
        
        header_size_info["headers_by_size"] = headers_by_size
        
        # Create filename with timestamp to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        header_info_file = os.path.join(temp_dir, f"header_size_info_{timestamp}.json")
        
        with open(header_info_file, "w", encoding="utf-8") as f:
            json.dump(header_size_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved header size information to {header_info_file}")
        
        # Step 4: Find largest header size with multiple occurrences (skip rare headers)
        optimal_size = self.find_optimal_header_level_by_frequency(size_counts, min_occurrences=3)
        
        if not optimal_size:
            logger.error("Failed to determine optimal header size - no suitable candidates")
            return [], []
        
        optimal_size_range = merged_sizes.get(optimal_size, [optimal_size])
        min_size = min(optimal_size_range)
        max_size = max(optimal_size_range)
        
        logger.info(f"Selected optimal font size: {optimal_size:.1f}pt (range: {min_size:.1f}-{max_size:.1f}pt)")
        logger.info(f"Expected chunks: {size_counts.get(optimal_size, 0)} headers (strategy: largest with multiple occurrences)")
        
        # Create a separate file with PDF word count and finalized header font size
        summary_file = os.path.join(temp_dir, f"pdf_summary_{timestamp}.json")
        summary_data = {
            "pdf_path": pdf_path,
            "total_words": total_word_count,
            "optimal_font_size": optimal_size,
            "optimal_font_size_range": f"{min_size:.1f}-{max_size:.1f}pt",
            "target_chunks": target_chunk_count,
            "expected_chunks": size_counts.get(optimal_size, 0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved PDF word count and finalized header font size to {summary_file}")
        
        # Update header size info file with selected optimal size
        if 'header_info_file' in locals():
            try:
                with open(header_info_file, "r", encoding="utf-8") as f:
                    header_size_info = json.load(f)
                
                header_size_info["selected_optimal_size"] = {
                    "size": optimal_size,
                    "range": [min_size, max_size],
                    "expected_chunks": size_counts.get(optimal_size, 0),
                    "difference_from_target": abs(size_counts.get(optimal_size, 0) - target_chunk_count)
                }
                
                with open(header_info_file, "w", encoding="utf-8") as f:
                    json.dump(header_size_info, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Updated header size information with optimal size selection in {header_info_file}")
            except Exception as e:
                logger.error(f"Error updating header size info file: {str(e)}")
        
        # Step 5: Create chunks using the finalized header size
        # Filter headers with the optimal size
        optimal_headers = [
            h for h in potential_headers 
            if min_size <= h["font_size"] <= max_size
        ]
        
        if not optimal_headers:
            logger.warning("No headers found with the optimal font size")
            return [], []
        
        # Sort headers by page and position
        optimal_headers.sort(key=lambda h: (h["page"], h["y"]))
        
        # Extract text using pypdf for consistent reading order
        reader = PdfReader(pdf_path)
        full_text = ""
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            full_text += f"\n\n--- PAGE {page_num + 1} ---\n"
            full_text += page_text
        
        # Find header positions in the text
        words = full_text.split()
        header_positions = []
        
        for i, header in enumerate(optimal_headers):
            header_text = header["text"]
            header_words = header_text.split()
            
            # Skip very short headers that could match lots of places
            if len(header_words) < 2 and len(header_text) < 10:
                continue
            
            # Find the position of this header in the text
            for word_idx in range(len(words) - len(header_words) + 1):
                match = True
                for j, header_word in enumerate(header_words):
                    if word_idx + j >= len(words):
                        match = False
                        break
                    
                    text_word = words[word_idx + j].lower().strip(".,!?;:()")
                    header_word_clean = header_word.lower().strip(".,!?;:()")
                    
                    if text_word != header_word_clean:
                        match = False
                        break
                
                if match:
                    header_positions.append({
                        **header,
                        "start_position": word_idx,
                        "end_position": word_idx + len(header_words),
                        "order": i
                    })
                    break
        
        # Sort by position in text
        header_positions.sort(key=lambda h: h["start_position"])
        
        # Create chunks based on header positions (chunk is text till next header)
        chunks = []
        
        for i, header in enumerate(header_positions):
            # Determine content boundaries
            content_start = header["end_position"]
            
            if i + 1 < len(header_positions):
                content_end = header_positions[i + 1]["start_position"]
            else:
                content_end = len(words)
            
            # Extract content
            content_words = words[content_start:content_end]
            content = " ".join(content_words).strip()
            
            # Clean content (remove page markers)
            content_clean = " ".join([word for word in content.split() 
                                    if not (word.startswith("---") and "PAGE" in word)])
            
            # Create chunk
            chunk = {
                "chunk_id": i + 1,
                "topic": header["text"],
                "content": content_clean,
                "word_count": len(content_clean.split()),
                "page": header["page"],
                "font_size": header["font_size"],
                "method": "strategic_header_chunking"
            }
            
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks using optimal font size {optimal_size:.1f}pt")
        
        if chunks:
            # Step 1: Process undersized chunks (< 50 words)
            logger.info("Processing undersized chunks...")
            chunks = self.process_undersized_chunks(chunks)
            
            if not chunks:
                logger.warning("No chunks remaining after undersized processing")
                return [], []
            
            avg_words = sum(c["word_count"] for c in chunks) / len(chunks)
            logger.info(f"Average chunk size after undersized processing: {avg_words:.0f} words")
            
            # Add summaries to chunks
            logger.info("Adding summaries to chunks...")
            chunks = self.add_summaries_to_chunks(chunks, method="extractive")
            
            # Process oversized chunks with hierarchical sub-header detection
            logger.info("Processing oversized chunks with hierarchical sub-header detection...")
            chunks = self.process_oversized_chunks(
                chunks=chunks,
                pdf_path=pdf_path,
                main_header_size=optimal_size,
                oversized_threshold=500,  # 2x average (276 * 2 ≈ 500)
                critical_threshold=800    # Definitely needs splitting
            )
            
            # Recalculate statistics after oversized chunk processing
            final_avg_words = sum(c["word_count"] for c in chunks) / len(chunks)
            logger.info(f"Final average chunk size after oversized processing: {final_avg_words:.0f} words")
            
            # Update header size info file with final chunk results
            if 'header_info_file' in locals():
                try:
                    with open(header_info_file, "r", encoding="utf-8") as f:
                        header_size_info = json.load(f)
                    
                    # Add chunk summary (including oversized processing results)
                    header_size_info["chunk_results"] = {
                        "total_chunks": len(chunks),
                        "average_chunk_size": final_avg_words,
                        "total_words_in_chunks": sum(c["word_count"] for c in chunks),
                        "smallest_chunk": min(c["word_count"] for c in chunks),
                        "largest_chunk": max(c["word_count"] for c in chunks),
                        "sub_chunks_created": sum(1 for c in chunks if c.get("sub_header_level", False)),
                        # Save histogram of chunk sizes (in buckets of 100 words)
                        "size_distribution": {
                            f"{i*100}-{(i+1)*100}": sum(1 for c in chunks if i*100 <= c["word_count"] < (i+1)*100)
                            for i in range(0, 10)  # 0-100, 100-200, ..., 900-1000
                        },
                        # Also add >1000 category
                        ">1000": sum(1 for c in chunks if c["word_count"] >= 1000),
                        "oversized_processing": {
                            "oversized_threshold": 500,
                            "critical_threshold": 800,
                            "chunks_over_500": sum(1 for c in chunks if c["word_count"] >= 500),
                            "chunks_over_800": sum(1 for c in chunks if c["word_count"] >= 800)
                        }
                    }
                    
                    with open(header_info_file, "w", encoding="utf-8") as f:
                        json.dump(header_size_info, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Updated header size information with final chunk results in {header_info_file}")
                except Exception as e:
                    logger.error(f"Error updating header size info file with chunk results: {str(e)}")
        else:
            logger.warning("No chunks created - check document headers")
        
        # Return both chunks and the detected headers for saving
        return chunks, optimal_headers
    
    def summarize_chunk(self, chunk: Dict[str, Any], method: str = "extractive") -> str:
        """
        Generate a summary for a chunk using different summarization methods
        
        Args:
            chunk: Chunk dictionary containing content and metadata
            method: Summarization method ('extractive', 'keywords', 'abstractive')
            
        Returns:
            Summary string for the chunk
        """
        content = chunk.get("content", "")
        if not content or len(content.split()) < 10:
            return "Content too short for meaningful summary."
        
        if method == "extractive":
            return self._extractive_summary(content, chunk.get("topic", ""))
        elif method == "keywords":
            return self._keyword_summary(content, chunk.get("topic", ""))
        elif method == "abstractive":
            return self._abstractive_summary(content, chunk.get("topic", ""))
        else:
            return self._extractive_summary(content, chunk.get("topic", ""))
    
    def _extractive_summary(self, content: str, topic: str) -> str:
        """
        Create extractive summary by selecting key sentences
        """
        sentences = self._split_into_sentences(content)
        
        if len(sentences) <= 2:
            return " ".join(sentences)
        
        # Score sentences based on multiple criteria
        sentence_scores = []
        
        for i, sentence in enumerate(sentences):
            score = 0
            words = sentence.lower().split()
            
            # Position-based scoring (first and last sentences often important)
            if i == 0:
                score += 2  # First sentence bonus
            if i == len(sentences) - 1:
                score += 1  # Last sentence bonus
            
            # Length-based scoring (avoid very short/long sentences)
            word_count = len(words)
            if 10 <= word_count <= 30:
                score += 2
            elif 5 <= word_count <= 40:
                score += 1
            
            # Topic relevance (if sentence contains topic words)
            if topic:
                topic_words = topic.lower().split()
                topic_matches = sum(1 for word in topic_words if word in words)
                score += topic_matches * 2
            
            # Key indicator words
            key_indicators = ['important', 'key', 'main', 'primary', 'significant', 
                            'critical', 'essential', 'fundamental', 'core', 'central',
                            'overview', 'summary', 'conclusion', 'result', 'finding']
            
            indicator_matches = sum(1 for indicator in key_indicators if indicator in words)
            score += indicator_matches
            
            # Avoid sentences with too many numbers/technical details
            number_count = sum(1 for word in words if any(char.isdigit() for char in word))
            if number_count > len(words) * 0.3:  # More than 30% numbers
                score -= 1
            
            sentence_scores.append((sentence, score, i))
        
        # Sort by score and select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top 2-3 sentences based on content length
        num_sentences = min(3, max(2, len(sentences) // 4))
        selected = sentence_scores[:num_sentences]
        
        # Sort selected sentences back to original order
        selected.sort(key=lambda x: x[2])
        
        summary = " ".join([s[0] for s in selected])
        return summary.strip()
    
    def _keyword_summary(self, content: str, topic: str) -> str:
        """
        Create summary based on key phrases and topic modeling
        """
        import re
        from collections import Counter
        
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                     'before', 'after', 'above', 'below', 'between', 'among', 'within',
                     'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                     'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                     'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you',
                     'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Filter meaningful words (length > 3, not stop words)
        meaningful_words = [word for word in words 
                          if len(word) > 3 and word not in stop_words]
        
        # Get most common words
        word_freq = Counter(meaningful_words)
        top_words = [word for word, count in word_freq.most_common(8)]
        
        # Extract key phrases (2-3 word combinations)
        sentences = self._split_into_sentences(content)
        key_phrases = []
        
        for sentence in sentences:
            words_in_sentence = sentence.lower().split()
            for i in range(len(words_in_sentence) - 1):
                phrase = f"{words_in_sentence[i]} {words_in_sentence[i+1]}"
                if any(word in phrase for word in top_words):
                    key_phrases.append(phrase)
        
        phrase_freq = Counter(key_phrases)
        top_phrases = [phrase for phrase, count in phrase_freq.most_common(3)]
        
        # Create summary
        summary_parts = []
        if topic:
            summary_parts.append(f"Topic: {topic}")
        
        if top_words:
            summary_parts.append(f"Key concepts: {', '.join(top_words[:5])}")
        
        if top_phrases:
            summary_parts.append(f"Key phrases: {'; '.join(top_phrases)}")
        
        return " | ".join(summary_parts)
    
    def _abstractive_summary(self, content: str, topic: str) -> str:
        """
        Create abstractive summary using simple template-based approach
        Note: In production, you might want to use AI models for true abstractive summarization
        """
        sentences = self._split_into_sentences(content)
        word_count = len(content.split())
        
        # Identify main concepts
        first_sentence = sentences[0] if sentences else ""
        last_sentence = sentences[-1] if len(sentences) > 1 else ""
        
        # Template-based summary
        if topic:
            if word_count < 100:
                summary = f"This section on '{topic}' briefly covers: {first_sentence}"
            elif word_count < 300:
                summary = f"This section discusses '{topic}'. {first_sentence} {last_sentence}"
            else:
                middle_sentence = sentences[len(sentences)//2] if len(sentences) > 2 else ""
                summary = f"This comprehensive section on '{topic}' explains: {first_sentence} Key details include: {middle_sentence} {last_sentence}"
        else:
            summary = self._extractive_summary(content, topic)
        
        return summary.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using simple rules
        """
        import re
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Only keep substantial sentences
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if sentence else ""
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def add_summaries_to_chunks(self, chunks: List[Dict[str, Any]], method: str = "extractive") -> List[Dict[str, Any]]:
        """
        Add summaries to all chunks in the list
        
        Args:
            chunks: List of chunk dictionaries
            method: Summarization method to use
            
        Returns:
            Updated chunks with summaries added
        """
        logger.info(f"Adding {method} summaries to {len(chunks)} chunks...")
        
        summarized_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Create summary
            summary = self.summarize_chunk(chunk, method)
            
            # Add summary to chunk
            updated_chunk = {
                **chunk,
                "summary": summary,
                "summary_method": method,
                "summary_length": len(summary.split())
            }
            
            summarized_chunks.append(updated_chunk)
            
            # Log progress for longer documents
            if i % 5 == 0 or i == len(chunks) - 1:
                logger.info(f"  Summarized {i + 1}/{len(chunks)} chunks")
        
        # Log summary statistics
        avg_summary_length = sum(c["summary_length"] for c in summarized_chunks) / len(summarized_chunks)
        logger.info(f"Summary statistics:")
        logger.info(f"  Average summary length: {avg_summary_length:.1f} words")
        logger.info(f"  Method used: {method}")
        
        return summarized_chunks

    def detect_oversized_chunks(self, chunks: List[Dict[str, Any]], 
                               oversized_threshold: int = 500, 
                               critical_threshold: int = 800) -> List[Dict[str, Any]]:
        """
        Detect oversized chunks that need hierarchical sub-header splitting
        
        Args:
            chunks: List of chunk dictionaries
            oversized_threshold: Word count threshold for "oversized" chunks (default: 500)
            critical_threshold: Word count threshold for "definitely needs splitting" (default: 800)
            
        Returns:
            List of chunk analysis with oversized detection flags
        """
        logger.info(f"Detecting oversized chunks (thresholds: {oversized_threshold}+ oversized, {critical_threshold}+ critical)")
        
        chunk_analysis = []
        oversized_count = 0
        critical_count = 0
        
        for chunk in chunks:
            word_count = chunk.get("word_count", 0)
            
            # Determine chunk status
            if word_count >= critical_threshold:
                status = "critical"
                critical_count += 1
            elif word_count >= oversized_threshold:
                status = "oversized"
                oversized_count += 1
            else:
                status = "normal"
            
            analysis = {
                **chunk,
                "size_status": status,
                "needs_splitting": word_count >= oversized_threshold,
                "priority_splitting": word_count >= critical_threshold,
                "size_ratio": word_count / oversized_threshold if oversized_threshold > 0 else 0
            }
            
            chunk_analysis.append(analysis)
        
        logger.info(f"Chunk size analysis:")
        logger.info(f"  Normal chunks (< {oversized_threshold} words): {len(chunks) - oversized_count - critical_count}")
        logger.info(f"  Oversized chunks ({oversized_threshold}-{critical_threshold-1} words): {oversized_count}")
        logger.info(f"  Critical chunks ({critical_threshold}+ words): {critical_count}")
        logger.info(f"  Total chunks needing splitting: {oversized_count + critical_count}")
        
        return chunk_analysis

    def detect_sub_headers_in_oversized_chunks(self, pdf_path: str, oversized_chunks: List[Dict[str, Any]], 
                                             main_header_size: float) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect smaller font size headers within oversized chunks for hierarchical splitting
        
        Args:
            pdf_path: Path to the PDF file
            oversized_chunks: List of oversized chunks that need splitting
            main_header_size: The main header font size used for chunking
            
        Returns:
            Dictionary mapping chunk_id to list of detected sub-headers
        """
        logger.info(f"Detecting sub-headers in {len(oversized_chunks)} oversized chunks...")
        logger.info(f"Looking for headers smaller than main size: {main_header_size:.1f}pt")
        
        # Open document for analysis
        doc = fitz.open(pdf_path)
        
        # Define sub-header size range (smaller than main headers but larger than normal text)
        min_sub_header_size = main_header_size * 0.6  # 60% of main header size
        max_sub_header_size = main_header_size * 0.95  # 95% of main header size
        
        logger.info(f"Sub-header size range: {min_sub_header_size:.1f}pt - {max_sub_header_size:.1f}pt")
        
        chunk_sub_headers = {}
        
        for chunk in oversized_chunks:
            chunk_id = chunk["chunk_id"]
            chunk_page = chunk["page"]
            chunk_topic = chunk["topic"]
            
            logger.info(f"Analyzing chunk {chunk_id}: '{chunk_topic}' ({chunk['word_count']} words)")
            
            # Extract all potential sub-headers from the chunk's page range
            potential_sub_headers = []
            
            # For simplicity, focus on the main page of the chunk
            # In a more advanced version, you could track page ranges
            page = doc[chunk_page - 1]  # Convert to 0-based indexing
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    line_text = ""
                    max_font_size = 0
                    line_bbox = None
                    
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            line_text += text + " "
                            font_size = span["size"]
                            if font_size > max_font_size:
                                max_font_size = font_size
                            if line_bbox is None:
                                line_bbox = span.get("bbox", [0, 0, 0, 0])
                    
                    line_text = line_text.strip()
                    
                    # Check if this could be a sub-header
                    if (line_text and 
                        min_sub_header_size <= max_font_size <= max_sub_header_size and
                        5 <= len(line_text) <= 150 and  # Reasonable header length
                        not line_text.endswith('.') and  # Headers usually don't end with periods
                        len(line_text.split()) <= 10):  # Headers are typically short
                        
                        potential_sub_headers.append({
                            "text": line_text,
                            "font_size": max_font_size,
                            "page": chunk_page,
                            "y": line_bbox[1] if line_bbox else 0,
                            "bbox": line_bbox
                        })
            
            # Filter and sort sub-headers
            if potential_sub_headers:
                # Remove duplicates
                unique_sub_headers = []
                seen_texts = set()
                
                for header in potential_sub_headers:
                    if header["text"] not in seen_texts:
                        unique_sub_headers.append(header)
                        seen_texts.add(header["text"])
                
                # Sort by Y position (top to bottom)
                unique_sub_headers.sort(key=lambda h: h["y"])
                
                chunk_sub_headers[chunk_id] = unique_sub_headers
                
                logger.info(f"  Found {len(unique_sub_headers)} potential sub-headers:")
                for i, sub_header in enumerate(unique_sub_headers):
                    logger.info(f"    {i+1}. '{sub_header['text']}' ({sub_header['font_size']:.1f}pt)")
            else:
                logger.info(f"  No sub-headers found in chunk {chunk_id}")
                chunk_sub_headers[chunk_id] = []
        
        doc.close()
        
        total_sub_headers = sum(len(headers) for headers in chunk_sub_headers.values())
        logger.info(f"Total sub-headers detected: {total_sub_headers}")
        
        return chunk_sub_headers

    def split_oversized_chunk_with_sub_headers(self, chunk: Dict[str, Any], 
                                             sub_headers: List[Dict[str, Any]], 
                                             pdf_path: str) -> List[Dict[str, Any]]:
        """
        Split an oversized chunk using detected sub-headers
        
        Args:
            chunk: The oversized chunk to split
            sub_headers: List of sub-headers detected within this chunk
            pdf_path: Path to the PDF file for text extraction
            
        Returns:
            List of smaller chunks created by splitting
        """
        if not sub_headers:
            logger.warning(f"No sub-headers available for splitting chunk {chunk['chunk_id']}")
            return [chunk]  # Return original chunk if no sub-headers
        
        logger.info(f"Splitting chunk {chunk['chunk_id']} using {len(sub_headers)} sub-headers")
        
        # Extract text using pypdf for consistent reading order
        reader = PdfReader(pdf_path)
        full_text = ""
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            full_text += f"\n\n--- PAGE {page_num + 1} ---\n"
            full_text += page_text
        
        words = full_text.split()
        
        # Find sub-header positions in text
        sub_header_positions = []
        
        for sub_header in sub_headers:
            header_words = sub_header["text"].split()
            
            # Find position in text
            for word_idx in range(len(words) - len(header_words) + 1):
                match = True
                for j, header_word in enumerate(header_words):
                    if word_idx + j >= len(words):
                        match = False
                        break
                    
                    text_word = words[word_idx + j].lower().strip(".,!?;:()")
                    header_word_clean = header_word.lower().strip(".,!?;:()")
                    
                    if text_word != header_word_clean:
                        match = False
                        break
                
                if match:
                    sub_header_positions.append({
                        **sub_header,
                        "start_position": word_idx,
                        "end_position": word_idx + len(header_words)
                    })
                    break
        
        if not sub_header_positions:
            logger.warning(f"Could not locate sub-headers in text for chunk {chunk['chunk_id']}")
            return [chunk]
        
        # Sort by position in text
        sub_header_positions.sort(key=lambda h: h["start_position"])
        
        # Find the original chunk boundaries
        original_chunk_words = chunk["content"].split()
        
        # Find where the original chunk starts and ends in the full text
        chunk_start_pos = None
        for word_idx in range(len(words) - len(original_chunk_words) + 1):
            # Check if chunk content matches at this position (first 10 words)
            match_words = min(10, len(original_chunk_words))
            match = True
            
            for j in range(match_words):
                if word_idx + j >= len(words):
                    match = False
                    break
                
                text_word = words[word_idx + j].lower().strip(".,!?;:()")
                chunk_word = original_chunk_words[j].lower().strip(".,!?;:()")
                
                if text_word != chunk_word:
                    match = False
                    break
            
            if match:
                chunk_start_pos = word_idx
                break
        
        if chunk_start_pos is None:
            logger.warning(f"Could not locate original chunk content in text for chunk {chunk['chunk_id']}")
            return [chunk]
        
        chunk_end_pos = chunk_start_pos + len(original_chunk_words)
        
        # Filter sub-headers that are within the chunk boundaries
        relevant_sub_headers = [
            h for h in sub_header_positions 
            if chunk_start_pos <= h["start_position"] < chunk_end_pos
        ]
        
        if not relevant_sub_headers:
            logger.info(f"No sub-headers found within chunk {chunk['chunk_id']} boundaries")
            return [chunk]
        
        logger.info(f"Found {len(relevant_sub_headers)} sub-headers within chunk boundaries")
        
        # Create sub-chunks
        sub_chunks = []
        
        for i, sub_header in enumerate(relevant_sub_headers):
            # Determine content boundaries
            content_start = sub_header["end_position"]
            
            if i + 1 < len(relevant_sub_headers):
                content_end = relevant_sub_headers[i + 1]["start_position"]
            else:
                content_end = chunk_end_pos
            
            # Extract content
            if content_start < content_end:
                content_words = words[content_start:content_end]
                content = " ".join(content_words).strip()
                
                # Clean content (remove page markers)
                content_clean = " ".join([word for word in content.split() 
                                        if not (word.startswith("---") and "PAGE" in word)])
                
                if content_clean and len(content_clean.split()) > 3:  # Only create if substantial content
                    sub_chunk = {
                        "chunk_id": f"{chunk['chunk_id']}.{i + 1}",
                        "topic": sub_header["text"],
                        "content": content_clean,  # Keep content pure and focused
                        "word_count": len(content_clean.split()),
                        "page": chunk["page"],
                        "font_size": sub_header["font_size"],
                        "method": "hierarchical_sub_header_split",
                        "parent_chunk_info": {
                            "parent_chunk_id": chunk["chunk_id"],
                            "parent_topic": chunk.get("topic", ""),
                            "parent_summary": chunk.get("summary", ""),
                            "parent_word_count": chunk.get("word_count", 0),
                            "split_reason": "oversized_hierarchical"
                        },
                        "sub_header_level": True,
                        "sub_header_font_size": sub_header["font_size"],
                        "main_header_font_size": chunk.get("font_size", 0)
                    }
                    
                    sub_chunks.append(sub_chunk)
        
        if sub_chunks:
            logger.info(f"Successfully split chunk {chunk['chunk_id']} into {len(sub_chunks)} sub-chunks")
            for sub_chunk in sub_chunks:
                logger.info(f"  - {sub_chunk['chunk_id']}: '{sub_chunk['topic']}' ({sub_chunk['word_count']} words)")
        else:
            logger.warning(f"Failed to create sub-chunks for chunk {chunk['chunk_id']}")
            return [chunk]
        
        return sub_chunks

    def merge_small_sub_chunks(self, chunks: List[Dict[str, Any]], 
                              min_chunk_size: int = 150) -> List[Dict[str, Any]]:
        """
        Merge small sub-chunks to ensure all chunks meet minimum size requirements
        
        Args:
            chunks: List of chunks (including sub-chunks)
            min_chunk_size: Minimum acceptable chunk size in words
            
        Returns:
            List of chunks with small sub-chunks merged appropriately
        """
        logger.info(f"Merging small sub-chunks (minimum size: {min_chunk_size} words)")
        
        # Separate regular chunks from sub-chunks
        regular_chunks = [c for c in chunks if not c.get("sub_header_level", False)]
        sub_chunks = [c for c in chunks if c.get("sub_header_level", False)]
        
        if not sub_chunks:
            logger.info("No sub-chunks found to merge")
            return chunks
        
        # Group sub-chunks by parent chunk
        sub_chunks_by_parent = {}
        for sub_chunk in sub_chunks:
            # Get parent ID from the new metadata structure
            parent_info = sub_chunk.get("parent_chunk_info", {})
            parent_id = parent_info.get("parent_chunk_id")
            
            if parent_id:
                if parent_id not in sub_chunks_by_parent:
                    sub_chunks_by_parent[parent_id] = []
                sub_chunks_by_parent[parent_id].append(sub_chunk)
        
        # Sort sub-chunks within each parent group by chunk_id
        for parent_id in sub_chunks_by_parent:
            sub_chunks_by_parent[parent_id].sort(key=lambda x: x["chunk_id"])
        
        logger.info(f"Found sub-chunks from {len(sub_chunks_by_parent)} parent chunks")
        
        merged_chunks = []
        
        for parent_id, parent_sub_chunks in sub_chunks_by_parent.items():
            logger.info(f"Processing {len(parent_sub_chunks)} sub-chunks from parent {parent_id}")
            
            # Identify small sub-chunks that need merging
            small_chunks = []
            good_chunks = []
            
            for sub_chunk in parent_sub_chunks:
                word_count = sub_chunk.get("word_count", 0)
                if word_count < min_chunk_size:
                    small_chunks.append(sub_chunk)
                    logger.info(f"  Small sub-chunk: '{sub_chunk['topic']}' ({word_count} words)")
                else:
                    good_chunks.append(sub_chunk)
                    logger.info(f"  Good sub-chunk: '{sub_chunk['topic']}' ({word_count} words)")
            
            if not small_chunks:
                # All sub-chunks are already good size
                merged_chunks.extend(parent_sub_chunks)
                continue
            
            # Strategy: Merge consecutive small chunks
            merged_parent_chunks = []
            current_merge_group = []
            
            for sub_chunk in parent_sub_chunks:
                word_count = sub_chunk.get("word_count", 0)
                
                if word_count < min_chunk_size:
                    # Add to current merge group
                    current_merge_group.append(sub_chunk)
                else:
                    # Process any pending merge group first
                    if current_merge_group:
                        merged_chunk = self._merge_sub_chunk_group(current_merge_group, min_chunk_size)
                        merged_parent_chunks.append(merged_chunk)
                        current_merge_group = []
                    
                    # Add the good-sized chunk as is
                    merged_parent_chunks.append(sub_chunk)
            
            # Handle any remaining merge group
            if current_merge_group:
                merged_chunk = self._merge_sub_chunk_group(current_merge_group, min_chunk_size)
                merged_parent_chunks.append(merged_chunk)
            
            merged_chunks.extend(merged_parent_chunks)
        
        # Combine regular chunks with merged sub-chunks
        final_chunks = regular_chunks + merged_chunks
        
        # Sort by original order (handling both numeric and string chunk_ids)
        def sort_key(chunk):
            chunk_id = chunk["chunk_id"]
            if isinstance(chunk_id, str) and "." in chunk_id:
                # Handle sub-chunk IDs like "4.1"
                parts = chunk_id.split(".")
                return (int(parts[0]), int(parts[1]))
            else:
                # Handle regular chunk IDs
                return (int(chunk_id), 0)
        
        final_chunks.sort(key=sort_key)
        
        # Renumber chunks to maintain consistency
        final_chunks = self._renumber_chunks(final_chunks)
        
        # Log merging results
        original_count = len(chunks)
        final_count = len(final_chunks)
        small_count_before = sum(1 for c in chunks if c.get("word_count", 0) < min_chunk_size)
        small_count_after = sum(1 for c in final_chunks if c.get("word_count", 0) < min_chunk_size)
        
        logger.info(f"Sub-chunk merging results:")
        logger.info(f"  Original chunks: {original_count}")
        logger.info(f"  Final chunks: {final_count}")
        logger.info(f"  Small chunks before: {small_count_before}")
        logger.info(f"  Small chunks after: {small_count_after}")
        logger.info(f"  Chunks merged: {original_count - final_count}")
        
        return final_chunks

    def _merge_sub_chunk_group(self, sub_chunks: List[Dict[str, Any]], 
                              min_chunk_size: int) -> Dict[str, Any]:
        """
        Merge a group of consecutive small sub-chunks into one larger chunk
        
        Args:
            sub_chunks: List of small sub-chunks to merge
            min_chunk_size: Minimum target size for merged chunk
            
        Returns:
            Single merged chunk
        """
        if len(sub_chunks) == 1:
            return sub_chunks[0]
        
        # Combine content from all sub-chunks
        combined_content = []
        combined_topics = []
        total_words = 0
        
        for sub_chunk in sub_chunks:
            # Add topic as a mini-header in the content
            topic = sub_chunk.get("topic", "")
            content = sub_chunk.get("content", "")
            
            if topic and content:
                combined_content.append(f"**{topic}**\n{content}")
            elif content:
                combined_content.append(content)
            
            combined_topics.append(topic)
            total_words += sub_chunk.get("word_count", 0)
        
        # Create merged chunk
        first_chunk = sub_chunks[0]
        last_chunk = sub_chunks[-1]
        
        # Create a descriptive topic that combines the sub-topics
        if len(combined_topics) <= 3:
            merged_topic = " + ".join(combined_topics)
        else:
            merged_topic = f"{combined_topics[0]} + {len(combined_topics)-1} more"
        
        # Prepare clean merged content without parent context in content
        merged_content = "\n\n".join(combined_content)
        
        merged_chunk = {
            "chunk_id": first_chunk["chunk_id"],  # Keep first chunk's ID
            "topic": merged_topic,
            "content": merged_content,  # Clean content without parent summary
            "word_count": len(merged_content.split()),
            "page": first_chunk.get("page"),
            "font_size": first_chunk.get("font_size"),
            "method": "merged_sub_chunks",
            "parent_chunk_info": first_chunk.get("parent_chunk_info", {}),  # Preserve parent metadata
            "sub_header_level": True,
            "sub_header_font_size": first_chunk.get("sub_header_font_size"),
            "main_header_font_size": first_chunk.get("main_header_font_size"),
            "merged_from": [c["chunk_id"] for c in sub_chunks],
            "original_topics": combined_topics
        }
        
        # Generate summary for merged chunk
        summary = self.summarize_chunk(merged_chunk, method="extractive")
        merged_chunk["summary"] = summary
        merged_chunk["summary_method"] = "extractive"
        merged_chunk["summary_length"] = len(summary.split())
        
        logger.info(f"  Merged {len(sub_chunks)} sub-chunks into '{merged_topic}' ({merged_chunk['word_count']} words)")
        
        return merged_chunk

    def _renumber_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Renumber chunks to maintain sequential order while preserving sub-chunk relationships
        
        Args:
            chunks: List of chunks to renumber
            
        Returns:
            List of chunks with updated chunk_ids
        """
        # Separate regular chunks from sub-chunks
        regular_chunks = [c for c in chunks if not c.get("sub_header_level", False)]
        sub_chunks = [c for c in chunks if c.get("sub_header_level", False)]
        
        # Renumber regular chunks
        for i, chunk in enumerate(regular_chunks, 1):
            chunk["chunk_id"] = i
        
        # Group sub-chunks by parent and renumber them
        sub_chunks_by_parent = {}
        for sub_chunk in sub_chunks:
            # Get parent ID from metadata structure
            parent_info = sub_chunk.get("parent_chunk_info", {})
            parent_id = parent_info.get("parent_chunk_id")
            
            if parent_id:
                if parent_id not in sub_chunks_by_parent:
                    sub_chunks_by_parent[parent_id] = []
                sub_chunks_by_parent[parent_id].append(sub_chunk)
        
        # Renumber sub-chunks within each parent group
        for parent_id, parent_sub_chunks in sub_chunks_by_parent.items():
            for i, sub_chunk in enumerate(parent_sub_chunks, 1):
                sub_chunk["chunk_id"] = f"{parent_id}.{i}"
        
        # Combine and sort again
        all_chunks = regular_chunks + sub_chunks
        
        def sort_key(chunk):
            chunk_id = chunk["chunk_id"]
            if isinstance(chunk_id, str) and "." in chunk_id:
                parts = chunk_id.split(".")
                return (int(parts[0]), int(parts[1]))
            else:
                return (int(chunk_id), 0)
        
        all_chunks.sort(key=sort_key)
        
        return all_chunks

    def process_oversized_chunks(self, chunks: List[Dict[str, Any]], pdf_path: str,
                               main_header_size: float,
                               oversized_threshold: int = 500,
                               critical_threshold: int = 800) -> List[Dict[str, Any]]:
        """
        Complete workflow for processing oversized chunks with hierarchical sub-header detection
        
        Args:
            chunks: List of all chunks
            pdf_path: Path to the PDF file
            main_header_size: The main header font size used for chunking
            oversized_threshold: Word count threshold for "oversized" chunks
            critical_threshold: Word count threshold for "definitely needs splitting"
            
        Returns:
            Updated list of chunks with oversized chunks split using sub-headers
        """
        logger.info("=== OVERSIZED CHUNK PROCESSING ===")
        
        # Step 1: Detect oversized chunks
        chunk_analysis = self.detect_oversized_chunks(chunks, oversized_threshold, critical_threshold)
        
        # Step 2: Filter chunks that need splitting
        oversized_chunks = [chunk for chunk in chunk_analysis if chunk["needs_splitting"]]
        
        if not oversized_chunks:
            logger.info("No oversized chunks found - no splitting needed")
            return chunks
        
        logger.info(f"Processing {len(oversized_chunks)} oversized chunks...")
        
        # Step 3: Detect sub-headers in oversized chunks
        chunk_sub_headers = self.detect_sub_headers_in_oversized_chunks(pdf_path, oversized_chunks, main_header_size)
        
        # Step 4: Split oversized chunks using sub-headers
        final_chunks = []
        
        for chunk in chunk_analysis:
            if chunk["needs_splitting"] and chunk["chunk_id"] in chunk_sub_headers:
                sub_headers = chunk_sub_headers[chunk["chunk_id"]]
                
                if sub_headers:
                    # Split the chunk
                    split_chunks = self.split_oversized_chunk_with_sub_headers(chunk, sub_headers, pdf_path)
                    final_chunks.extend(split_chunks)
                else:
                    # No sub-headers found, keep original chunk
                    logger.info(f"Keeping oversized chunk {chunk['chunk_id']} - no sub-headers available")
                    final_chunks.append(chunk)
            else:
                # Normal-sized chunk, keep as is
                final_chunks.append(chunk)
        
        # Step 5: Add summaries to new sub-chunks
        logger.info("Adding summaries to newly created sub-chunks...")
        new_sub_chunks = [chunk for chunk in final_chunks if chunk.get("sub_header_level", False)]
        
        if new_sub_chunks:
            for sub_chunk in new_sub_chunks:
                if "summary" not in sub_chunk:
                    summary = self.summarize_chunk(sub_chunk, method="extractive")
                    sub_chunk["summary"] = summary
                    sub_chunk["summary_method"] = "extractive"
                    sub_chunk["summary_length"] = len(summary.split())
        
        # Step 6: Log final results
        original_count = len(chunks)
        final_count = len(final_chunks)
        split_count = sum(1 for c in final_chunks if c.get("sub_header_level", False))
        
        logger.info("=== OVERSIZED CHUNK PROCESSING COMPLETE ===")
        logger.info(f"Original chunks: {original_count}")
        logger.info(f"Final chunks: {final_count}")
        logger.info(f"New sub-chunks created: {split_count}")
        logger.info(f"Net chunk increase: {final_count - original_count}")
        
        # Step 7: Merge small sub-chunks to ensure minimum size requirements
        logger.info("Merging small sub-chunks to meet minimum size requirements...")
        final_chunks = self.merge_small_sub_chunks(final_chunks, min_chunk_size=150)
        
        # Step 8: Log final results after merging
        final_final_count = len(final_chunks)
        small_count_remaining = sum(1 for c in final_chunks if c.get("word_count", 0) < 150)
        
        logger.info("=== FINAL PROCESSING COMPLETE ===")
        logger.info(f"Chunks after merging: {final_final_count}")
        logger.info(f"Small chunks remaining (< 150 words): {small_count_remaining}")
        logger.info(f"Total processing: {original_count} → {final_final_count} chunks")
        
        return final_chunks

    def save_results(self, chunks: List[Dict[str, Any]], headers: List[Dict[str, Any]], output_prefix: str = "clean_hybrid"):
        """Save both headers and chunks to JSON files"""
        
        # Save headers
        headers_file = f"{output_prefix}_headers.json"
        with open(headers_file, 'w', encoding='utf-8') as f:
            json.dump(headers, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(headers)} headers to {headers_file}")
        
        # Save chunks
        chunks_file = f"{output_prefix}_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(chunks)} chunks to {chunks_file}")
        
        # Create a summary report
        summary = {
            "total_headers": len(headers),
            "total_chunks": len(chunks),
            "total_words": sum(chunk["word_count"] for chunk in chunks),
            "average_chunk_size": sum(chunk["word_count"] for chunk in chunks) / len(chunks) if chunks else 0,
            "chunk_size_distribution": {
                "min": min(chunk["word_count"] for chunk in chunks) if chunks else 0,
                "max": max(chunk["word_count"] for chunk in chunks) if chunks else 0,
                "sizes": [chunk["word_count"] for chunk in chunks]
            },
            "method": "clean_header_based_no_llm",
            "approach": "One chunk per header section"
        }
        
        summary_file = f"{output_prefix}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved summary to {summary_file}")


def main():
    """Main function to test the strategic header chunking"""
    
    # Check if PDF file exists
    pdf_path = "doc/White Paper_Universal Identity v1.0.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please make sure the PDF file exists in the doc/ directory")
        return
    
    print("🔄 STRATEGIC HEADER-BASED PDF CHUNKING")
    print("=" * 50)
    print("Strategy: Determine optimal header size based on word count")
    print("Method: 5-step approach (font size grouping, word count, target chunks)")
    print()
    
    # Target words per chunk
    target_words = 200
    
    # Create the chunker
    chunker = CleanHybridPDFChunker()
    
    # Use the strategic chunking method
    print("� Processing document using strategic header chunking...")
    chunks, headers = chunker.strategic_header_chunking(pdf_path, target_words)
    
    if chunks:
        print(f"\n✅ Successfully created {len(chunks)} strategic header-based chunks!")
        print("-" * 60)
        
        total_words = 0
        oversized_count = 0
        sub_chunk_count = 0
        
        for i, chunk in enumerate(chunks, 1):
            word_count = chunk.get("word_count", 0)
            total_words += word_count
            
            # Track oversized chunks and sub-chunks
            if word_count >= 500:
                oversized_count += 1
            if chunk.get("sub_header_level", False):
                sub_chunk_count += 1
            
            # Size indicators with oversized detection
            size_info = ""
            if word_count < 50:
                size_info = " [Very Short]"
            elif word_count >= 800:
                size_info = " [CRITICAL SIZE]"
            elif word_count >= 500:
                size_info = " [OVERSIZED]"
            elif word_count > 300:
                size_info = " [Large]"
            
            # Sub-chunk indicator
            sub_indicator = ""
            merged_indicator = ""
            context_indicator = ""
            
            if chunk.get("sub_header_level", False):
                sub_indicator = " 🔗"
                
                # Get parent information from metadata
                parent_info_data = chunk.get("parent_chunk_info", {})
                parent_topic = parent_info_data.get("parent_topic", "Unknown")
                parent_info = f" (split from: '{parent_topic}')"
                
                # Check if this chunk has parent context
                if parent_info_data.get("parent_summary"):
                    context_indicator = " 📋"
                
                # Check if this is a merged chunk
                if chunk.get("method") == "merged_sub_chunks":
                    merged_indicator = " 🔀"
                    original_topics = chunk.get("original_topics", [])
                    if original_topics:
                        parent_info += f" | Merged: {', '.join(original_topics[:3])}"
                        if len(original_topics) > 3:
                            parent_info += f" + {len(original_topics)-3} more"
            else:
                parent_info = ""
            
            print(f"{i}. {chunk.get('topic', 'Unknown Topic')}{size_info}{sub_indicator}{merged_indicator}{context_indicator}")
            print(f"   📝 Words: {word_count}")
            print(f"   📄 Page: {chunk.get('page', 'Unknown')}")
            print(f"   🔤 Font size: {chunk.get('font_size', 0):.1f}pt")
            
            if parent_info:
                print(f"   🔗 Sub-chunk{parent_info}")
                
                # Show parent metadata if available
                parent_info_data = chunk.get("parent_chunk_info", {})
                if parent_info_data:
                    print(f"   📊 Parent metadata:")
                    if parent_info_data.get("parent_summary"):
                        parent_summary_preview = parent_info_data["parent_summary"][:100] + "..." if len(parent_info_data["parent_summary"]) > 100 else parent_info_data["parent_summary"]
                        print(f"      📋 Parent summary: {parent_summary_preview}")
                    if parent_info_data.get("parent_word_count"):
                        print(f"      📝 Parent size: {parent_info_data['parent_word_count']} words")
                    if parent_info_data.get("split_reason"):
                        print(f"      ⚡ Split reason: {parent_info_data['split_reason']}")
            
            # Show hierarchical font size information for sub-chunks
            if chunk.get("sub_header_level", False):
                main_font = chunk.get("main_header_font_size", 0)
                sub_font = chunk.get("sub_header_font_size", 0)
                if main_font and sub_font:
                    print(f"   � Font hierarchy: {main_font:.1f}pt (main) → {sub_font:.1f}pt (sub)")
                else:
                    print(f"   🔤 Font size: {chunk.get('font_size', 0):.1f}pt")
            else:
                print(f"   🔤 Font size: {chunk.get('font_size', 0):.1f}pt")
            
            # Show summary if available
            if 'summary' in chunk:
                summary_preview = chunk['summary'][:150] + "..." if len(chunk['summary']) > 150 else chunk['summary']
                print(f"   📋 Summary: {summary_preview}")
            
            # Show content preview
            content_preview = chunk.get('content', '')[:100] + "..." if len(chunk.get('content', '')) > 100 else chunk.get('content', '')
            print(f"   📄 Preview: {content_preview}")
            print()
        
        print(f"📊 SUMMARY:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total words: {total_words}")
        print(f"   Average chunk size: {total_words / len(chunks):.0f} words")
        print(f"   Method: Strategic header chunking with oversized detection")
        print(f"   Sub-chunks created: {sub_chunk_count}")
        print(f"   Merged chunks: {sum(1 for c in chunks if c.get('method') == 'merged_sub_chunks')}")
        print(f"   Small chunks remaining (< 150 words): {sum(1 for c in chunks if c.get('word_count', 0) < 150)}")
        print(f"   Remaining oversized chunks (500+ words): {oversized_count}")
        print(f"   Critical chunks (800+ words): {sum(1 for c in chunks if c.get('word_count', 0) >= 800)}")
        
        # Save results
        chunker.save_results(chunks, headers, "strategic_chunking")
        print(f"\n💾 Results saved with 'strategic_chunking_' prefix")
    
    else:
        print("❌ Failed to create chunks")
        print("Check the document structure and font sizes for potential issues.")

    def create_topic_chunks_from_headers(self, pdf_path: str, headers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pure topic-based chunking: Create one chunk per header section.
        No word count targets - natural topic boundaries determine chunk size.
        
        Args:
            pdf_path: Path to the PDF file
            headers: List of headers to use as topic boundaries
            
        Returns:
            List of topic-based chunks
        """
        from pypdf import PdfReader
        
        logger.info(f"Creating topic-based chunks from {len(headers)} headers")
        
        if not headers:
            logger.warning("No headers provided for chunking")
            return []
        
        # Sort headers by page and position
        headers.sort(key=lambda h: (h["page"], h.get("y", 0)))
        
        # Extract full text using pypdf
        reader = PdfReader(pdf_path)
        full_text = ""
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            full_text += f"\n\n--- PAGE {page_num + 1} ---\n"
            full_text += page_text
        
        # Find header positions in text
        words = full_text.split()
        header_positions = []
        
        for i, header in enumerate(headers):
            header_text = header["text"]
            header_words = header_text.split()
            
            # Find position in text
            for word_idx in range(len(words) - len(header_words) + 1):
                match = True
                for j, header_word in enumerate(header_words):
                    if word_idx + j >= len(words):
                        match = False
                        break
                    
                    text_word = words[word_idx + j].lower().strip(".,!?;:()")
                    header_word_clean = header_word.lower().strip(".,!?;:()")
                    
                    if text_word != header_word_clean:
                        match = False
                        break
                
                if match:
                    header_positions.append({
                        **header,
                        "start_position": word_idx,
                        "end_position": word_idx + len(header_words),
                        "order": i
                    })
                    break
        
        # Sort by position in text
        header_positions.sort(key=lambda h: h["start_position"])
        
        # Create topic chunks
        chunks = []
        
        for i, header in enumerate(header_positions):
            # Content starts after header
            content_start = header["end_position"]
            
            # Content ends at next header (or end of document)
            if i + 1 < len(header_positions):
                content_end = header_positions[i + 1]["start_position"]
            else:
                content_end = len(words)
            
            # Extract content
            content_words = words[content_start:content_end]
            content = " ".join(content_words).strip()
            
            # Clean content (remove page markers)
            content_clean = " ".join([word for word in content.split() 
                                    if not (word.startswith("---") and "PAGE" in word)])
            
            # Create topic chunk
            chunk = {
                "chunk_id": i + 1,
                "topic": header["text"],
                "associated_header": header["text"],
                "content": content_clean,
                "word_count": len(content_clean.split()) if content_clean else 0,
                "page": header["page"],
                "font_size": header["font_size"],
                "method": "topic_based_chunking",
                "header_info": {
                    "font_size": header["font_size"],
                    "is_bold": header.get("is_bold", False),
                    "font_name": header.get("font_name", "unknown")
                }
            }
            
            chunks.append(chunk)
            
            logger.info(f"Created topic chunk {i+1}: '{header['text']}' ({chunk['word_count']} words)")
        
        logger.info(f"Topic-based chunking complete: {len(chunks)} chunks created")
        
        # Add extractive summaries
        logger.info("Adding extractive summaries to topic chunks...")
        chunks = self.add_summaries_to_chunks(chunks, method="extractive")
        
        return chunks

    def process_and_save(self, pdf_path: str, output_dir: str = "output", 
                        target_words_per_chunk: int = 200, 
                        save_format: str = "json") -> str:
        """
        Convenience method: Process PDF and save chunks to specified directory.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output (default: "output")
            target_words_per_chunk: Target words per chunk for strategic chunking
            save_format: Output format - "json" or "csv" (default: "json")
            
        Returns:
            Path to the saved output file
        """
        import os
        from datetime import datetime
        
        logger.info(f"Processing PDF and saving to {output_dir}/")
        
        # Process PDF
        chunks, headers = self.strategic_header_chunking(pdf_path, target_words_per_chunk)
        
        if not chunks:
            logger.warning("No chunks created - check document structure")
            return ""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if save_format.lower() == "json":
            output_file = os.path.join(output_dir, f"{pdf_name}_chunks.json")
            
            # Save JSON with metadata
            output_data = {
                "metadata": {
                    "source_pdf": pdf_path,
                    "processing_date": datetime.now().isoformat(),
                    "total_chunks": len(chunks),
                    "total_words": sum(c.get("word_count", 0) for c in chunks),
                    "average_chunk_size": sum(c.get("word_count", 0) for c in chunks) / len(chunks) if chunks else 0,
                    "chunking_method": "strategic_header_chunking"
                },
                "chunks": chunks
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
        elif save_format.lower() == "csv":
            import csv
            output_file = os.path.join(output_dir, f"{pdf_name}_chunks.csv")
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['chunk_id', 'topic', 'content', 'word_count', 'page', 'method'])
                writer.writeheader()
                for chunk in chunks:
                    writer.writerow({
                        'chunk_id': chunk.get('chunk_id', ''),
                        'topic': chunk.get('topic', ''),
                        'content': chunk.get('content', ''),
                        'word_count': chunk.get('word_count', 0),
                        'page': chunk.get('page', ''),
                        'method': chunk.get('method', '')
                    })
        else:
            raise ValueError(f"Unsupported save format: {save_format}")
        
        logger.info(f"Saved {len(chunks)} chunks to {output_file}")
        return output_file


if __name__ == "__main__":
    main()
