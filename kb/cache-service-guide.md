# Cache Service Troubleshooting Guide

## Overview
This guide covers Redis cluster issues, cache memory management, replication problems, and cache backup/recovery procedures.

## Common Cache Service Issues

### 1. Redis Cluster Node Failure

**Symptoms:**
- Redis cluster node failures (ERR-14001)
- Cache unavailability across services
- Increased database load due to cache misses

**Root Causes:**
- Hardware failures
- Network partitions
- Memory exhaustion
- Redis software bugs

**Solutions:**

#### Immediate Actions:
1. **Check Cluster Status**
   ```bash
   # Check cluster health
   redis-cli --cluster check <cluster-node>:6379
   
   # Check node status
   redis-cli -h <node-host> -p 6379 cluster nodes
   ```

2. **Identify Failed Nodes**
   ```python
   def check_redis_cluster_health():
       cluster_nodes = get_redis_cluster_nodes()
       failed_nodes = []
       
       for node in cluster_nodes:
           try:
               client = redis.Redis(host=node['host'], port=node['port'])
               client.ping()  # Test connectivity
           except redis.ConnectionError:
               failed_nodes.append(node)
               log.error(f"Redis node failed: {node['host']}:{node['port']}")
       
       return failed_nodes
   ```

3. **Failover to Replica Nodes**
   ```python
   def promote_replica_to_master(failed_master_node):
       # Find replica for failed master
       replicas = find_replicas_for_master(failed_master_node)
       
       if replicas:
           # Promote first available replica
           new_master = replicas[0]
           execute_redis_command(
               f"CLUSTER FAILOVER {new_master['host']}:{new_master['port']}"
           )
           log.info(f"Promoted {new_master['host']} to master")
           return True
       else:
           log.error("No replicas available for failover")
           return False
   ```

#### Long-term Solutions:
- Implement Redis cluster auto-failover
- Add redundant Redis nodes
- Use Redis Sentinel for high availability
- Implement cluster monitoring and alerting

### 2. Cache Eviction Policy Misconfiguration

**Symptoms:**
- Cache eviction policy errors (ERR-14002)
- Unexpected data loss from cache
- Poor cache hit rates

**Root Causes:**
- Incorrect maxmemory policy
- Insufficient memory allocation
- Inefficient key expiration policies
- Large object sizes

**Solutions:**

#### Immediate Actions:
1. **Check Current Memory Configuration**
   ```bash
   # Check memory usage
   redis-cli INFO memory
   
   # Check eviction policy
   redis-cli CONFIG GET maxmemory-policy
   ```

2. **Analyze Memory Usage Patterns**
   ```python
   def analyze_redis_memory_usage():
       client = redis.Redis(host='localhost', port=6379)
       
       # Get memory statistics
       info = client.info('memory')
       
       memory_analysis = {
           'used_memory': info['used_memory'],
           'used_memory_peak': info['used_memory_peak'],
           'used_memory_percentage': (info['used_memory'] / info['maxmemory']) * 100,
           'evicted_keys': info['evicted_keys'],
           'expired_keys': info['expired_keys']
       }
       
       return memory_analysis
   ```

3. **Optimize Eviction Policy**
   ```python
   def configure_eviction_policy():
       client = redis.Redis(host='localhost', port=6379)
       
       # Set appropriate eviction policy
       # allkeys-lru: Evict least recently used keys
       # volatile-lru: Evict LRU among keys with expire set
       client.config_set('maxmemory-policy', 'allkeys-lru')
       
       # Set memory limit (e.g., 4GB)
       client.config_set('maxmemory', '4gb')
       
       log.info("Redis eviction policy configured")
   ```

#### Long-term Solutions:
- Implement cache size monitoring
- Use appropriate data structures
- Implement cache key expiration strategies
- Consider Redis memory optimization techniques

### 3. Cache Memory Usage Critical

**Symptoms:**
- Memory usage approaching critical threshold (WARN-12001)
- Redis performance degradation
- Risk of OOM (Out of Memory) kills

**Root Causes:**
- Memory leaks in application
- Too many cached objects
- Large object sizes
- Insufficient memory limits

**Solutions:**

#### Immediate Actions:
1. **Emergency Memory Cleanup**
   ```python
   def emergency_cache_cleanup():
       client = redis.Redis(host='localhost', port=6379)
       
       # Delete specific high-memory keys
       large_keys = find_large_keys(client, size_threshold=1024*1024)  # > 1MB
       for key in large_keys:
           client.delete(key)
           log.info(f"Deleted large key: {key}")
       
       # Force eviction if needed
       if get_memory_usage_percentage() > 90:
           client.execute_command('MEMORY PURGE')
   ```

2. **Implement Memory Monitoring**
   ```python
   def monitor_cache_memory():
       client = redis.Redis(host='localhost', port=6379)
       
       while True:
           memory_info = client.info('memory')
           memory_percent = (memory_info['used_memory'] / memory_info['maxmemory']) * 100
           
           if memory_percent > 80:
               send_alert(f"Cache memory usage critical: {memory_percent}%")
           
           time.sleep(60)  # Check every minute
   ```

3. **Add Application-Level Memory Management**
   ```python
   class CacheManager:
       def __init__(self, max_memory_mb=1024):
           self.max_memory = max_memory_mb * 1024 * 1024
           self.current_memory = 0
       
       def set_with_memory_limit(self, key, value, ttl=3600):
           # Calculate memory size
           size = len(pickle.dumps(value))
           
           # Check if adding would exceed limit
           if self.current_memory + size > self.max_memory:
               self.evict_older_entries(size)
           
           # Add to cache
           cache.set(key, value, ttl=ttl)
           self.current_memory += size
   ```

#### Long-term Solutions:
- Implement automatic memory-based eviction
- Use Redis memory optimization techniques
- Add cache size limits per application
- Implement cache key lifecycle management

### 4. Cache Replication Lag

**Symptoms:**
- Replication lag between cluster nodes (ERR-14003)
- Inconsistent cache data across nodes
- Read-after-write consistency issues

**Root Causes:**
- Network latency between nodes
- High write load
- Insufficient replication bandwidth
- Replication buffer overflow

**Solutions:**

#### Immediate Actions:
1. **Check Replication Lag**
   ```bash
   # Check replication offset
   redis-cli -h <master> INFO replication
   redis-cli -h <replica> INFO replication
   ```

2. **Monitor Replication Status**
   ```python
   def check_replication_lag():
       master_client = redis.Redis(host='master', port=6379)
       replica_client = redis.Redis(host='replica', port=6379)
       
       master_offset = master_client.info()['master_repl_offset']
       replica_offset = replica_client.info()['master_repl_offset']
       
       lag = master_offset - replica_offset
       
       if lag > 10000:  # Threshold: 10K bytes
           send_alert(f"Replication lag high: {lag} bytes")
       
       return lag
   ```

3. **Optimize Replication Configuration**
   ```python
   def optimize_replication_settings():
       client = redis.Redis(host='localhost', port=6379)
       
       # Increase replication buffer
       client.config_set('repl-backlog-size', '256mb')
       
       # Reduce replication timeout
       client.config_set('repl-timeout', 30)
       
       # Enable diskless replication
       client.config_set('repl-diskless-sync', 'yes')
       
       log.info("Replication settings optimized")
   ```

#### Long-term Solutions:
- Implement Redis cluster with proper sharding
- Use Redis Sentinel for automatic failover
- Add network optimization between nodes
- Consider read replicas for read-heavy workloads

## Cache Performance Optimization

### Key Metrics to Monitor:
- Cache hit ratio
- Memory usage percentage
- Response time (latency)
- Eviction rate
- Replication lag
- Connection pool utilization

### Performance Tuning:
```python
# Redis configuration optimization
redis_config = {
    'maxmemory': '4gb',
    'maxmemory-policy': 'allkeys-lru',
    'timeout': 300,
    'tcp-keepalive': 60,
    'tcp-backlog': 511,
    'save': '',  # Disable RDB snapshots for pure cache
    'appendonly': 'no'  # Disable AOF for pure cache
}
```

## Cache Backup and Recovery

### Backup Strategy:
```python
def backup_redis_data():
    # For persistent cache data
    import subprocess
    
    # Create RDB snapshot
    subprocess.run([
        'redis-cli',
        'BGSAVE'
    ])
    
    # Copy RDB file to backup location
    shutil.copy(
        '/var/lib/redis/dump.rdb',
        f'/backup/redis/dump_{datetime.now().strftime("%Y%m%d_%H%M%S")}.rdb'
    )
```

### Recovery Procedure:
```python
def restore_redis_from_backup(backup_file):
    # Stop Redis
    subprocess.run(['systemctl', 'stop', 'redis'])
    
    # Copy backup file
    shutil.copy(backup_file, '/var/lib/redis/dump.rdb')
    
    # Start Redis
    subprocess.run(['systemctl', 'start', 'redis'])
    
    log.info(f"Redis restored from {backup_file}")
```

## Security Considerations

### Redis Security Best Practices:
1. **Enable Authentication**
   ```bash
   redis-cli CONFIG SET requirepass "strong-password"
   ```

2. **Disable Dangerous Commands**
   ```bash
   redis-cli CONFIG SET rename-command FLUSHDB ""
   redis-cli CONFIG SET rename-command FLUSHALL ""
   redis-cli CONFIG SET rename-command CONFIG ""
   ```

3. **Network Security**
   - Bind to specific interfaces only
   - Use firewall rules
   - Enable TLS for Redis connections

## Related Documentation
- [Redis Cluster Administration](../infrastructure/redis-cluster.md)
- [Cache Strategy Patterns](../patterns/caching-patterns.md)
- [Memory Optimization Guide](../performance/memory-optimization.md)
- [High Availability Architecture](../architecture/high-availability.md)