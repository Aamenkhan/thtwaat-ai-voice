import os
from diffusers import StableDiffusionPipeline
import torch

# load model
print("Loading AI image model...")

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32
)

pipe = pipe.to("cpu")

# read scenes
with open("scenes.txt","r",encoding="utf-8") as f:
    scenes = f.readlines()

# create images folder
os.makedirs("images", exist_ok=True)

print("Generating images...")

for i, scene in enumerate(scenes):

    prompt = f"cinematic documentary scene, {scene.strip()}, dramatic lighting, ultra realistic"

    image = pipe(prompt).images[0]

    path = f"images/image{i+1}.png"

    image.save(path)

    print("Image created:", path)

print("All images generated")