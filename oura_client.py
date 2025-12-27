"""
Oura Ring API Client
Fetches sleep and activity data from the Oura Ring API v2
"""

import requests
from datetime import datetime, timedelta
from typing import Optional


class OuraClient:
    """Client for interacting with the Oura Ring API v2"""
    
    BASE_URL = "https://api.ouraring.com"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request to the Oura API"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_daily_sleep(self, start_date: str, end_date: str) -> dict:
        """
        Get daily sleep scores and contributors
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing sleep data with scores and contributors
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/daily_sleep", params)
    
    def get_sleep_periods(self, start_date: str, end_date: str) -> dict:
        """
        Get detailed sleep period data including heart rate, HRV, etc.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing detailed sleep period data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/sleep", params)
    
    def get_daily_activity(self, start_date: str, end_date: str) -> dict:
        """
        Get daily activity scores and metrics
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing activity data with scores and metrics
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/daily_activity", params)
    
    def get_daily_readiness(self, start_date: str, end_date: str) -> dict:
        """
        Get daily readiness scores and recovery metrics
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing readiness data with scores and contributors
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/daily_readiness", params)
    
    def get_daily_stress(self, start_date: str, end_date: str) -> dict:
        """
        Get daily stress data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing stress and recovery time data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/daily_stress", params)
    
    def get_workouts(self, start_date: str, end_date: str) -> dict:
        """
        Get workout data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing workout data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/workout", params)
    
    def get_sleep_time(self, start_date: str, end_date: str) -> dict:
        """
        Get recommended sleep time/bedtime window
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing recommended bedtime data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._make_request("v2/usercollection/sleep_time", params)
    
    def get_todays_data(self) -> dict:
        """
        Get today's sleep data (last night's sleep) and yesterday's activity data.
        
        Oura assigns sleep to the day you WAKE UP, so at 10am on Dec 27th:
        - Sleep data: Dec 27th (the sleep you just woke up from, night of Dec 26-27)
        - Activity data: Dec 26th (yesterday's full day of activity)
        
        Returns:
            Dict containing sleep and activity data
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        data = {
            "date": today,
            "activity_date": yesterday,
            "fetched_at": datetime.now().isoformat(),
            "daily_sleep": None,
            "sleep_periods": None,
            "daily_activity": None,
            "daily_readiness": None,
            "daily_stress": None,
            "workouts": None,
            "sleep_time": None
        }
        
        # Sleep data: today (the sleep you woke up from this morning)
        try:
            data["daily_sleep"] = self.get_daily_sleep(today, tomorrow)
        except requests.exceptions.RequestException as e:
            data["daily_sleep"] = {"error": str(e)}
        
        try:
            data["sleep_periods"] = self.get_sleep_periods(today, tomorrow)
        except requests.exceptions.RequestException as e:
            data["sleep_periods"] = {"error": str(e)}
        
        # Readiness is based on last night's sleep, so it's today
        try:
            data["daily_readiness"] = self.get_daily_readiness(today, tomorrow)
        except requests.exceptions.RequestException as e:
            data["daily_readiness"] = {"error": str(e)}
        
        # Activity data: yesterday (full day of activity)
        try:
            data["daily_activity"] = self.get_daily_activity(yesterday, today)
        except requests.exceptions.RequestException as e:
            data["daily_activity"] = {"error": str(e)}
        
        try:
            data["daily_stress"] = self.get_daily_stress(yesterday, today)
        except requests.exceptions.RequestException as e:
            data["daily_stress"] = {"error": str(e)}
        
        try:
            data["workouts"] = self.get_workouts(yesterday, today)
        except requests.exceptions.RequestException as e:
            data["workouts"] = {"error": str(e)}
        
        try:
            data["sleep_time"] = self.get_sleep_time(yesterday, today)
        except requests.exceptions.RequestException as e:
            data["sleep_time"] = {"error": str(e)}
        
        return data


if __name__ == "__main__":
    # Quick test
    import os
    from dotenv import load_dotenv
    import json
    
    load_dotenv()
    token = os.getenv("OURA_ACCESS_TOKEN")
    
    if token:
        client = OuraClient(token)
        data = client.get_yesterdays_data()
        print(json.dumps(data, indent=2))
    else:
        print("No OURA_ACCESS_TOKEN found in environment")

