import os
import requests
from PIL import Image
from io import BytesIO
import re
import random

def GenerateImage(prompts, output_paths, width=1024, height=1024, nologo=True, seed=12345):
    """
    Generates one or more images using the Pollinations AI API and saves them locally.

    Parameters:
    ----------
    prompts : str or list of str
        A single prompt string, or a list of prompt strings for image generation.
    
    output_paths : str or list of str
        A single output path (filename ending in .png, .jpg or .jpeg), or a list of such paths matching the number of prompts.

    width : int, optional
        Width of the generated image(s). Default is 1024.
    
    height : int, optional
        Height of the generated image(s). Default is 1024.
    
    nologo : bool, optional
        Whether to request images without logo/branding. Default is True.
    
    seed : int, str, or None, optional
        Seed value for image randomness. Use an integer for deterministic results.
        If "random" or None, a new random seed is used per image. Default is 12345.

    Returns:
    -------
    list of str
        A list of messages indicating success or failure for each image generation.
    """

    # Normalize inputs
    if isinstance(prompts, str): prompts = [prompts]
    if isinstance(output_paths, str): output_paths = [output_paths]

    # Validate
    if not isinstance(prompts, list) or not all(isinstance(p, str) and p.strip() for p in prompts):
        raise ValueError("❌ Prompts must be non-empty strings.")
    
    valid_ext_pattern = re.compile(r".+\.(png|jpg|jpeg)$", re.IGNORECASE)
    if not isinstance(output_paths, list) or not all(isinstance(p, str) and valid_ext_pattern.match(p) for p in output_paths):
        raise ValueError("❌ Output paths must end with .png, .jpg, or .jpeg")

    if len(prompts) != len(output_paths):
        raise ValueError("❌ Number of prompts and output paths must match.")

    results = []

    for prompt, out_path in zip(prompts, output_paths):
        try:
            directory = os.path.dirname(out_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            used_seed = random.randint(1, 999999) if seed in [None, "random"] else int(seed)
            encoded_prompt = prompt.replace(' ', '%20')

            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            url += f"?nologo={'true' if nologo else 'false'}&width={width}&height={height}&seed={used_seed}"

            try:
                response = requests.get(url, timeout=15)
            except requests.exceptions.Timeout:
                raise TimeoutError(f"❌ Timeout for prompt: '{prompt}'")

            if response.status_code != 200:
                raise RuntimeError(f"❌ HTTP {response.status_code} error for prompt: '{prompt}'")

            image = Image.open(BytesIO(response.content))
            image.save(out_path, quality=100, optimize=False)
            results.append(f"✅ Image for prompt '{prompt}' (seed={used_seed}) saved to '{out_path}'")

        except Exception as e:
            raise RuntimeError(f"❌ Error generating image for prompt '{prompt}': {e}")

    return results
