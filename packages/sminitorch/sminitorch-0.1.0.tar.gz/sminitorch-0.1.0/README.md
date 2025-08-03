# sminitorch

`sminitorch` (Small/Mini Torch) es un framework de deep learning educativo y minimalista inspirado en PyTorch. Proporciona Tensores con diferenciación automática (autograd) y componentes básicos para construir redes neuronales.

Utiliza `micronumpy` como su backend para las operaciones numéricas, manteniendo todo el ecosistema en Python puro.

## Características

- `sminitorch.Tensor`: un contenedor para `micronumpy.ndarray` con autograd.
- `sminitorch.nn`: Módulos para construir redes (`Linear`, `ReLU`, `Tanh`).
- `sminitorch.optim`: Optimizadores como `SGD`.
