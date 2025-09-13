import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinterdnd2 as tkdnd
from PIL import Image, ImageTk
import requests
from io import BytesIO
import numpy as np
from sklearn.cluster import KMeans
import os

class PixelArtConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Art Converter")
        self.root.geometry("1200x700")
        
        # Variables
        self.original_image = None
        self.pixel_art_image = None
        self.palette_colors = []
        
        # Settings variables
        self.pixel_size = tk.IntVar(value=8)
        self.color_count = tk.IntVar(value=16)
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        
        # New canvas settings
        self.canvas_width = tk.IntVar(value=96)
        self.canvas_height = tk.IntVar(value=96)
        self.proportional_resize = tk.BooleanVar(value=True)
        self.transparent_background = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎨 Pixel Art Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Left panel - Settings
        self.create_settings_panel(main_frame)
        
        # Center panel - Image display
        self.create_image_panel(main_frame)
        
        # Right panel - Palette and controls
        self.create_control_panel(main_frame)
        
    def create_settings_panel(self, parent):
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Canvas Size Settings
        canvas_frame = ttk.LabelFrame(settings_frame, text="Canvas Size", padding="5")
        canvas_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Width setting
        ttk.Label(canvas_frame, text="Width:").grid(row=0, column=0, sticky="w")
        width_spinbox = ttk.Spinbox(canvas_frame, from_=16, to=512, width=8,
                                   textvariable=self.canvas_width)
        width_spinbox.grid(row=0, column=1, padx=(5, 10))
        
        # Height setting
        ttk.Label(canvas_frame, text="Height:").grid(row=0, column=2, sticky="w")
        height_spinbox = ttk.Spinbox(canvas_frame, from_=16, to=512, width=8,
                                    textvariable=self.canvas_height)
        height_spinbox.grid(row=0, column=3, padx=5)
        
        # Proportional resize checkbox
        prop_check = ttk.Checkbutton(canvas_frame, text="Proportional resize",
                                    variable=self.proportional_resize)
        prop_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Transparent background checkbox
        trans_check = ttk.Checkbutton(canvas_frame, text="Transparent background",
                                     variable=self.transparent_background)
        trans_check.grid(row=1, column=2, columnspan=2, sticky="w", pady=5)
        
        # Preset buttons
        preset_frame = ttk.Frame(canvas_frame)
        preset_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        presets = [("32×32", 32, 32), ("64×64", 64, 64), ("96×96", 96, 96), 
                  ("128×128", 128, 128), ("256×256", 256, 256)]
        
        for i, (name, w, h) in enumerate(presets):
            btn = ttk.Button(preset_frame, text=name, width=8,
                           command=lambda w=w, h=h: self.set_canvas_size(w, h))
            btn.grid(row=0, column=i, padx=2)
        
        # Pixel size setting
        ttk.Label(settings_frame, text="Pixel Size:").grid(row=1, column=0, 
                                                           sticky="w", pady=2)
        pixel_scale = ttk.Scale(settings_frame, from_=2, to=20, 
                               variable=self.pixel_size, orient="horizontal")
        pixel_scale.grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Label(settings_frame, textvariable=self.pixel_size).grid(row=2, column=1, 
                                                                    padx=(5, 0))
        
        # Color count setting
        ttk.Label(settings_frame, text="Colors:").grid(row=3, column=0, 
                                                      sticky="w", pady=(10, 2))
        color_scale = ttk.Scale(settings_frame, from_=4, to=64, 
                               variable=self.color_count, orient="horizontal")
        color_scale.grid(row=4, column=0, sticky="ew", pady=2)
        ttk.Label(settings_frame, textvariable=self.color_count).grid(row=4, column=1, 
                                                                     padx=(5, 0))
        
        # Brightness setting
        ttk.Label(settings_frame, text="Brightness:").grid(row=5, column=0, 
                                                           sticky="w", pady=(10, 2))
        brightness_scale = ttk.Scale(settings_frame, from_=0.3, to=2.0, 
                                    variable=self.brightness, orient="horizontal")
        brightness_scale.grid(row=6, column=0, sticky="ew", pady=2)
        brightness_label = ttk.Label(settings_frame, text="1.0")
        brightness_label.grid(row=6, column=1, padx=(5, 0))
        
        # Update brightness label
        def update_brightness_label(*args):
            brightness_label.config(text=f"{self.brightness.get():.1f}")
        self.brightness.trace('w', update_brightness_label)
        
        # Contrast setting
        ttk.Label(settings_frame, text="Contrast:").grid(row=7, column=0, 
                                                         sticky="w", pady=(10, 2))
        contrast_scale = ttk.Scale(settings_frame, from_=0.3, to=2.0, 
                                  variable=self.contrast, orient="horizontal")
        contrast_scale.grid(row=8, column=0, sticky="ew", pady=2)
        contrast_label = ttk.Label(settings_frame, text="1.0")
        contrast_label.grid(row=8, column=1, padx=(5, 0))
        
        # Update contrast label
        def update_contrast_label(*args):
            contrast_label.config(text=f"{self.contrast.get():.1f}")
        self.contrast.trace('w', update_contrast_label)
        
        # Convert button
        convert_btn = ttk.Button(settings_frame, text="Convert to Pixel Art", 
                                command=self.convert_to_pixel_art)
        convert_btn.grid(row=9, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        
        # Reset button
        reset_btn = ttk.Button(settings_frame, text="Reset Settings", 
                              command=self.reset_settings)
        reset_btn.grid(row=10, column=0, columnspan=2, pady=2, sticky="ew")
        
        settings_frame.columnconfigure(0, weight=1)
        
    def set_canvas_size(self, width, height):
        """Set canvas size from preset buttons"""
        self.canvas_width.set(width)
        self.canvas_height.set(height)
        
    def create_image_panel(self, parent):
        image_frame = ttk.LabelFrame(parent, text="Image Preview", padding="10")
        image_frame.grid(row=1, column=1, sticky="nsew")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(image_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        # Original image tab
        original_frame = ttk.Frame(notebook)
        notebook.add(original_frame, text="Original")
        
        self.original_canvas = tk.Canvas(original_frame, bg="white", 
                                        width=400, height=400)
        self.original_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Pixel art tab
        pixel_frame = ttk.Frame(notebook)
        notebook.add(pixel_frame, text="Pixel Art")
        
        # Create checkered background for pixel art canvas to show transparency
        self.pixel_canvas = tk.Canvas(pixel_frame, bg="white", 
                                     width=400, height=400)
        self.pixel_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Drag and drop area
        self.drop_label = ttk.Label(original_frame,
                                    text="Drag an image here\nor click to browse",
                                    font=("Arial", 12))
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Configure click to browse for images
        self.original_canvas.bind('<Button-1>', self.browse_file)
        
        # Configure grid weights
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(0, weight=1)
        pixel_frame.columnconfigure(0, weight=1)
        pixel_frame.rowconfigure(0, weight=1)
        
    def create_checkered_background(self, canvas, width, height, square_size=10):
        """Create a checkered background to show transparency"""
        canvas.delete("checkerboard")
        for x in range(0, width, square_size):
            for y in range(0, height, square_size):
                if (x // square_size + y // square_size) % 2:
                    color = "#E0E0E0"
                else:
                    color = "#F0F0F0"
                canvas.create_rectangle(x, y, x + square_size, y + square_size,
                                      fill=color, outline="", tags="checkerboard")
        
    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=2, sticky="nsew", padx=(10, 0))
        
        # URL input
        ttk.Label(control_frame, text="Image URL:").grid(row=0, column=0, 
                                                         sticky="w", pady=2)
        self.url_entry = ttk.Entry(control_frame, width=30)
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=2)
        
        load_url_btn = ttk.Button(control_frame, text="Load from URL", 
                                 command=self.load_from_url)
        load_url_btn.grid(row=2, column=0, sticky="ew", pady=(2, 10))
        
        # Canvas info display
        self.canvas_info_label = ttk.Label(control_frame, text="Canvas: 96×96", 
                                          font=("Arial", 9, "bold"))
        self.canvas_info_label.grid(row=3, column=0, sticky="w", pady=(10, 5))
        
        # Update canvas info when size changes
        def update_canvas_info(*args):
            w, h = self.canvas_width.get(), self.canvas_height.get()
            self.canvas_info_label.config(text=f"Canvas: {w}×{h}")
        self.canvas_width.trace('w', update_canvas_info)
        self.canvas_height.trace('w', update_canvas_info)
        
        # Download buttons
        ttk.Label(control_frame, text="Download:").grid(row=4, column=0, 
                                                        sticky="w", pady=(10, 2))
        
        download_btn = ttk.Button(control_frame, text="Download Pixel Art", 
                                 command=self.download_pixel_art)
        download_btn.grid(row=5, column=0, sticky="ew", pady=2)
        
        palette_btn = ttk.Button(control_frame, text="Download Palette", 
                                command=self.download_palette)
        palette_btn.grid(row=6, column=0, sticky="ew", pady=2)
        
        # Palette display
        ttk.Label(control_frame, text="Color Palette:").grid(row=7, column=0, 
                                                             sticky="w", pady=(20, 5))
        
        self.palette_frame = ttk.Frame(control_frame)
        self.palette_frame.grid(row=8, column=0, sticky="ew", pady=5)
        
        # Instructions
        instructions = """
        Instructions:
        1. Set canvas size and options
        2. Click canvas or paste URL to load image
        3. Adjust settings on the left
        4. Click 'Convert to Pixel Art'
        5. Download your pixel art!
        
        Tips:
        • Proportional resize maintains aspect ratio
        • Transparent background removes white areas
        • Lower pixel size = more detailed
        • More colors = smoother gradients
        """
        
        instruction_label = ttk.Label(control_frame, text=instructions, 
                                     justify="left", font=("Arial", 9))
        instruction_label.grid(row=9, column=0, sticky="ew", pady=(20, 0))
        
        control_frame.columnconfigure(0, weight=1)
        
    def on_drop(self, event):
        """Handle drag and drop files"""
        files = event.data.split()
        if files:
            file_path = files[0].strip('{}')
            self.load_image(file_path)
            
    def browse_file(self, event=None):
        """Browse for image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
            
    def load_from_url(self):
        """Load image from URL"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
            
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.load_image(BytesIO(response.content))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image from URL:\n{str(e)}")
            
    def resize_image_to_canvas(self, image):
        """Resize image to fit canvas size with optional proportional scaling"""
        canvas_w = self.canvas_width.get()
        canvas_h = self.canvas_height.get()
        
        if self.proportional_resize.get():
            # Proportional resize - fit image within canvas bounds
            image.thumbnail((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            
            # Create new image with canvas size and transparent/white background
            if self.transparent_background.get():
                new_image = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
                # Center the resized image
                x = (canvas_w - image.width) // 2
                y = (canvas_h - image.height) // 2
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                new_image.paste(image, (x, y), image)
            else:
                new_image = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
                # Center the resized image
                x = (canvas_w - image.width) // 2
                y = (canvas_h - image.height) // 2
                if image.mode == 'RGBA':
                    new_image.paste(image, (x, y), image)
                else:
                    new_image.paste(image, (x, y))
            
            return new_image
        else:
            # Non-proportional resize - stretch to exact canvas size
            if self.transparent_background.get() and image.mode != 'RGBA':
                image = image.convert('RGBA')
            elif not self.transparent_background.get() and image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            
    def load_image(self, source):
        """Load image from file path or BytesIO object"""
        try:
            if isinstance(source, BytesIO):
                img = Image.open(source)
            else:
                # Check if it's a WebP file and try alternative loading
                if isinstance(source, str) and source.lower().endswith('.webp'):
                    try:
                        img = Image.open(source)
                    except Exception as webp_error:
                        # Try using webp library as fallback
                        try:
                            import webp
                            # Convert WebP to PIL Image using webp library
                            webp_data = webp.load_image(source)
                            img = Image.fromarray(webp_data)
                        except ImportError:
                            raise Exception("WebP support not available. Try: pip install --upgrade Pillow")
                        except Exception as fallback_error:
                            raise Exception(f"WebP loading failed. Original error: {webp_error}")
                else:
                    img = Image.open(source)
                    
            # Resize image to canvas size
            self.original_image = self.resize_image_to_canvas(img)
                
            self.display_original_image()
            
            # Show format info
            img_format = getattr(img, 'format', 'Unknown')
            original_size = img.size
            new_size = self.original_image.size
            messagebox.showinfo("Success", 
                f"Image loaded and resized!\n"
                f"Format: {img_format}\n"
                f"Original: {original_size[0]} × {original_size[1]}\n"
                f"Canvas: {new_size[0]} × {new_size[1]}")
            
        except Exception as e:
            error_msg = str(e)
            if "cannot identify image file" in error_msg.lower():
                messagebox.showerror("Error", 
                    f"Unsupported image format or corrupted file.\n\n"
                    f"Supported formats: JPEG, PNG, GIF, BMP, TIFF, WebP\n"
                    f"For WebP support, try:\n"
                    f"pip install --upgrade Pillow\n\n"
                    f"Error: {error_msg}")
            elif "webp" in error_msg.lower():
                messagebox.showerror("WebP Error", 
                    f"WebP support issue.\n\n"
                    f"Solutions:\n"
                    f"1. pip install --upgrade Pillow\n"
                    f"2. Convert WebP to PNG online first\n"
                    f"3. Install system WebP libraries\n\n"
                    f"Error: {error_msg}")
            else:
                messagebox.showerror("Error", f"Failed to load image:\n{error_msg}")
            
    def display_original_image(self):
        """Display the original image on canvas"""
        if not self.original_image:
            return
            
        # Hide the click to browse label
        self.drop_label.place_forget()
            
        # Resize image to fit canvas while maintaining aspect ratio
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet rendered, use default size
            canvas_width, canvas_height = 400, 400
            
        # Create checkered background if image has transparency
        if self.original_image.mode == 'RGBA':
            self.create_checkered_background(self.original_canvas, canvas_width, canvas_height)
            
        img_copy = self.original_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage and display
        self.original_photo = ImageTk.PhotoImage(img_copy)
        self.original_canvas.delete("image")
        
        x = (canvas_width - img_copy.width) // 2
        y = (canvas_height - img_copy.height) // 2
        self.original_canvas.create_image(x, y, anchor="nw", image=self.original_photo, tags="image")
        
    def convert_to_pixel_art(self):
        """Convert the loaded image to pixel art"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please load an image first")
            return
            
        try:
            # Work with the image
            img = self.original_image.copy()
            has_transparency = img.mode == 'RGBA'
            
            if has_transparency:
                # Handle transparency
                img_array = np.array(img)
                rgb_array = img_array[:,:,:3]
                alpha_array = img_array[:,:,3]
                
                # Apply brightness and contrast to RGB channels only
                rgb_array = rgb_array.astype(np.float32)
                rgb_array *= self.brightness.get()
                rgb_array = (rgb_array - 128) * self.contrast.get() + 128
                rgb_array = np.clip(rgb_array, 0, 255)
                
                # Combine back with alpha
                img_array = np.dstack([rgb_array.astype(np.uint8), alpha_array])
                img = Image.fromarray(img_array, 'RGBA')
            else:
                # Handle RGB images
                img_array = np.array(img, dtype=np.float32)
                img_array *= self.brightness.get()
                img_array = (img_array - 128) * self.contrast.get() + 128
                img_array = np.clip(img_array, 0, 255)
                img = Image.fromarray(img_array.astype(np.uint8))
            
            # Resize image to create pixel effect
            pixel_size = self.pixel_size.get()
            small_img = img.resize(
                (img.width // pixel_size, img.height // pixel_size),
                Image.Resampling.NEAREST
            )
            
            # Reduce colors using K-means clustering
            if has_transparency:
                # For RGBA images, only cluster non-transparent pixels
                img_array = np.array(small_img)
                mask = img_array[:,:,3] > 0  # Non-transparent pixels
                
                if np.any(mask):
                    rgb_data = img_array[mask][:,:3]  # Get RGB values of non-transparent pixels
                    
                    kmeans = KMeans(n_clusters=min(self.color_count.get(), len(rgb_data)), 
                                  random_state=42, n_init=10)
                    kmeans.fit(rgb_data)
                    
                    # Replace colors with cluster centers
                    new_colors = kmeans.cluster_centers_.astype(int)
                    labels = kmeans.labels_
                    new_rgb_data = new_colors[labels]
                    
                    # Apply new colors to non-transparent pixels
                    new_img_array = img_array.copy()
                    new_img_array[mask] = np.column_stack([new_rgb_data, img_array[mask][:,3]])
                    
                    self.pixel_art_image = Image.fromarray(new_img_array.astype(np.uint8), 'RGBA')
                    self.palette_colors = new_colors
                else:
                    # All pixels are transparent
                    self.pixel_art_image = small_img
                    self.palette_colors = []
            else:
                # For RGB images, process normally
                img_array = np.array(small_img)
                img_data = img_array.reshape(-1, 3)
                
                kmeans = KMeans(n_clusters=self.color_count.get(), random_state=42, n_init=10)
                kmeans.fit(img_data)
                
                new_colors = kmeans.cluster_centers_.astype(int)
                labels = kmeans.labels_
                
                new_img_data = new_colors[labels]
                new_img_array = new_img_data.reshape(img_array.shape)
                
                self.pixel_art_image = Image.fromarray(new_img_array.astype(np.uint8))
                self.palette_colors = new_colors
            
            # Scale back up to canvas size
            self.pixel_art_image = self.pixel_art_image.resize(
                (self.canvas_width.get(), self.canvas_height.get()), 
                Image.Resampling.NEAREST
            )
            
            self.display_pixel_art()
            self.display_palette()
            
            messagebox.showinfo("Success", "Pixel art conversion complete!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert image:\n{str(e)}")
            
    def display_pixel_art(self):
        """Display the pixel art on canvas"""
        if not self.pixel_art_image:
            return
            
        # Resize image to fit canvas
        canvas_width = self.pixel_canvas.winfo_width()
        canvas_height = self.pixel_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 400, 400
            
        # Create checkered background if image has transparency
        if self.pixel_art_image.mode == 'RGBA':
            self.create_checkered_background(self.pixel_canvas, canvas_width, canvas_height)
        
        img_copy = self.pixel_art_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.NEAREST)
        
        # Convert to PhotoImage and display
        self.pixel_photo = ImageTk.PhotoImage(img_copy)
        self.pixel_canvas.delete("image")
        
        x = (canvas_width - img_copy.width) // 2
        y = (canvas_height - img_copy.height) // 2
        self.pixel_canvas.create_image(x, y, anchor="nw", image=self.pixel_photo, tags="image")
        
    def display_palette(self):
        """Display the color palette"""
        # Clear existing palette
        for widget in self.palette_frame.winfo_children():
            widget.destroy()
            
        # Display palette colors
        if len(self.palette_colors) == 0:
            return
            
        # Create color swatches
        colors_per_row = 4
        for i, color in enumerate(self.palette_colors):
            row = i // colors_per_row
            col = i % colors_per_row
            
            # Convert color to hex
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            
            # Create color swatch
            color_frame = tk.Frame(self.palette_frame, bg=hex_color, 
                                 width=30, height=30, relief="raised", bd=1)
            color_frame.grid(row=row, column=col, padx=2, pady=2)
            color_frame.grid_propagate(False)
            
            # Add tooltip with hex value
            def create_tooltip(frame, text):
                def show_tooltip(event):
                    tooltip = tk.Toplevel()
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                    label = tk.Label(tooltip, text=text, background="yellow")
                    label.pack()
                    frame.tooltip = tooltip
                    
                def hide_tooltip(event):
                    if hasattr(frame, 'tooltip'):
                        frame.tooltip.destroy()
                        
                frame.bind("<Enter>", show_tooltip)
                frame.bind("<Leave>", hide_tooltip)
                
            create_tooltip(color_frame, hex_color)
            
    def download_pixel_art(self):
        """Download the pixel art image"""
        if not self.pixel_art_image:
            messagebox.showwarning("Warning", "No pixel art to download")
            return
            
        # Suggest appropriate file extension based on transparency
        if self.pixel_art_image.mode == 'RGBA':
            default_ext = ".png"
            filetypes = [
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        else:
            default_ext = ".png"
            filetypes = [
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
            
        file_path = filedialog.asksaveasfilename(
            title="Save Pixel Art",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        
        if file_path:
            try:
                self.pixel_art_image.save(file_path)
                messagebox.showinfo("Success", f"Pixel art saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
                
    def download_palette(self):
        """Download the color palette as an image"""
        if len(self.palette_colors) == 0:
            messagebox.showwarning("Warning", "No palette to download")
            return
            
        try:
            # Create palette image
            swatch_size = 50
            colors_per_row = 8
            rows = (len(self.palette_colors) + colors_per_row - 1) // colors_per_row
            
            palette_width = colors_per_row * swatch_size
            palette_height = rows * swatch_size
            
            palette_img = Image.new('RGB', (palette_width, palette_height), 'white')
            
            for i, color in enumerate(self.palette_colors):
                row = i // colors_per_row
                col = i % colors_per_row
                
                x1 = col * swatch_size
                y1 = row * swatch_size
                x2 = x1 + swatch_size
                y2 = y1 + swatch_size
                
                # Create color swatch
                swatch = Image.new('RGB', (swatch_size, swatch_size), tuple(color))
                palette_img.paste(swatch, (x1, y1, x2, y2))
                
            # Save palette
            file_path = filedialog.asksaveasfilename(
                title="Save Color Palette",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                palette_img.save(file_path)
                messagebox.showinfo("Success", f"Palette saved to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save palette:\n{str(e)}")
            
    def reset_settings(self):
        """Reset all settings to default values"""
        self.pixel_size.set(8)
        self.color_count.set(16)
        self.brightness.set(1.0)
        self.contrast.set(1.0)
        self.canvas_width.set(96)
        self.canvas_height.set(96)
        self.proportional_resize.set(True)
        self.transparent_background.set(False)

def main():
    # Check for required packages
    try:
        import tkinterdnd2
        import PIL
        import numpy
        import sklearn
        import requests
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install tkinterdnd2 Pillow numpy scikit-learn requests")
        return
        
    root = tkdnd.Tk()
    app = PixelArtConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
