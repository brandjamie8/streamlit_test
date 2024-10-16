import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from colorsys import rgb_to_hls, hls_to_rgb
import json

st.set_page_config(layout="wide")

st.title('Matplotlib Colormap Explorer')

# Initialize session state for colors
if 'colors' not in st.session_state:
    st.session_state.colors = []
if 'original_colors' not in st.session_state:
    st.session_state.original_colors = []

# Colormap descriptions
colormap_descriptions = {
    'viridis': "Viridis is a perceptually uniform colormap, often used for scientific visualizations.",
    'plasma': "Plasma is a vibrant colormap, useful for showing data with high dynamic range.",
    'inferno': "Inferno is a colormap designed for better perception by viewers with color blindness.",
    'magma': "Magma is similar to Inferno but has a slightly more muted color range.",
    'cividis': "Cividis is a colormap designed to be colorblind-friendly and perceptually uniform.",
    'Blues': "Blues is a sequential colormap ranging from light to dark blue.",
    'BuGn': "BuGn is a sequential colormap ranging from light blue to green.",
    'BuPu': "BuPu is a sequential colormap ranging from light blue to purple.",
    'GnBu': "GnBu is a sequential colormap ranging from green to blue.",
    'OrRd': "OrRd is a sequential colormap ranging from orange to red.",
    'Spectral': "Spectral is a diverging colormap useful for highlighting differences across a central value.",
    'cool': "Cool is a linear colormap transitioning from blue to cyan.",
    'spring': "Spring is a sequential colormap transitioning from magenta to green.",
    'summer': "Summer is a sequential colormap transitioning from green to yellow.",
    'autumn': "Autumn is a sequential colormap transitioning from red to orange.",
    'winter': "Winter is a sequential colormap transitioning from cyan to blue.",
}

# Sidebar controls
st.sidebar.header('Controls')

# Dark Mode Toggle
dark_mode = st.sidebar.checkbox('Toggle Dark/Light Mode')

if dark_mode:
    st.markdown("""
    <style>
    body {
        background-color: #333333;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Colormap selection
colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'OrRd', 'Spectral', 'cool', 'spring', 'summer', 'autumn', 'winter']
colormap = st.sidebar.selectbox('Select Colormap:', [''] + colormaps)

# Show colormap description
if colormap:
    st.sidebar.write('**Colormap Description:**', colormap_descriptions.get(colormap, 'No description available.'))

# Number of colors
num_colors = st.sidebar.number_input('Number of Colors:', min_value=1, max_value=256, value=5)

# Generate colors
if colormap:
    cmap = plt.get_cmap(colormap, num_colors)
    colors = [mcolors.rgb2hex(cmap(i)) for i in range(cmap.N)]
    st.session_state.colors = colors
    st.session_state.original_colors = colors

# Download Palette
if st.sidebar.button('Download Palette'):
    palette_data = [{'hex': color} for color in st.session_state.colors]
    json_str = json.dumps(palette_data, indent=2)
    st.download_button('Download Palette as JSON', data=json_str, file_name='color-palette.json', mime='application/json')

# Custom Colorpicker
st.sidebar.subheader('Add a Custom Color')
custom_color = st.sidebar.color_picker('Pick a color')
if st.sidebar.button('Add Custom Color'):
    st.session_state.colors.append(custom_color)
    st.session_state.original_colors.append(custom_color)

# Gradient Creation Tool
st.sidebar.subheader('Generate Gradient')
gradient_color1 = st.sidebar.color_picker('Color 1', '#ff0000')
gradient_color2 = st.sidebar.color_picker('Color 2', '#0000ff')
if st.sidebar.button('Generate Gradient'):
    cmap_custom = mcolors.LinearSegmentedColormap.from_list('custom_gradient', [gradient_color1, gradient_color2])
    gradient_colors = [mcolors.rgb2hex(cmap_custom(i)) for i in np.linspace(0, 1, num_colors)]
    st.session_state.colors = gradient_colors
    st.session_state.original_colors = gradient_colors

# Adjustments
st.sidebar.subheader('Adjustments')
brightness = st.sidebar.slider('Brightness:', -0.5, 0.5, 0.0, step=0.05)
saturation = st.sidebar.slider('Saturation:', -0.5, 0.5, 0.0, step=0.05)

def adjust_color(color, brightness_adj, saturation_adj):
    r, g, b = mcolors.to_rgb(color)
    h, l, s = rgb_to_hls(r, g, b)
    l = max(0.0, min(1.0, l + brightness_adj))
    s = max(0.0, min(1.0, s + saturation_adj))
    r_new, g_new, b_new = hls_to_rgb(h, l, s)
    return mcolors.to_hex((r_new, g_new, b_new))

colors_adjusted = [adjust_color(color, brightness, saturation) for color in st.session_state.colors]

# Sort Options
st.sidebar.subheader('Sort Options')
sort_option = st.sidebar.selectbox('Sort Colors By:', ['Original Order', 'Brightness', 'Hue', 'Saturation'])

def color_brightness(color):
    r, g, b = mcolors.to_rgb(color)
    return rgb_to_hls(r, g, b)[1]

def color_hue(color):
    r, g, b = mcolors.to_rgb(color)
    return rgb_to_hls(r, g, b)[0]

def color_saturation_value(color):
    r, g, b = mcolors.to_rgb(color)
    return rgb_to_hls(r, g, b)[2]

if sort_option == 'Brightness':
    colors_adjusted.sort(key=color_brightness)
elif sort_option == 'Hue':
    colors_adjusted.sort(key=color_hue)
elif sort_option == 'Saturation':
    colors_adjusted.sort(key=color_saturation_value)
elif sort_option == 'Original Order':
    colors_adjusted = [adjust_color(color, brightness, saturation) for color in st.session_state.original_colors]

# Colorblind Simulation
st.sidebar.subheader('Simulate Colorblindness')
simulate_option = st.sidebar.selectbox('Simulate Colorblindness:', ['None', 'Protanopia', 'Deuteranopia', 'Tritanopia', 'Achromatopsia'])

def simulate_colorblindness(color, type):
    # Simple simulation by adjusting colors (placeholder)
    if type == 'Protanopia' or type == 'Deuteranopia':
        # Reduce red/green components
        r, g, b = mcolors.to_rgb(color)
        r *= 0.5
        g *= 0.5
        return mcolors.to_hex((r, g, b))
    elif type == 'Tritanopia':
        # Reduce blue component
        r, g, b = mcolors.to_rgb(color)
        b *= 0.5
        return mcolors.to_hex((r, g, b))
    elif type == 'Achromatopsia':
        # Desaturate color completely
        r, g, b = mcolors.to_rgb(color)
        h, l, s = rgb_to_hls(r, g, b)
        s = 0
        r_new, g_new, b_new = hls_to_rgb(h, l, s)
        return mcolors.to_hex((r_new, g_new, b_new))
    else:
        return color

if simulate_option != 'None':
    colors_adjusted = [simulate_colorblindness(color, simulate_option) for color in colors_adjusted]

# Reset Colors
if st.sidebar.button('Reset Colors'):
    st.session_state.colors = st.session_state.original_colors.copy()
    colors_adjusted = st.session_state.colors.copy()
    brightness = 0.0
    saturation = 0.0

# Display Colormap Preview
st.subheader('Colormap Preview')
st.write('Colormap Preview (Gradient):')
st.markdown(f"<div style='height: 30px; background: linear-gradient(to right, {', '.join(colors_adjusted)});'></div>", unsafe_allow_html=True)

# Display Adjusted Colors
st.subheader('Color Palette')
cols = st.columns(len(colors_adjusted))
for col, color in zip(cols, colors_adjusted):
    r, g, b = [int(255 * c) for c in mcolors.to_rgb(color)]
    rgb_text = f"rgb({r}, {g}, {b})"
    col.markdown(f"<div style='background-color:{color}; height:60px;'></div>", unsafe_allow_html=True)
    col.markdown(f"<p style='text-align: center;'>{color}<br>{rgb_text}</p>", unsafe_allow_html=True)

# Python Script Output
st.subheader('Python Script Output')
python_code = f"# Python color palette:\n# Use this in your script:\ncolors = [\n" + ',\n'.join([f"    '{color}'" for color in colors_adjusted]) + "\n]"
st.code(python_code, language='python')
