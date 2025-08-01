---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- dense
- generated_from_trainer
- dataset_size:1600
- loss:CosineSimilarityLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: 'Position: Frontend Developer


    Requirements:

    • 2+ years frontend

    • modern frameworks

    • design sense


    Required Skills:

    • JavaScript

    • React

    • Angular

    • CSS

    • Vue.js


    Responsibilities:

    • web development

    • UI/UX

    • responsive design

    '
  sentences:
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in frontend developer


    EXPERIENCE

    • Developed responsive web applications using React

    • Collaborated with UX designers on user interfaces

    • Optimized website performance and accessibility


    SKILLS

    Microsoft Office, Customer Service, Sales, Marketing


    EDUCATION

    Bachelor of Arts in Web Design

    '
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in software engineer


    EXPERIENCE

    • Developed web applications using Python and Django

    • Built REST APIs for mobile applications

    • Implemented automated testing and CI/CD pipelines


    SKILLS

    Python, Java, JavaScript, SQL, Git, Django, REST API


    EDUCATION

    Bachelor of Science in Computer Science

    '
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in frontend developer


    EXPERIENCE

    • Developed responsive web applications using React

    • Collaborated with UX designers on user interfaces

    • Optimized website performance and accessibility


    SKILLS

    JavaScript, React, HTML5, CSS3, TypeScript, Redux


    EDUCATION

    Bachelor of Arts in Web Design

    '
- source_sentence: 'Position: Software Engineer


    Requirements:

    • Bachelor degree

    • 2+ years experience

    • problem solving


    Required Skills:

    • SQL

    • Git

    • API

    • JavaScript

    • Java


    Responsibilities:

    • software development

    • coding

    • programming

    '
  sentences:
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in frontend developer


    EXPERIENCE

    • Developed responsive web applications using React

    • Collaborated with UX designers on user interfaces

    • Optimized website performance and accessibility


    SKILLS

    JavaScript, React, HTML5, Excel, Communication, Leadership


    EDUCATION

    Bachelor of Arts in Web Design

    '
  - ''
  - ''
- source_sentence: 'Position: Product Manager


    Requirements:

    • MBA preferred

    • technical background

    • leadership


    Required Skills:

    • Roadmapping

    • Analytics

    • Agile

    • JIRA

    • Scrum


    Responsibilities:

    • product strategy

    • stakeholder management

    • market analysis

    '
  sentences:
  - ''
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in frontend developer


    EXPERIENCE

    • Developed responsive web applications using React

    • Collaborated with UX designers on user interfaces

    • Optimized website performance and accessibility


    SKILLS

    JavaScript, React, HTML5, CSS3, TypeScript, Redux


    EDUCATION

    Bachelor of Arts in Web Design

    '
  - ''
- source_sentence: 'Position: Product Manager


    Requirements:

    • MBA preferred

    • technical background

    • leadership


    Required Skills:

    • Analytics

    • Agile

    • Roadmapping

    • JIRA

    • Scrum


    Responsibilities:

    • product strategy

    • stakeholder management

    • market analysis

    '
  sentences:
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in data scientist


    EXPERIENCE

    • Built machine learning models for predictive analytics

    • Analyzed large datasets using Python and R

    • Created data visualizations and statistical reports


    SKILLS

    Python, R, Machine Learning, Statistics, Pandas, Scikit-learn


    EDUCATION

    Master of Science in Data Science

    '
  - ''
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in frontend developer


    EXPERIENCE

    • Developed responsive web applications using React

    • Collaborated with UX designers on user interfaces

    • Optimized website performance and accessibility


    SKILLS

    JavaScript, React, HTML5, Excel, Communication, Leadership


    EDUCATION

    Bachelor of Arts in Web Design

    '
- source_sentence: 'Position: DevOps Engineer


    Requirements:

    • cloud experience

    • automation tools

    • scripting


    Required Skills:

    • Docker

    • Kubernetes

    • AWS

    • Terraform

    • CI/CD


    Responsibilities:

    • infrastructure

    • automation

    • deployment

    '
  sentences:
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in frontend developer


    EXPERIENCE

    • Developed responsive web applications using React

    • Collaborated with UX designers on user interfaces

    • Optimized website performance and accessibility


    SKILLS

    Microsoft Office, Customer Service, Sales, Marketing


    EDUCATION

    Bachelor of Arts in Web Design

    '
  - ''
  - 'PROFESSIONAL SUMMARY

    Experienced professional with background in data scientist


    EXPERIENCE

    • Built machine learning models for predictive analytics

    • Analyzed large datasets using Python and R

    • Created data visualizations and statistical reports


    SKILLS

    Microsoft Office, Customer Service, Sales, Marketing


    EDUCATION

    Master of Science in Data Science

    '
pipeline_tag: sentence-similarity
library_name: sentence-transformers
metrics:
- pearson_cosine
- spearman_cosine
model-index:
- name: SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2
  results:
  - task:
      type: semantic-similarity
      name: Semantic Similarity
    dataset:
      name: resume job eval
      type: resume-job-eval
    metrics:
    - type: pearson_cosine
      value: 0.8415691944374307
      name: Pearson Cosine
    - type: spearman_cosine
      value: 0.8243601414941
      name: Spearman Cosine
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/UKPLab/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 256, 'do_lower_case': False, 'architecture': 'BertModel'})
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
  (2): Normalize()
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Position: DevOps Engineer\n\nRequirements:\n• cloud experience\n• automation tools\n• scripting\n\nRequired Skills:\n• Docker\n• Kubernetes\n• AWS\n• Terraform\n• CI/CD\n\nResponsibilities:\n• infrastructure\n• automation\n• deployment\n',
    '',
    'PROFESSIONAL SUMMARY\nExperienced professional with background in data scientist\n\nEXPERIENCE\n• Built machine learning models for predictive analytics\n• Analyzed large datasets using Python and R\n• Created data visualizations and statistical reports\n\nSKILLS\nMicrosoft Office, Customer Service, Sales, Marketing\n\nEDUCATION\nMaster of Science in Data Science\n',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.7613, 0.1896],
#         [0.7613, 1.0000, 0.2258],
#         [0.1896, 0.2258, 1.0000]])
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Semantic Similarity

* Dataset: `resume-job-eval`
* Evaluated with [<code>EmbeddingSimilarityEvaluator</code>](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html#sentence_transformers.evaluation.EmbeddingSimilarityEvaluator)

| Metric              | Value      |
|:--------------------|:-----------|
| pearson_cosine      | 0.8416     |
| **spearman_cosine** | **0.8244** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 1,600 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                         | sentence_1                                                                        | label                                                          |
  |:--------|:-----------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                             | string                                                                            | float                                                          |
  | details | <ul><li>min: 41 tokens</li><li>mean: 46.51 tokens</li><li>max: 54 tokens</li></ul> | <ul><li>min: 2 tokens</li><li>mean: 35.01 tokens</li><li>max: 64 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.55</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                          | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                      | label                            |
  |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|
  | <code>Position: Data Scientist<br><br>Requirements:<br>• Masters/PhD preferred<br>• statistical background<br>• programming<br><br>Required Skills:<br>• Python<br>• NumPy<br>• Statistics<br>• R<br>• Machine Learning<br><br>Responsibilities:<br>• data analysis<br>• statistical modeling<br>• machine learning<br></code>      | <code>PROFESSIONAL SUMMARY<br>Experienced professional with background in data scientist<br><br>EXPERIENCE<br>• Built machine learning models for predictive analytics<br>• Analyzed large datasets using Python and R<br>• Created data visualizations and statistical reports<br><br>SKILLS<br>Python, R, Machine Learning, Statistics, Pandas, Scikit-learn<br><br>EDUCATION<br>Master of Science in Data Science<br></code> | <code>0.9245688685853339</code>  |
  | <code>Position: Data Scientist<br><br>Requirements:<br>• Masters/PhD preferred<br>• statistical background<br>• programming<br><br>Required Skills:<br>• Pandas<br>• Machine Learning<br>• Python<br>• NumPy<br>• Statistics<br><br>Responsibilities:<br>• data analysis<br>• statistical modeling<br>• machine learning<br></code> | <code>PROFESSIONAL SUMMARY<br>Experienced professional with background in software engineer<br><br>EXPERIENCE<br>• Developed web applications using Python and Django<br>• Built REST APIs for mobile applications<br>• Implemented automated testing and CI/CD pipelines<br><br>SKILLS<br>Microsoft Office, Customer Service, Sales, Marketing<br><br>EDUCATION<br>Bachelor of Science in Computer Science<br></code>          | <code>0.06412046932803538</code> |
  | <code>Position: DevOps Engineer<br><br>Requirements:<br>• cloud experience<br>• automation tools<br>• scripting<br><br>Required Skills:<br>• CI/CD<br>• Terraform<br>• Kubernetes<br>• Docker<br>• AWS<br><br>Responsibilities:<br>• infrastructure<br>• automation<br>• deployment<br></code>                                      | <code></code>                                                                                                                                                                                                                                                                                                                                                                                                                   | <code>0.824642637812928</code>   |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `eval_strategy`: steps
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `num_train_epochs`: 4
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: steps
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 4
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch | Step | resume-job-eval_spearman_cosine |
|:-----:|:----:|:-------------------------------:|
| 1.0   | 100  | 0.7890                          |
| 2.0   | 200  | 0.8207                          |
| 3.0   | 300  | 0.8244                          |


### Framework Versions
- Python: 3.13.5
- Sentence Transformers: 5.0.0
- Transformers: 4.54.1
- PyTorch: 2.7.1+cpu
- Accelerate: 1.9.0
- Datasets: 4.0.0
- Tokenizers: 0.21.4

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->