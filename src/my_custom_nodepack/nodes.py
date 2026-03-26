from inspect import cleandoc
import hashlib
import json
import os
import requests

import folder_paths
class Example:
    """
    A example node

    Class methods
    -------------
    INPUT_TYPES (dict):
        Tell the main program input parameters of nodes.
    IS_CHANGED:
        optional method to control when the node is re executed.

    Attributes
    ----------
    RETURN_TYPES (`tuple`):
        The type of each element in the output tulple.
    RETURN_NAMES (`tuple`):
        Optional: The name of each output in the output tulple.
    FUNCTION (`str`):
        The name of the entry-point method. For example, if `FUNCTION = "execute"` then it will run Example().execute()
    OUTPUT_NODE ([`bool`]):
        If this node is an output node that outputs a result/image from the graph. The SaveImage node is an example.
        The backend iterates on these output nodes and tries to execute all their parents if their parent graph is properly connected.
        Assumed to be False if not present.
    CATEGORY (`str`):
        The category the node should appear in the UI.
    execute(s) -> tuple || None:
        The entry point method. The name of this method must be the same as the value of property `FUNCTION`.
        For example, if `FUNCTION = "execute"` then this method's name must be `execute`, if `FUNCTION = "foo"` then it must be `foo`.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
            Return a dictionary which contains config for all input fields.
            Some types (string): "MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT".
            Input types "INT", "STRING" or "FLOAT" are special values for fields on the node.
            The type can be a list for selection.

            Returns: `dict`:
                - Key input_fields_group (`string`): Can be either required, hidden or optional. A node class must have property `required`
                - Value input_fields (`dict`): Contains input fields config:
                    * Key field_name (`string`): Name of a entry-point method's argument
                    * Value field_config (`tuple`):
                        + First value is a string indicate the type of field or a list for selection.
                        + Secound value is a config for type "INT", "STRING" or "FLOAT".
        """
        return {
            "required": {
                "image": ("Image", { "tooltip": "This is an image"}),
                "int_field": ("INT", {
                    "default": 0,
                    "min": 0, #Minimum value
                    "max": 4096, #Maximum value
                    "step": 64, #Slider's step
                    "display": "number" # Cosmetic only: display as "number" or "slider"
                }),
                "float_field": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001, #The value represeting the precision to round to, will be set to the step value by default. Can be set to False to disable rounding.
                    "display": "number"}),
                "print_to_screen": (["enable", "disable"],),
                "string_field": ("STRING", {
                    "multiline": False, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "Hello World!"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    #RETURN_NAMES = ("image_output_name",)
    DESCRIPTION = cleandoc(__doc__)
    FUNCTION = "test"

    #OUTPUT_NODE = False
    #OUTPUT_TOOLTIPS = ("",) # Tooltips for the output node

    CATEGORY = "Example"

    def test(self, image, string_field, int_field, float_field, print_to_screen):
        if print_to_screen == "enable":
            print(f"""Your input contains:
                string_field aka input text: {string_field}
                int_field: {int_field}
                float_field: {float_field}
            """)
        #do some processing on the image, in this example I just invert it
        image = 1.0 - image
        return (image,)

    """
        The node will always be re executed if any of the inputs change but
        this method can be used to force the node to execute again even when the inputs don't change.
        You can make this node return a number or a string. This value will be compared to the one returned the last time the node was
        executed, if it is different the node will be executed again.
        This method is used in the core repo for the LoadImage node where they return the image hash as a string, if the image hash
        changes between executions the LoadImage node is executed again.
    """
    #@classmethod
    #def IS_CHANGED(s, image, string_field, int_field, float_field, print_to_screen):
    #    return ""


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
        if not lora_stack:
            output_tags = opt_prompt or ""
            return (lora_stack, output_tags)

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
                    print("No informations found.")
                    lora_tags[lora_name] = []
                    _save_dict_to_json(lora_tags, json_tags_path)

        output_tags = separator.join(all_tags)
        if opt_prompt:
            output_tags = f"{opt_prompt}{separator}{output_tags}" if output_tags else opt_prompt

        return (lora_stack, output_tags)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Example": Example,
    "LoraStackerTagsQuery": LoraStackerTagsQuery,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node",
    "LoraStackerTagsQuery": "LoRA Stacker Tags (CivitAI)",
}
