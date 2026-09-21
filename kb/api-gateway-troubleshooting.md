# API Gateway Troubleshooting Guide

## Overview
This guide covers API Gateway issues including circuit breaker activation, rate limiting problems, load balancer failures, and backend service connectivity issues.

## Common API Gateway Issues

### 1. Circuit Breaker Activation for Backend Services

**Symptoms:**
- Circuit breaker triggered errors (ERR-13003)
- Request failures for multiple backend services
- Service unavailability cascading through the system

**Root Causes:**
- Backend service failures or high error rates
- Network connectivity issues
- Insufficient backend service capacity
- Aggressive circuit breaker thresholds

**Solutions:**

#### Immediate Actions:
1. **Check Circuit Breaker Status**
   ```python
   def get_circuit_breaker_status(service_name):
       status = circuit_breaker_registry.get(service_name)
       return {
           'state': status.state,  # OPEN, CLOSED, HALF_OPEN
           'failure_count': status.failure_count,
           'last_failure_time': status.last_failure_time,
           'success_count': status.success_count
       }
   ```

2. **Analyze Backend Service Health**
   ```python
   def analyze_backend_health(service_name):
       health_metrics = {
           'response_time': measure_response_time(service_name),
           'error_rate': calculate_error_rate(service_name),
           'availability': check_availability(service_name),
           'throughput': measure_throughput(service_name)
       }
       return health_metrics
   ```

3. **Manual Circuit Breaker Reset (Emergency)**
   ```python
   def emergency_circuit_breaker_reset(service_name):
       circuit_breaker = circuit_breaker_registry.get(service_name)
       if circuit_breaker.state == 'OPEN':
           # Reset to CLOSED state
           circuit_breaker.reset()
           log.info(f"Emergency reset of circuit breaker for {service_name}")
   ```

#### Long-term Solutions:
- Implement adaptive circuit breaker thresholds
- Add backend service health monitoring
- Use multiple circuit breaker strategies (timeout-based, error-rate-based)
- Implement service degradation and fallback mechanisms

### 2. Rate Limiter Configuration Issues

**Symptoms:**
- Rate limiter sync failures (ERR-13001)
- Inconsistent rate limiting across instances
- Legitimate requests being blocked

**Root Causes:**
- Rate limiter configuration inconsistencies
- Distributed rate limiter synchronization issues
- Insufficient rate limit thresholds
- Rate limiter service failures

**Solutions:**

#### Immediate Actions:
1. **Check Rate Limiter Configuration**
   ```python
   def validate_rate_limiter_config():
       configs = get_all_rate_limiter_configs()
       for config in configs:
           if config['requests_per_minute'] < 10:
               log.warning(f"Suspiciously low rate limit: {config}")
           if config['burst_size'] > config['requests_per_minute'] * 2:
               log.warning(f"Burst size too high: {config}")
   ```

2. **Implement Distributed Rate Limiting**
   ```python
   import redis
   
   def check_rate_limit(user_id, endpoint, limit=100):
       redis_client = redis.Redis(host='redis-cluster')
       
       key = f"rate_limit:{user_id}:{endpoint}"
       current = redis_client.incr(key)
       
       if current == 1:
           redis_client.expire(key, 60)  # 1 minute window
       
       return current <= limit
   ```

3. **Add Rate Limiter Fallback**
   ```python
   def check_rate_limit_with_fallback(user_id, endpoint):
       try:
           return distributed_rate_limit_check(user_id, endpoint)
       except RedisError:
           # Fallback to local rate limiting
           return local_rate_limit_check(user_id, endpoint)
   ```

#### Long-term Solutions:
- Implement centralized rate limiter service
- Add rate limiter configuration versioning
- Use consistent hashing for distributed rate limiting
- Implement rate limiter analytics and optimization

### 3. Load Balancer Health Check Failures

**Symptoms:**
- Load balancer health check failures (ERR-13002)
- Traffic not reaching backend services
- Uneven load distribution

**Root Causes:**
- Backend service health endpoint failures
- Network connectivity issues
- Health check timeout misconfiguration
- Backend service overload

**Solutions:**

#### Immediate Actions:
1. **Verify Health Endpoint Configuration**
   ```python
   def validate_health_endpoints():
       services = get_all_backend_services()
       for service in services:
           try:
               response = requests.get(
                   f"{service['url']}/health",
                   timeout=5
               )
               if response.status_code != 200:
                   log.error(f"Health check failed for {service['name']}")
           except requests.exceptions.RequestException:
               log.error(f"Health check error for {service['name']}")
   ```

2. **Adjust Health Check Parameters**
   ```python
   # Load balancer configuration
   health_check_config = {
       'interval': 10,      # Check every 10 seconds
       'timeout': 5,        # 5 second timeout
       'unhealthy_threshold': 3,  # 3 failures before marking unhealthy
       'healthy_threshold': 2     # 2 successes before marking healthy
   }
   ```

3. **Implement Graceful Health Check Handling**
   ```python
   def handle_health_check(service_name):
       try:
           # Quick health check
           response = requests.get(f"http://{service_name}/health/quick", timeout=2)
           if response.status_code == 200:
               return True
       except:
           pass
       
       # Fallback to deep health check
       try:
           response = requests.get(f"http://{service_name}/health/deep", timeout=10)
           return response.status_code == 200
       except:
           return False
   ```

#### Long-term Solutions:
- Implement multiple health check tiers (quick, deep)
- Add health check result caching
- Use consistent health check endpoints across services
- Implement load balancer active-passive failover

### 4. API Version Compatibility Issues

**Symptoms:**
- API version validation failures (ERR-13004)
- Client integration errors
- Backward compatibility problems

**Root Causes:**
- Breaking API changes without versioning
- Client applications using outdated API versions
- Insufficient API version documentation
- API deprecation policies not enforced

**Solutions:**

#### Immediate Actions:
1. **Implement API Version Validation**
   ```python
   def validate_api_version(request):
       api_version = request.headers.get('API-Version', 'v1')
       supported_versions = ['v1', 'v2', 'v3']
       
       if api_version not in supported_versions:
           if is_deprecated_version(api_version):
               return send_deprecation_warning(api_version)
           else:
               raise UnsupportedVersionError(api_version)
       
       return True
   ```

2. **Add API Version Routing**
   ```python
   from flask import Flask, request
   
   app = Flask(__name__)
   
   @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
   def api_router(path):
       api_version = request.headers.get('API-Version', 'v1')
       
       # Route to appropriate version handler
       if api_version == 'v1':
           return handle_v1_request(path, request)
       elif api_version == 'v2':
           return handle_v2_request(path, request)
       else:
           return handle_latest_request(path, request)
   ```

3. **Implement API Deprecation Policy**
   ```python
   def check_api_deprecation(api_version):
       deprecation_schedule = {
           'v1': {'deprecated': '2024-01-01', 'sunset': '2024-06-01'},
           'v2': {'deprecated': '2024-12-01', 'sunset': '2025-06-01'}
       }
       
       if api_version in deprecation_schedule:
           schedule = deprecation_schedule[api_version]
           today = datetime.now().date()
           
           if today >= datetime.strptime(schedule['sunset'], '%Y-%m-%d').date():
               raise DeprecatedVersionError(api_version)
           elif today >= datetime.strptime(schedule['deprecated'], '%Y-%m-%d').date():
               send_deprecation_warning(api_version, schedule['sunset'])
   ```

#### Long-term Solutions:
- Implement semantic versioning for APIs
- Add API version compatibility testing
- Create API version migration guides
- Implement automated API version checking

## API Gateway Monitoring

### Key Metrics to Monitor:
- Request success rate
- Average response time
- Circuit breaker state changes
- Rate limiter performance
- Backend service health
- Error rates by endpoint

### Monitoring Dashboard:
```python
def get_gateway_metrics():
    return {
        'total_requests': get_total_requests(),
        'success_rate': calculate_success_rate(),
        'avg_response_time': calculate_avg_response_time(),
        'circuit_breaker_status': get_all_circuit_breaker_status(),
        'rate_limiter_stats': get_rate_limiter_stats(),
        'backend_health': get_backend_service_health()
    }
```

## Emergency Procedures

### API Gateway Complete Outage

**Steps:**
1. **Assess Impact**
   - Check which backend services are affected
   - Monitor error rates and response times
   - Identify affected user segments

2. **Implement Emergency Routing**
   ```python
   def emergency_routing(request):
       # Bypass circuit breakers temporarily
       with bypass_circuit_breakers():
           try:
               return route_to_backend(request)
           except:
               # Return cached response if available
               cached_response = cache.get(request.cache_key)
               if cached_response:
                   return cached_response
               # Return degraded response
               return degraded_response(request)
   ```

3. **Scale Backend Services**
   ```python
   def emergency_scale_service(service_name):
       current_instances = get_instance_count(service_name)
       target_instances = current_instances * 2  # Double capacity
       
       scale_service(service_name, target_instances)
       log.info(f"Emergency scaling {service_name} to {target_instances} instances")
   ```

4. **Enable Maintenance Mode (if needed)**
   ```python
   def enable_maintenance_mode():
       # Return maintenance page for all requests
       app.config['MAINTENANCE_MODE'] = True
       
       @app.before_request
       def check_maintenance():
           if app.config['MAINTENANCE_MODE']:
               if not is_authorized_maintenance_user():
                   return render_template('maintenance.html'), 503
   ```

## Performance Optimization

### API Gateway Caching Strategy:
```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@app.route('/api/products/<product_id>')
@cache.cached(timeout=300)  # 5 minutes
def get_product(product_id):
    return fetch_product_from_service(product_id)
```

### Request Compression:
```python
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Enable gzip compression
```

## Security Considerations

### API Gateway Security Best Practices:
1. **Implement rate limiting** to prevent abuse
2. **Use HTTPS** for all API communications
3. **Validate and sanitize** all input data
4. **Implement authentication** and authorization
5. **Add request signing** for sensitive operations
6. **Monitor for API abuse** and unusual patterns

### Security Headers:
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## Related Documentation
- [Circuit Breaker Pattern Implementation](../patterns/circuit-breaker.md)
- [Rate Limiting Strategies](../security/rate-limiting.md)
- [API Versioning Best Practices](../api/api-versioning.md)
- [Load Balancer Configuration](../infrastructure/load-balancer.md)