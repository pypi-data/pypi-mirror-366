from typing import Dict, Any
import requests
import os
import csv
from datetime import datetime, timedelta
import json
import logging

from pm_studio_mcp.config import config
from pm_studio_mcp.utils.data_handlers.base_handler import BaseHandler

class DataAIHandler(BaseHandler):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataAIHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key: str = None, working_dir: str = None):
        if self._initialized:
            return
            
        self.logger = logging.getLogger(__name__)
        
        self.api_key = api_key or config.DATA_AI_API_KEY
        if not self.api_key:
            raise ValueError("DATA_AI_API_KEY is missing in environment variables.")
        
        self.working_dir = working_dir or config.WORKING_PATH
        if not self.working_dir:
            raise ValueError("WORKING_PATH is missing in environment variables.")
        
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)

        self.base_url = "https://api.data.ai/v1.3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        mapping_path = os.path.join(os.path.dirname(__file__), "dataai_product_id_mapping.json")
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.product_id_map = json.load(f)

        self._initialized = True
        self.logger.info("DataAI handler initialized successfully")

    def _save_csv(self, data: list, file_path: str):
        if not data:
            return
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def _generate_date_ranges(self, start: str, end: str, window_days: int = 31):
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        ranges = []
        current_start = start_date
        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=window_days - 1), end_date)
            ranges.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
            current_start = current_end + timedelta(days=1)
        return ranges

    def get_app_metadata(self, product_id: str, market: str) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/apps/{market}/app/{product_id}/details"
        try:
            self.logger.info(f"Fetching app metadata for {product_id} in {market}")
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            app_info = data.get("product", {})
            output_file = os.path.join(self.working_dir, f"dataai_details_{market}_{product_id}.csv")
            if output_file and app_info:
                self._save_csv([app_info], output_file)
                self.logger.info(f"Saved app metadata to {output_file}")
            
            metadata_keys = list(app_info.keys()) if app_info else []
            self.logger.info(f"Retrieved {market.upper()} metadata with {len(app_info)} fields")
            
            search_stats = {
                "api_calls": 1,
                "market": market,
                "product_id": product_id,
                "metadata_fields": len(app_info),
                "metadata_keys": metadata_keys
            }
            
            debug_info = {
                "endpoint": endpoint,
                "market": market,
                "product_id": product_id,
                "output_file": output_file,
                "metadata_count": len(app_info)
            }
            
            self.logger.info(f"App metadata stats: {search_stats}")
            
            return {
                "status": "success", 
                "data_length": len(data), 
                "output_file": output_file,
                "search_stats": search_stats,
                "debug_info": debug_info
            }
        except Exception as e:
            self.logger.error(f"Error fetching app metadata for {product_id} in {market}: {str(e)}")
            debug_info = {
                "endpoint": endpoint,
                "market": market,
                "product_id": product_id,
                "error_details": str(e)
            }
            self.logger.error(f"Debug info: {debug_info}")
            return {
                "status": "error", 
                "message": str(e),
                "debug_info": debug_info
            }

    def get_all_ratings(self, product_id: str, market: str) -> Dict[str, Any]:
        all_ratings = []
        page_index = 0
        api_calls = 0
        
        try:
            self.logger.info(f"Fetching all ratings for {product_id} in {market}")
            while True:
                endpoint = f"{self.base_url}/apps/{market}/app/{product_id}/ratings"
                params = {"page_index": page_index}
                try:
                    api_calls += 1
                    self.logger.info(f"Making API call #{api_calls} for ratings (page {page_index})")
                    response = requests.get(endpoint, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    ratings = data.get("ratings", [])
                    all_ratings.extend(ratings)
                    self.logger.info(f"Retrieved {len(ratings)} ratings on page {page_index}")
                    if not data.get("next_page"):
                        self.logger.info(f"No more pages available for ratings")
                        break
                    page_index += 1
                except Exception as e:
                    self.logger.error(f"Error fetching ratings on page {page_index}: {str(e)}")
                    debug_info = {
                        "endpoint": endpoint,
                        "params": params,
                        "api_calls_made": api_calls,
                        "ratings_collected": len(all_ratings),
                        "error_details": str(e)
                    }
                    self.logger.error(f"Debug info: {debug_info}")
                    return {
                        "status": "error", 
                        "message": str(e),
                        "debug_info": debug_info
                    }
            
            output_file = os.path.join(self.working_dir, f"dataai_ratings_all_{market}_{product_id}.csv")
            if output_file and all_ratings:
                self._save_csv(all_ratings, output_file)
                self.logger.info(f"Saved {len(all_ratings)} ratings to {output_file}")
            
            self.logger.info(f"Retrieved {len(all_ratings)} total ratings for {product_id} in {market}")
            
            search_stats = {
                "api_calls": api_calls,
                "pages_retrieved": page_index + 1,
                "market": market,
                "product_id": product_id,
                "total_ratings": len(all_ratings)
            }
            
            debug_info = {
                "endpoint": endpoint,
                "market": market,
                "product_id": product_id,
                "api_calls": api_calls,
                "pages_retrieved": page_index + 1,
                "output_file": output_file
            }
            
            self.logger.info(f"Ratings stats: {search_stats}")
            
            return {
                "status": "success", 
                "data_length": len(all_ratings), 
                "output_file": output_file,
                "search_stats": search_stats,
                "debug_info": debug_info
            }
        except Exception as e:
            self.logger.error(f"Error retrieving all ratings: {str(e)}")
            debug_info = {
                "market": market,
                "product_id": product_id,
                "api_calls_made": api_calls,
                "error_details": str(e)
            }
            self.logger.error(f"Debug info: {debug_info}")
            return {
                "status": "error", 
                "message": f"Error retrieving ratings: {str(e)}",
                "debug_info": debug_info
            }

    def get_all_reviews(self, product_id: str, market: str, start_date: str, end_date: str) -> Dict[str, Any]:
        all_reviews = []
        date_ranges = self._generate_date_ranges(start_date, end_date)
        page_size = 100
        api_calls = 0
        date_ranges_processed = 0
        
        try:
            self.logger.info(f"Fetching all reviews for {product_id} in {market} from {start_date} to {end_date}")
            self.logger.info(f"Generated {len(date_ranges)} date ranges for API pagination")
            
            for date_start, date_end in date_ranges:
                date_ranges_processed += 1
                page_index = 0
                self.logger.info(f"Processing date range {date_ranges_processed}/{len(date_ranges)}: {date_start} to {date_end}")
                
                while True:
                    endpoint = f"{self.base_url}/apps/{market}/app/{product_id}/reviews"
                    params = {
                        "start_date": date_start,
                        "end_date": date_end,
                        "page_index": page_index,
                        "page_size": page_size
                    }
                    try:
                        api_calls += 1
                        self.logger.info(f"Making API call #{api_calls} for reviews (range {date_ranges_processed}/{len(date_ranges)}, page {page_index})")
                        response = requests.get(endpoint, headers=self.headers, params=params)
                        response.raise_for_status()
                        data = response.json()
                        reviews = data.get("reviews", [])
                        all_reviews.extend(reviews)
                        self.logger.info(f"Retrieved {len(reviews)} reviews on page {page_index}")
                        
                        if not data.get("next_page"):
                            self.logger.info(f"No more pages available for this date range")
                            break
                        page_index += 1
                    except Exception as e:
                        self.logger.error(f"Error fetching reviews on page {page_index} for date range {date_start} to {date_end}: {str(e)}")
                        debug_info = {
                            "endpoint": endpoint,
                            "params": params,
                            "api_calls_made": api_calls,
                            "date_ranges_processed": date_ranges_processed,
                            "reviews_collected": len(all_reviews),
                            "error_details": str(e)
                        }
                        self.logger.error(f"Debug info: {debug_info}")
                        return {
                            "status": "error", 
                            "message": str(e),
                            "debug_info": debug_info
                        }
            
            output_file = os.path.join(self.working_dir, f"dataai_reviews_all_{market}_{product_id}_{start_date}_to_{end_date}.csv")
            if output_file and all_reviews:
                self._save_csv(all_reviews, output_file)
                self.logger.info(f"Saved {len(all_reviews)} reviews to {output_file}")
            
            with_text, without_text = count_reviews_with_and_without_text(all_reviews)
            
            self.logger.info(f"Retrieved {len(all_reviews)} total reviews for {product_id} in {market}")
            self.logger.info(f"Reviews breakdown: With text: {with_text}, Without text: {without_text}")
            
            search_stats = {
                "api_calls": api_calls,
                "date_ranges": len(date_ranges),
                "market": market,
                "product_id": product_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "reviews_breakdown": {
                    "total": len(all_reviews),
                    "with_text": with_text,
                    "without_text": without_text
                }
            }
            
            debug_info = {
                "endpoint": endpoint if 'endpoint' in locals() else f"{self.base_url}/apps/{market}/app/{product_id}/reviews",
                "market": market,
                "product_id": product_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "api_calls": api_calls,
                "date_ranges_processed": date_ranges_processed,
                "output_file": output_file
            }
            
            self.logger.info(f"Reviews stats: {search_stats}")
            
            return {
                "status": "success", 
                "data_length": len(all_reviews), 
                "output_file": output_file,
                "search_stats": search_stats,
                "debug_info": debug_info
            }
        except Exception as e:
            self.logger.error(f"Error retrieving all reviews: {str(e)}")
            debug_info = {
                "market": market,
                "product_id": product_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "api_calls_made": api_calls,
                "date_ranges_processed": date_ranges_processed,
                "error_details": str(e)
            }
            self.logger.error(f"Debug info: {debug_info}")
            return {
                "status": "error", 
                "message": f"Error retrieving reviews: {str(e)}",
                "debug_info": debug_info
            }

    def get_app_timeline(self, product_id: str, market: str, start_date: str, end_date: str, event_filters: str = None) -> Dict[str, Any]:
        """
        Get timeline events for an app including version changes, screenshots, description changes, etc.
        
        Args:
            product_id (str): Product ID
            market (str): Market (ios, google-play, etc.)
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            event_filters (str, optional): Comma-separated list of event types to filter by.
                Options: app_description, size_change, icon_change, name_change, price_change, company_change, screenshot_change, version_change
        
        Returns:
            Dict containing timeline events data
        """
        all_events = []
        page_index = 0
        page_size = 30  # Max allowed by API
        api_calls = 0
        
        try:
            self.logger.info(f"Fetching timeline events for {product_id} in {market} from {start_date} to {end_date}")
            if event_filters:
                self.logger.info(f"Event filters: {event_filters}")
            
            while True:
                endpoint = f"{self.base_url}/apps/{market}/app/{product_id}/events"
                params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "page_index": page_index,
                    "page_size": page_size
                }
                
                # Add event filters if specified
                if event_filters:
                    params["event_filters"] = event_filters
                
                try:
                    api_calls += 1
                    self.logger.info(f"Making API call #{api_calls} for timeline events (page {page_index})")
                    response = requests.get(endpoint, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Check for API response code
                    if data.get("code") != 200:
                        error_message = f"API returned error code {data.get('code', 'unknown')}"
                        self.logger.error(error_message)
                        return {
                            "status": "error",
                            "message": error_message,
                            "debug_info": {
                                "endpoint": endpoint,
                                "params": params,
                                "api_response_code": data.get("code"),
                                "api_calls_made": api_calls
                            }
                        }
                    
                    events = data.get("data", [])
                    all_events.extend(events)
                    self.logger.info(f"Retrieved {len(events)} events on page {page_index}")
                    
                    # Check if there's a next page
                    pagination = data.get("pagination", {})
                    if not pagination.get("next_page"):
                        self.logger.info(f"No more pages available for timeline events")
                        break
                    page_index += 1
                    
                except Exception as e:
                    self.logger.error(f"Error fetching timeline events on page {page_index}: {str(e)}")
                    debug_info = {
                        "endpoint": endpoint,
                        "params": params,
                        "api_calls_made": api_calls,
                        "events_collected": len(all_events),
                        "error_details": str(e)
                    }
                    self.logger.error(f"Debug info: {debug_info}")
                    return {
                        "status": "error", 
                        "message": str(e),
                        "debug_info": debug_info
                    }
            
            # Process and categorize events
            event_summary = self._analyze_timeline_events(all_events)
            
            output_file = os.path.join(self.working_dir, f"dataai_timeline_{market}_{product_id}_{start_date}_to_{end_date}.csv")
            if output_file and all_events:
                # Flatten complex nested data for CSV export
                flattened_events = self._flatten_timeline_events(all_events)
                self._save_csv(flattened_events, output_file)
                self.logger.info(f"Saved {len(all_events)} timeline events to {output_file}")
            
            self.logger.info(f"Retrieved {len(all_events)} total timeline events for {product_id} in {market}")
            
            search_stats = {
                "api_calls": api_calls,
                "pages_retrieved": page_index + 1,
                "market": market,
                "product_id": product_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "event_filters": event_filters,
                "total_events": len(all_events),
                "event_types_found": list(event_summary.keys()),
                "events_by_type": event_summary
            }
            
            debug_info = {
                "endpoint": endpoint if 'endpoint' in locals() else f"{self.base_url}/apps/{market}/app/{product_id}/events",
                "market": market,
                "product_id": product_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "api_calls": api_calls,
                "pages_retrieved": page_index + 1,
                "output_file": output_file,
                "event_filters_used": event_filters
            }
            
            self.logger.info(f"Timeline events stats: {search_stats}")
            
            return {
                "status": "success", 
                "data_length": len(all_events), 
                "output_file": output_file,
                "search_stats": search_stats,
                "debug_info": debug_info,
                "event_summary": event_summary
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving timeline events: {str(e)}")
            debug_info = {
                "market": market,
                "product_id": product_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "api_calls_made": api_calls,
                "event_filters": event_filters,
                "error_details": str(e)
            }
            self.logger.error(f"Debug info: {debug_info}")
            return {
                "status": "error", 
                "message": f"Error retrieving timeline events: {str(e)}",
                "debug_info": debug_info
            }

    def _analyze_timeline_events(self, events: list) -> Dict[str, int]:
        """
        Analyze timeline events and provide summary statistics.
        
        Args:
            events (list): List of timeline events
            
        Returns:
            Dict with event type counts
        """
        event_summary = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_summary[event_type] = event_summary.get(event_type, 0) + 1
        
        return event_summary

    def _flatten_timeline_events(self, events: list) -> list:
        """
        Flatten complex timeline events for CSV export.
        
        Args:
            events (list): List of timeline events with potentially nested data
            
        Returns:
            List of flattened events suitable for CSV export
        """
        flattened = []
        for event in events:
            flattened_event = {
                "date": event.get("date"),
                "event_type": event.get("event_type"),
                "old_value": self._flatten_value(event.get("old_value")),
                "new_value": self._flatten_value(event.get("new_value")),
                "release_note": event.get("release_note", "")
            }
            flattened.append(flattened_event)
        
        return flattened

    def _flatten_value(self, value) -> str:
        """
        Flatten complex values (like screenshot changes) to string format.
        
        Args:
            value: The value to flatten (can be string, dict, or list)
            
        Returns:
            String representation of the value
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            # For complex objects like screenshot changes, create a summary
            return json.dumps(value, ensure_ascii=False)[:500] + "..." if len(json.dumps(value, ensure_ascii=False)) > 500 else json.dumps(value, ensure_ascii=False)
        elif isinstance(value, (list, tuple)):
            return str(value)[:500] + "..." if len(str(value)) > 500 else str(value)
        else:
            return str(value) if value is not None else ""

    def fetch_data(self, product_name, start_date=None, end_date=None, **kwargs):
        """
        Fetch data from Data.ai API for a given product.
        
        Args:
            product_name (str): Name of the product to fetch data for
            start_date (str or datetime, optional): Start date for data range (YYYY-MM-DD format)
            end_date (str or datetime, optional): End date for data range (YYYY-MM-DD format)
            **kwargs: Additional parameters including:
                - device (str): Platform(s) to fetch data from ("android", "ios", "all")
                - target_data_type (str): Type of data to fetch. Options:
                    * "metadata": App metadata and basic information
                    * "ratings": App ratings data
                    * "reviews": User reviews with text content
                    * "timeline": App timeline events (version changes, screenshots, etc.)
                - event_filters (str, optional): For timeline data - comma-separated event types:
                    * "app_description": Description changes
                    * "size_change": App size changes
                    * "icon_change": Icon changes
                    * "name_change": App name changes
                    * "price_change": Price changes
                    * "company_change": Publisher/company changes
                    * "screenshot_change": Screenshot changes
                    * "version_change": Version updates with release notes
                - debug (bool): Enable debug logging
        
        Returns:
            Dict with status, data_length, output_file, search_stats, and debug_info
        """
        # Unwrap nested kwargs if present (e.g., kwargs={'device': ..., ...})
        if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
            # Merge nested kwargs into the main kwargs
            nested_kwargs = kwargs.pop("kwargs")
            kwargs.update(nested_kwargs)
            self.logger.info(f"Unwrapped nested kwargs: {nested_kwargs.keys()}")

        if not product_name:
            self.logger.error("Product name is required")
            raise ValueError("Product name is required.")

        debug = kwargs.get("debug", False)
        if debug:
            self.logger.info(f"Debug mode enabled with kwargs: {kwargs}")

        # Process date parameters
        if start_date:
            if isinstance(start_date, datetime):
                start_date = start_date.strftime('%Y-%m-%d')
            elif not isinstance(start_date, str):
                self.logger.error(f"Invalid start_date format: {start_date}")
                raise ValueError(f"Invalid start_date format: {start_date}. Expected string or datetime object.")
        else:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            self.logger.info(f"Using default start_date: {start_date}")

        if end_date:
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
            elif not isinstance(end_date, str):
                self.logger.error(f"Invalid end_date format: {end_date}")
                raise ValueError(f"Invalid end_date format: {end_date}. Expected string or datetime object.")
        else:
            end_date = datetime.now().strftime('%Y-%m-%d')
            self.logger.info(f"Using default end_date: {end_date}")

        device = kwargs.get("device", "all")
        self.logger.info(f"Device parameter: {device}")
        
        if isinstance(device, str):
            platforms = [d.strip().lower() for d in device.split(",") if d.strip()]
        elif isinstance(device, (list, tuple)):
            platforms = [str(d).strip().lower() for d in device]
        else:
            platforms = ["all"]
        
        self.logger.info(f"Parsed platforms: {platforms}")

        target_data_type = kwargs.get("target_data_type", "reviews").lower()
        self.logger.info(f"Target data type: {target_data_type}")

        # Normalize platforms
        valid_platforms = set()
        for p in platforms:
            if p in ("android", "google-play"):
                valid_platforms.add("google-play")
            elif p in ("ios", "apple"):
                valid_platforms.add("ios")
            elif p == "all":
                valid_platforms.update(["google-play", "ios"])
        
        self.logger.info(f"Normalized valid platforms: {valid_platforms}")

        if not valid_platforms:
            self.logger.error(f"No valid platform specified in 'device' argument: {device}")
            raise ValueError("No valid platform specified in 'device' argument.")

        product_id_info = self.product_id_map.get(product_name)
        if not product_id_info:
            self.logger.error(f"Product name '{product_name}' not found in product_id_map")
            raise ValueError(f"Product name '{product_name}' not found in product_id_map.")

        product_id_list = []
        for platform in valid_platforms:
            pid = product_id_info.get("android") if platform == "google-play" else product_id_info.get("ios")
            if pid:
                product_id_list.append((platform, pid))
        
        self.logger.info(f"Product IDs to process: {product_id_list}")

        if not product_id_list:
            self.logger.error(f"No product IDs found for '{product_name}' and platforms {valid_platforms}")
            raise ValueError(f"No product IDs found for '{product_name}' and platforms {valid_platforms}.")

        result = []
        for _market, product_id in product_id_list:
            self.logger.info(f"Processing {target_data_type} for {product_id} in {_market}")
            
            if target_data_type == "metadata":
                res = self.get_app_metadata(product_id, _market)
            elif target_data_type == "ratings":
                res = self.get_all_ratings(product_id, _market)
            elif target_data_type == "reviews":
                res = self.get_all_reviews(product_id, _market, start_date=start_date, end_date=end_date)
            elif target_data_type == "timeline":
                event_filters = kwargs.get("event_filters", None)
                res = self.get_app_timeline(product_id, _market, start_date=start_date, end_date=end_date, event_filters=event_filters)
            else:
                self.logger.warning(f"Unknown target_data_type: {target_data_type}, skipping")
                continue
                
            result.append(res)

        date_info = {
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }

        # Create debug info that will be included in all responses
        debug_info = {
            "product_name": product_name,
            "date_range": date_info["date_range"],
            "platforms_searched": list(valid_platforms),
            "target_data_type": target_data_type,
            "product_ids": [(market, pid) for market, pid in product_id_list],
            "results_count": len(result),
            "result_details": [
                {
                    "platform": platform,
                    "product_id": pid,
                    "status": res.get("status"),
                    "data_length": res.get("data_length", 0)
                } 
                for (platform, pid), res in zip(product_id_list, result) if isinstance(res, dict)
            ]
        }
        
        self.logger.info(f"Processed {len(result)} results for {product_name}")

        if len(result) == 0:
            self.logger.warning(f"No data retrieved for {product_name}")
            return {
                "status": "error", 
                "message": "No data retrieved", 
                "debug_info": debug_info,
                "data_length": 0
            }
        elif len(result) == 1:
            self.logger.info(f"Returning single result for {product_name}")
            single_result = result[0]
            if isinstance(single_result, dict):
                single_result["date_range"] = date_info["date_range"]
                # Add debug info to single result
                single_result["debug_info"] = debug_info
                # Add search stats similar to Reddit handler
                single_result["search_stats"] = {
                    "product_name": product_name,
                    "platform": product_id_list[0][0] if product_id_list else "unknown",
                    "product_id": product_id_list[0][1] if product_id_list else "unknown",
                    "target_data_type": target_data_type,
                    "date_range": date_info["date_range"]
                }
                return single_result
            else:
                self.logger.error(f"Unexpected result format: {type(single_result).__name__}")
                return {
                    "status": "error", 
                    "message": "Unexpected result format", 
                    "debug_info": {
                        **debug_info,
                        "result_type": type(single_result).__name__
                    },
                    "data_length": 0
                }
        else:
            # Calculate total items across all results
            total_items = sum(item.get("data_length", 0) for item in result if isinstance(item, dict))
            
            self.logger.info(f"Returning multiple results for {product_name} with total items: {total_items}")
            
            # Create detailed stats for multiple results
            return {
                "status": "success",
                "message": f"Retrieved data for {len(result)} platforms",
                "results": result,
                "data_length": total_items,
                "date_range": date_info["date_range"],
                "debug_info": debug_info,
                "search_stats": {
                    "product_name": product_name,
                    "platforms": [platform for platform, _ in product_id_list],
                    "target_data_type": target_data_type,
                    "total_items": total_items,
                    "platforms_count": len(valid_platforms),
                    "results_breakdown": [
                        {
                            "platform": platform,
                            "items_count": res.get("data_length", 0),
                            "status": res.get("status", "unknown")
                        }
                        for (platform, _), res in zip(product_id_list, result) if isinstance(res, dict)
                    ]
                }
            }


def count_reviews_with_and_without_text(reviews):
    with_text = 0
    without_text = 0
    for r in reviews:
        if r.get("text"):
            with_text += 1
        else:
            without_text += 1
    return with_text, without_text


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    working_dir = os.environ.get("WORKING_DIR")

    if not working_dir:
        logger.error("WORKING_DIR is not set in environment variables")
        raise ValueError("WORKING_DIR is not set in environment variables.")
    
    api_key = os.environ.get("DATA_AI_API_KEY")
    if not api_key:
        logger.error("DATA_AI_API_KEY is not set in environment variables")
        raise ValueError("DATA_AI_API_KEY is not set in environment variables.")

    handler = DataAIHandler(api_key=api_key, working_dir=working_dir)

    app_list = [
        ("ios", "1288723196"),
        ("google-play", "20600008137685")
    ]
    
    for market, product_id in app_list:
        logger.info(f"Processing {market} with product ID {product_id}")
        handler.get_app_metadata(product_id, market)
        handler.get_all_ratings(product_id, market)
        handler.get_all_reviews(
            product_id, market,
            start_date="2024-01-01",
            end_date="2024-03-15"
        )

    app_name = "Chrome"
    logger.info(f"Testing fetch_data for {app_name}")
    
    # Test reviews data
    handler.fetch_data(
        product_name=app_name,
        start_date="2024-05-01",
        end_date="2024-06-01",
        device="all",
        target_data_type="reviews",
        debug=True
    )
    
    # Test timeline data with version changes and screenshots
    logger.info(f"Testing timeline data for {app_name}")
    handler.fetch_data(
        product_name=app_name,
        start_date="2024-01-01",
        end_date="2024-06-01",
        device="ios",  # Timeline API works better with specific platforms
        target_data_type="timeline",
        event_filters="version_change,screenshot_change,app_description",
        debug=True
    )