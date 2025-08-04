from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

if TYPE_CHECKING:
    from furiosa_llm.models import ModelMetadata
    from furiosa_llm.models.config_types import (
        BucketWithOutputLogitsSize,
        GeneratorConfig,
        ModelRewritingConfig,
        ParallelConfig,
        PipelineMetadata,
    )
    from furiosa_llm.parallelize.pipeline import Pipeline

def get_artifact_deser_data(artifact_data: str) -> str: ...

class Artifact:
    metadata: ArtifactMetadata
    model: ModelArtifact
    speculative_model: Optional[ModelArtifact]
    version: SchemaVersion
    prefill_chunk_size: Optional[int]

    def load_without_blob(artifact_path: str) -> "Artifact": ...
    def load(
        artifact_path: str,
        devices: Optional[str],
        data_parallel_size: Optional[int],
        pipeline_parallel_size: Optional[int],
        num_blocks_per_pp_stage: Optional[Sequence[int]],
        device_mesh: Optional[Sequence[Sequence[Sequence[str]]]],
        target_buckets_with_output_logits_size: Optional[List[BucketWithOutputLogitsSize]],
    ) -> "Artifact": ...
    def override_with(
        self,
        devices: Optional[str],
        data_parallel_size: Optional[int],
        pipeline_parallel_size: Optional[int],
        num_blocks_per_pp_stage: Optional[Sequence[int]],
        device_mesh: Optional[Sequence[Sequence[Sequence[str]]]],
        target_buckets_with_output_logits_size: Optional[List[BucketWithOutputLogitsSize]],
    ) -> None: ...

class ModelArtifact:
    generator_config: GeneratorConfig
    hf_config: Dict[str, Any]
    model_metadata: ModelMetadata
    model_rewriting_config: ModelRewritingConfig
    parallel_config: ParallelConfig

    pipelines: List[Pipeline]
    pipeline_metadata_list: List[PipelineMetadata]

    max_prompt_len: Optional[int]

class ArtifactMetadata:
    artifact_id: str
    name: str
    timestamp: int
    furiosa_llm_version: str
    furiosa_compiler_version: str

class SchemaVersion:
    major: int
    minor: int
