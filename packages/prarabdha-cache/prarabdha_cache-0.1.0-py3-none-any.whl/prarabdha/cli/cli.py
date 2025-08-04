import typer
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import sys

from ..chats.core import SegmentCacheManager, SegmentCacheManagerFactory, DefaultChatStrategy
from ..core.kv_store import MultiLayerKVStore
from ..core.vector_index import SemanticVectorIndex

app = typer.Typer(help="Prarabdha - Modular AI Cache System")

def create_cache_manager(redis_url: Optional[str] = None) -> SegmentCacheManager:
    """Create cache manager based on configuration"""
    if redis_url:
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
        
        # Parse Redis URL if provided
        if redis_url.startswith('redis://'):
            parts = redis_url.replace('redis://', '').split('/')
            if len(parts) > 1:
                host_port = parts[0].split(':')
                if len(host_port) > 1:
                    redis_config['host'] = host_port[0]
                    redis_config['port'] = int(host_port[1])
                else:
                    redis_config['host'] = host_port[0]
                
                if len(parts) > 1 and parts[1].isdigit():
                    redis_config['db'] = int(parts[1])
        
        return SegmentCacheManagerFactory.create_redis_manager(redis_config)
    else:
        return SegmentCacheManagerFactory.create_default_manager()

@app.command()
def ingest(
    file_path: str = typer.Argument(..., help="Path to JSON file containing chat segments"),
    redis_url: Optional[str] = typer.Option(None, "--redis", help="Redis URL (e.g., redis://localhost:6379/0)"),
    strategy: str = typer.Option("default", "--strategy", help="Caching strategy (default, high-performance)"),
    enable_rag: bool = typer.Option(True, "--rag/--no-rag", help="Enable RAG similarity search"),
    similarity_threshold: float = typer.Option(0.8, "--threshold", help="Similarity threshold for RAG"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Ingest chat segments into the cache"""
    
    # Validate file path
    if not Path(file_path).exists():
        typer.echo(f"Error: File {file_path} does not exist", err=True)
        raise typer.Exit(1)
    
    # Create cache manager
    if strategy == "high-performance":
        cache_manager = SegmentCacheManagerFactory.create_high_performance_manager()
    else:
        cache_manager = create_cache_manager(redis_url)
    
    # Configure RAG settings
    cache_manager.enable_rag = enable_rag
    cache_manager.rag_similarity_threshold = similarity_threshold
    
    # Load and process segments
    try:
        with open(file_path, 'r') as f:
            segments = json.load(f)
        
        if not isinstance(segments, list):
            segments = [segments]
        
        typer.echo(f"Processing {len(segments)} segments...")
        
        cached_count = 0
        skipped_count = 0
        
        for i, segment in enumerate(segments):
            if verbose:
                typer.echo(f"Processing segment {i+1}/{len(segments)}")
            
            cache_key = cache_manager.cache_segment(segment)
            if cache_key:
                cached_count += 1
                if verbose:
                    typer.echo(f"  Cached with key: {cache_key}")
            else:
                skipped_count += 1
                if verbose:
                    typer.echo(f"  Skipped segment")
        
        # Get final stats
        stats = cache_manager.get_stats()
        
        typer.echo(f"\nIngestion complete!")
        typer.echo(f"Cached segments: {cached_count}")
        typer.echo(f"Skipped segments: {skipped_count}")
        typer.echo(f"Total cache size: {stats.get('cache_size', 0)}")
        
        if enable_rag:
            vector_stats = stats.get('vector_index', {})
            typer.echo(f"Vector index size: {vector_stats.get('total_vectors', 0)}")
        
    except json.JSONDecodeError:
        typer.echo(f"Error: Invalid JSON in file {file_path}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error during ingestion: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def inspect(
    cache_key: Optional[str] = typer.Argument(None, help="Specific cache key to inspect"),
    redis_url: Optional[str] = typer.Option(None, "--redis", help="Redis URL"),
    format: str = typer.Option("json", "--format", help="Output format (json, table)"),
    limit: int = typer.Option(10, "--limit", help="Number of items to show")
):
    """Inspect cache contents and statistics"""
    
    cache_manager = create_cache_manager(redis_url)
    stats = cache_manager.get_stats()
    
    if cache_key:
        # Inspect specific key
        segment = cache_manager.get_segment(cache_key)
        if segment:
            if format == "json":
                typer.echo(json.dumps(segment, indent=2, default=str))
            else:
                typer.echo(f"Cache Key: {cache_key}")
                typer.echo(f"Content: {segment.get('content', 'N/A')[:100]}...")
                typer.echo(f"User ID: {segment.get('user_id', 'N/A')}")
                typer.echo(f"Session ID: {segment.get('session_id', 'N/A')}")
                typer.echo(f"Timestamp: {segment.get('timestamp', 'N/A')}")
        else:
            typer.echo(f"Cache key '{cache_key}' not found")
    else:
        # Show general statistics
        if format == "json":
            typer.echo(json.dumps(stats, indent=2, default=str))
        else:
            typer.echo("Cache Statistics:")
            typer.echo(f"  Total Requests: {stats.get('total_requests', 0)}")
            typer.echo(f"  Cache Hits: {stats.get('hits', 0)}")
            typer.echo(f"  Cache Misses: {stats.get('misses', 0)}")
            typer.echo(f"  Hit Rate: {stats.get('hit_rate', 0):.2%}")
            typer.echo(f"  Memory Size: {stats.get('memory_size', 0)}")
            typer.echo(f"  Disk Size: {stats.get('disk_size', 0)}")
            
            if stats.get('redis_available'):
                typer.echo(f"  Redis Available: Yes")
                typer.echo(f"  Redis Keys: {stats.get('total_keys', 0)}")
            
            if 'vector_index' in stats:
                vector_stats = stats['vector_index']
                typer.echo(f"  Vector Index Size: {vector_stats.get('total_vectors', 0)}")
                typer.echo(f"  Similarity Threshold: {vector_stats.get('similarity_threshold', 0)}")

@app.command()
def clear(
    redis_url: Optional[str] = typer.Option(None, "--redis", help="Redis URL"),
    confirm: bool = typer.Option(False, "--yes", help="Skip confirmation prompt")
):
    """Clear all cache data"""
    
    if not confirm:
        if not typer.confirm("Are you sure you want to clear all cache data?"):
            typer.echo("Operation cancelled")
            raise typer.Exit(0)
    
    cache_manager = create_cache_manager(redis_url)
    cache_manager.flush()
    
    typer.echo("Cache cleared successfully")

@app.command()
def stats(
    redis_url: Optional[str] = typer.Option(None, "--redis", help="Redis URL"),
    format: str = typer.Option("table", "--format", help="Output format (json, table)"),
    export: Optional[str] = typer.Option(None, "--export", help="Export stats to file")
):
    """Show detailed cache statistics"""
    
    cache_manager = create_cache_manager(redis_url)
    stats = cache_manager.get_stats()
    
    if export:
        try:
            with open(export, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            typer.echo(f"Statistics exported to {export}")
        except Exception as e:
            typer.echo(f"Error exporting stats: {e}", err=True)
            raise typer.Exit(1)
    
    if format == "json":
        typer.echo(json.dumps(stats, indent=2, default=str))
    else:
        typer.echo("Detailed Cache Statistics")
        typer.echo("=" * 50)
        
        # Performance stats
        typer.echo("\nPerformance:")
        typer.echo(f"  Total Requests: {stats.get('total_requests', 0)}")
        typer.echo(f"  Cache Hits: {stats.get('hits', 0)}")
        typer.echo(f"  Cache Misses: {stats.get('misses', 0)}")
        typer.echo(f"  Hit Rate: {stats.get('hit_rate', 0):.2%}")
        
        # Storage stats
        typer.echo("\nStorage:")
        typer.echo(f"  Memory Size: {stats.get('memory_size', 0)} items")
        typer.echo(f"  Disk Size: {stats.get('disk_size', 0)} items")
        
        if stats.get('redis_available'):
            typer.echo(f"  Redis Available: Yes")
            typer.echo(f"  Redis Keys: {stats.get('total_keys', 0)}")
            typer.echo(f"  Redis Memory: {stats.get('total_memory_bytes', 0)} bytes")
        
        # Vector index stats
        if 'vector_index' in stats:
            vector_stats = stats['vector_index']
            typer.echo("\nVector Index:")
            typer.echo(f"  Total Vectors: {vector_stats.get('total_vectors', 0)}")
            typer.echo(f"  Index Type: {vector_stats.get('index_type', 'N/A')}")
            typer.echo(f"  Dimension: {vector_stats.get('dimension', 0)}")
            typer.echo(f"  Similarity Threshold: {vector_stats.get('similarity_threshold', 0)}")

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query or content"),
    redis_url: Optional[str] = typer.Option(None, "--redis", help="Redis URL"),
    k: int = typer.Option(5, "--limit", help="Number of similar segments to return"),
    threshold: float = typer.Option(0.8, "--threshold", help="Similarity threshold"),
    format: str = typer.Option("table", "--format", help="Output format (json, table)")
):
    """Search for similar segments using RAG"""
    
    cache_manager = create_cache_manager(redis_url)
    
    # Create a query segment
    query_segment = {
        'content': query,
        'user_id': 'search_user',
        'session_id': 'search_session',
        'timestamp': int(time.time())
    }
    
    # Find similar segments
    similar_segments = cache_manager.find_similar_segments(query_segment, k)
    
    if not similar_segments:
        typer.echo("No similar segments found")
        return
    
    if format == "json":
        results = []
        for vector_id, similarity, metadata in similar_segments:
            segment = cache_manager.get_segment(metadata.get('cache_key', ''))
            results.append({
                'vector_id': vector_id,
                'similarity': similarity,
                'metadata': metadata,
                'segment': segment
            })
        typer.echo(json.dumps(results, indent=2, default=str))
    else:
        typer.echo(f"Found {len(similar_segments)} similar segments:")
        typer.echo("-" * 80)
        
        for i, (vector_id, similarity, metadata) in enumerate(similar_segments, 1):
            segment = cache_manager.get_segment(metadata.get('cache_key', ''))
            content = segment.get('content', 'N/A') if segment else 'N/A'
            
            typer.echo(f"{i}. Similarity: {similarity:.3f}")
            typer.echo(f"   Content: {content[:100]}...")
            typer.echo(f"   Cache Key: {metadata.get('cache_key', 'N/A')}")
            typer.echo()

if __name__ == "__main__":
    app()
