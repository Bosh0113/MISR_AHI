import imageio
import numpy


def create_gif(image_list, gif_name, duration):
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(image_name))

    imageio.mimsave(gif_name, frames, 'GIF', duration=duration)


if __name__ == "__main__":
    bands = numpy.arange(0, 4, 1)
    cameras = numpy.arange(0, 9, 1)

    BRF_fig_path = './SRF_map_png/'
    duration = 1
    for band_num in bands:
        band_str = str(band_num)
        gif_path = BRF_fig_path + 'map_band' + band_str + '.gif'
        gif_imgs = []
        for camera_num in cameras:
            camera_str = str(camera_num)
            BRF_fig = BRF_fig_path + 'map_b_' + band_str + '_c_' + camera_str + '.png'
            gif_imgs.append(BRF_fig)
        create_gif(gif_imgs, gif_path, duration)
