"""
Logged UMAP Wrapper

This module provides wrapper functions for the UMAP Analogy Engine that
automatically log all activities for transparency and auditability.

It wraps the core functions from umap_analogy_engine.py and adds comprehensive
activity logging without modifying the original implementation.
"""

import torch
import torch.nn as nn
from typing import List, Tuple, Optional, Dict, Any
import time

from umap_analogy_engine import (
    train_relation_aware_umap,
    find_analogy,
    analogy_from_pair,
    extract_relation_axes,
    ParametricUMAP
)
from activity_logger import ActivityLogger, ActivityType, LogLevel


class LoggedUMAPEngine:
    """
    Wrapper class that adds activity logging to UMAP Analogy Engine operations.

    Example:
        engine = LoggedUMAPEngine(task_name="word_analogies_experiment")

        # Train with logging
        model, embeddings = engine.train(
            X=data,
            pair_indices_list=relations,
            relation_names=["capital", "gender"]
        )

        # Query with logging
        result = engine.find_analogy(
            model=model,
            X=data,
            query_idx=10,
            relation_idx=0
        )

        # Generate reports
        engine.close_and_report()
    """

    def __init__(
        self,
        task_name: str = "umap_analogy",
        enable_logging: bool = True,
        enable_console: bool = True,
        log_level: LogLevel = LogLevel.INFO
    ):
        """
        Initialize logged UMAP engine.

        Args:
            task_name: Name for this task/experiment
            enable_logging: Whether to enable logging
            enable_console: Whether to print logs to console
            log_level: Minimum log level to record
        """
        self.task_name = task_name
        self.enable_logging = enable_logging

        if enable_logging:
            self.logger = ActivityLogger(
                task_name=task_name,
                enable_console=enable_console,
                min_level=log_level
            )
        else:
            self.logger = None

        self.model = None
        self.embeddings = None
        self.training_stats = {}

    def train(
        self,
        X: torch.Tensor,
        pair_indices_list: List[List[Tuple[int, int]]],
        relation_names: Optional[List[str]] = None,
        # UMAP parameters
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        spread: float = 1.0,
        # Training parameters
        epochs: int = 200,
        edge_batch_size: int = 2048,
        negative_sample_rate: int = 5,
        lr: float = 1e-3,
        d_low: int = 2,
        # Loss weights
        align_weight: float = 1.0,
        ortho_weight: float = 0.5,
        auto_align: bool = True,
        # Model parameters
        hidden_dims: Optional[List[int]] = None,
        dropout_p: float = 0.1,
        use_amp: bool = False,
        # Logging
        verbose: bool = True,
        # Cluster parameters
        kmeans_iters: int = 50,
        kmeans_update_freq: int = 10,
        device: Optional[str] = None
    ) -> Tuple[nn.Module, torch.Tensor]:
        """
        Train UMAP model with relation awareness and activity logging.

        All parameters are passed through to the underlying train_relation_aware_umap
        function. See umap_analogy_engine.py for detailed parameter descriptions.

        Returns:
            Tuple of (trained_model, low_dimensional_embeddings)
        """
        start_time = time.time()

        # Log configuration
        if self.logger:
            config = {
                "data_shape": list(X.shape),
                "n_relations": len(pair_indices_list),
                "relation_names": relation_names or [f"relation_{i}" for i in range(len(pair_indices_list))],
                "n_neighbors": n_neighbors,
                "min_dist": min_dist,
                "spread": spread,
                "epochs": epochs,
                "edge_batch_size": edge_batch_size,
                "negative_sample_rate": negative_sample_rate,
                "learning_rate": lr,
                "output_dimensions": d_low,
                "align_weight": align_weight,
                "ortho_weight": ortho_weight,
                "auto_align": auto_align,
                "hidden_dims": hidden_dims or [512, 256, 128],
                "dropout": dropout_p,
                "use_amp": use_amp,
                "kmeans_iters": kmeans_iters,
                "kmeans_update_freq": kmeans_update_freq,
                "device": device or ("cuda" if torch.cuda.is_available() else "cpu")
            }

            self.logger.log_config("training_configuration", config)
            self.logger.log_activity(
                activity_type=ActivityType.TRAINING,
                message=f"Starting training: {epochs} epochs, {len(pair_indices_list)} relations",
                level=LogLevel.INFO,
                metadata={"config": config}
            )

        # Create callback for epoch logging
        epoch_losses = []

        def epoch_callback(epoch: int, losses: Dict[str, float]):
            """Callback to log each epoch"""
            epoch_losses.append(losses)
            if self.logger and epoch % 10 == 0:  # Log every 10 epochs
                self.logger.log_training_epoch(
                    epoch=epoch,
                    total_epochs=epochs,
                    losses=losses
                )

        try:
            # Call original training function
            # Note: The original function doesn't support callbacks, so we'll
            # wrap it and log the overall results
            model, embeddings = train_relation_aware_umap(
                X=X,
                pair_indices_list=pair_indices_list,
                relation_names=relation_names,
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                spread=spread,
                epochs=epochs,
                edge_batch_size=edge_batch_size,
                negative_sample_rate=negative_sample_rate,
                lr=lr,
                d_low=d_low,
                align_weight=align_weight,
                ortho_weight=ortho_weight,
                auto_align=auto_align,
                hidden_dims=hidden_dims,
                dropout_p=dropout_p,
                use_amp=use_amp,
                verbose=verbose,
                kmeans_iters=kmeans_iters,
                kmeans_update_freq=kmeans_update_freq,
                device=device
            )

            # Store results
            self.model = model
            self.embeddings = embeddings

            # Calculate training time
            training_time = time.time() - start_time

            # Log completion
            if self.logger:
                self.training_stats = {
                    "training_time_seconds": training_time,
                    "final_embedding_shape": list(embeddings.shape),
                    "model_parameters": sum(p.numel() for p in model.parameters())
                }

                self.logger.log_activity(
                    activity_type=ActivityType.TRAINING,
                    message=f"Training completed successfully in {training_time:.2f}s",
                    level=LogLevel.INFO,
                    metadata=self.training_stats
                )

                # Log model info
                self.logger.log_model_info(
                    model_name="ParametricUMAP",
                    parameters={
                        "input_dim": X.shape[1],
                        "output_dim": d_low,
                        "hidden_dims": hidden_dims or [512, 256, 128],
                        "total_parameters": self.training_stats["model_parameters"]
                    }
                )

            return model, embeddings

        except Exception as e:
            # Log error
            if self.logger:
                self.logger.log_error(
                    error_message="Training failed",
                    exception=e,
                    metadata={"epoch": len(epoch_losses)}
                )
            raise

    def find_analogy(
        self,
        model: nn.Module,
        X: torch.Tensor,
        query_idx: int,
        relation_idx: int,
        pair_indices_list: List[List[Tuple[int, int]]],
        k: int = 5,
        metric: str = "euclidean",
        device: Optional[str] = None
    ) -> Tuple[List[int], List[float]]:
        """
        Find analogies with activity logging.

        Args:
            model: Trained UMAP model
            X: Input data
            query_idx: Index of query item
            relation_idx: Which relation to apply
            pair_indices_list: List of relation pairs
            k: Number of results to return
            metric: "euclidean" or "cosine"
            device: Device to use

        Returns:
            Tuple of (top_k_indices, top_k_distances)
        """
        start_time = time.time()

        try:
            # Call original function
            top_k_idx, top_k_dist = find_analogy(
                model=model,
                X=X,
                query_idx=query_idx,
                relation_idx=relation_idx,
                pair_indices_list=pair_indices_list,
                k=k,
                metric=metric,
                device=device
            )

            # Log inference
            if self.logger:
                inference_time = time.time() - start_time
                self.logger.log_inference(
                    query=f"query_idx={query_idx}, relation_idx={relation_idx}",
                    result=f"top_{k}_results={top_k_idx}",
                    method="find_analogy",
                    metadata={
                        "query_idx": query_idx,
                        "relation_idx": relation_idx,
                        "k": k,
                        "metric": metric,
                        "top_k_indices": top_k_idx,
                        "top_k_distances": top_k_dist,
                        "inference_time_seconds": inference_time
                    }
                )

            return top_k_idx, top_k_dist

        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    error_message="Analogy finding failed",
                    exception=e,
                    metadata={
                        "query_idx": query_idx,
                        "relation_idx": relation_idx
                    }
                )
            raise

    def analogy_from_pair(
        self,
        model: nn.Module,
        X: torch.Tensor,
        ref_a: int,
        ref_b: int,
        query_idx: int,
        k: int = 5,
        metric: str = "euclidean",
        device: Optional[str] = None
    ) -> Tuple[List[int], List[float]]:
        """
        Find analogy using a reference pair with activity logging.

        Args:
            model: Trained UMAP model
            X: Input data
            ref_a: First element of reference pair
            ref_b: Second element of reference pair (defines relation)
            query_idx: Query item index
            k: Number of results to return
            metric: "euclidean" or "cosine"
            device: Device to use

        Returns:
            Tuple of (top_k_indices, top_k_distances)
        """
        start_time = time.time()

        try:
            # Call original function
            top_k_idx, top_k_dist = analogy_from_pair(
                model=model,
                X=X,
                ref_a=ref_a,
                ref_b=ref_b,
                query_idx=query_idx,
                k=k,
                metric=metric,
                device=device
            )

            # Log inference
            if self.logger:
                inference_time = time.time() - start_time
                self.logger.log_inference(
                    query=f"pair=({ref_a}, {ref_b}), query_idx={query_idx}",
                    result=f"top_{k}_results={top_k_idx}",
                    method="analogy_from_pair",
                    metadata={
                        "ref_a": ref_a,
                        "ref_b": ref_b,
                        "query_idx": query_idx,
                        "k": k,
                        "metric": metric,
                        "top_k_indices": top_k_idx,
                        "top_k_distances": top_k_dist,
                        "inference_time_seconds": inference_time
                    }
                )

            return top_k_idx, top_k_dist

        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    error_message="Analogy from pair failed",
                    exception=e,
                    metadata={
                        "ref_a": ref_a,
                        "ref_b": ref_b,
                        "query_idx": query_idx
                    }
                )
            raise

    def extract_relations(
        self,
        embeddings: torch.Tensor,
        pair_indices_list: List[List[Tuple[int, int]]],
        relation_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract relation axes with logging.

        Returns:
            List of dictionaries with relation information
        """
        try:
            # Extract relation axes
            relation_info = extract_relation_axes(
                embeddings=embeddings,
                pair_indices_list=pair_indices_list,
                relation_names=relation_names
            )

            # Log extraction
            if self.logger:
                self.logger.log_activity(
                    activity_type=ActivityType.MODEL,
                    message=f"Extracted {len(relation_info)} relation axes",
                    level=LogLevel.INFO,
                    metadata={
                        "n_relations": len(relation_info),
                        "relation_info": relation_info
                    }
                )

            return relation_info

        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    error_message="Relation extraction failed",
                    exception=e
                )
            raise

    def close_and_report(self, generate_report: bool = True) -> Optional[str]:
        """
        Close the logging session and optionally generate a summary report.

        Args:
            generate_report: Whether to generate a summary report

        Returns:
            Path to generated report if generate_report is True
        """
        if not self.logger:
            return None

        # Close session with summary
        summary = {
            "task_name": self.task_name,
            "training_completed": self.model is not None,
            "training_stats": self.training_stats
        }

        self.logger.close_session(summary=summary)

        # Generate report if requested
        if generate_report:
            from report_generator import ReportGenerator

            generator = ReportGenerator()
            session_id = self.logger.get_session_id()

            # Generate both session and training reports
            report_path = generator.generate_session_report(session_id)

            if self.model is not None:
                generator.generate_training_summary(session_id)

            return report_path

        return None

    def get_session_id(self) -> Optional[str]:
        """Get the current session ID"""
        if self.logger:
            return self.logger.get_session_id()
        return None

    def get_log_file(self) -> Optional[str]:
        """Get the path to the current log file"""
        if self.logger:
            return str(self.logger.get_log_file_path())
        return None
