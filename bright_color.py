import numpy as np
import matplotlib.pyplot as plt
from coloraide import Color as BaseColor
from coloraide.spaces.hct import HCT as HCTSpace
from aquarel import load_theme


# 注册 HCT 色域
class Color(BaseColor):
    pass


Color.register(HCTSpace(), overwrite=True)


def plot_color_list(color_list):
    """
    Plot a list of colors using matplotlib.

    :param color_list: List of color strings in hexadecimal format.
    """
    # Create a figure and a subplot
    fig, ax = plt.subplots(figsize=(8, 2))

    # Number of colors
    num_colors = len(color_list)

    theme = load_theme("arctic_light")
    theme.apply()

    # Create an array representing the colors
    # The shape should be (1, num_colors, 3) for RGB
    color_array = np.array([Color(c).convert("srgb").coords() for c in color_list])
    color_array = color_array[np.newaxis, :, :]  # Reshape to (1, num_colors, 3)

    # Remove axes
    ax.set_axis_off()

    # Display the colors
    ax.imshow(color_array, aspect="auto")
    theme.apply_transforms()
    # Show the plot
    plt.show()


def convert_to_grayscale(hex_colors):
    """
    Convert a list of hex color strings to grayscale.

    :param hex_colors: List of color strings in hexadecimal format.
    :return: List of grayscale color strings in hexadecimal format.
    """
    grayscale_colors = []
    for hex_color in hex_colors:
        color = Color(hex_color).convert("hsl")  # Convert to HSL
        color.set("saturation", 0)  # Set saturation to 0 for grayscale
        grayscale_hex = color.convert("srgb").to_string(
            hex=True
        )  # Convert back to sRGB and then to Hex
        grayscale_colors.append(grayscale_hex)

    return grayscale_colors


def grayscale_hex_to_luminance(hex_color):
    color = Color(hex_color).convert("srgb")
    r, g, b = color.coords()
    luminance = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return luminance


color_chain = []
for i in range(0, 360, 10):
    c = Color("hct", [i, 145, 50])
    tones = range(0, 101, 1)
    color_hex_list = [
        c.clone().set("tone", tone).convert("srgb").to_string(hex=True)
        for tone in tones
    ]
    # plot_color_list(color_hex_list)
    grayscale_hex_list = convert_to_grayscale(color_hex_list)

    # Plot the grayscale colors
    # plot_color_list(grayscale_hex_list)

    luminance_values = [
        grayscale_hex_to_luminance(hex_color) for hex_color in grayscale_hex_list
    ]
    luminance_values = [round(value, 2) for value in luminance_values]
    equal_indices = []
    for i in range(len(luminance_values) - 2):
        if luminance_values[i] == luminance_values[i + 1] == luminance_values[i + 2]:
            equal_indices.append(i)
    print(equal_indices[-1], color_hex_list[equal_indices[-1]])
    color_chain.append(color_hex_list[equal_indices[-1]])
    # plot_color_list([color_hex_list[equal_indices[-1]]])
    # plt.figure(figsize=(10, 4))
    # plt.bar(range(len(luminance_values)), luminance_values, color=grayscale_hex_list)
    # plt.xlabel('Color Index')
    # plt.ylabel('Luminance')
    # plt.title('Luminance of Grayscale Colors')
    # plt.show()

plot_color_list(color_chain)
print(color_chain)
