# LoRA Stacker CivitAI Tags

Automatically fetches the trained trigger words (tags) for every LoRA in a stack from CivitAI and returns them as a ready-to-use prompt string.

> [!WARNING]
> **This node requires [Efficiency Nodes for ComfyUI](https://github.com/jags111/efficiency-nodes-comfyui).**
> It consumes the `LORA_STACK` type produced by the *Efficient Loader* / *LoRA Stacker* nodes in that pack.
> Install it first — this node will not function without it.
>
> - Registry: https://registry.comfy.org/nodes/efficiency-nodes-comfyui
> - GitHub: https://github.com/jags111/efficiency-nodes-comfyui

## Quickstart

1. Install [ComfyUI](https://docs.comfy.org/get_started).
1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager).
1. Install **[Efficiency Nodes for ComfyUI](https://registry.comfy.org/nodes/efficiency-nodes-comfyui)** (required dependency — see warning above).
1. Look up **LoRA Stacker CivitAI Tags** in ComfyUI-Manager and install it. If installing manually, clone this repository under `ComfyUI/custom_nodes`.
1. Restart ComfyUI.

# Features

- **LoRA Stacker Tags (CivitAI)** — Given a `LORA_STACK`, looks up each LoRA's trained trigger words on CivitAI via its SHA-256 hash and returns them as a single comma-separated string ready to inject into a prompt.
- Passes the `LORA_STACK` through unchanged (fully compatible with Efficiency nodes and similar stacker nodes).
- Caches results in `loras_tags.json` alongside the node so repeat runs don't hit the API.
- `force_fetch` flag bypasses the cache and re-queries CivitAI.
- Optionally prepends an existing prompt string via the `opt_prompt` input.

## Nodes

### LoRA Stacker Tags (CivitAI) — `LoraStackerTagsQuery`

**Inputs**

| Name | Type | Description |
|---|---|---|
| `lora_stack` | `LORA_STACK` | Stack of LoRA models from a LoRA stacker node |
| `query_tags` | `BOOLEAN` | Query CivitAI for LoRAs not already cached (default: `true`) |
| `print_tags` | `BOOLEAN` | Print retrieved tags to the ComfyUI console (default: `false`) |
| `force_fetch` | `BOOLEAN` | Ignore cache and re-fetch from CivitAI (default: `false`) |
| `separator` | `STRING` | Delimiter placed between tags (default: `", "`) |
| `opt_prompt` | `STRING` | *(optional)* Prompt string to prepend before the tags |

**Outputs**

| Name | Type | Description |
|---|---|---|
| `LORA_STACK` | `LORA_STACK` | Pass-through, unchanged |
| `TAGS` | `STRING` | Trained words from CivitAI, joined by `separator` |

**Dependencies:** `requests` (installed automatically). Requires internet access to query the CivitAI API.

## Develop

To install the dev dependencies and pre-commit (will run the ruff hook), do:

```bash
cd lora-stacker-civitai-tags
pip install -e .[dev]
pre-commit install
```

The `-e` flag above will result in a "live" install, in the sense that any changes you make to your node extension will automatically be picked up the next time you run ComfyUI.

## Publish to Github

Install Github Desktop or follow these [instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for ssh.

1. Create a Github repository that matches the directory name. 
2. Push the files to Git
```
git add .
git commit -m "project scaffolding"
git push
``` 

## Writing custom nodes

An example custom node is located in [node.py](src/my_custom_nodepack/nodes.py). To learn more, read the [docs](https://docs.comfy.org/essentials/custom_node_overview).


## Tests

This repo contains unit tests written in Pytest in the `tests/` directory. It is recommended to unit test your custom node.

- [build-pipeline.yml](.github/workflows/build-pipeline.yml) will run pytest and linter on any open PRs
- [validate.yml](.github/workflows/validate.yml) will run [node-diff](https://github.com/Comfy-Org/node-diff) to check for breaking changes

## Publishing to Registry

If you wish to share this custom node with others in the community, you can publish it to the registry. We've already auto-populated some fields in `pyproject.toml` under `tool.comfy`, but please double-check that they are correct.

You need to make an account on https://registry.comfy.org and create an API key token.

- [ ] Go to the [registry](https://registry.comfy.org). Login and create a publisher id (everything after the `@` sign on your registry profile). 
- [ ] Add the publisher id into the pyproject.toml file.
- [ ] Create an api key on the Registry for publishing from Github. [Instructions](https://docs.comfy.org/registry/publishing#create-an-api-key-for-publishing).
- [ ] Add it to your Github Repository Secrets as `REGISTRY_ACCESS_TOKEN`.

A Github action will run on every git push. You can also run the Github action manually. Full instructions [here](https://docs.comfy.org/registry/publishing). Join our [discord](https://discord.com/invite/comfyorg) if you have any questions!

