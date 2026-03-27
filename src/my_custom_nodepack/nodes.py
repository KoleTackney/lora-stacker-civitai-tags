import hashlib
import json
import os
import requests
import folder_paths

def _load_json_from_file(file_path):
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None


def _save_dict_to_json(data_dict, file_path):
    try:
        with open(file_path, "w") as json_file:
            json.dump(data_dict, json_file, indent=4)
    except Exception as exc:
        print(f"Error saving JSON to file: {exc}")


def _get_model_version_info(hash_value):
    api_url = f"https://civitai.com/api/v1/model-versions/by-hash/{hash_value}"
    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as exc:
        print(f"Error requesting CivitAI info: {exc}")
    return None


def _calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def query_lora_stack_tags(
    lora_stack,
    query_tags,
    print_tags,
    force_fetch,
    separator,
    opt_prompt=None,
):
    if not lora_stack:
        output_tags = opt_prompt or ""
        return lora_stack, output_tags

    json_tags_path = os.path.join(os.path.dirname(__file__), "loras_tags.json")
    lora_tags = _load_json_from_file(json_tags_path) or {}

    all_tags = []
    for lora_name, _, _ in lora_stack:
        if lora_name == "None":
            continue

        cached_tags = lora_tags.get(lora_name)
        if cached_tags is not None and cached_tags:
            all_tags.extend(cached_tags)
            continue
        if cached_tags is not None and not cached_tags and not (query_tags or force_fetch):
            continue

        lora_path = folder_paths.get_full_path("loras", lora_name)
        if not lora_path:
            continue

        if query_tags or force_fetch:
            print("calculating lora hash")
            lora_sha256 = _calculate_sha256(lora_path)
            print("requesting infos")
            model_info = _get_model_version_info(lora_sha256)
            if model_info is not None and "trainedWords" in model_info:
                print("tags found!")
                lora_tags[lora_name] = model_info["trainedWords"]
                _save_dict_to_json(lora_tags, json_tags_path)
                all_tags.extend(model_info["trainedWords"])
                if print_tags:
                    print("trainedWords:", ", ".join(model_info["trainedWords"]))
            else:
                print("No information found.")
                lora_tags[lora_name] = []
                _save_dict_to_json(lora_tags, json_tags_path)

    output_tags = separator.join(all_tags)
    if opt_prompt:
        output_tags = f"{opt_prompt}{separator}{output_tags}" if output_tags else opt_prompt

    return lora_stack, output_tags


class LoraStackerTagsQuery:
    """
    Fetch CivitAI trainedWords for a LoRA stack and return a CSV string.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_stack": ("LORA_STACK",),
                "query_tags": ("BOOLEAN", {"default": True}),
                "print_tags": ("BOOLEAN", {"default": False}),
                "force_fetch": ("BOOLEAN", {"default": False}),
                "separator": ("STRING", {"default": ", "}),
            },
            "optional": {
                "opt_prompt": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("LORA_STACK", "STRING")
    RETURN_NAMES = ("LORA_STACK", "TAGS")
    FUNCTION = "query_lora_stack_tags"
    CATEGORY = "My Custom Nodes/LoRA"

    def query_lora_stack_tags(
        self,
        lora_stack,
        query_tags,
        print_tags,
        force_fetch,
        separator,
        opt_prompt=None,
    ):
        return query_lora_stack_tags(
            lora_stack, query_tags, print_tags, force_fetch, separator, opt_prompt
        )


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LoraStackerTagsQuery": LoraStackerTagsQuery,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraStackerTagsQuery": "LoRA Stacker Tags (CivitAI)",
}
