# demo/app.py

import gradio as gr
import torch
import time
import logging
import random
import numpy as np
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
import threading
import queue
import spaces

# Import the component and ALL its utilities
from gradio_livelog import LiveLog 
from gradio_livelog.utils import ProgressTracker, capture_logs

# --- 1. LOGIC FOR THE "LIVELOG FEATURE DEMO" TAB ---

# Configure logging for the demo
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_process(disable_console: bool, run_error_case: bool):
    """
    The generator function for the interactive feature demo.
    """
    with capture_logs(disable_console=disable_console) as get_logs:
        total_steps = 100
        tracker = ProgressTracker(total=total_steps, description="Simulating a process...")
        logging.info(f"Starting simulated process with {total_steps} steps...")
        for record in get_logs(): yield {"type": "log", "level": record.levelname, "content": record.getMessage()}
        for i in range(total_steps):
            time.sleep(0.03)
            current_step = i + 1
            if current_step == 10: logging.warning(f"Low disk space warning at step {current_step}.")
            elif current_step == 30: logging.log(logging.INFO + 5, f"Asset pack loaded successfully at step {current_step}.")
            elif current_step == 75: logging.critical(f"Checksum mismatch! Data may be corrupt at step {current_step}.")
            if run_error_case and current_step == 50:
                logging.error("A fatal simulation error occurred! Aborting.")
                for record in get_logs(): yield {"type": "log", "level": record.levelname, "content": record.getMessage()}
                yield tracker.update(advance=0, status="error")
                return
            yield tracker.update()
            for record in get_logs():
                level_name = "SUCCESS" if record.levelno == logging.INFO + 5 else record.levelname
                yield {"type": "log", "level": level_name, "content": record.getMessage()}
        logging.log(logging.INFO + 5, "Process completed successfully!")
        for record in get_logs():
            level_name = "SUCCESS" if record.levelno == logging.INFO + 5 else record.levelname
            yield {"type": "log", "level": level_name, "content": record.getMessage()}
        yield tracker.update(advance=0, status="success")

def update_livelog_properties(mode, color, lines, scroll):
    return gr.update(display_mode=mode, background_color=color, line_numbers=lines, autoscroll=scroll)

def clear_output():
    return None

def run_success_case(disable_console: bool):
    yield from run_process(disable_console=disable_console, run_error_case=False)

def run_error_case(disable_console: bool):
    yield from run_process(disable_console=disable_console, run_error_case=True)


# --- 2. LOGIC FOR THE "Diffusion Pipeline Integration" TAB ---
MODEL_ID = "SG161222/RealVisXL_V5.0"
MAX_SEED = np.iinfo(np.int32).max

print("Loading Stable Diffusion model... This may take a moment.")
pipe = StableDiffusionXLPipeline.from_pretrained(
    MODEL_ID, torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False
)
pipe.enable_vae_tiling()
pipe.enable_model_cpu_offload()
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
print("Model loaded successfully.")
pipe.set_progress_bar_config(disable=True)

@spaces.GPU(duration=60, enable_queue=True)
def run_diffusion_in_thread(prompt: str, update_queue: queue.Queue):
    """This function contains the blocking pipe() call and runs in a worker thread."""
    tracker = None
    try:
        seed = random.randint(0, MAX_SEED)
        generator = torch.Generator(device="cuda").manual_seed(seed)
        prompt_style = f"hyper-realistic 8K image of {prompt}. ultra-detailed, lifelike, high-resolution, sharp, vibrant colors, photorealistic"
        negative_prompt_style = "cartoonish, low resolution, blurry, simplistic, abstract, deformed, ugly"
        num_inference_steps = 20
        
        update_queue.put((None, {"type": "log", "level": "INFO", "content": f"Using seed: {seed}"}))
        update_queue.put((None, {"type": "log", "level": "INFO", "content": "Starting diffusion process..."}))
        
        tracker = ProgressTracker(total=num_inference_steps, description="Diffusion Steps")

        def progress_callback(pipe_instance, step, timestep, callback_kwargs):
            update_dict = tracker.update()
            update_queue.put((None, update_dict))
            return callback_kwargs
            
        images = pipe(
            prompt=prompt_style, 
            negative_prompt=negative_prompt_style, 
            width=1024, 
            height=1024,
            guidance_scale=3.0, 
            num_inference_steps=num_inference_steps, 
            generator=generator,
            callback_on_step_end=progress_callback
        ).images

        update_queue.put((images, {"type": "log", "level": "SUCCESS", "content": "Image generated successfully!"}))
        final_update = tracker.update(advance=0, status="success")
        update_queue.put((images, final_update))

    except Exception as e:
        logging.error(f"Error in diffusion thread: {e}", exc_info=True)
        if tracker:
            error_update = tracker.update(advance=0, status="error")
            update_queue.put((None, error_update))
        update_queue.put((None, {"type": "log", "level": "ERROR", "content": f"An error occurred: {e}"}))
    finally:
        update_queue.put(None)

def generate(prompt):
    """This function starts the worker thread and yields updates from the queue."""
    yield None, {"type": "log", "level": "INFO", "content": "Preparing generation..."}
    update_queue = queue.Queue()
    diffusion_thread = threading.Thread(target=run_diffusion_in_thread, args=(prompt, update_queue))
    diffusion_thread.start()
    while True:
        update = update_queue.get()
        if update is None: break
        yield update


# --- 3. THE COMBINED GRADIO UI with TABS ---
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.HTML("<h1><center>LiveLog Component Showcase</center></h1>")

    with gr.Tabs():
       
        with gr.TabItem("LiveLog Feature Demo"):
            gr.Markdown("### Test all features of the LiveLog component interactively.")
            with gr.Row():
                with gr.Column(scale=3):
                    feature_logger = LiveLog(
                        label="Process Output", line_numbers=True, height=550,
                        background_color="#000000", display_mode="full"
                    )
                with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### Component Properties")
                        display_mode_radio = gr.Radio(["full", "log", "progress"], label="Display Mode", value="full")
                        bg_color_picker = gr.ColorPicker(label="Background Color", value="#000000")
                        line_numbers_checkbox = gr.Checkbox(label="Show Line Numbers", value=True)
                        autoscroll_checkbox = gr.Checkbox(label="Autoscroll", value=True)
                    with gr.Group():
                        gr.Markdown("### Simulation Controls")
                        disable_console_checkbox = gr.Checkbox(label="Disable Python Console Output", value=False)
                        start_btn = gr.Button("Run Success Case", variant="primary")
                        error_btn = gr.Button("Run Error Case")
            
            start_btn.click(fn=run_success_case, inputs=[disable_console_checkbox], outputs=feature_logger)
            error_btn.click(fn=run_error_case, inputs=[disable_console_checkbox], outputs=feature_logger)
            feature_logger.clear(fn=clear_output, inputs=None, outputs=[feature_logger])
            controls = [display_mode_radio, bg_color_picker, line_numbers_checkbox, autoscroll_checkbox]
            for control in controls:
                control.change(fn=update_livelog_properties, inputs=controls, outputs=feature_logger)
        with gr.TabItem("Diffusion Pipeline Integration"):
            gr.Markdown("### Use `LiveLog` to monitor a real image generation process.")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Group():
                        prompt = gr.Textbox(
                            label="Enter your prompt", show_label=False,
                            placeholder="A cinematic photo of a robot in a floral garden...",
                            scale=8, container=False
                        )
                        run_button = gr.Button("Generate", scale=1, variant="primary")
                    
                    livelog_viewer = LiveLog(
                        label="Process Monitor", height=250, display_mode="full", line_numbers=False, disable_console=True
                    )
                
                with gr.Column(scale=2):
                    result_gallery = gr.Gallery(
                        label="Result", columns=1, show_label=False, height=500, min_width=768
                    )

            run_button.click(fn=generate, inputs=[prompt], outputs=[result_gallery, livelog_viewer])
            prompt.submit(fn=generate, inputs=[prompt], outputs=[result_gallery, livelog_viewer])

if __name__ == "__main__":
    demo.queue(max_size=50).launch(debug=True)