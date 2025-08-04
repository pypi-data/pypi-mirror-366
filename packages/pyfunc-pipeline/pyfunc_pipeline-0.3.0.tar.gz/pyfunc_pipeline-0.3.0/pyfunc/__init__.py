from .pipeline import Pipeline, pipeline, pipe
from .placeholder import Placeholder
from .utils import square, increment, half
from .errors import PipelineError

_ = Placeholder()

# Make pipe the primary entry point
__all__ = ['pipe', 'Pipeline', 'pipeline', 'Placeholder', '_', 'square', 'increment', 'half', 'PipelineError']
