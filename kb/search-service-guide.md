# Search Service Troubleshooting Guide

## Overview
This guide covers search service issues including Elasticsearch cluster health, index rebuild failures, query performance problems, and autocomplete service integration.

## Common Search Service Issues

### 1. Elasticsearch Cluster Health Degraded

**Symptoms:**
- Elasticsearch cluster health errors (ERR-9001)
- Slow search results
- Index unavailability
- Cluster state red/yellow

**Root Causes:**
- Node failures or unavailability
- Insufficient heap memory
- Disk space exhaustion
- Network partition between nodes
- Long-running GC pauses

**Solutions:**

#### Immediate Actions:
1. **Check Cluster Health**
   ```bash
   # Check cluster health
   curl -X GET "localhost:9200/_cluster/health?pretty"
   
   # Check node status
   curl -X GET "localhost:9200/_cat/nodes?v"
   
   # Check indices status
   curl -X GET "localhost:9200/_cat/indices?v"
   ```

2. **Identify Problematic Nodes**
   ```python
   from elasticsearch import Elasticsearch
   
   def analyze_cluster_health():
       es = Elasticsearch(['http://localhost:9200'])
       
       health = es.cluster.health()
       nodes = es.cluster.info()
       
       analysis = {
           'cluster_status': health['status'],
           'number_of_nodes': health['number_of_nodes'],
           'active_shards': health['active_shards'],
           'relocating_shards': health['relocating_shards'],
           'initializing_shards': health['initializing_shards'],
           'unassigned_shards': health['unassigned_shards']
       }
       
       if health['status'] == 'red':
           log.critical("Cluster in RED state - immediate action required")
       elif health['status'] == 'yellow':
           log.warning("Cluster in YELLOW state - investigation needed")
       
       return analysis
   ```

3. **Check JVM Memory Usage**
   ```bash
   # Check JVM heap usage
   curl -X GET "localhost:9200/_nodes/stats/jvm?pretty"
   
   # Look for heap usage percentage
   # If > 80%, consider increasing heap or optimizing queries
   ```

#### Long-term Solutions:
- Implement Elasticsearch cluster scaling
- Add dedicated master nodes
- Use hot-warm architecture for time-series data
- Implement cluster monitoring and alerting

### 2. Search Index Rebuild Failed

**Symptoms:**
- Index rebuild failures (ERR-9002)
- Stale search results
- Missing documents in search
- Index corruption

**Root Causes:**
- Insufficient disk space
- Memory exhaustion during rebuild
- Mapping conflicts
- Network issues during rebuild
- Corrupted source data

**Solutions:**

#### Immediate Actions:
1. **Check Disk Space**
   ```bash
   # Check disk space on Elasticsearch nodes
   df -h
   
   # Check Elasticsearch disk usage
   curl -X GET "localhost:9200/_cat/allocation?v"
   ```

2. **Implement Safe Index Rebuild**
   ```python
   from elasticsearch import Elasticsearch
   
   def safe_index_rebuild(index_name, source_data):
       es = Elasticsearch(['http://localhost:9200'])
       
       # Create new index with timestamp
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       new_index = f"{index_name}_{timestamp}"
       
       try:
           # Create new index
           es.indices.create(index=new_index, body=get_index_mapping())
           
           # Bulk index data
           success_count = bulk_index_data(es, new_index, source_data)
           
           # Update alias to point to new index
           es.indices.update_aliases(body={
               "actions": [
                   {"remove": {"index": f"{index_name}_*", "alias": index_name}},
                   {"add": {"index": new_index, "alias": index_name}}
               ]
           })
           
           # Delete old indices
           cleanup_old_indices(es, index_name, keep_last=2)
           
           return success_count
           
       except Exception as e:
           log.error(f"Index rebuild failed: {e}")
           # Cleanup failed index
           es.indices.delete(index=new_index, ignore=[404])
           raise
   ```

3. **Add Index Health Monitoring**
   ```python
   def monitor_index_health(index_name):
       es = Elasticsearch(['http://localhost:9200'])
       
       while True:
           try:
               health = es.indices.health(index=index_name)
               
               if health['status'] == 'red':
                   send_alert(f"Index {index_name} is in RED state")
                   # Attempt recovery
                   attempt_index_recovery(index_name)
               
               time.sleep(60)  # Check every minute
               
           except Exception as e:
               log.error(f"Index monitoring error: {e}")
               time.sleep(60)
   ```

#### Long-term Solutions:
- Implement incremental index updates
- Use index lifecycle management (ILM)
- Add index backup and restore procedures
- Implement index partitioning by time

### 3. Search Query Performance Degradation

**Symptoms:**
- Search query latency increased (WARN-7001)
- Slow search results
- High query execution times
- User experience degradation

**Root Causes:**
- Inefficient query patterns
- Missing or incorrect mappings
- Insufficient caching
- Complex aggregations
- Large result sets

**Solutions:**

#### Immediate Actions:
1. **Analyze Slow Queries**
   ```python
   from elasticsearch import Elasticsearch
   
   def analyze_slow_queries():
       es = Elasticsearch(['http://localhost:9200'])
       
       # Enable slow log
       es.indices.put_settings(index="_all", body={
           "index.search.slowlog.threshold.query.warn": "5s",
           "index.search.slowlog.threshold.query.info": "2s"
       })
       
       # Check slow log
       slow_logs = get_elasticsearch_logs('/var/log/elasticsearch/*.log')
       slow_queries = parse_slow_queries(slow_logs)
       
       return slow_queries
   ```

2. **Optimize Query Patterns**
   ```python
   def optimize_search_query(original_query):
       optimized_query = {
           "query": {
               "bool": {
                   "must": [
                       {"match": {"title": original_query["title"]}},
                       {"range": {"timestamp": {"gte": "now-30d"}}}
                   ]
               }
           },
           "size": 20,  # Limit result size
           "_source": ["title", "url", "timestamp"],  # Return only needed fields
           "timeout": "3s"  # Add query timeout
       }
       return optimized_query
   ```

3. **Implement Query Result Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_cached_search_results(query_hash, index_name):
       # Check cache for results
       cached_results = cache.get(f"search_{query_hash}")
       if cached_results:
           return cached_results
       
       # Execute search if not cached
       results = execute_search(query_hash, index_name)
       cache.set(f"search_{query_hash}", results, ttl=300)  # 5 minutes
       return results
   ```

#### Long-term Solutions:
- Implement query profiling and optimization
- Use appropriate analyzers and tokenizers
- Add search result pagination
- Implement search analytics and optimization

### 4. Autocomplete Service Integration Timeout

**Symptoms:**
- Autocomplete service timeout errors (ERR-9003)
- Typeahead suggestions not appearing
- Search interface degradation

**Root Causes:**
- Autocomplete service overload
- Network latency
- Inefficient autocomplete algorithms
- Large suggestion datasets

**Solutions:**

#### Immediate Actions:
1. **Implement Autocomplete Timeout Handling**
   ```python
   import concurrent.futures
   
   def get_autocomplete_suggestions_with_timeout(query, timeout=2):
       with concurrent.futures.ThreadPoolExecutor() as executor:
           future = executor.submit(get_autocomplete_suggestions, query)
           try:
               return future.result(timeout=timeout)
           except concurrent.futures.TimeoutError:
               log.warning(f"Autocomplete timeout for query: {query}")
               return get_fallback_suggestions(query)
   ```

2. **Add Autocomplete Result Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=500)
   def get_cached_autocomplete(query_prefix):
       cache_key = f"autocomplete_{query_prefix.lower()}"
       cached_suggestions = cache.get(cache_key)
       
       if cached_suggestions:
           return cached_suggestions
       
       # Generate suggestions
       suggestions = generate_autocomplete_suggestions(query_prefix)
       cache.set(cache_key, suggestions, ttl=600)  # 10 minutes
       return suggestions
   ```

3. **Implement Fallback Autocomplete**
   ```python
   def get_fallback_suggestions(query):
       # Simple prefix-based fallback
       common_prefixes = load_common_search_prefixes()
       
       suggestions = [
           prefix for prefix in common_prefixes
           if prefix.lower().startswith(query.lower())
       ][:10]  # Limit to 10 suggestions
      
       return suggestions
   ```

#### Long-term Solutions:
- Implement dedicated autocomplete service
- Use Elasticsearch completion suggester
- Add autocomplete analytics
- Implement predictive search

### 5. Search Index Synchronization Delay

**Symptoms:**
- Index sync delays (WARN-4001 from order service)
- Outdated search results
- Recently added items not appearing in search

**Root Causes:**
- Indexing backlog
- Slow indexing performance
- Network issues between services
- Bulk indexing failures

**Solutions:**

#### Immediate Actions:
1. **Check Indexing Queue Status**
   ```python
   def check_indexing_queue():
       queue_status = {
           'queue_size': get_queue_size('indexing_queue'),
           'processing_rate': get_processing_rate('indexing_queue'),
           'failed_items': get_failed_items('indexing_queue')
       }
       
       if queue_status['queue_size'] > 10000:
           send_alert("Indexing queue backlog critical")
       
       return queue_status
   ```

2. **Implement Indexing Priority Queue**
   ```python
   import heapq
   
   class PriorityIndexingQueue:
       def __init__(self):
           self.queue = []
       
       def add_indexing_task(self, task, priority):
           heapq.heappush(self.queue, (priority, task))
       
       def get_next_task(self):
           if self.queue:
               return heapq.heappop(self.queue)[1]
           return None
   ```

3. **Add Bulk Indexing Optimization**
   ```python
   from elasticsearch.helpers import bulk
   
   def optimized_bulk_index(es, index_name, documents):
       # Process in batches
       batch_size = 1000
       success_count = 0
       
       for i in range(0, len(documents), batch_size):
           batch = documents[i:i + batch_size]
           
           try:
               success, failed = bulk(es, batch, index=index_name)
               success_count += success
               
               if failed:
                   log.warning(f"Failed to index {len(failed)} documents")
                   
           except Exception as e:
               log.error(f"Bulk indexing error: {e}")
       
       return success_count
   ```

#### Long-term Solutions:
- Implement real-time indexing
- Use change data capture (CDC)
- Add index monitoring and alerting
- Implement index partitioning strategy

## Search Performance Optimization

### Key Metrics to Monitor:
- Search query latency (p50, p95, p99)
- Index refresh rate
- Cache hit ratio
- Cluster health status
- JVM heap usage
- Disk I/O performance

### Performance Tuning:
```python
# Elasticsearch optimization settings
optimization_config = {
    "index": {
        "refresh_interval": "30s",  # Reduce refresh frequency
        "number_of_shards": 3,     # Optimal shard count
        "number_of_replicas": 1    # Replication factor
    },
    "search": {
        "max_concurrent_shard_requests": 8,
        "default_search_timeout": "10s"
    }
}
```

## Search Analytics

### Query Analytics:
```python
def track_search_query(query, results_count, execution_time):
    analytics_data = {
        'query': query,
        'results_count': results_count,
        'execution_time': execution_time,
        'timestamp': datetime.now(),
        'user_id': get_current_user_id()
    }
    
    # Send to analytics service
    send_to_analytics('search_queries', analytics_data)
```

### Popular Searches:
```python
def get_popular_searches(days=7):
    es = Elasticsearch(['http://localhost:9200'])
   
    popular = es.search(index="search_analytics", body={
        "size": 10,
        "query": {
            "range": {
                "timestamp": {
                    "gte": f"now-{days}d/d"
                }
            }
        },
        "aggs": {
            "popular_queries": {
                "terms": {
                    "field": "query.keyword",
                    "size": 10
                }
            }
        }
    })
   
    return popular['aggregations']['popular_queries']['buckets']
```

## Security Considerations

### Search Security Best Practices:
1. **Implement Query Validation**
   ```python
   def validate_search_query(query):
       # Check for dangerous patterns
       dangerous_patterns = ['DROP', 'DELETE', 'UPDATE', 'INSERT']
       
       for pattern in dangerous_patterns:
           if pattern.upper() in query.upper():
               raise SecurityError(f"Potentially dangerous query pattern: {pattern}")
       
       return True
   ```

2. **Add Search Rate Limiting**
   ```python
   from ratelimit import limits, sleep_and_retry
   
   @sleep_and_retry
   @limits(calls=100, period=60)  # 100 searches per minute per user
   def perform_search(user_id, query):
       return execute_search(query)
   ```

3. **Implement Field-Level Security**
   ```python
   def apply_field_security(user, search_results):
       # Remove sensitive fields based on user permissions
       if not user.has_permission('view_internal'):
           for result in search_results:
               result.pop('internal_data', None)
               result.pop('admin_notes', None)
       
       return search_results
   ```

## Related Documentation
- [Elasticsearch Administration](../infrastructure/elasticsearch-admin.md)
- [Search Query Optimization](../performance/search-optimization.md)
- [Index Lifecycle Management](../data/index-lifecycle.md)
- [Search Analytics Guide](../analytics/search-analytics.md)