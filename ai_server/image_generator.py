from diffusers import StableDiffusionPipeline
import torch

print("Loading Stable Diffusion model...")

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5"
)

pipe = pipe.to("cpu")

prompts = [
    "epic historical warrior cinematic lighting",
    "ancient battlefield dramatic sky",
    "historical leader portrait cinematic"
]

print("Generating images...")

for i, prompt in enumerate(prompts):
    image = pipe(prompt).images[0]
    image.save(f"image{i+1}.png")

print("Images generated!")