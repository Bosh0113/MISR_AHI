import numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation

i = 0


def animate(*args):
    global i
    if (i < 8):
        i += 1
    else:
        i = 0
    im.set_array(animate_images[i])
    return im,


if __name__ == "__main__":
    BRF_data_path = './SRF_62/'
    bands = numpy.arange(0, 4, 1)
    cameras = numpy.arange(0, 9, 1)
    
    BRFs_b_c = []
    for band_num in bands:
        BRFs_b = []
        BRFs_b_im = []
        band_str = str(band_num)
        for camera_num in cameras:
            camera_str = str(camera_num)
            BRF_filename = BRF_data_path + 'b_' + band_str + '_c_' + camera_str + '.npy'
            BRF62_bbc = numpy.load(BRF_filename)
            BRFs_b.append(BRF62_bbc)
        BRFs_b_c.append(BRFs_b)

    # # mapping animation
    # fig = plt.figure()
    # band_n = 0  # band 0, 1, 2, 3
    # animate_images = BRFs_b_c[band_n]
    # im = plt.imshow(animate_images[0], animated=True, cmap=plt.cm.jet, vmin=0, vmax=11000)
    # ani = animation.FuncAnimation(fig, animate, blit=True)
    # # ani.save("./SRF_gif/b" + str(band_n) + "c.gif")
    # plt.colorbar()
    # plt.show()

    # # mapping figures
    # BRF_fig_path = './SRF_png/'
    # for band_num in bands:
    #     band_str = str(band_num)
    #     for camera_num in cameras:
    #         camera_str = str(camera_num)
    #         BRF_fig = BRF_fig_path + 'b_' + band_str + '_c_' + camera_str + '.png'
    #         plt.imshow(BRFs_b_c[band_num][camera_num], cmap=plt.cm.jet, vmin=0, vmax=11000)
    #         plt.savefig(BRF_fig)