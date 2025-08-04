from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
import threading
import psutil
import os


class DashboardManager:
    """Manages real-time dashboard for cache monitoring."""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.websocket_connections: List[WebSocket] = []
        self.monitoring_active = False
        self.monitoring_thread = None
    
    async def connect_websocket(self, websocket: WebSocket):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.websocket_connections.append(websocket)
        
        # Send initial data
        await self.send_dashboard_data(websocket)
    
    def disconnect_websocket(self, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
    
    async def send_dashboard_data(self, websocket: WebSocket):
        """Send dashboard data to a WebSocket client."""
        try:
            data = self.get_dashboard_data()
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            print(f"Error sending dashboard data: {e}")
    
    async def broadcast_dashboard_data(self):
        """Broadcast dashboard data to all connected clients."""
        if not self.websocket_connections:
            return
        
        data = self.get_dashboard_data()
        message = json.dumps(data)
        
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.websocket_connections.remove(websocket)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_stats(),
            'cache': self.get_cache_stats(),
            'performance': self.get_performance_stats(),
            'memory': self.get_memory_stats(),
            'vectors': self.get_vector_stats()
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - psutil.boot_time()
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if hasattr(self.cache_manager, 'get_stats'):
            stats = self.cache_manager.get_stats()
        else:
            stats = {}
        
        return {
            'total_entries': stats.get('total_entries', 0),
            'hit_rate': stats.get('hit_rate', 0.0),
            'miss_rate': stats.get('miss_rate', 0.0),
            'memory_size': stats.get('memory_size', 0),
            'disk_size': stats.get('disk_size', 0),
            'redis_size': stats.get('redis_size', 0)
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if hasattr(self.cache_manager, 'get_stats'):
            stats = self.cache_manager.get_stats()
        else:
            stats = {}
        
        return {
            'total_requests': stats.get('total_requests', 0),
            'cache_hits': stats.get('cache_hits', 0),
            'cache_misses': stats.get('cache_misses', 0),
            'average_response_time': stats.get('average_response_time', 0.0),
            'requests_per_second': stats.get('requests_per_second', 0.0)
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        memory = psutil.virtual_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'cached': getattr(memory, 'cached', 0),
            'buffers': getattr(memory, 'buffers', 0)
        }
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector index statistics."""
        if hasattr(self.cache_manager, 'vector_index'):
            vector_index = self.cache_manager.vector_index
            return {
                'total_vectors': getattr(vector_index, 'total_vectors', 0),
                'index_type': getattr(vector_index, 'index_type', 'unknown'),
                'dimension': getattr(vector_index, 'dimension', 0),
                'similarity_threshold': getattr(vector_index, 'similarity_threshold', 0.8)
            }
        return {
            'total_vectors': 0,
            'index_type': 'none',
            'dimension': 0,
            'similarity_threshold': 0.8
        }
    
    def start_monitoring(self):
        """Start background monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Broadcast data every 5 seconds
                asyncio.run(self.broadcast_dashboard_data())
                time.sleep(5)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)


# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Prarabdha Cache Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-unit {
            font-size: 14px;
            color: #666;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .chart {
            width: 100%;
            height: 300px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-connected { background-color: #4CAF50; }
        .status-disconnected { background-color: #f44336; }
        .real-time-indicator {
            background-color: #4CAF50;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Prarabdha Cache Dashboard</h1>
            <p>Real-time monitoring and analytics</p>
            <div class="real-time-indicator">
                <span id="status-indicator" class="status-indicator status-disconnected"></span>
                <span id="connection-status">Disconnected</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Cache Hit Rate</div>
                <div class="stat-value" id="hit-rate">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Total Entries</div>
                <div class="stat-value" id="total-entries">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Memory Usage</div>
                <div class="stat-value" id="memory-usage">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">CPU Usage</div>
                <div class="stat-value" id="cpu-usage">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Vector Index</div>
                <div class="stat-value" id="vector-count">0</div>
                <div class="stat-unit">vectors</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Requests/sec</div>
                <div class="stat-value" id="requests-per-sec">0</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Performance Metrics</h3>
            <canvas id="performance-chart" class="chart"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>Memory Usage</h3>
            <canvas id="memory-chart" class="chart"></canvas>
        </div>
    </div>
    
    <script>
        let ws = null;
        let performanceChart = null;
        let memoryChart = null;
        let performanceData = [];
        let memoryData = [];
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                document.getElementById('status-indicator').className = 'status-indicator status-connected';
                document.getElementById('connection-status').textContent = 'Connected';
            };
            
            ws.onclose = function() {
                document.getElementById('status-indicator').className = 'status-indicator status-disconnected';
                document.getElementById('connection-status').textContent = 'Disconnected';
                setTimeout(connectWebSocket, 5000);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
        }
        
        function updateDashboard(data) {
            // Update stats
            document.getElementById('hit-rate').textContent = data.cache.hit_rate.toFixed(1) + '%';
            document.getElementById('total-entries').textContent = data.cache.total_entries;
            document.getElementById('memory-usage').textContent = data.system.memory_percent.toFixed(1) + '%';
            document.getElementById('cpu-usage').textContent = data.system.cpu_percent.toFixed(1) + '%';
            document.getElementById('vector-count').textContent = data.vectors.total_vectors;
            document.getElementById('requests-per-sec').textContent = data.performance.requests_per_second.toFixed(1);
            
            // Update charts
            updatePerformanceChart(data);
            updateMemoryChart(data);
        }
        
        function updatePerformanceChart(data) {
            const timestamp = new Date(data.timestamp);
            
            performanceData.push({
                x: timestamp,
                y: data.performance.requests_per_second
            });
            
            // Keep only last 50 points
            if (performanceData.length > 50) {
                performanceData.shift();
            }
            
            if (performanceChart) {
                performanceChart.data.datasets[0].data = performanceData;
                performanceChart.update('none');
            } else {
                const ctx = document.getElementById('performance-chart').getContext('2d');
                performanceChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Requests/sec',
                            data: performanceData,
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'second'
                                }
                            },
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        }
        
        function updateMemoryChart(data) {
            const timestamp = new Date(data.timestamp);
            
            memoryData.push({
                x: timestamp,
                y: data.memory.percent
            });
            
            // Keep only last 50 points
            if (memoryData.length > 50) {
                memoryData.shift();
            }
            
            if (memoryChart) {
                memoryChart.data.datasets[0].data = memoryData;
                memoryChart.update('none');
            } else {
                const ctx = document.getElementById('memory-chart').getContext('2d');
                memoryChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Memory Usage %',
                            data: memoryData,
                            borderColor: '#f44336',
                            backgroundColor: 'rgba(244, 67, 54, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'second'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
        }
        
        // Connect on page load
        connectWebSocket();
    </script>
</body>
</html>
"""


def create_dashboard_app(cache_manager) -> FastAPI:
    """Create FastAPI app with dashboard endpoints."""
    app = FastAPI(title="Prarabdha Dashboard")
    dashboard_manager = DashboardManager(cache_manager)
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Serve dashboard HTML."""
        return DASHBOARD_HTML
    
    @app.websocket("/ws/dashboard")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time dashboard updates."""
        await dashboard_manager.connect_websocket(websocket)
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            dashboard_manager.disconnect_websocket(websocket)
    
    @app.on_event("startup")
    async def startup_event():
        """Start monitoring on app startup."""
        dashboard_manager.start_monitoring()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop monitoring on app shutdown."""
        dashboard_manager.stop_monitoring()
    
    return app 