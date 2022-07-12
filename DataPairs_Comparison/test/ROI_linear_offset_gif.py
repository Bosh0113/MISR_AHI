import os
import imageio


def create_gif(image_list, gif_name, duration):
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(image_name))

    imageio.mimsave(gif_name, frames, 'GIF', duration=duration)


if __name__ == "__main__":
    # roi_name = '26.1_150'
    # png_folder = r'D:\Work_PhD\MISR_AHI_WS\220712\26.1_150_scatters'
    # roi_name = '60.0_130'
    # png_folder = r'D:\Work_PhD\MISR_AHI_WS\220712\60.0_130_scatters'
    roi_name = '60.0_200'
    png_folder = r'D:\Work_PhD\MISR_AHI_WS\220712\60.0_200_scatters'
    storage_folder = r'D:\Work_PhD\MISR_AHI_WS\220712'
    file_list = os.listdir(png_folder)
    band_names = ['band3', 'band4']
    for band_name in band_names:
        png_list = []
        gif_file = roi_name + '_' + band_name + '.gif'
        gif_filename = os.path.join(storage_folder, gif_file)
        for png_file in file_list:
            if band_name in png_file:
                png_filename = os.path.join(png_folder, png_file)
                png_list.append(png_filename)
        create_gif(png_list, gif_filename, 0.2)