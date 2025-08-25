"""
Hyperparameter optimization for medical literature classification models
Uses Optuna for efficient hyperparameter tuning
"""
import logging
import optuna
from typing import Dict, List, Callable, Any, Optional
import numpy as np
from sklearn.model_selection import cross_val_score
from .ml_models import create_model, TransformerClassifier, TraditionalMLClassifier

logger = logging.getLogger(__name__)


class HyperparameterOptimizer:
    """
    Hyperparameter optimization using Optuna
    Supports both transformer and traditional ML models
    """
    
    def __init__(self, model_type: str, optimization_metric: str = 'f1_macro'):
        self.model_type = model_type
        self.optimization_metric = optimization_metric
        self.study = None
        self.best_params = None
        self.training_data = None
        
    def _objective_transformer(self, trial: optuna.Trial) -> float:
        """Objective function for transformer models"""
        # Suggest hyperparameters
        params = {
            'learning_rate': trial.suggest_float('learning_rate', 1e-6, 1e-3, log=True),
            'per_device_train_batch_size': trial.suggest_categorical('batch_size', [8, 16, 32]),
            'num_train_epochs': trial.suggest_int('num_epochs', 2, 8),
            'weight_decay': trial.suggest_float('weight_decay', 0.0, 0.3),
            'warmup_steps': trial.suggest_int('warmup_steps', 100, 1000),
        }
        
        # Additional transformer-specific parameters
        if 'bert' in self.model_type:
            bert_model = trial.suggest_categorical('bert_model', ['biobert', 'clinicalbert', 'scibert'])
            max_length = trial.suggest_categorical('max_length', [256, 512])
        else:
            bert_model = self.model_type
            max_length = 512
        
        try:
            # Create and train model
            if self.model_type in ['gemma2-2b']:
                # For Gemma models, don't pass bert_model parameter
                model = create_model(
                    model_type=self.model_type,
                    max_length=max_length,
                    num_labels=10  # Default, will be updated during training
                )
            else:
                model = create_model(
                    model_type=self.model_type,
                    bert_model=bert_model,
                    max_length=max_length
                )
            
            texts, labels = self.training_data
            
            # Training arguments
            training_args = {
                'output_dir': f'./optuna_trial_{trial.number}',
                'num_train_epochs': params['num_train_epochs'],
                'per_device_train_batch_size': params['per_device_train_batch_size'],
                'per_device_eval_batch_size': params['per_device_train_batch_size'],
                'learning_rate': params['learning_rate'],
                'weight_decay': params['weight_decay'],
                'warmup_steps': params['warmup_steps'],
                'logging_steps': 50,
                'eval_strategy': 'steps',
                'eval_steps': 100,
                'save_steps': 500,
                'load_best_model_at_end': True,
                'metric_for_best_model': f'eval_{self.optimization_metric}',
                'greater_is_better': True,
                'dataloader_num_workers': 0,  # Avoid multiprocessing issues
            }
            
            # Train model
            results = model.train(texts, labels, training_args)
            
            # Return the metric we're optimizing for
            metric_key = f'eval_{self.optimization_metric}'
            if metric_key in results:
                return results[metric_key]
            else:
                # Fallback to available metrics
                return results.get('eval_f1_macro', results.get('eval_accuracy', 0.0))
                
        except Exception as e:
            logger.error(f"Trial {trial.number} failed: {str(e)}")
            return 0.0  # Return worst possible score
    
    def _objective_traditional(self, trial: optuna.Trial) -> float:
        """Objective function for traditional ML models"""
        # Suggest hyperparameters based on algorithm
        algorithm = trial.suggest_categorical('algorithm', ['svm', 'random_forest', 'logistic_regression'])
        max_features = trial.suggest_categorical('max_features', [5000, 10000, 20000])
        
        params = {
            'algorithm': algorithm,
            'max_features': max_features
        }
        
        # Algorithm-specific parameters
        if algorithm == 'svm':
            params['C'] = trial.suggest_float('C', 0.01, 100, log=True)
            params['kernel'] = trial.suggest_categorical('kernel', ['linear', 'rbf'])
        elif algorithm == 'random_forest':
            params['n_estimators'] = trial.suggest_int('n_estimators', 50, 300)
            params['max_depth'] = trial.suggest_int('max_depth', 5, 20)
        elif algorithm == 'logistic_regression':
            params['C'] = trial.suggest_float('C', 0.01, 100, log=True)
        
        try:
            # Create and train model
            model = create_model(model_type='traditional', **params)
            
            texts, labels = self.training_data
            results = model.train(texts, labels)
            
            # Return the metric we're optimizing for
            return results.get(self.optimization_metric, results.get('f1_macro', 0.0))
            
        except Exception as e:
            logger.error(f"Trial {trial.number} failed: {str(e)}")
            return 0.0
    
    def _objective_hybrid(self, trial: optuna.Trial) -> float:
        """Objective function for hybrid ensemble models"""
        # Suggest parameters for both components
        transformer_type = trial.suggest_categorical('transformer_type', ['biobert', 'clinicalbert', 'scibert'])
        traditional_algorithm = trial.suggest_categorical('traditional_algorithm', ['svm', 'random_forest'])
        
        # Ensemble weights
        transformer_weight = trial.suggest_float('transformer_weight', 0.3, 0.9)
        traditional_weight = 1.0 - transformer_weight
        
        # Transformer parameters
        learning_rate = trial.suggest_float('learning_rate', 1e-6, 1e-3, log=True)
        batch_size = trial.suggest_categorical('batch_size', [8, 16, 32])
        num_epochs = trial.suggest_int('num_epochs', 2, 6)  # Fewer epochs for ensemble
        
        try:
            # Create hybrid model
            model = create_model(
                model_type='hybrid',
                transformer_type=transformer_type,
                traditional_algorithm=traditional_algorithm
            )
            
            # Set ensemble weights
            model.weights = {'transformer': transformer_weight, 'traditional': traditional_weight}
            
            texts, labels = self.training_data
            
            # Training arguments for transformer component
            transformer_args = {
                'output_dir': f'./optuna_hybrid_trial_{trial.number}',
                'num_train_epochs': num_epochs,
                'per_device_train_batch_size': batch_size,
                'per_device_eval_batch_size': batch_size,
                'learning_rate': learning_rate,
                'logging_steps': 50,
                'eval_strategy': 'steps',
                'eval_steps': 200,
                'save_steps': 500,
                'load_best_model_at_end': True,
                'dataloader_num_workers': 0,
            }
            
            # Train ensemble
            results = model.train(texts, labels, transformer_args)
            
            # Use transformer results as proxy (could be improved with ensemble validation)
            transformer_results = results['transformer_results']
            return transformer_results.get(f'eval_{self.optimization_metric}', 
                                         transformer_results.get('eval_f1_macro', 0.0))
            
        except Exception as e:
            logger.error(f"Hybrid trial {trial.number} failed: {str(e)}")
            return 0.0
    
    def optimize(self, texts: List[str], labels: List[List[str]], 
                 n_trials: int = 20, timeout: Optional[int] = None,
                 study_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run hyperparameter optimization
        
        Args:
            texts: Training texts
            labels: Training labels
            n_trials: Number of optimization trials
            timeout: Maximum time in seconds
            study_name: Optional study name for persistence
            
        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Starting hyperparameter optimization for {self.model_type}")
        logger.info(f"Optimization metric: {self.optimization_metric}")
        logger.info(f"Number of trials: {n_trials}")
        
        # Store training data
        self.training_data = (texts, labels)
        
        # Create or load study
        if study_name:
            storage_url = f"sqlite:///optuna_{study_name}.db"
            self.study = optuna.create_study(
                direction='maximize',
                study_name=study_name,
                storage=storage_url,
                load_if_exists=True
            )
        else:
            self.study = optuna.create_study(direction='maximize')
        
        # Select objective function based on model type
        if self.model_type in ['bert', 'biobert', 'clinicalbert', 'scibert', 'gemma2-2b']:
            objective_fn = self._objective_transformer
        elif self.model_type == 'traditional':
            objective_fn = self._objective_traditional
        elif self.model_type == 'hybrid':
            objective_fn = self._objective_hybrid
        else:
            raise ValueError(f"Unsupported model type for optimization: {self.model_type}")
        
        # Run optimization
        try:
            self.study.optimize(
                objective_fn,
                n_trials=n_trials,
                timeout=timeout,
                show_progress_bar=True
            )
            
            self.best_params = self.study.best_params
            best_value = self.study.best_value
            
            logger.info(f"Optimization completed!")
            logger.info(f"Best {self.optimization_metric}: {best_value:.4f}")
            logger.info(f"Best parameters: {self.best_params}")
            
            # Analyze optimization results
            trials_df = self.study.trials_dataframe()
            
            return {
                'best_params': self.best_params,
                'best_value': best_value,
                'n_trials': len(self.study.trials),
                'optimization_metric': self.optimization_metric,
                'study': self.study,
                'trials_dataframe': trials_df,
                'model_type': self.model_type
            }
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}", exc_info=True)
            raise
    
    def get_optimization_history(self) -> Dict[str, Any]:
        """Get optimization history and statistics"""
        if not self.study:
            return {}
        
        trials = self.study.trials
        values = [trial.value for trial in trials if trial.value is not None]
        
        if not values:
            return {}
        
        return {
            'n_trials': len(trials),
            'best_value': max(values),
            'worst_value': min(values),
            'mean_value': np.mean(values),
            'std_value': np.std(values),
            'improvement_over_trials': values,
            'best_trial_number': self.study.best_trial.number if self.study.best_trial else None
        }
    
    def create_optimized_model(self, **override_params) -> Any:
        """Create a model with optimized hyperparameters"""
        if not self.best_params:
            raise ValueError("Must run optimization before creating optimized model")
        
        # Combine best params with any overrides
        params = self.best_params.copy()
        params.update(override_params)
        
        # Create model based on type
        if self.model_type in ['bert', 'biobert', 'clinicalbert', 'scibert']:
            bert_model = params.pop('bert_model', self.model_type)
            max_length = params.pop('max_length', 512)
            
            return create_model(
                model_type=self.model_type,
                bert_model=bert_model,
                max_length=max_length
            )
        
        elif self.model_type in ['gemma2-2b']:
            max_length = params.pop('max_length', 512)
            num_labels = params.pop('num_labels', 10)
            
            return create_model(
                model_type=self.model_type,
                max_length=max_length,
                num_labels=num_labels
            )
        
        elif self.model_type == 'traditional':
            return create_model(model_type='traditional', **params)
        
        elif self.model_type == 'hybrid':
            transformer_type = params.pop('transformer_type', 'biobert')
            traditional_algorithm = params.pop('traditional_algorithm', 'svm')
            
            model = create_model(
                model_type='hybrid',
                transformer_type=transformer_type,
                traditional_algorithm=traditional_algorithm
            )
            
            # Set optimized ensemble weights
            if 'transformer_weight' in params:
                transformer_weight = params['transformer_weight']
                model.weights = {
                    'transformer': transformer_weight,
                    'traditional': 1.0 - transformer_weight
                }
            
            return model
        
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def get_training_args_for_best_params(self) -> Dict[str, Any]:
        """Get training arguments optimized for the best parameters"""
        if not self.best_params:
            raise ValueError("Must run optimization before getting training args")
        
        if self.model_type in ['bert', 'biobert', 'clinicalbert', 'scibert', 'hybrid']:
            return {
                'output_dir': './best_model',
                'num_train_epochs': self.best_params.get('num_epochs', 3),
                'per_device_train_batch_size': self.best_params.get('batch_size', 16),
                'per_device_eval_batch_size': self.best_params.get('batch_size', 16),
                'learning_rate': self.best_params.get('learning_rate', 2e-5),
                'weight_decay': self.best_params.get('weight_decay', 0.01),
                'warmup_steps': self.best_params.get('warmup_steps', 500),
                'logging_steps': 100,
                'eval_strategy': 'steps',
                'eval_steps': 200,
                'save_steps': 500,
                'load_best_model_at_end': True,
                'metric_for_best_model': f'eval_{self.optimization_metric}',
                'greater_is_better': True,
            }
        
        return {}


def optimize_model_hyperparameters(
    texts: List[str], 
    labels: List[List[str]],
    model_type: str = 'biobert',
    optimization_metric: str = 'f1_macro',
    n_trials: int = 20,
    timeout: Optional[int] = None,
    study_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to optimize hyperparameters for a model
    
    Args:
        texts: Training texts
        labels: Training labels  
        model_type: Type of model to optimize
        optimization_metric: Metric to optimize for
        n_trials: Number of optimization trials
        timeout: Maximum optimization time in seconds
        study_name: Optional study name for persistence
        
    Returns:
        Dictionary with optimization results
    """
    optimizer = HyperparameterOptimizer(model_type, optimization_metric)
    
    results = optimizer.optimize(
        texts=texts,
        labels=labels,
        n_trials=n_trials,
        timeout=timeout,
        study_name=study_name
    )
    
    # Add the optimizer to results for future use
    results['optimizer'] = optimizer
    
    return results
