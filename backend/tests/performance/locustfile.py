"""Locust load testing configuration for BWARM Dashboard API.

Usage:
    # Run with web UI (http://localhost:8089)
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

    # Headless mode (100 users, 10/sec spawn rate, 60s duration)
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 60s --headless

    # CSV output
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --users 500 --spawn-rate 50 --run-time 300s --headless \
           --csv=results/load_test
"""

import random
from locust import HttpUser, task, between, events


class AuthenticatedUser(HttpUser):
    """Simulates an authenticated user interacting with the API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    access_token = None
    refresh_token = None

    def on_start(self):
        """Login before starting tasks."""
        self.login()

    def login(self):
        """Authenticate and get tokens."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "admin123",
            },
            name="/api/v1/auth/login",
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")

    def get_headers(self):
        """Get authorization headers."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    @task(5)
    def get_works_list(self):
        """Get paginated works list (most common operation)."""
        page = random.randint(1, 10)
        limit = random.choice([10, 25, 50])
        
        self.client.get(
            f"/api/v1/works/?page={page}&limit={limit}",
            headers=self.get_headers(),
            name="/api/v1/works/ (list)",
        )

    @task(3)
    def get_dashboard_statistics(self):
        """Get dashboard statistics (heavily cached)."""
        self.client.get(
            "/api/v1/works/statistics",
            headers=self.get_headers(),
            name="/api/v1/works/statistics",
        )

    @task(2)
    def search_works(self):
        """Search for works."""
        search_terms = ["symphony", "concerto", "sonata", "beethoven", "mozart"]
        search = random.choice(search_terms)
        
        self.client.get(
            f"/api/v1/works/search?q={search}&limit=20",
            headers=self.get_headers(),
            name="/api/v1/works/search",
        )

    @task(2)
    def get_work_detail(self):
        """Get individual work details."""
        work_id = random.randint(1, 100)
        
        self.client.get(
            f"/api/v1/works/{work_id}",
            headers=self.get_headers(),
            name="/api/v1/works/{id}",
        )

    @task(1)
    def get_user_profile(self):
        """Get current user profile."""
        self.client.get(
            "/api/v1/auth/me",
            headers=self.get_headers(),
            name="/api/v1/auth/me",
        )

    @task(1)
    def refresh_tokens(self):
        """Refresh authentication tokens."""
        if self.refresh_token:
            response = self.client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token},
                name="/api/v1/auth/refresh",
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")


class UnauthenticatedUser(HttpUser):
    """Simulates unauthenticated users (login attempts only)."""

    wait_time = between(2, 5)

    @task
    def attempt_login(self):
        """Simulate login attempts."""
        # Mix of valid and invalid credentials
        if random.random() < 0.8:  # 80% valid
            email = "admin@example.com"
            password = "admin123"
        else:  # 20% invalid
            email = f"user{random.randint(1, 1000)}@example.com"
            password = "wrongpassword"
        
        self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
            name="/api/v1/auth/login (unauth)",
        )


class UploadUser(HttpUser):
    """Simulates users uploading catalog files."""

    wait_time = between(5, 10)  # Uploads are less frequent
    access_token = None

    def on_start(self):
        """Login before uploading."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin123"},
        )
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")

    @task
    def check_upload_status(self):
        """Check status of uploads."""
        if self.access_token:
            self.client.get(
                "/api/v1/catalog/uploads",
                headers={"Authorization": f"Bearer {self.access_token}"},
                name="/api/v1/catalog/uploads (status)",
            )


# Event handlers for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, **kwargs):
    """Track cache hits."""
    if response and hasattr(response, 'headers'):
        cache_hit = response.headers.get('X-Cache-Hit', 'false')
        if cache_hit == 'true':
            # Track cache hits (this would be logged to custom metrics)
            pass


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test configuration."""
    print("\n" + "=" * 60)
    print("BWARM Dashboard Load Test Starting")
    print("=" * 60)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if environment.runner else 'N/A'}")
    print("=" * 60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("Load Test Complete - Summary")
    print("=" * 60)
    
    stats = environment.stats
    
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Failure Rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"\nAverage Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Median Response Time: {stats.total.median_response_time:.2f}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th Percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"\nRequests per Second: {stats.total.total_rps:.2f}")
    
    print("\n" + "=" * 60 + "\n")
