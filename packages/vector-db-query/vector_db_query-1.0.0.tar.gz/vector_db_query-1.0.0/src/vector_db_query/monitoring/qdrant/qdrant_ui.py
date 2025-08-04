"""
Qdrant management UI component.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import json
import numpy as np

from .manager import get_qdrant_manager
from .models import (
    CollectionConfig, CollectionInfo, CollectionStatus,
    PointData, SearchRequest, Distance, IndexType,
    OptimizationStatus
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class QdrantManagementUI:
    """
    Qdrant vector database management UI.
    """
    
    def __init__(self):
        """Initialize Qdrant management UI."""
        self.manager = get_qdrant_manager()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'qdrant_selected_collection' not in st.session_state:
            st.session_state.qdrant_selected_collection = None
        if 'qdrant_search_results' not in st.session_state:
            st.session_state.qdrant_search_results = []
        if 'qdrant_active_operations' not in st.session_state:
            st.session_state.qdrant_active_operations = []
    
    def render(self):
        """Render the Qdrant management UI."""
        st.header("🗃️ Qdrant Vector Database Management")
        
        # Check connection
        health = asyncio.run(self.manager.check_health())
        
        if health['status'] != 'healthy':
            st.error(f"Qdrant connection failed: {health.get('error', 'Unknown error')}")
            st.info("Make sure Qdrant is running on localhost:6333")
            return
        
        # Tabs
        tabs = st.tabs([
            "📊 Overview",
            "📚 Collections",
            "🔍 Search",
            "📥 Data Import",
            "🔧 Operations",
            "⚡ Optimization",
            "💾 Backup"
        ])
        
        with tabs[0]:
            self._render_overview_tab()
        
        with tabs[1]:
            self._render_collections_tab()
        
        with tabs[2]:
            self._render_search_tab()
        
        with tabs[3]:
            self._render_import_tab()
        
        with tabs[4]:
            self._render_operations_tab()
        
        with tabs[5]:
            self._render_optimization_tab()
        
        with tabs[6]:
            self._render_backup_tab()
    
    def _render_overview_tab(self):
        """Render overview tab."""
        st.subheader("Qdrant Overview")
        
        # Get metrics
        metrics = asyncio.run(self.manager.get_metrics())
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Collections",
                metrics.total_collections,
                help="Total number of collections"
            )
        
        with col2:
            st.metric(
                "Total Vectors",
                f"{metrics.total_vectors:,}",
                help="Total vectors across all collections"
            )
        
        with col3:
            st.metric(
                "Total Points",
                f"{metrics.total_points:,}",
                help="Total points (may include metadata without vectors)"
            )
        
        with col4:
            total_gb = metrics.total_size_bytes / (1024**3)
            st.metric(
                "Total Size",
                f"{total_gb:.2f} GB",
                help="Total storage size"
            )
        
        # Collections overview
        st.markdown("### Collections Summary")
        
        collections = asyncio.run(self.manager.list_collections())
        
        if collections:
            # Create summary dataframe
            data = []
            for col in collections:
                data.append({
                    'Name': col.name,
                    'Status': col.status.value,
                    'Vectors': f"{col.vectors_count:,}",
                    'Points': f"{col.points_count:,}",
                    'Segments': col.segments_count,
                    'Size (MB)': f"{col.size_bytes / (1024**2):.1f}",
                    'Vector Dim': col.config.vector_size,
                    'Distance': col.config.distance.value
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Collection sizes pie chart
                fig = px.pie(
                    values=[c.size_bytes for c in collections],
                    names=[c.name for c in collections],
                    title="Storage Distribution by Collection"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Vector count bar chart
                fig = px.bar(
                    x=[c.name for c in collections],
                    y=[c.vectors_count for c in collections],
                    title="Vector Count by Collection",
                    labels={'x': 'Collection', 'y': 'Vector Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No collections found")
        
        # Performance metrics
        st.markdown("### Performance Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Avg Search Latency",
                f"{metrics.avg_search_latency_ms:.1f} ms",
                help="Average search latency"
            )
        
        with col2:
            st.metric(
                "Avg Insert Latency", 
                f"{metrics.avg_insert_latency_ms:.1f} ms",
                help="Average insertion latency"
            )
        
        with col3:
            st.metric(
                "Requests/sec",
                f"{metrics.requests_per_second:.1f}",
                help="Current request rate"
            )
    
    def _render_collections_tab(self):
        """Render collections management tab."""
        st.subheader("Collection Management")
        
        # Create new collection
        with st.expander("➕ Create New Collection", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                collection_name = st.text_input(
                    "Collection Name",
                    placeholder="my_collection",
                    key="new_collection_name"
                )
                
                vector_size = st.number_input(
                    "Vector Dimension",
                    min_value=1,
                    max_value=4096,
                    value=768,
                    help="Dimension of vectors to store"
                )
                
                distance = st.selectbox(
                    "Distance Metric",
                    [d.value for d in Distance],
                    help="Similarity metric for vector search"
                )
            
            with col2:
                index_type = st.selectbox(
                    "Index Type",
                    [i.value for i in IndexType],
                    help="Index structure for efficient search"
                )
                
                replication_factor = st.number_input(
                    "Replication Factor",
                    min_value=1,
                    value=1,
                    help="Number of replicas for fault tolerance"
                )
                
                if st.button("Create Collection", type="primary"):
                    if collection_name:
                        config = CollectionConfig(
                            name=collection_name,
                            vector_size=vector_size,
                            distance=Distance(distance),
                            index_type=IndexType(index_type),
                            replication_factor=replication_factor
                        )
                        
                        with st.spinner("Creating collection..."):
                            try:
                                info = asyncio.run(self.manager.create_collection(config))
                                st.success(f"Created collection: {info.name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating collection: {e}")
        
        # List existing collections
        st.markdown("### Existing Collections")
        
        collections = asyncio.run(self.manager.list_collections())
        
        if not collections:
            st.info("No collections found. Create one to get started.")
            return
        
        # Collection selector
        selected_collection = st.selectbox(
            "Select Collection",
            [c.name for c in collections],
            index=0 if not st.session_state.qdrant_selected_collection else 
                  [c.name for c in collections].index(st.session_state.qdrant_selected_collection)
                  if st.session_state.qdrant_selected_collection in [c.name for c in collections]
                  else 0,
            key="collection_selector"
        )
        
        st.session_state.qdrant_selected_collection = selected_collection
        
        # Get selected collection info
        collection_info = next(c for c in collections if c.name == selected_collection)
        
        # Collection details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Collection Info")
            st.write(f"**Status**: {collection_info.status.value}")
            st.write(f"**Vector Dimension**: {collection_info.config.vector_size}")
            st.write(f"**Distance Metric**: {collection_info.config.distance.value}")
            st.write(f"**Index Type**: {collection_info.config.index_type.value}")
        
        with col2:
            st.markdown("#### Statistics")
            st.write(f"**Vectors**: {collection_info.vectors_count:,}")
            st.write(f"**Points**: {collection_info.points_count:,}")
            st.write(f"**Segments**: {collection_info.segments_count}")
            st.write(f"**Size**: {collection_info.size_bytes / (1024**2):.1f} MB")
        
        with col3:
            st.markdown("#### Health")
            if collection_info.has_errors:
                st.error(f"Errors: {collection_info.error_message}")
            else:
                st.success("Healthy")
            
            st.write(f"**Optimized**: {'Yes' if collection_info.is_optimized else 'No'}")
            
            if collection_info.optimized_at:
                st.write(f"**Last Optimized**: {collection_info.optimized_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Collection actions
        st.markdown("#### Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh", key="refresh_collection"):
                st.rerun()
        
        with col2:
            if st.button("⚡ Optimize", key="optimize_collection"):
                with st.spinner("Optimizing collection..."):
                    task = asyncio.run(self.manager.optimize_collection(selected_collection))
                    st.info(f"Optimization started. Task ID: {task.task_id}")
        
        with col3:
            if st.button("📸 Create Snapshot", key="snapshot_collection"):
                with st.spinner("Creating snapshot..."):
                    try:
                        snapshot_name = asyncio.run(self.manager.create_snapshot(selected_collection))
                        st.success(f"Created snapshot: {snapshot_name}")
                    except Exception as e:
                        st.error(f"Error creating snapshot: {e}")
        
        with col4:
            if st.button("🗑️ Delete", key="delete_collection", type="secondary"):
                if st.checkbox("Confirm deletion"):
                    with st.spinner("Deleting collection..."):
                        success = asyncio.run(self.manager.delete_collection(selected_collection))
                        if success:
                            st.success(f"Deleted collection: {selected_collection}")
                            st.session_state.qdrant_selected_collection = None
                            st.rerun()
                        else:
                            st.error("Failed to delete collection")
    
    def _render_search_tab(self):
        """Render search tab."""
        st.subheader("Vector Search")
        
        if not st.session_state.qdrant_selected_collection:
            st.info("Please select a collection from the Collections tab first.")
            return
        
        collection_name = st.session_state.qdrant_selected_collection
        st.info(f"Searching in collection: **{collection_name}**")
        
        # Search configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Vector input
            vector_input_method = st.radio(
                "Vector Input Method",
                ["Random Vector", "Manual Input", "From Text (Mock)"],
                horizontal=True
            )
            
            if vector_input_method == "Random Vector":
                # Get collection info for vector size
                info = asyncio.run(self.manager.get_collection_info(collection_name))
                vector = np.random.randn(info.config.vector_size).tolist()
                st.info(f"Generated random {info.config.vector_size}-dimensional vector")
                
            elif vector_input_method == "Manual Input":
                vector_str = st.text_area(
                    "Vector (comma-separated values)",
                    placeholder="0.1, 0.2, 0.3, ...",
                    height=100
                )
                try:
                    vector = [float(x.strip()) for x in vector_str.split(",") if x.strip()]
                except:
                    vector = []
                    st.error("Invalid vector format")
            
            else:  # From Text
                text = st.text_area(
                    "Text to vectorize",
                    placeholder="Enter text to convert to vector...",
                    height=100
                )
                if text:
                    # Mock vectorization - in real implementation would use actual embedding model
                    info = asyncio.run(self.manager.get_collection_info(collection_name))
                    vector = np.random.randn(info.config.vector_size).tolist()
                    st.info("Text vectorized (mock implementation)")
                else:
                    vector = []
        
        with col2:
            # Search parameters
            limit = st.number_input(
                "Results Limit",
                min_value=1,
                max_value=100,
                value=10
            )
            
            score_threshold = st.number_input(
                "Score Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.1,
                help="Minimum similarity score (0 = no threshold)"
            )
            
            with_vectors = st.checkbox(
                "Include Vectors in Results",
                value=False
            )
        
        # Filters
        with st.expander("🔽 Advanced Filters", expanded=False):
            st.markdown("#### Payload Filters")
            st.info("Add filters based on payload fields (JSON format)")
            
            filter_json = st.text_area(
                "Filter (JSON)",
                placeholder='{"must": [{"key": "category", "match": {"value": "science"}}]}',
                height=100
            )
            
            filter_dict = None
            if filter_json:
                try:
                    filter_dict = json.loads(filter_json)
                    st.success("Valid filter")
                except:
                    st.error("Invalid JSON format")
        
        # Search button
        if st.button("🔍 Search", type="primary", disabled=len(vector) == 0):
            with st.spinner("Searching..."):
                request = SearchRequest(
                    collection_name=collection_name,
                    vector=vector,
                    limit=limit,
                    filter=filter_dict,
                    with_vector=with_vectors,
                    score_threshold=score_threshold if score_threshold > 0 else None
                )
                
                try:
                    results = asyncio.run(self.manager.search(request))
                    st.session_state.qdrant_search_results = results
                    
                    # Track search
                    self.change_tracker.track_change(
                        category=ChangeCategory.MONITORING,
                        change_type=ChangeType.VIEW,
                        description=f"Performed search in {collection_name}",
                        details={
                            'results_count': len(results),
                            'limit': limit,
                            'threshold': score_threshold
                        }
                    )
                except Exception as e:
                    st.error(f"Search failed: {e}")
                    st.session_state.qdrant_search_results = []
        
        # Display results
        if st.session_state.qdrant_search_results:
            st.markdown(f"### Search Results ({len(st.session_state.qdrant_search_results)} found)")
            
            for i, result in enumerate(st.session_state.qdrant_search_results):
                with st.expander(f"Result {i+1} - ID: {result.id} (Score: {result.score:.4f})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if result.payload:
                            st.markdown("**Payload:**")
                            st.json(result.payload)
                        else:
                            st.info("No payload data")
                    
                    with col2:
                        st.metric("Score", f"{result.score:.4f}")
                        st.write(f"**ID**: {result.id}")
                    
                    if result.vector:
                        st.markdown("**Vector:**")
                        st.text(f"[{', '.join(f'{v:.4f}' for v in result.vector[:10])}...]")
    
    def _render_import_tab(self):
        """Render data import tab."""
        st.subheader("Data Import")
        
        if not st.session_state.qdrant_selected_collection:
            st.info("Please select a collection from the Collections tab first.")
            return
        
        collection_name = st.session_state.qdrant_selected_collection
        st.info(f"Importing to collection: **{collection_name}**")
        
        # Import method
        import_method = st.radio(
            "Import Method",
            ["Manual Entry", "JSON File", "CSV File", "Generate Test Data"],
            horizontal=True
        )
        
        points_to_import = []
        
        if import_method == "Manual Entry":
            st.markdown("#### Add Points Manually")
            
            col1, col2 = st.columns(2)
            
            with col1:
                point_id = st.text_input("Point ID", placeholder="unique-id-123")
                
                vector_str = st.text_area(
                    "Vector (comma-separated)",
                    placeholder="0.1, 0.2, 0.3, ...",
                    height=100
                )
            
            with col2:
                payload_json = st.text_area(
                    "Payload (JSON)",
                    placeholder='{"title": "Example", "category": "test"}',
                    height=100
                )
                
                if st.button("Add Point"):
                    try:
                        vector = [float(x.strip()) for x in vector_str.split(",") if x.strip()]
                        payload = json.loads(payload_json) if payload_json else {}
                        
                        point = PointData(
                            id=point_id,
                            vector=vector,
                            payload=payload
                        )
                        
                        st.success(f"Point {point_id} ready for import")
                        points_to_import = [point]
                    except Exception as e:
                        st.error(f"Error creating point: {e}")
        
        elif import_method == "JSON File":
            st.markdown("#### Import from JSON")
            
            uploaded_file = st.file_uploader(
                "Choose JSON file",
                type=['json'],
                help="JSON array of points with id, vector, and payload fields"
            )
            
            if uploaded_file:
                try:
                    data = json.load(uploaded_file)
                    
                    points_to_import = [
                        PointData(
                            id=item['id'],
                            vector=item['vector'],
                            payload=item.get('payload', {})
                        )
                        for item in data
                    ]
                    
                    st.success(f"Loaded {len(points_to_import)} points from file")
                except Exception as e:
                    st.error(f"Error loading JSON: {e}")
        
        elif import_method == "CSV File":
            st.markdown("#### Import from CSV")
            st.info("CSV should have columns: id, vector (JSON array), and optional payload columns")
            
            uploaded_file = st.file_uploader(
                "Choose CSV file",
                type=['csv']
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Preview
                    st.write("Preview:")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    # Convert to points
                    points_to_import = []
                    for _, row in df.iterrows():
                        vector = json.loads(row['vector']) if isinstance(row['vector'], str) else row['vector']
                        
                        # Build payload from other columns
                        payload = {}
                        for col in df.columns:
                            if col not in ['id', 'vector']:
                                payload[col] = row[col]
                        
                        points_to_import.append(
                            PointData(
                                id=row['id'],
                                vector=vector,
                                payload=payload
                            )
                        )
                    
                    st.success(f"Prepared {len(points_to_import)} points for import")
                except Exception as e:
                    st.error(f"Error loading CSV: {e}")
        
        else:  # Generate Test Data
            st.markdown("#### Generate Test Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                num_points = st.number_input(
                    "Number of Points",
                    min_value=1,
                    max_value=10000,
                    value=100
                )
                
                # Get vector size from collection
                info = asyncio.run(self.manager.get_collection_info(collection_name))
                vector_dim = info.config.vector_size
                st.info(f"Vector dimension: {vector_dim}")
            
            with col2:
                include_payload = st.checkbox("Include Sample Payload", value=True)
                
                if st.button("Generate Data"):
                    points_to_import = []
                    
                    for i in range(num_points):
                        point = PointData(
                            id=f"test-{i}",
                            vector=np.random.randn(vector_dim).tolist(),
                            payload={
                                "index": i,
                                "category": f"category-{i % 5}",
                                "timestamp": datetime.now().isoformat(),
                                "score": np.random.rand()
                            } if include_payload else {}
                        )
                        points_to_import.append(point)
                    
                    st.success(f"Generated {num_points} test points")
        
        # Import button
        if points_to_import:
            st.markdown(f"### Ready to Import: {len(points_to_import)} points")
            
            batch_size = st.number_input(
                "Batch Size",
                min_value=1,
                max_value=1000,
                value=100,
                help="Number of points to insert per batch"
            )
            
            if st.button("📥 Import Points", type="primary"):
                with st.spinner(f"Importing {len(points_to_import)} points..."):
                    operation = asyncio.run(
                        self.manager.insert_points(
                            collection_name,
                            points_to_import,
                            batch_size
                        )
                    )
                    
                    if operation.status == "completed":
                        st.success(f"Successfully imported {operation.processed_count} points")
                        st.balloons()
                    else:
                        st.error(f"Import failed: {', '.join(operation.errors)}")
    
    def _render_operations_tab(self):
        """Render operations tab."""
        st.subheader("Active Operations")
        
        # Get active operations
        operations = self.manager.get_active_operations()
        
        if operations:
            st.markdown(f"### {len(operations)} Active Operations")
            
            for op in operations:
                status_color = {
                    "pending": "🟡",
                    "processing": "🔵",
                    "completed": "🟢",
                    "failed": "🔴"
                }.get(op.status, "⚪")
                
                with st.expander(f"{status_color} {op.operation_type.upper()} - {op.collection_name}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Operation ID**: {op.operation_id}")
                        st.write(f"**Type**: {op.operation_type}")
                        st.write(f"**Collection**: {op.collection_name}")
                        st.write(f"**Status**: {op.status}")
                    
                    with col2:
                        st.write(f"**Points**: {len(op.points)}")
                        st.write(f"**Processed**: {op.processed_count}")
                        st.write(f"**Errors**: {op.error_count}")
                        
                        if op.duration_ms():
                            st.write(f"**Duration**: {op.duration_ms():.0f}ms")
                    
                    if op.errors:
                        st.error(f"Errors: {', '.join(op.errors)}")
                    
                    # Progress bar
                    if op.status == "processing" and len(op.points) > 0:
                        progress = op.processed_count / len(op.points)
                        st.progress(progress)
        else:
            st.info("No active operations")
        
        # Operation history
        st.markdown("### Recent Operations")
        
        # This would show historical operations from change tracker
        recent_changes = self.change_tracker.get_recent_changes(
            category=ChangeCategory.DATABASE,
            limit=20
        )
        
        if recent_changes:
            data = []
            for change in recent_changes:
                if 'operation_id' in change.details:
                    data.append({
                        'Time': change.timestamp.strftime('%H:%M:%S'),
                        'Operation': change.description,
                        'Duration': f"{change.details.get('duration_ms', 0):.0f}ms",
                        'Count': change.details.get('points_count', change.details.get('count', 0))
                    })
            
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
    
    def _render_optimization_tab(self):
        """Render optimization tab."""
        st.subheader("Collection Optimization")
        
        # Get all collections
        collections = asyncio.run(self.manager.list_collections())
        
        if not collections:
            st.info("No collections available for optimization")
            return
        
        # Optimization recommendations
        st.markdown("### Optimization Recommendations")
        
        needs_optimization = []
        for col in collections:
            if not col.is_optimized or col.segments_count > 5:
                needs_optimization.append(col)
        
        if needs_optimization:
            st.warning(f"{len(needs_optimization)} collections could benefit from optimization")
            
            for col in needs_optimization:
                with st.expander(f"⚡ {col.name}"):
                    st.write(f"**Segments**: {col.segments_count} (recommended: < 5)")
                    st.write(f"**Size**: {col.size_bytes / (1024**2):.1f} MB")
                    st.write(f"**Optimized**: {'No' if not col.is_optimized else 'Yes'}")
                    
                    if st.button(f"Optimize {col.name}", key=f"opt_{col.name}"):
                        with st.spinner("Starting optimization..."):
                            task = asyncio.run(self.manager.optimize_collection(col.name))
                            st.info(f"Optimization started. Task ID: {task.task_id}")
        else:
            st.success("All collections are optimized")
        
        # Active optimization tasks
        st.markdown("### Active Optimization Tasks")
        
        tasks = self.manager.get_optimization_tasks()
        active_tasks = [t for t in tasks if t.status == OptimizationStatus.IN_PROGRESS]
        
        if active_tasks:
            for task in active_tasks:
                with st.expander(f"🔄 {task.collection_name} - {task.optimization_type}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Task ID**: {task.task_id}")
                        st.write(f"**Collection**: {task.collection_name}")
                        st.write(f"**Type**: {task.optimization_type}")
                        st.write(f"**Started**: {task.started_at.strftime('%H:%M:%S')}")
                    
                    with col2:
                        st.write(f"**Progress**: {task.progress:.0f}%")
                        st.write(f"**Segments Before**: {task.segments_before}")
                        
                        if task.estimated_completion:
                            st.write(f"**ETA**: {task.estimated_completion.strftime('%H:%M:%S')}")
                    
                    # Progress bar
                    st.progress(task.progress / 100)
        else:
            st.info("No active optimization tasks")
        
        # Completed optimizations
        st.markdown("### Recent Optimizations")
        
        completed_tasks = [t for t in tasks if t.status == OptimizationStatus.COMPLETED][-5:]
        
        if completed_tasks:
            data = []
            for task in completed_tasks:
                data.append({
                    'Collection': task.collection_name,
                    'Completed': task.completed_at.strftime('%Y-%m-%d %H:%M'),
                    'Segments': f"{task.segments_before} → {task.segments_after}",
                    'Space Saved': f"{task.space_saved_bytes() / (1024**2):.1f} MB",
                    'Duration': f"{task.duration_seconds():.1f}s"
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    def _render_backup_tab(self):
        """Render backup and snapshots tab."""
        st.subheader("Backup & Snapshots")
        
        # Create snapshot
        st.markdown("### Create Snapshot")
        
        collections = asyncio.run(self.manager.list_collections())
        
        if collections:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                collection_to_snapshot = st.selectbox(
                    "Select Collection",
                    [c.name for c in collections],
                    key="snapshot_collection_select"
                )
            
            with col2:
                if st.button("📸 Create Snapshot", type="primary"):
                    with st.spinner("Creating snapshot..."):
                        try:
                            snapshot_name = asyncio.run(
                                self.manager.create_snapshot(collection_to_snapshot)
                            )
                            st.success(f"Created snapshot: {snapshot_name}")
                        except Exception as e:
                            st.error(f"Error creating snapshot: {e}")
        
        # Backup configuration
        st.markdown("### Backup Configuration")
        
        backup_type = st.radio(
            "Backup Type",
            ["Full Backup", "Collection Backup", "Incremental"],
            horizontal=True
        )
        
        if backup_type == "Collection Backup":
            selected_collections = st.multiselect(
                "Select Collections",
                [c.name for c in collections]
            )
        else:
            selected_collections = [c.name for c in collections]
        
        backup_path = st.text_input(
            "Backup Destination",
            value="/tmp/qdrant-backup",
            help="Path where backup files will be stored"
        )
        
        if st.button("🔄 Start Backup", type="primary"):
            st.info("Backup functionality would be implemented here")
            # In a real implementation, this would trigger actual backup
        
        # Restore options
        st.markdown("### Restore from Backup")
        
        restore_path = st.text_input(
            "Backup Source",
            placeholder="/path/to/backup",
            help="Path to backup files"
        )
        
        if st.button("📥 Restore", type="secondary"):
            if restore_path:
                st.info("Restore functionality would be implemented here")
                # In a real implementation, this would trigger actual restore