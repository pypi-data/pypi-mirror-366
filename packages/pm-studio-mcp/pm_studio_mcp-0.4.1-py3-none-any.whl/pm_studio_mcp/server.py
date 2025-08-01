from mcp.server.fastmcp import FastMCP
import asyncio
import os
from typing import List, Dict, Optional, Union
from pm_studio_mcp.utils.file_utils import FileUtils
from pm_studio_mcp.utils.web.search import SearchUtils
from pm_studio_mcp.utils.data_visualization_utils import SimpleDataViz
from pm_studio_mcp.utils.graph.chat import ChatUtils
from pm_studio_mcp.utils.graph.calendar import CalendarUtils
from pm_studio_mcp.utils.graph.mail import MailUtils
from pm_studio_mcp.utils.greeting import GreetingUtils
from pm_studio_mcp.utils.titan.titan_metadata_utils import TitanMetadataUtils
from pm_studio_mcp.utils.web.crawl import CrawlerUtils
from pm_studio_mcp.utils.titan.titan_query_utils import TitanQuery
from pm_studio_mcp.utils.data_handlers.product_insights_orchestrator import ProductInsightsOrchestrator
from pm_studio_mcp.config import config
import logging
from pm_studio_mcp.utils.graph.channel import ChannelUtils
from pm_studio_mcp.utils.publish.publish_utils import PublishUtils

# Create MCP server instance with uppercase log level
logging.basicConfig(level=logging.INFO)
mcp = FastMCP("pm-studio-mcp")

# All business logic and tool functions below, use config.XXX directly for configuration.
# For example: config.WORKING_PATH, config.REDDIT_CLIENT_ID, config.DATA_AI_API_KEY, etc.

@mcp.tool()
async def get_pm_studio_guide(name: str, intent: str = "default"):  # this is the one of the tool of my MCP server
    """
    Get a PM Studio system prompt when user send a greeting or ask for help.
    Get a PM Studio workflow guide when user want to perform a PM task, for example, product research, user feedback analysis, competitor analysis, data analysis, mission review, information gathering etc.
    DO not invoke when user wants to run a their own customized prompt or workflow.
    
    Args:
        name (str): User's name for personalization
        intent (str): Specific intent to customize the prompt for.
                     Options: "feedback_analysis", "competitor_analysis", "data_analysis", "mission_review", "default"
                     - "default": General PM Studio guide with lightweight workflow descriptions
                     - "feedback_analysis": user feedback analysis, user verbatim analysis, feedback sentiment analysis, feedback summarization
                     - "competitor_analysis": Full competitor analysis, information gathering, SWOT analysis, market research, industry analysis  
                     - "data_analysis": Full Titan data analysis, metrics analysis, data insights
                     - "mission_review": Mission statement review, cycle planning
    """
    return GreetingUtils.get_pm_studio_guide(name, intent)

@mcp.tool()
async def google_web_tool(keywords: List[str], num_results: int = 10):
    """
    Perform a Google web search with the given keywords and return search result URLs.

    Args:
        keywords: List of search keywords
        num_results: Number of search results to return (default: 10)

    Returns:
        Dict containing:
            - status: "success" or "error"
            - query: Original search query
            - results: List of search result URLs (when successful)
            - message: Error message (when failed)

    Notes:
        - Uses an improved retry mechanism to handle network issues
        - Automatically retries failed requests up to max_retries times
    """
    return SearchUtils.search_google(keywords, num_results)


@mcp.tool()
async def convert_to_markdown_tool(file_path: str):
    """
    Convert a document (doc/excel/ppt/pdf/images/csv/json/xml) to markdown format using MarkItDown.

    Args:
        file_path (str): Path to the input document file

    Returns:
        str: Path to the generated markdown file or error message
    """
    return FileUtils.convert_to_markdown_tool(file_path, config.WORKING_PATH)

# The following function `scrape_reddit_tool` is commented out because it is not currently in use.
# It is intended for future implementation or debugging purposes. If no longer needed, consider removing it.

@mcp.tool()
async def crawl_website_tool(
    url: str, 
    max_pages: int = 5, 
    timeout: int = 15, 
    selectors: Optional[List[str]] = None,
    deep_crawl: Optional[str] = None, 
    question: Optional[str] = None
):
    """
Crawl web page content from given URLs and output as markdown file.

Special Modes:
- For CSS extraction, use question parameter like:
  "extract css" or "抓取样式"
- This will capture page content and CSS styles
- ONLY SINGLE URL supported for CSS extraction mode, multiple URLs or CSV file not supported

Args:    url (str): URL source in one of these formats:
        - Single URL: "https://example.com"
        - Multiple URLs (≤5): Pipe-separated list "url1|url2|url3"
        - Multiple URLs (strongly recommended for >5): Path to ONE SINGLE CSV file containing URLs (one URL per line, no header)
    max_pages (int): Maximum number of pages to crawl (default: 5)
    timeout (int): Timeout in seconds for each request (default: 15)
    selectors (List[str], optional): CSS selectors to extract specific content
    deep_crawl (str, optional): Strategy for deep crawling ('bfs' or 'dfs')
    question (str, optional): Special instructions for enhanced crawling:
        - "extract css": Captures CSS styles, single URL only
        - "抓取样式": Same as above, for Chinese users
        - Normal text: Uses for content-specific extraction

Returns:
    dict: Dictionary with crawl results and status including path to output files
    
Enhanced Returns (when in CSS mode):
    dict: Dictionary with extended results including:
        - markdown_path: Standard markdown content
        - css_path: Extracted CSS styles file
        - assets_summary: Summary of extracted assets

Notes:
    - For >5 URLs and NOT FOR CSS extraction, CSV format is strongly recommended for better reliability
    - CSV file should contain one URL per line with no header row, only ONE SINGLE csv file is necessary
    """
    # Usage examples:
    # 1. Single URL:
    #    url = "https://example.com"
    # 2. Multiple URLs (pipe-separated):
    #    url = "https://site1.com|https://site2.com|https://site3.com"
    # 3. ONE SINGLE CSV file (strongly recommended for >5 URLs):
    #    url = "/path/to/urls.csv"  # CSV format: one URL per line, no header
    try:
        result = await CrawlerUtils.crawl_website(
            url=url,
            timeout=timeout,
            working_dir=config.WORKING_PATH,
            selectors=selectors,
            deep_crawl=deep_crawl,
            question=question
        )
        return result
    except Exception as e:
        import time
        error_file = os.path.join(config.WORKING_PATH, f"error_{int(time.time())}.md")
        with open(error_file, 'w') as f:
            f.write(f"# Error crawling {url}\n\n{str(e)}")
            
        return {
            "status": "error",
            "message": f"Failed to crawl website: {str(e)}",
            "url": url,
            "output_file": error_file,
            "markdown_path": error_file
        }

#@mcp.tool()
#async def login():
#   """
#    start authentication process against MSAL.
#
#    Returns:
#        bool: True if authentication is not needed, False otherwise
#    """
#    return AuthUtils().login()


@mcp.tool()
async def send_message_to_chat_tool(chat_type: str, chat_name: str, message: str, message_content_path: str = None, user_index: int = None, image_path: str = None):
    """
    Send a message to a private Teams chat (not for public team channels).
    This tool is ONLY for private conversations:
        - One-on-one chats with colleagues
        - Small group chats outside of formal teams
        - Self-chat (sending messages to yourself)

    DO NOT use this tool for sending messages to public team channels. For that purpose, use send_message_to_channel_tool instead.

    Send a note to Teams chat, it can be a group chat, a self chat or a oneOnOne chat.
    when type is "person", it will search for the person in your Teams contacts and send the message to the matched person.
    When multiple users match the name, prompt matched items in the chat for user to choose.
    
    Args:
        chat_type (str): The type of chat to send the message to. Can be
            * "myself"  - Self chat, send message to yourself
            * "group"-  Group chat, send message to a group chat
            * "person" - One-on-one chat with a person
        chat_name (str): The name of the chat
            * if type is "myself", it's optinal"
            * if type is "group", it's the name of the group chat
            * if type is "person", it's the name of the person to chat with, when multiple users match the name, pls show the matched list and DO ask user to select which one is the correct one to send, make sure don't send to some user directly for multiple matches case.
        message (str): The message to send.
        message_content_path (str, optional): Path to a file containing the message content. If provided, the content of the file will be used as the message.
        user_index (int, optional): If multiple users match the name, this is the index of the user to select (1-based).
        image_path (str, optional): path of the image file to send instead of (or along with) the text message.
   
    Returns:
        dict: Dictionary containing status and response data
    """

    if message_content_path:
        # If a content file is provided, read its content
        try:
            with open(message_content_path, 'r', encoding='utf-8') as f:
                message = f.read()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read content file: {str(e)}"
            }


    response = ChatUtils.send_message_to_chat(chat_type, chat_name, message, user_index=user_index, image_path=image_path)

    if response.get("status") == "multiple_matches" and response.get("users"):
            return {
                "status": "multiple_matches",
                "users": response.get("users", []),
                "message": f"Multiple users match the name '{chat_name}'. Please choose one from the following list:\n\n",
                "requires_user_input": True
            }
    else:
        return response
   


@mcp.tool()
async def send_message_to_channel_tool(channel_info: dict, message: str):
    """
    Send a message to a public Teams channel within a team (not for private chats).
    
    This tool is ONLY for sending messages to official Teams channels that exist within a team workspace.
    DO NOT use this tool for:
    - Private one-to-one chats (@mentions to individuals)
    - Group chats outside of a formal team
    - Self chats (sending messages to yourself)
    
    Args:
        channel_info (dict): Dictionary containing one of the following:
            - 'team_name' and 'channel_name': e.g. {"team_name": "Marketing Team", "channel_name": "General"}
            - 'team_id' and 'channel_id': For direct API references
            - 'channel_url': Full URL to the channel
        message (str): The message content (supports HTML and @mentions)
    
    For private chats or group conversations, use send_message_to_chat_tool instead.
    
    Returns:
        dict: Response status and details
    """
    return ChannelUtils.send_message_to_channel(channel_info, message)

@mcp.tool()
async def get_calendar_events(start_date: str, end_date: str):
    """
    get the calendar events from Microsoft Graph API.
    Args:
        start_date: Start date in ISO format withh Beijing timezone, e.g. 2023-10-01T00:00:00+08:00
        end_date: End date in ISO format withh Beijing timezone, e.g. 2023-10-31T23:59:59+08:00
    Returns:
        dict: Dictionary containing status and response data    """
    return CalendarUtils.get_calendar_events(start_date, end_date)

@mcp.tool()
async def send_mail_tool(to_recipients: List[str], subject: str, body: str, is_html: bool = False):
    """
    Send an email using Microsoft Graph API.
    
    Args:
        to_recipients (List[str]): List of email addresses to send to
        subject (str): Email subject
        body (str): Email body content
        is_html (bool, optional): Whether the body content is HTML format. Defaults to False.
        
    Returns:
        dict: Dictionary containing status and response data with keys:
            - status: "success" or "error"
            - message: Status message or error details
    """
    return MailUtils.send_mail(to_recipients, subject, body, is_html)

@mcp.tool()
async def generate_data_visualization(visualization_type: str, data_source: str, chart_options: Dict):
    """
    🎯 Simple Data Visualization Tool - Generates PNG image files only
    
    ⚠️ IMPORTANT: This tool ONLY generates PNG format image files, NOT for HTML files!
    
    Args:
        visualization_type: Chart type ('bar', 'line', 'pie', 'scatter')
            - 'line': Line chart, suitable for time series data and trend display (preferred)
            - 'bar': Bar chart, suitable for categorical data comparison
            - 'pie': Pie chart, suitable for proportion/share data
            - 'scatter': Scatter plot, only for correlation analysis between two variables
        data_source: Absolute path to CSV file (must be a CSV file)
        chart_options: Chart options dictionary
            - title (optional): Chart title
            - filename (optional): Output filename, must end with .png
            
    Returns:
        dict: Result dictionary containing:
            - success: bool - Whether successful
            - output_path: str - Absolute path to generated PNG image file
            - message: str - Status message
            - chart_type: str - Actual chart type used
            
    Output format: Generates high-quality PNG image files (300 DPI), saved in working_dir directory
    """
    try:
        # Force ensure PNG image generation
        viz = SimpleDataViz()
        
        # Ensure filename ends with .png
        if 'filename' in chart_options and chart_options['filename']:
            if not chart_options['filename'].endswith('.png'):
                chart_options['filename'] = chart_options['filename'].rsplit('.', 1)[0] + '.png'
        
        result = viz.generate_chart(
            chart_type=visualization_type,
            data_source=data_source,
            **chart_options
        )
        
        # Additional validation: ensure output path is PNG file
        if result.get('success') and result.get('output_path'):
            if not result['output_path'].endswith('.png'):
                result['message'] += " Warning: Output file is not PNG format!"
            else:
                result['message'] += f" PNG image saved to: {result['output_path']}"
        
        return result
    
    except Exception as e:
        return {"success": False, "message": f"Error generating PNG visualization: {str(e)}"}

@mcp.tool()
async def titan_query_data_tool(query_str: str, table: str):
    """
    Query data from Titan API and save results to a CSV file.
    
    ⚠️ CRITICAL TIME RANGE HANDLING REQUIREMENT ⚠️
    >>> ALL "RECENT" TIME QUERIES MUST ADD 3 EXTRA DAYS FOR DATA DELAYS <<<
    * For "recent week"/"last 7 days" use (current_date - 10 days) to (current_date - 1)
    * For "recent month"/"last month" use (current_date - 33 days) to (current_date - 1)
    * This rule is MANDATORY for ALL time-series data queries with keywords like "last 7 days", "recent", "last week", "past" etc.
    
    Applicable Scenarios:
    - Retrieving product core metrics (e.g., DAU, MAU, DAD, BSoM, Minutes)
    - Analyzing internal system structured data
    - Querying data with precise date ranges and parameter filtering
    
    Not Applicable For:
    - Analyzing user sentiment feedback
    - Collecting app store reviews
    - Social media user discussion analysis
    
    Examples:
    - Querying Edge Browser, or Edge Mac, or Edge Mobile, or CN AI Browser (like Doubao or Quark) daily active users (or DAU, DAD, BSoM, Minutes) for the last 30 days
    - Analyzing product usage duration and retention rate
    """
    try:
        titan_query = TitanQuery(
            titan_endpoint=config.TITAN_ENDPOINT,
        )
        result = titan_query.query_data_from_titan_tool(
            query_str=query_str,
            table=table,
            output_dir=config.WORKING_PATH
        )
        return result
    except Exception as e:
        return {
            "error": str(e)
        }

@mcp.tool()
async def titan_search_table_metadata_tool(table_name: str):
    """
    Search for SQL templates based on template name or description keyword.
    This tool performs exact and fuzzy matching on SQL templates.

    Applicable Scenarios:
    - Finding pre-defined SQL templates
    - Discovering available core metric query templates
    - Exploring data structure and field information
    
    Not Applicable For:
    - Directly retrieving data (must be used with titan_query_data_tool)
    - Searching for user feedback or comments
    - Finding unstructured data
    
    Examples:
    - Searching for "DAU, DAD, BSoM, Minutes, etc" related templates
    - Finding query templates for "RETENTION" metrics
    
    Args:
        table_name (str): Template name or keyword (e.g., "mac_dau", "retention by browser")

    Returns:
        dict: Dictionary containing search results
            - status: Search status ("success" or "error")
            - message: Status message with summary of found templates
            - template_matches: List of matching templates with their table info:
                - table: Table name containing the template
                - template: Template name
                - description: Template description
                - table_description: Table description
                - filter_columns: Filter configurations
            - result_path: Path to the saved JSON file (if templates found)
    """
    return TitanMetadataUtils.find_templates_tool(table_name, config.WORKING_PATH)

@mcp.tool()
async def titan_generate_sql_from_template_tool(template_name: str, filter_values: dict = None):
    """
    Generate SQL query from a template with provided filter values.
    This tool generates executable SQL by replacing placeholders in the template with provided filter values.
    
    ⚠️ CRITICAL TIME RANGE HANDLING REQUIREMENT ⚠️
    >>> ALL "RECENT" TIME QUERIES MUST ADD 3 EXTRA DAYS FOR DATA DELAYS <<<
    * For "recent week"/"last 7 days" use (current_date - 10 days) to (current_date - 1)
    * For "recent month"/"last month" use (current_date - 33 days) to (current_date - 1)
    * This rule is MANDATORY for ALL time-series data queries with keywords like "last 7 days", "recent", "last", "past" etc.
    
    Applicable Scenarios:
    - Generating executable SQL queries from templates
    - Customizing queries for specific products and time ranges
    - Retrieving structured data without writing complete SQL queries
    
    Not Applicable For:
    - Directly executing queries (must be used with titan_query_data_tool)
    - Processing unstructured data
    - Sentiment analysis and user feedback collection
    
    Examples:
    - Generating SQL to query Edge Browser, or Edge Mac, or Edge Mobile, or CN AI Browser (like Doubao or Quark, etc) DAU for the last 30 days
    - Creating RETENTION queries with date filtering conditions
    
    Args:
        template_name (str): Name of the SQL template to use (obtained from search_table_metadata_tool)
        filter_values (dict, optional): Dictionary of filter values to apply to the template.
            Keys should match the filter column names in the template.
            If not provided, default values will be used where available.

    Returns:
        dict: Dictionary containing:
            - status: "success", "error", or "warning"
            - message: Status message
            - sql: Generated SQL query (if successful)
            - template_info: Original template information
            - filter_values: Applied filter values (including default values)
            - used_default_values: Dictionary of values that used defaults (if any)
            - remaining_filters: List of optional filters that were not provided (if warning)
    """
    return TitanMetadataUtils.generate_sql_from_template(
        template_name=template_name,
        filter_values=filter_values
    )

@mcp.tool()
async def fetch_product_insights(product_name: str, goal: str = "user_sentiment", start_date: str = None, end_date: str = None, target_platforms: Union[List[str], str] = None, **kwargs):
    """
    MCP tool to fetch product insights from appropriate sources based on goal and target platforms.
    
    Applicable Scenarios:
    - Analyzing user sentiment and feedback for products
    - Gathering app store reviews and ratings
    - Monitoring social media discussions about products
    - Tracking customer perception across multiple platforms
    
    Not Applicable For:
    - Retrieving product core metrics (DAU, MAU, etc.)
    - Analyzing internal system structured data
    - Querying data with precise numerical metrics
    
    Examples:
    - Analyzing user sentiment for Microsoft Edge in the past 3 months
    - Collecting app store reviews for Edge iOS or Android app
    - Monitoring Twitter discussions about browser features
    - Comparing user feedback across Reddit and app stores

    Args:
        product_name (str): The product or service name to analyze (e.g., "Microsoft Edge", "Chrome", "Brave", "DuckDuckGo" etc.)
        goal (str): Insight goal. Options include:
            - "user_sentiment": User sentiment and feedback analysis
            - "campaign_analysis": Marketing campaign performance analysis
            - "product_update": Product update and feature analysis
            - "release_notes": Application release notes and version history (uses Timeline API)
            - "chrome_release_notes": Chrome-specific release notes
            - "firefox_release_notes": Firefox-specific release notes  
            - "edge_release_notes": Microsoft Edge-specific release notes
            - "timeline": Application timeline events and changes
            - "version_history": Version change history
            - Any goal containing "release", "version", "update", or "timeline" will automatically use Timeline API
        start_date (str, optional): Start date for data in format 'YYYY-MM-DD'. Defaults to 3 months ago if not provided.
        end_date (str, optional): End date for data in format 'YYYY-MM-DD'. Defaults to current date if not provided.
        target_platforms (Union[List[str], str], optional): One or more platforms to target (currently supports "reddit", "data ai", "unwrap ai"). Can be a single string or a list of strings. Defaults to None, which means all platforms will be considered. If twitter or X is mentioned, then use "unwrap ai"
        kwargs: Additional parameters for specific handlers 
            - keywords (List[str]): List of keywords for filtering data for Reddit
            - sources: Simple list of sources to filter by for Unwrap AI (e.g., ["reddit", "twitter", "gplay", "appstore"])
            - group_filters (List[Dict]): Group filter objects for Unwrap AI filtering by group membership
                Example: [{"group": [{"id": 11764027}], "filterCondition": "OR"}]
            - subreddit_name (str): Name of the subreddit to search for Reddit (default: "all")
            - post_limit (int): Maximum number of posts to retrieve for Reddit
            - time_filter (str): Time filter for Reddit posts
            - device (str): Device to analyze ("ios", "android", "desktop", "all") for DataAI
            - target_data_type (str): Type of data to fetch ("reviews", "ratings", "metadata", "timeline") for DataAI
            - event_filters (str): Event filters for Timeline API ("version_change", "screenshot_change", etc.)
            - sources (List[str]): List of sources to filter by for Unwrap AI (e.g., ["reddit", "twitter", "gplay", "appstore"])
            - fetch_all (bool): Whether to fetch all entries with pagination for Unwrap AI (default: False)
            - customer_id (str): Customer ID for Google Ads API (optional, if not provided, will use the first client ID under the manager account)

    Returns:
        dict: Dictionary containing fetched insights from relevant platforms
    """

    # Initialize the orchestrator as a module-level singleton
    product_insights_orchestrator = ProductInsightsOrchestrator()

    # Process inputs and initialize result structure
    platforms_to_process = []
    
    if target_platforms:
        # Handle both string and list inputs for target_platforms
        if isinstance(target_platforms, str):
            platforms_to_process = [target_platforms]
        else:
            platforms_to_process = target_platforms
    else:
        # If no specific platforms provided, use None to get default behavior
        platforms_to_process = [None]
    
    # Initialize consistent result structure
    result = {
        "goal": goal,
        "product": product_name,
        "date_range": f"{start_date} to {end_date}" if start_date and end_date else "default range",
        "platforms_processed": platforms_to_process if platforms_to_process != [None] else ["auto-selected"],
        "platform_results": {},
        "platform_statuses": {},
        "combined_results": []
    }
    
    # Process each platform (or default if None)
    for platform in platforms_to_process:
        # Delegate the work to the orchestrator for each platform
        platform_result = product_insights_orchestrator.fetch_insights(
            product_name=product_name,
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            target_platform=platform,
            **kwargs
        )
        
        # Track which platforms were actually used (may differ from input if platform=None)
        platform_key = platform if platform else "auto-selected"
        result["platform_results"][platform_key] = platform_result
        
        # Track the status of each platform
        platform_status = platform_result.get("status", "unknown")
        result["platform_statuses"][platform_key] = platform_status
        
        # Add to combined results list
        if "results" in platform_result and platform_result["results"]:
            result["combined_results"].extend(platform_result["results"])
    
    # Determine overall status based on individual platform statuses
    statuses = result["platform_statuses"].values()
    
    if all(status == "success" for status in statuses):
        result["status"] = "success"
        result["message"] = f"Successfully fetched insights from all {len(platforms_to_process)} platform(s)"
    elif all(status in ["error", "failure"] for status in statuses):
        result["status"] = "error"
        result["message"] = f"Failed to fetch insights from any platform"
    elif any(status in ["error", "failure"] for status in statuses):
        result["status"] = "partial_success"
        success_count = sum(1 for status in statuses if status == "success")
        result["message"] = f"Successfully fetched insights from {success_count} out of {len(platforms_to_process)} platform(s)"
    elif any(status == "warning" for status in statuses):
        result["status"] = "warning"
        result["message"] = f"Fetched insights with warnings from some platform(s)"
    else:
        result["status"] = "unknown"
        result["message"] = f"Fetched insights with mixed or unknown statuses"
    
    # Add summary information
    result["total_results_count"] = len(result["combined_results"])
    
    return result

@mcp.tool()
async def publish_html_to_github_pages_tool(html_file_path: str, image_paths: Optional[List[str]] = None):
    """
    Publish local HTML file and associated images to reports branch and return GitHub Pages access link.
    
    The tool automatically analyzes the HTML file to detect image references (img src attributes)
    and places uploaded images at the corresponding paths to maintain correct relative references.
    
    Args:
        html_file_path (str): Local HTML file path
        image_paths (List[str], optional): List of image file paths to upload. Images will be
            automatically placed at paths that match their references in the HTML file.
        
    Returns:
        dict: Contains status, url, message
        
    Examples:
        - If HTML contains: <img src="charts/revenue.png" />
          And image_paths includes: ["/local/path/revenue.png"]
          Then revenue.png will be uploaded to: charts/revenue.png
          
        - If HTML contains: <img src="assets/images/logo.jpg" />
          And image_paths includes: ["/local/path/logo.jpg"]  
          Then logo.jpg will be uploaded to: assets/images/logo.jpg
          
        - If an image is not referenced in HTML, it will be placed in assets/images/ as fallback
        
    Notes:
        - Supports relative paths in HTML (e.g., "images/chart.png", "assets/logo.jpg")
        - Skips external URLs (http://, https://, data:, etc.)
        - Automatically creates necessary directories
        - Supports common image formats: jpg, jpeg, png, gif, svg, webp, etc.
    """
    import asyncio
    import time
    loop = asyncio.get_running_loop()
    try:
        start = time.time()
        print(f"[DEBUG] [start] Publishing HTML file: {html_file_path}", flush=True)
        url = await loop.run_in_executor(
            None,
            lambda: PublishUtils.publish_html(html_file_path, image_paths)
        )
        print(f"[DEBUG] [done] PublishUtils.publish_html finished in {time.time()-start:.2f}s", flush=True)
        message = f"HTML report published to GitHub Pages: {url}"
        if image_paths:
            message += f"\nUploaded {len(image_paths)} image(s) to assets/images/"
        print(f"[DEBUG] [return] Returning success result", flush=True)
        return {
            "status": "success",
            "url": url,
            "message": message
        }
    except Exception as e:
        print(f"[DEBUG] [error] Exception: {e}", flush=True)
        return {
            "status": "error",
            "message": str(e)
        }

def serve():
    mcp.run(transport='stdio')
