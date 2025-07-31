---
title: doteval
hide:
  - navigation
  - toc
  - feedback
---

#

<div class="index-container" markdown style="max-width: 800px; margin: 0 auto;">

<figure markdown>
  ![doteval](assets/images/doteval.svg){ width="200" }
</figure>

<center>
    <h1 class="title">Simple, Powerful LLM Evaluation</h1>
    <p class="subtitle">Simple, powerful, and extensible evaluation framework for Large Language Models</p>

    <a href="welcome.md">Get started</a> • <a href="https://github.com/dottxt-ai/doteval">View on GitHub</a>

<div class="index-pre-code">
```bash
pip install dottxt-eval
```
</div>
</center>

---

## Quick Example

Evaluate your model on the GSM8K math dataset in just a few lines:

```python title="eval_gsm8k.py"
import functools
from doteval import foreach
from doteval.evaluators import exact_match

@foreach("question,answer", gsm8k_dataset())
def eval_gsm8k(question, answer, generator, template):
    """Evaluate model performance on GSM8K math problems."""
    prompt = template(question=question)
    result = generator(prompt, max_tokens=100)
    return exact_match(result, answer)
```

Run it with pytest:

```bash
pytest eval_gsm8k.py::eval_gsm8k --experiment gsm8k_eval
```

View results:

```bash
doteval show gsm8k_eval
```

## Why doteval?

<div class="grid cards" markdown>

-   :fontawesome-solid-code: **Simple API**

    ---

    Define evaluations with just a decorator. No complex setup required.

    ```python
    @foreach("question,answer", dataset)
    def eval_model(question, answer, model):
        response = model.generate(question)
        return exact_match(response, answer)
    ```

-   :fontawesome-solid-flask: **pytest Integration**

    ---

    Run evaluations as tests with full pytest ecosystem support.

    ```bash
    pytest eval_gsm8k.py --experiment my_eval
    ```

</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-clock-rotate-left: **Automatic Resumption**

    ---

    Resume interrupted evaluations automatically. Track progress across runs.

    ```bash
    doteval list
    doteval show my_eval_session
    ```

-   :fontawesome-solid-bolt: **Scalable**

    ---

    Scale evaluations with built-in async support and concurrency control.

    ```python
    @foreach("prompt,expected", dataset)
    async def eval_async(prompt, expected, model):
        return await model.generate_async(prompt)
    ```

</div>

---

## Documentation

<div class="grid cards" markdown>

-   :fontawesome-solid-rocket: **[Getting Started](welcome.md)**

    ---

    New to doteval? Start here for installation, quickstart, and core concepts.

-   :fontawesome-solid-graduation-cap: **[Tutorials](tutorials/01-your-first-evaluation.md)**

    ---

    Step-by-step guides from your first evaluation to production deployment.

-   :fontawesome-solid-wrench: **[How-To Guides](how-to/index.md)**

    ---

    Problem-focused guides for structured generation, debugging, and production issues.

-   :fontawesome-solid-book: **[Reference](reference/index.md)**

    ---

    Complete API documentation and technical reference materials.

</div>

---

<div class="footer-info" markdown>

Built with ❤️ by [dottxt](https://dottxt.co) • [GitHub](https://github.com/dottxt-ai/doteval) • [PyPI](https://pypi.org/project/dottxt-eval/)

</div>

</div>
