#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web Crawler Utilities for PM Studio MCP

This module implements web crawling functionality with support for:
- Multiple URL batch processing
- Detailed progress statistics
- MCP tool integration
"""

import os
import time
import asyncio
import re
import logging
import sys
import signal
import traceback
import requests
import csv  # 添加CSV模块导入
import aiohttp
import json
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
from io import StringIO
from datetime import datetime
from urllib.parse import urlparse, unquote, urljoin

# Disable logging output
logging.basicConfig(level=logging.CRITICAL)

# Global state for crawler
_crawler_state = {
    "should_exit": False,  # Signal handler flag
    "current_stats": {}    # Batch crawling statistics
}

# Helper functions for internal tracking only (no terminal output)

def _update_and_log_progress(stats):
    """Silently update crawling progress without terminal output"""
    if not stats or stats["total_urls"] <= 0:
        return
        
    # Just update the stats without any terminal output
    # This function now only serves to internally track progress
    # All terminal output code has been removed to reduce noise

def _setup_signal_handlers():
    """Set up signal handlers for graceful exit"""
    def signal_handler(sig, frame):
        # Silent exit without logging
        _crawler_state["should_exit"] = True
    
    # Register SIGINT and SIGTERM handlers
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (AttributeError, ValueError):
        # Some environments might not support signal handling
        logging.warning("Signal handling not supported in this environment")

def _check_exit_requested():
    """Check if exit was requested via signal"""
    if _crawler_state["should_exit"]:
        raise Exception("Crawling interrupted by user")

# For other loggers, still keep them silent
for logger_name in logging.root.manager.loggerDict:
    if logger_name != "__main__":
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
        logging.getLogger(logger_name).propagate = False

# Context manager to suppress stdout/stderr
@contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress all stdout and stderr output"""
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

# Try to import crawl4ai with suppressed output
with suppress_stdout_stderr():
    try:
        import crawl4ai
        # Try to disable all logging in crawl4ai
        if hasattr(crawl4ai, 'set_verbose'):
            crawl4ai.set_verbose(False)
        if hasattr(crawl4ai, 'set_logging_level'):
            crawl4ai.set_logging_level('CRITICAL')
        # Try to access and disable loggers directly
        for name in logging.root.manager.loggerDict:
            if 'crawl4ai' in name.lower():
                logging.getLogger(name).setLevel(logging.CRITICAL)
                logging.getLogger(name).propagate = False
                logging.getLogger(name).disabled = True
        CRAWL4AI_AVAILABLE = True
    except ImportError:
        CRAWL4AI_AVAILABLE = False


class CrawlerUtils:
    """Utility class for web crawling operations"""

    @staticmethod
    def _extract_from_html(html: str, url: str) -> tuple:
        """Extract main content and title from HTML"""
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else url
        
        # Try to extract main content area
        main_content_match = re.search(r'<(article|main|div\s+class="[^"]*content[^"]*")[^>]*>(.*?)</\\1>', 
                                      html, re.IGNORECASE | re.DOTALL)
        
        content_html = main_content_match.group(2) if main_content_match else html
        
        # Clean HTML
        text = re.sub(r'<script.*?</script>', '', content_html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<style.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Preserve paragraph structure
        text = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\n\1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n +', '\n', text)
        text = re.sub(r'\n+', '\n\n', text)
        
        # Create markdown content
        content = f"# {title}\n\n{text}"
        return content, text

    @staticmethod
    async def _fallback_http_get(url: str, timeout: int = 30) -> tuple:
        """Enhanced HTTP request fallback, providing more complete content extraction"""
        try:
            # Use async IO to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Execute synchronous HTTP request in thread pool
            def fetch():
                import requests
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
                return requests.get(url, timeout=timeout, headers=headers).text
                
            html = await loop.run_in_executor(None, fetch)
            
            # Use more advanced content extraction methods
            try:
                # Try to use newspaper library to extract article content (if available)
                extract_with_newspaper = await loop.run_in_executor(None, lambda: CrawlerUtils._extract_with_newspaper(html, url))
                if extract_with_newspaper and len(extract_with_newspaper[0]) > 200:
                    return extract_with_newspaper
            except:
                # If newspaper extraction fails, continue with regex method
                pass
                
            # Use regex to extract content
            return CrawlerUtils._extract_from_html(html, url)
            
        except Exception as e:
            return f"# Failed to crawl {url}\n\nError: {str(e)}", ""
            
    @staticmethod
    def _extract_with_newspaper(html: str, url: str) -> tuple:
        """Use newspaper library to extract article content"""
        try:
            from newspaper import Article
            from io import StringIO
            
            # Create Article object and use provided HTML
            article = Article(url)
            article.download_state = 2  # Set as downloaded state
            article.html = html
            article.parse()
            
            title = article.title or url
            text = article.text or ""
            
            # Create markdown content
            content = f"# {title}\n\n{text}"
            
            return content, text
        except ImportError:
            # newspaper library not available
            return "", ""
        except Exception:
            # Other errors
            return "", ""

    @staticmethod
    async def crawl_single_url(
        url: str, 
        timeout: int = 15,
        working_dir: str = "",
        return_content: bool = True
    ) -> Dict[str, Any]:
        """
        Crawl a single website URL and extract content.
        """
        # 检查URL是否指向PDF文件，如果是则跳过处理
        if url.lower().endswith('.pdf') or '.pdf?' in url.lower():
            # 创建输出文件和结果
            clean_url = url.replace('https://', '').replace('http://', '')
            clean_url = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in clean_url.split('/')[0])
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"skipped_pdf_{clean_url}_{timestamp}.md"
            
            if working_dir:
                os.makedirs(working_dir, exist_ok=True)
                output_file = os.path.join(working_dir, output_file)
                
            # 写入跳过信息到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# 已跳过PDF文件 - {url}\n\n该URL指向PDF文件，已被跳过处理。")
                
            # 返回跳过状态
            return {
                "status": "skipped",
                "message": "URL指向PDF文件，已跳过处理",
                "url": url,
                "output_file": os.path.abspath(output_file),
                "markdown_path": os.path.abspath(output_file),
                "html_path": os.path.abspath(output_file)
            }
        
        # Temporarily suppress stdout/stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        try:
            # Ensure working directory exists
            if working_dir:
                os.makedirs(working_dir, exist_ok=True)
                
            # Clean URL and create output filename
            clean_url = url.replace('https://', '').replace('http://', '')
            clean_url = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in clean_url.split('/')[0])
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"crawl_{clean_url}_{timestamp}.md"
            
            if working_dir:
                output_file = os.path.join(working_dir, output_file)
            
            # Result content variables
            content_to_write = ""
            extracted_text = ""
            
            if CRAWL4AI_AVAILABLE:
                try:
                    with suppress_stdout_stderr():
                        # Get crawler class
                        Crawler = getattr(crawl4ai, "AsyncWebCrawler", None) or getattr(crawl4ai, "WebCrawler", None)
                        
                        if Crawler:
                            async with Crawler() as crawler:
                                # Disable logging output
                                kwargs = {
                                    "url": url,
                                    "extract_content": True,
                                    "timeout": timeout,
                                    "show_progress": False,
                                    "verbose": False
                                }
                                
                                if hasattr(crawler, "set_verbose"):
                                    crawler.set_verbose(False)
                                
                                # Pass necessary parameters to get more complete content
                                result = await crawler.arun(**kwargs)
                                
                                # Extract markdown content - using more complete extraction logic
                                if hasattr(result, 'markdown') and result.markdown:
                                    content_to_write = result.markdown
                                    extracted_text = result.text if hasattr(result, 'text') else ""
                                elif hasattr(result, 'content') and result.content:
                                    content_to_write = f"# Content from {url}\n\n{result.content}"
                                    extracted_text = result.content
                                elif hasattr(result, 'text') and result.text:
                                    content_to_write = f"# Content from {url}\n\n{result.text}"
                                    extracted_text = result.text
                                elif hasattr(result, 'html') and result.html:
                                    # If only HTML is available, try to extract the main content
                                    content_to_write, extracted_text = CrawlerUtils._extract_from_html(result.html, url)
                        else:
                            # Use crawl function directly, add more parameters for more complete content
                            result = await crawl4ai.crawl(
                                url,
                                extract_content=True,
                                timeout=timeout
                            )
                            
                            # Same content extraction logic as above
                            if hasattr(result, 'markdown') and result.markdown:
                                content_to_write = result.markdown
                                extracted_text = result.text if hasattr(result, 'text') else ""
                            elif hasattr(result, 'content') and result.content:
                                content_to_write = f"# Content from {url}\n\n{result.content}"
                                extracted_text = result.content
                            elif hasattr(result, 'text') and result.text:
                                content_to_write = f"# Content from {url}\n\n{result.text}"
                                extracted_text = result.text
                            elif hasattr(result, 'html') and result.html:
                                content_to_write, extracted_text = CrawlerUtils._extract_from_html(result.html, url)
                    
                except Exception:
                    # Use requests as fallback method
                    content_to_write, extracted_text = await CrawlerUtils._fallback_http_get(url, timeout)
            else:
                # When crawl4ai is not available, use fallback method
                content_to_write, extracted_text = await CrawlerUtils._fallback_http_get(url, timeout)
                
            # When content is empty or only contains links, use fallback method
            if not content_to_write.strip() or ("Links:" in content_to_write and len(content_to_write.split("\n")) < 5):
                content_to_write_fallback, extracted_text_fallback = await CrawlerUtils._fallback_http_get(url, timeout)
                
                # Only use fallback content when original is empty or contains fewer lines
                if not content_to_write.strip() or content_to_write.count("\n") < content_to_write_fallback.count("\n"):
                    content_to_write = content_to_write_fallback
                    extracted_text = extracted_text_fallback
                  # Save file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content_to_write)
                
            result = {
                "status": "success",
                "pages_crawled": 1,
                "summary_file": os.path.abspath(output_file),
                "output_file": os.path.abspath(output_file),
                "content": content_to_write,
                "extracted_text": extracted_text,
                "markdown_path": os.path.abspath(output_file),
                "html_path": os.path.abspath(output_file)
            }            
            if not return_content:
                print(f"DEBUG: Clearing content in single URL result because return_content=False")
                result["content"] = ""
                result["extracted_text"] = ""
            
            return result
                
        except Exception as e:
            # Handle error case
            error_content = f"# Error crawling {url}\n\n```\n{str(e)}\n```"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(error_content)
                
            return {
                "status": "error",
                "message": f"Error crawling website: {str(e)}",
                "url": url,
                "output_file": os.path.abspath(output_file),
                "markdown_path": os.path.abspath(output_file)
            }
        finally:
            # Restore stdout/stderr
            sys.stdout, sys.stderr = old_stdout, old_stderr

    @staticmethod
    async def crawl_website(
        url: str, 
        max_pages: int = 5, 
        timeout: int = 15, 
        selectors: Optional[List[str]] = None,
        working_dir: str = "",
        deep_crawl: Optional[str] = None,
        question: Optional[str] = None,
        return_content: bool = True,
        save_json_summary: bool = False
    ) -> Dict[str, Any]:
        """
        Crawl a website and extract content. Supports multiple URLs separated by pipe (|).
        
        Args:
            url: URL or URLs separated by | character to crawl, or path to a CSV file containing URLs
            max_pages: Maximum number of pages to crawl per URL
            timeout: Timeout in seconds for each request
            selectors: CSS selectors to extract specific content
            working_dir: Directory to save output files
            deep_crawl: Strategy for deep crawling ('bfs' or 'dfs')
            question: Specific question for LLM extraction or enhanced crawling mode
            return_content: If False, 'content' and 'extracted_text' will be empty in the returned dict.
            save_json_summary: 是否保存JSON资源汇总文件，默认为False
            
        Returns:
            Dictionary with crawl results and status
        """
        # 检查是否为增强模式（CSS样式）
        if question and CrawlerUtils._is_enhanced_crawl_request(question):
            return await CrawlerUtils._crawl_enhanced_mode(url, timeout, working_dir, question, save_json_summary)
        
        # 检查是否为CSV文件路径
        if url.lower().endswith('.csv') and os.path.exists(url):
            return await CrawlerUtils.crawl_from_csv(url, timeout, working_dir, return_content)
            
        # 以下为原有代码逻辑
        # Check if url contains multiple URLs separated by pipe (|)
        # Also handle URL-encoded pipe (%7C or %7c)
        url = unquote(url)  # Decode URL-encoded characters
        
        # Split by pipe if it exists
        urls = [u.strip() for u in url.split('|') if u.strip()]
          # If no valid URLs found, treat as a single URL (may have been encoding issue)
        if not urls:
            urls = [url]
        
        # 多URL时自动设置return_content=False以避免大模型token超限
        if len(urls) > 1:
            print(f"DEBUG: 检测到多URL请求 ({len(urls)}个URL)，自动设置return_content=False")
            return_content = False
        
        # If only one URL, use the simpler method
        if len(urls) == 1:
            return await CrawlerUtils.crawl_single_url(urls[0], timeout, working_dir, return_content)
        
        # For multiple URLs, use batch processing with progress tracking
        return await CrawlerUtils.crawl_multiple_urls(urls, timeout, working_dir, return_content)

    @staticmethod
    async def crawl_from_csv(
        csv_file_path: str,
        timeout: int = 15,
        working_dir: str = "",
        return_content: bool = False  # 默认为False以避免token超限
    ) -> Dict[str, Any]:
        """
        从CSV文件中读取URL列表并进行抓取。
        
        Args:
            csv_file_path: CSV文件的绝对路径，文件中每行一个URL
            timeout: 每个请求的超时时间（秒）
            working_dir: 保存输出文件的目录
            return_content: 如果为False，返回的字典中'content'和'extracted_text'将为空
            
        Returns:
            包含抓取结果和状态的字典
        """
        # 检查CSV文件是否存在
        if not os.path.exists(csv_file_path):
            return {
                "status": "error",
                "message": f"CSV文件不存在: {csv_file_path}"
            }
            
        # 从CSV文件读取URL
        urls = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if row and row[0].strip():
                        urls.append(row[0].strip())
        except Exception as e:
            return {
                "status": "error",
                "message": f"读取CSV文件失败: {str(e)}"
            }
            
        # 如果没有找到有效的URL
        if not urls:
            return {
                "status": "error",
                "message": "CSV文件中没有找到有效的URL"
            }
            
        # 使用现有的多URL抓取功能
        result = await CrawlerUtils.crawl_multiple_urls(urls, timeout, working_dir, False)
        
        # 添加CSV源文件信息
        result["csv_source"] = os.path.abspath(csv_file_path)
        
        return result

    @staticmethod
    async def crawl_multiple_urls(
        urls: List[str],
        timeout: int = 15,
        working_dir: str = "",
        return_content: bool = True
    ) -> Dict[str, Any]:
        """
        Crawl multiple URLs in sequence with detailed progress tracking.
        
        Args:
            urls: List of URLs to crawl
            timeout: Timeout in seconds for each request
            working_dir: Directory to save output files
            return_content: If False, 'content' and 'extracted_text' will be empty in the returned dict.
            
        Returns:
            Dictionary with combined results and statistics
        """
        # Set up signal handling for graceful exit
        _setup_signal_handlers()
        
        # Ensure working directory exists
        if working_dir:
            os.makedirs(working_dir, exist_ok=True)
        
        # Initialize statistics
        stats = {
            "start_time": time.time(),
            "total_urls": len(urls),
            "processed_urls": 0,
            "successful_urls": 0,
            "failed_urls": 0,
            "results": []
        }
          # Store stats in global state to allow sharing across functions
        _crawler_state["current_stats"] = stats
        
        # Just initialize progress tracking without any output
        _update_and_log_progress(stats)
        
        for url in urls:
            try:
                # Check if exit was requested
                _check_exit_requested()
                
                # Crawl this URL without logging
                result = await CrawlerUtils.crawl_single_url(url, timeout, working_dir, return_content)
                
                # Store result
                stats["results"].append(result)
                
                # Update statistics
                if result.get("status") == "success":
                    stats["successful_urls"] += 1
                elif result.get("status") == "skipped":
                    # 已跳过的PDF不计入失败数
                    stats["processed_urls"] += 1  # 将计数提前到这里避免重复计数
                    # 跳过后面的统计更新
                    continue
                else:
                    stats["failed_urls"] += 1
                
            except Exception as e:
                # Silently record failure without terminal output
                stats["failed_urls"] += 1
                
                # Create error file for this URL
                try:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    clean_url = url.replace('https://', '').replace('http://', '')
                    clean_url = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in clean_url.split('/')[0])
                    error_file = f"error_{clean_url}_{timestamp}.md"
                    
                    if working_dir:
                        error_file = os.path.join(working_dir, error_file)
                        
                    with open(error_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Error crawling {url}\n\n```\n{str(e)}\n```")
                        
                    # Add error result
                    stats["results"].append({
                        "status": "error",
                        "message": f"Error crawling website: {str(e)}",
                        "url": url,
                        "output_file": os.path.abspath(error_file),
                        "markdown_path": os.path.abspath(error_file)
                    })
                except:
                    pass
                    
            # Update stats
            stats["processed_urls"] += 1
            # Track progress silently
            _update_and_log_progress(stats)
        
        # Complete statistics
        stats["end_time"] = time.time()
        stats["total_time"] = stats["end_time"] - stats["start_time"]
        
        # List all result files
        result_files = []
        for result in stats["results"]:
            if result.get("status") == "success" and "markdown_path" in result:
                result_files.append(result["markdown_path"])
          # Return summary result without generating combined file
        result = {
            "status": "success" if stats["successful_urls"] > 0 else "partial_success" if stats["successful_urls"] > 0 else "error",
            "total_urls": stats["total_urls"],
            "successful_urls": stats["successful_urls"],
            "failed_urls": stats["failed_urls"],
            "total_time_seconds": stats["total_time"],
            "individual_results": stats["results"],
            "result_files": result_files,
            "markdown_path": result_files[0] if result_files else ""
        }          # 如果不返回内容，清空individual_results中的content和extracted_text
        if not return_content:
            print(f"DEBUG: Clearing content because return_content=False")
            for item in result["individual_results"]:
                if "content" in item:
                    item["content"] = ""
                if "extracted_text" in item:
                    item["extracted_text"] = ""
                    
        return result

    @staticmethod
    def _is_enhanced_crawl_request(question: str) -> bool:
        """判断是否为增强抓取请求（CSS）"""
        if not question:
            return False

        question_lower = question.lower()
        css_keywords = ["css", "样式", "style", "stylesheet"]

        has_css = any(keyword in question_lower for keyword in css_keywords)

        return has_css

    @staticmethod
    async def _crawl_enhanced_mode(url: str, timeout: int, working_dir: str, question: str, save_json_summary: bool = False) -> Dict[str, Any]:
        """增强模式：同时抓取内容和CSS
        
        Args:
            url: 要抓取的URL
            timeout: 超时时间（秒）
            working_dir: 保存文件的工作目录
            question: 抓取相关的问题/指令
            save_json_summary: 是否保存JSON资源汇总文件，默认为False
        """
        try:
            # 确保工作目录存在
            if working_dir:
                os.makedirs(working_dir, exist_ok=True)

            # 生成基础文件名
            clean_url = url.replace('https://', '').replace('http://', '')
            clean_url = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in clean_url.split('/')[0])
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_name = f"{clean_url}_{timestamp}"

            # 先抓取基础内容
            standard_result = await CrawlerUtils.crawl_single_url(url, timeout, working_dir, True)
            
            if standard_result["status"] != "success":
                return standard_result

            # 获取HTML内容用于CSS提取
            html_content = await CrawlerUtils._get_html_content(url, timeout)
            
            # 提取CSS样式
            css_result = await CrawlerUtils._extract_css_styles(url, html_content, working_dir, base_name)
            
            # 生成资源汇总
            assets_summary = {
                "url": url,
                "timestamp": timestamp,
                "markdown_file": standard_result.get("output_file", ""),
                "css_file": css_result.get("css_file", ""),
                "css_info": css_result
            }
            
            # 根据开关决定是否保存JSON汇总文件
            assets_file = ""
            if save_json_summary:
                assets_file = os.path.join(working_dir, f"assets_summary_{base_name}.json")
                with open(assets_file, 'w', encoding='utf-8') as f:
                    json.dump(assets_summary, f, indent=2, ensure_ascii=False)

            # 构建增强结果
            enhanced_result = standard_result.copy()
            
            # 检查CSS抓取是否成功并添加用户提示
            user_notice = ""
            if css_result.get("css_file", "") or css_result.get("css_content", "").strip():
                user_notice = """
✅ CSS抓取成功完成！

💡 使用建议：
   • 配合网站截图使用，让AI mock效果更佳
   • CSS样式 + 页面截图 = 1+1>2 的协同效果
   • 可用于本地页面模拟、UI复现、设计参考等场景
────────────────────────────────────────
"""
                # 打印用户提示到控制台，确保能被看到
                print("\n" + user_notice.strip() + "\n")
            
            # 构建明显成功消息，确保CSS提示信息显眼
            success_message = f"🎉 网站爬取完成！\n"
            success_message += f"📄 内容文件: {standard_result.get('output_file', '未知')}\n"
            if css_result.get("css_file", ""):
                success_message += f"🎨 CSS文件: {css_result.get('css_file', '')}\n"
                # 将CSS成功提示直接放在主消息最前面，确保大模型能看到
                if user_notice.strip():
                    success_message = user_notice.strip() + "\n\n" + success_message
            
            enhanced_result.update({
                "css_file": css_result.get("css_file", ""),
                "css_content": css_result.get("css_content", ""),
                "assets_summary": assets_file if save_json_summary else "",
                "enhanced_mode": True,
                "css_info": css_result,
                "user_notice": user_notice.strip(),
                "message": success_message
            })

            return enhanced_result

        except Exception as e:
            return {
                "status": "error",
                "message": f"Enhanced crawl failed: {str(e)}",
                "url": url
            }

    @staticmethod
    async def _get_html_content(url: str, timeout: int) -> str:
        """获取页面HTML内容"""
        try:
            if CRAWL4AI_AVAILABLE:
                with suppress_stdout_stderr():
                    Crawler = getattr(crawl4ai, "AsyncWebCrawler", None) or getattr(crawl4ai, "WebCrawler", None)
                    if Crawler:
                        async with Crawler() as crawler:
                            result = await crawler.arun(
                                url=url,
                                timeout=timeout,
                                show_progress=False,
                                verbose=False
                            )
                            if hasattr(result, 'html') and result.html:
                                return result.html
            
            # 回退到requests
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(
                url, 
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            ))
            return response.text
            
        except Exception:
            return ""

    @staticmethod
    async def _extract_css_styles(url: str, html: str, working_dir: str, base_name: str) -> Dict[str, Any]:
        """提取CSS样式"""
        result = {
            "inline_styles": "",
            "external_css": [],
            "css_content": "",
            "css_file": ""
        }

        if not html:
            return result

        try:
            # 1. 提取内联样式
            style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
            result["inline_styles"] = "\n".join(style_matches)

            # 2. 提取外部CSS链接
            css_links = re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']', html, re.IGNORECASE)

            # 3. 下载外部CSS文件
            external_css_content = ""
            for css_url in css_links:
                if not css_url.startswith('http'):
                    css_url = urljoin(url, css_url)
                result["external_css"].append(css_url)

                try:
                    css_content = await CrawlerUtils._download_css_file(css_url)
                    external_css_content += f"\n/* From: {css_url} */\n{css_content}\n"
                except Exception as e:
                    external_css_content += f"\n/* Failed to load: {css_url} - {str(e)} */\n"

            # 4. 合并所有CSS
            result["css_content"] = result["inline_styles"] + "\n" + external_css_content

            # 5. 保存CSS文件
            if result["css_content"].strip():
                css_file = os.path.join(working_dir, f"styles_{base_name}.css")
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(result["css_content"])
                result["css_file"] = css_file

        except Exception as e:
            result["error"] = f"CSS extraction failed: {str(e)}"

        return result

    @staticmethod
    async def _download_css_file(css_url: str) -> str:
        """下载CSS文件内容"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(css_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception:
            pass
        return ""
