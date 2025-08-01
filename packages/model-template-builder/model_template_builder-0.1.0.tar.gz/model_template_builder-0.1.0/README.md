# Model Template Builder

### a tool for dockerizing vLLM models into a docker container

#### Usage
```shell
virtualenv .venv
source .venv/bin/activate
python main.py --model_name <your-model-name> --image_name <your-image-name>
```

#### or
```python
from model_template_builder.dockerize import dockerize_hugging_face_model_vllm

dockerize_hugging_face_model_vllm(model_name='your-model-name', image_name='your-image-name')
```