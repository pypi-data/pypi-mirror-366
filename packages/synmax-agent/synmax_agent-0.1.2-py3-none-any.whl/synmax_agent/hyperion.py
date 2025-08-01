import os
import httpx
import cbor2
import pickle
import time
from io import BytesIO
from pathlib import Path
import pandas as pd

# get access token from environment variable
access_token = os.environ.get("ACCESS_TOKEN", None)
if access_token:
    print(f"✅ ACCESS_TOKEN loaded from environment (length: {len(access_token)})")
else:
    print("❌ ACCESS_TOKEN not found in environment variables")
    print("💡 Make sure your .env file contains: ACCESS_TOKEN=your_token_here")

class ChatClient:
    def __init__(self, access_token=None, local=False, session_id=None):
        # Initialize session state
        self.session_id = session_id
        
        # Configure URL
        if local:
            self.base_url = "http://localhost:8000"
        else:
            self.base_url = "https://hyperion-dwa-1050800409605.us-central1.run.app"
        
        # Configure access token
        if access_token:
            self.access_token = access_token
        else:
            self.access_token = os.environ.get("ACCESS_TOKEN", None)
            
        if self.access_token is None:
            raise ValueError(
                "ACCESS_TOKEN not provided. "
                "Pass it to ChatClient() or set ACCESS_TOKEN environment variable."
            )
        
        # Set up HTTP client configuration (moved from chat method)
        self.headers = {"Access-Key": self.access_token}
        
        # Configure timeout settings for streaming operations
        self.timeout = httpx.Timeout(
            connect=10.0,   # Time to establish connection
            read=600.0,     # Longer read timeout that resets on data
            write=10.0,     # Time to write data
            pool=10.0       # Time to get connection from pool
        )
        
        # Create reusable HTTP client
        self.httpclient = httpx.Client(headers=self.headers, timeout=self.timeout)
        
    def _handle_response(self, response):
        """Handle common response errors, especially 401 authentication errors"""
        if response.is_error:
            print(f"Error response from server. Status code: {response.status_code}")
            if response.status_code == 401:
                print("🔐 Authentication Error: Your access token is invalid or expired.")
                return False  # Indicates error was handled
        return True  # Indicates no error or error should be raised
    
    def _get(self, url, **kwargs):
        """Wrapper for GET requests with built-in error handling"""
        response = self.httpclient.get(url, **kwargs)
        if not self._handle_response(response):
            return None
        response.raise_for_status()
        return response
    
    def _stream(self, method, url, **kwargs):
        """Wrapper for streaming requests with built-in error handling"""
        stream = self.httpclient.stream(method, url, **kwargs)
        # For streaming, we check errors when entering the context
        return stream

    def download_dataset(self, dataset_id):
        url = self.base_url + "/download_dataset"
        params = {"dataset_id": dataset_id, "session_id": self.session_id}
        response = self._get(url, params=params)
        if response is None:  # 401 error handled
            return None

        return pd.read_parquet(BytesIO(response.content))
    
    def list_datasets(self):
        # Build URL with proper parameter handling
        url = self.base_url + "/list_datasets"
        params = {}
        if self.session_id is not None:
            params["session_id"] = self.session_id
        else:
            print("This is a new session, no datasets have been added yet")
            return []
            
        # Use regular request for simple JSON response (not streaming)
        response = self._get(url, params=params)
        if response is None:  # 401 error handled
            return []

        # Parse and pretty-print JSON response
        import json
        data = response.json()
        
        # print the datasets
        if isinstance(data, list):
            print(f"\nFound {len(data)} datasets:")
            for i, dataset in enumerate(data, 1):
                print(f"\n{i}. {dataset.get('dataset_name', 'Unnamed Dataset')}")
                if isinstance(dataset, dict):
                    for key, value in dataset.items():
                        if key != 'dataset_name':  # Don't repeat the dataset name
                            print(f"   {key}: {value}")
                print("--------------------------------")
        
        return data
    
    def list_charts(self):
        # Check if session_id is available (required by server)
        if self.session_id is None:
            print("This is a new session, no charts have been added yet")
            return []
            
        # Build URL with proper parameter handling
        url = self.base_url + "/list_charts"
        params = {"session_id": self.session_id}  # session_id is required
            
        # Use regular request for simple JSON response (not streaming)
        response = self._get(url, params=params)
        if response is None:  # 401 error handled
            return []

        # Parse and pretty-print JSON response
        import json
        data = response.json()
        
        # print the charts
        if isinstance(data, list):
            if len(data) == 0:
                print("📭 No charts found in this session")
            else:
                print(f"\nFound {len(data)} charts:")
                for i, chart in enumerate(data, 1):
                    chart_id = chart.get('chart_id', chart.get('id', 'Unknown'))
                    print(f"\n{i}. Chart ID: {chart_id}")
                    print(f"   Title: {chart.get('title', 'Untitled Chart')}")
                    print(f"   Type: {chart.get('chart_type', 'Unknown')}")
                    print(f"   Created: {chart.get('created_at', 'Unknown')}")
                    print(f"   Updated: {chart.get('updated_at', 'Unknown')}")
                    print(f"   File ID: {chart.get('file_id', 'Unknown')}")
                    
                    # Show other chart properties
                    excluded_keys = {'file_id', 'chart_id', 'id', 'title', 'chart_type', 'created_at', 'updated_at'}
                    for key, value in chart.items():
                        if key not in excluded_keys and value is not None:
                            print(f"   {key}: {value}")
                    print("--------------------------------")
        
        return data
    
    def chat(self, prompt):
        """Send a chat message responses are printed and saved to class instance"""
        params = {"prompt": prompt}
        
        if self.session_id is not None:
            params["session_id"] = self.session_id
            print(f"📤 Sending request WITH session_id: {self.session_id}")

        responsedata = {}
        
        # Track last activity time for timeout management
        last_activity_time = time.time()
        max_idle_time = 300.0  # 5 minutes of no activity before giving up
        
        with self._stream(
                "POST",
                self.base_url + "/generate",
                json=params,
                ) as response:
            if not self._handle_response(response):
                return  # 401 error handled
            response.raise_for_status()
            
            # Accumulate all bytes first, then parse CBOR messages
            accumulated_bytes = b""
            
            for chunk in response.iter_bytes():
                # Reset activity timer whenever we receive ANY data
                last_activity_time = time.time()
                
                accumulated_bytes += chunk
                
                # Try to parse complete CBOR messages from accumulated bytes
                buffer = BytesIO(accumulated_bytes)
                processed_bytes = 0
                
                while True:
                    try:
                        # Save position before attempting to read
                        start_pos = buffer.tell()
                        
                        # Try to load one CBOR item
                        item = cbor2.load(buffer)
                        
                        # Successfully parsed an item, update processed bytes
                        processed_bytes = buffer.tell()
                        
                        # Reset activity timer whenever we parse a complete CBOR item
                        last_activity_time = time.time()
                        
                        # Process the CBOR item
                        tag = item[0]
                        value = item[1]
                        match tag:
                            case 0: # session id
                                old_session_id = self.session_id
                                self.session_id = value
                                if old_session_id != self.session_id:
                                    print(f"🔄 Created New Session ID: {self.session_id}")
                            case 1: # message
                                print(value)
                            case 2: # structured data
                                responsedata[value] = item[2]
                                # Save to class instance as well
                                setattr(self, value, item[2])
                            case 3: # structured pickle
                                unpickled_data = pickle.loads(item[2])
                                responsedata[value] = unpickled_data
                                # Save to class instance as well
                                setattr(self, value, unpickled_data)
                                
                    except EOFError:
                        # Not enough bytes for a complete CBOR item, break and wait for more data
                        break
                    except Exception as e:
                        # Other CBOR parsing error, break and wait for more data
                        print(f"CBOR parsing error: {e}")
                        break
                
                # Remove processed bytes from accumulated buffer
                if processed_bytes > 0:
                    accumulated_bytes = accumulated_bytes[processed_bytes:]
                
                # Check if we've been idle too long (as a safety net)
                current_time = time.time()
                if current_time - last_activity_time > max_idle_time:
                    print(f"\n⚠️  No activity for {max_idle_time} seconds, stopping...")
                    break
    
    def reset_session(self):
        """Reset the session ID to start a new conversation"""
        old_session_id = self.session_id
        self.session_id = None
        print(f"🔄 Session reset: {old_session_id} -> None")

    def download_chart(self, chart_id, save_path=None):
        """
        Download a chart by chart_id and save to file
        
        Args:
            chart_id (int): The chart ID to download
            save_path (str): Optional path to save the file. Defaults to project root directory.
            
        Returns:
            str: Path to saved file
        """
        # Use current directory as default save path
        if save_path is None:
            save_path = "."
        if not chart_id:
            raise ValueError("chart_id must be provided")
            
        url = self.base_url + "/download_chart"
        params = {"session_id": self.session_id, "chart_id": chart_id}
            
        response = self._get(url, params=params)
        if response is None:  # 401 error handled
            return None
        
        # Get filename from response headers or generate default
        content_disposition = response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        else:
            # Fallback filename
            extension = ".png"  # Default
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type:
                extension = ".jpg"
            elif 'svg' in content_type:
                extension = ".svg"
            filename = f"chart_{chart_id}{extension}"
        
        chart_bytes = response.content
        
        # Save to specified path
        import os
        import subprocess
        import platform
        
        if os.path.isdir(save_path):
            # If save_path is a directory, append filename
            file_path = os.path.join(save_path, filename)
        else:
            # Use save_path as the full file path
            file_path = save_path
            
        with open(file_path, 'wb') as f:
            f.write(chart_bytes)
        print(f"📊 Chart saved to: {file_path}")
        
        # Automatically open the saved file
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
                
            print(f"🖼️ Chart opened with default viewer")
            
        except Exception as e:
            print(f"⚠️ Could not auto-open chart: {e}")
            print(f"💡 Manually open: {file_path}")
        
        return file_path

if __name__ == "__main__":
    # Create a persistent chat client
    # chat_client = ChatClient(local=True, session_id="session_20250620_193719")
    chat_client = ChatClient(local=True)

    # question = input("\nEnter a question: ")
    question = "show me a map of all haynesville DUCs"      
    chat_client.chat(question)
                

