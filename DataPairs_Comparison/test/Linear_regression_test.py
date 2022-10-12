import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, linregress, pearsonr
from sklearn.metrics import mean_squared_error
import numpy as np
import math


def pearson(array_x, array_y):
    print(pearsonr(array_x, array_y))


def identifer(li):
    result = []
    for a in li:
        mean = np.nanmean(a)
        std = np.nanstd(a)
        down = mean - 3 * std
        up = mean + 3 * std
        n_a = np.where(a < down, np.nan, a)
        n_a = np.where(n_a > up, np.nan, n_a)
        result.append(n_a)
    return result


def mean_slope_mapping(roi_name, X, Y, x_label, y_label, axis_min=0.0, axis_max=0.5):
    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')

    # k, b = np.polyfit(X, Y, deg=1)
    k, b, r, p, std_err = linregress(X, Y)
    
    rmse = math.sqrt(mean_squared_error(X, Y))
    N = len(X)

    x = np.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = np.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    # Calculate the point density
    xy = np.vstack([X, Y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    X, Y, z = X[idx], Y[idx], z[idx]
    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)

    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=8)

    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=8)

    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')

    im = ax1.scatter(X, Y, marker='o', c=z, s=15, cmap='Spectral_r')

    ax1.set_xticks(np.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(np.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    ax1.set_xlabel(x_label, fontsize=10)
    ax1.set_ylabel(y_label, fontsize=10)

    ax1.plot(x, y, color='k', linewidth=2, linestyle='-.')
    ax1.plot(xx, yy, color='r', linewidth=2, linestyle='-')

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.22

    ax1.text(text_x, text_y, s='N = {}\nRMSE = {}\ny = {}x + {}'.format(N, round(rmse, 3), round(k, 2), round(b, 2)), fontsize=8)

    # cax = add_right_cax(ax1, pad=0.06, width=0.03)
    # cb = fig.colorbar(im, cax=cax)
    # cb.ax.set_xlabel('Count', rotation=360)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    # fig.savefig(os.path.join(WORK_SPACE, '{} Band4 SR.jpg'.format(roi_name)), dpi=1000, bbox_inches='tight')
    plt.show()
    plt.clf()



def scipy_linearRegression(roi_name, X, Y, x_label, y_label, axis_min=0.0, axis_max=0.5):

    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')

    # k, b = np.polyfit(X, Y, deg=1)
    k, b, r, p, std_err = linregress(X, Y)
    
    rmse = math.sqrt(mean_squared_error(X, Y))
    N = len(X)

    x = np.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = np.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    # Calculate the point density
    xy = np.vstack([X, Y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    X, Y, z = X[idx], Y[idx], z[idx]
    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)

    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=8)

    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=8)

    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')

    im = ax1.scatter(X, Y, marker='o', c=z, s=15, cmap='Spectral_r')

    ax1.set_xticks(np.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(np.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    ax1.set_xlabel(x_label, fontsize=10)
    ax1.set_ylabel(y_label, fontsize=10)

    ax1.plot(x, y, color='k', linewidth=2, linestyle='-.')
    ax1.plot(xx, yy, color='r', linewidth=2, linestyle='-')

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.22

    ax1.text(text_x, text_y, s='N = {}\nRMSE = {}\ny = {}x + {}'.format(N, round(rmse, 3), round(k, 2), round(b, 2)), fontsize=8)

    # cax = add_right_cax(ax1, pad=0.06, width=0.03)
    # cb = fig.colorbar(im, cax=cax)
    # cb.ax.set_xlabel('Count', rotation=360)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    # fig.savefig(os.path.join(WORK_SPACE, '{} Band4 SR.jpg'.format(roi_name)), dpi=1000, bbox_inches='tight')
    plt.show()
    plt.clf()


def make_fig(roi_name, X, Y, axis_min=0.0, axis_max=0.5):

    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')

    k, b = np.polyfit(X, Y, deg=1)
    rmse = math.sqrt(mean_squared_error(X, Y))
    N = len(X)

    x = np.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = np.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    # Calculate the point density
    xy = np.vstack([X, Y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    X, Y, z = X[idx], Y[idx], z[idx]
    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)

    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=8)

    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=8)

    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')

    im = ax1.scatter(X, Y, marker='o', c=z, s=15, cmap='Spectral_r')

    ax1.set_xticks(np.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(np.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    ax1.set_ylabel("AHI Ref Band4", fontsize=10)
    ax1.set_xlabel("MISR Ref Band4", fontsize=10)

    ax1.plot(x, y, color='k', linewidth=2, linestyle='-.')
    ax1.plot(xx, yy, color='r', linewidth=2, linestyle='-')

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.22

    ax1.text(text_x, text_y, s='N = {}\nRMSE = {}\ny = {}x + {}'.format(N, round(rmse, 3), round(k, 2), round(b, 2)), fontsize=8)

    # cax = add_right_cax(ax1, pad=0.06, width=0.03)
    # cb = fig.colorbar(im, cax=cax)
    # cb.ax.set_xlabel('Count', rotation=360)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    # fig.savefig(os.path.join(WORK_SPACE, '{} Band4 SR.jpg'.format(roi_name)), dpi=1000, bbox_inches='tight')
    plt.show()
    plt.clf()


if __name__ == "__main__":
    array1 = [0.049746688455343246, 0.06538790464401245, 0.05516389012336731, 0.05516389012336731, 0.07286516577005386, 0.07400964200496674, 0.06889763474464417, 0.06103888154029846, 0.055774278938770294, 0.057681743055582047, 0.057681743055582047, 0.06607458740472794, 0.07179698348045349, 0.05638466775417328, 0.08080022037029266, 0.04883110523223877, 0.04883110523223877, 0.08888787031173706, 0.08522553741931915, 0.07042361050844193, 0.07042361050844193, 0.04616065323352814, 0.03998046740889549, 0.03723371773958206, 0.05920771509408951, 0.05920771509408951, 0.05394311249256134, 0.05119636282324791, 0.04081975296139717, 0.04081975296139717, 0.06218336150050163, 0.1109381690621376, 0.04562656581401825, 0.04562656581401825, 0.03898858651518822, 0.03647073358297348, 0.03250320255756378, 0.05684245750308037, 0.05684245750308037, 0.05035707727074623, 0.052569735795259476, 0.03448696807026863, 0.043032411485910416, 0.043032411485910416, 0.09064273536205292, 0.07484892755746841, 0.033495087176561356, 0.033495087176561356, 0.03318989276885986, 0.03799670189619064, 0.04493987560272217, 0.04097234830260277, 0.04097234830260277, 0.04036195948719978, 0.03402917832136154, 0.04791552200913429, 0.04791552200913429, 0.03921747952699661, 0.06493011116981506, 0.04677104204893112, 0.04677104204893112, 0.040285661816596985, 0.03898858651518822, 0.043032411485910416, 0.041506439447402954, 0.03853079304099083, 0.03853079304099083, 0.050967466086149216, 0.06889763474464417, 0.04791552200913429, 0.029146065935492516, 0.027696393430233, 0.04677104204893112, 0.03502105921506882, 0.03502105921506882, 0.03288469836115837, 0.029985349625349045, 0.041430141776800156, 0.04616065323352814, 0.04616065323352814, 0.05760544538497925, 0.06309894472360611, 0.04013306647539139, 0.04791552200913429, 0.03723371773958206, 0.04440578818321228, 0.045855458825826645, 0.045855458825826645, 0.04127754271030426, 0.02258438616991043, 0.030748337507247925, 0.031206127256155014, 0.04654214531183243, 0.04654214531183243, 0.043108709156513214, 0.041506439447402954, 0.03639443218708038, 0.03639443218708038, 0.044253189116716385, 0.047381430864334106, 0.0637856274843216, 0.0637856274843216, 0.02815418317914009, 0.03135872632265091, 0.04112494736909866, 0.036241836845874786, 0.036241836845874786, 0.035936642438173294, 0.034715864807367325, 0.0398278683423996, 0.0398278683423996, 0.04799181967973709, 0.04410059005022049, 0.04242202267050743, 0.04867850989103317, 0.02823048271238804, 0.022508088499307632, 0.030672037973999977, 0.03448696807026863, 0.03814930096268654, 0.03814930096268654, 0.039064884185791016, 0.033952876925468445, 0.0395989753305912, 0.0395989753305912, 0.039446376264095306, 0.03685222566127777, 0.04883110523223877, 0.033876579254865646, 0.033876579254865646, 0.03318989276885986, 0.04120124503970146, 0.03715742006897926, 0.03715742006897926, 0.03883598744869232, 0.037844106554985046, 0.0474577322602272, 0.0474577322602272, 0.039675273001194, 0.035860344767570496, 0.04410059005022049, 0.03334248811006546, 0.036318134516477585, 0.036318134516477585, 0.037920404225587845, 0.04234572499990463, 0.042650919407606125, 0.042650919407606125, 0.05279863253235817, 0.05249343812465668, 0.036241836845874786, 0.036241836845874786, 0.039904169738292694, 0.052569735795259476, 0.02098211646080017, 0.02655191347002983, 0.02655191347002983, 0.04967039078474045, 0.05325642228126526, 0.029909051954746246, 0.029909051954746246, 0.06386192888021469, 0.07446743547916412, 0.037920404225587845, 0.037920404225587845, 0.04432948678731918, 0.05745284631848335, 0.03013794869184494, 0.023194774985313416, 0.042574621737003326, 0.042574621737003326, 0.03860709071159363, 0.03418177366256714, 0.031969115138053894, 0.043108709156513214, 0.04715253412723541, 0.044176891446113586, 0.03807300329208374, 0.03807300329208374, 0.051425255835056305]
    array2 = [0.0736455251635153, 0.07800582290153735, 0.0652990260077752, 0.06910360304055023, 0.07630872123017214, 0.07572949498105509, 0.07307735171447838, 0.06738785842540365, 0.06701228526986208, 0.06474273939429362, 0.07119971974267858, 0.06289817892659487, 0.06306212498376569, 0.0540943121136784, 0.06973881626379771, 0.06127244563451937, 0.05442730415646314, 0.08746119163379108, 0.0908671393567154, 0.08405614859381286, 0.05688812232663017, 0.05379351425773793, 0.04451733356603656, 0.048296408865405996, 0.058679057926200796, 0.05966073361861224, 0.05803264985912455, 0.06243687271365891, 0.05510264089322259, 0.04841157717599381, 0.07838954289842151, 0.09088743422820376, 0.08115187685965179, 0.04776841066951718, 0.04940178222794297, 0.042394730432581414, 0.039147518820695455, 0.051179793337804674, 0.05901337856846063, 0.05412570445152024, 0.06065151743951611, 0.04433451085263095, 0.04302538772670503, 0.05576329649873949, 0.06554466118412992, 0.08505619279063699, 0.05642584883824125, 0.04303604527733329, 0.04271655269782178, 0.03749300464980967, 0.050210733590151525, 0.04824979116026225, 0.047601535539552806, 0.04858239893879818, 0.04139515965591861, 0.04499191692196038, 0.046954694343125346, 0.04205091093701124, 0.049080750520006516, 0.054797312603066584, 0.04810601125362246, 0.04484114174829713, 0.04337414248088208, 0.042050759961372766, 0.05184919544506807, 0.047933465414759714, 0.04336017025469538, 0.05250732036440264, 0.062291024646562075, 0.05316074526372826, 0.04336134981762233, 0.040420887678158504, 0.051210196036497846, 0.053494986108244984, 0.04435371731498303, 0.04141551812253177, 0.03390056299335301, 0.042243501735272436, 0.04665113997076877, 0.04812195915462611, 0.050246392164764675, 0.06931482625735183, 0.05367503435867752, 0.05285773557749007, 0.04616904750752028, 0.0500926413394448, 0.05107124217809842, 0.05286567628361081, 0.05450059777309099, 0.029488326531580795, 0.036850113554354226, 0.04191548021524056, 0.044697283576367805, 0.05318635867702861, 0.057101602417770195, 0.04747790285264763, 0.05188641444431501, 0.045518368626819565, 0.05025846975986835, 0.04928095813196984, 0.05482825487661182, 0.06558631016746753, 0.03410357512323629, 0.03703037205279295, 0.04028627375102256, 0.04192203037664007, 0.04763946082794701, 0.04568061656406021, 0.044377131707920986, 0.04830065119202051, 0.042746144282579265, 0.053524573823514034, 0.04977329255830792, 0.04781625042822728, 0.05614141578241237, 0.03395683353588057, 0.03344472866992079, 0.038828431518594705, 0.040453670212206895, 0.0424145456204756, 0.04323535328057479, 0.04193141137980267, 0.0417689876901362, 0.04226135071955512, 0.048470647308801296, 0.04683976231780839, 0.0460252217898798, 0.05320825365172222, 0.04022622552197905, 0.03823840860516556, 0.03869778039817525, 0.042927245239178624, 0.040150663666458336, 0.04505690720440854, 0.04604034291607598, 0.04653130335834221, 0.05192260188643024, 0.050292844754912136, 0.04588411279824585, 0.0460494698995005, 0.04702766449400858, 0.03778525362616409, 0.03956550512320146, 0.040032977008111134, 0.04440583945188593, 0.04179082697859766, 0.04653228079103492, 0.04424907786271239, 0.05355947692845422, 0.06333949450560115, 0.047358820567598714, 0.045238916599857425, 0.047687738299140164, 0.050953091312644874, 0.02890806491759872, 0.031144065282302083, 0.03628644687241089, 0.045072699996912186, 0.04735302208103991, 0.04506779357961419, 0.04670431598397335, 0.05552136534889282, 0.0744059815376469, 0.04769327935035581, 0.04540762277502496, 0.05650227833195511, 0.05911343650568491, 0.03423463398737364, 0.027783504027306654, 0.0325434316280119, 0.04966761848102425, 0.04932500946692783, 0.04098858509482671, 0.03903048998748214, 0.047690263768056046, 0.04965101806173268, 0.04818567994909914, 0.04622949678148448, 0.05487949179099573, 0.057814678002201136]

    # make_fig('', np.array(array1), np.array(array2))
    # make_fig('', np.array(array2), np.array(array1))
    # scipy_linearRegression('', np.array(array1), np.array(array2), 'Array_MISR', 'Array_AHI')
    # scipy_linearRegression('', np.array(array2), np.array(array1), 'Array_AHI', 'Array_MISR')
    # pearson(array1, array2)