def get_parameter(LC,SGLI,AHI,band):
    AHI = identifer(AHI)
    SGLI = identifer(SGLI)
    slope,offset = get_SBAF(LC,band)

    SGLI_1 = np.array(SGLI).flatten()
    AHI_1 = np.array(AHI).flatten()
    nan_mask_1 = np.where(np.isnan(SGLI_1),False,True)
    nan_mask_2 = np.where(np.isnan(AHI_1),False,True)
    nan_mask = []
    for i in range(len(nan_mask_1)):
        if nan_mask_1[i] == False or  nan_mask_2[i] == False:
            nan_mask.append(False)
        else:
            nan_mask.append(True)
    SGLI_1 = SGLI_1[nan_mask]
    AHI_1 = AHI_1[nan_mask]

    X = SGLI_1 * slope + offset
    Y = AHI_1

    rmse = np.sqrt(mean_squared_error(X ,Y))
    p = np.polyfit(X ,Y,1)    

    k = round(p[0],2)
    b = round(p[1],2)
    rmse = round(rmse.astype('float64'),3)
    pccs = np.corrcoef(X, Y)[0,1]
    r = round(pccs.astype('float64'),3)
    
    return X,Y,k,b,r,rmse,len(X)

def add_right_cax(ax, pad, width):

    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(
        axpos.x1 + pad,
        axpos.y0,
        axpos.x1 + pad + width,
        axpos.y1
    )
    cax = ax.figure.add_axes(caxpos)

    return cax

def make_fig(j,LC,axis_max,axis_min,X,Y,k,b,r,rmse,N,band):
        
    ax1 = axes[j]
    ax1.set_aspect('equal', adjustable='box')    
    x = np.arange(axis_min,axis_max+1)
    y = 1 * x
    
    xx = np.arange(axis_min,axis_max+0.1,0.05) 
    yy = k * xx + b
    
    # Calculate the point density
    xy = np.vstack([X,Y])
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

    ax1.tick_params(axis="y",which='minor',length=5,direction='in',labelsize=8)
    ax1.tick_params(axis="y",which='major',length=10,direction='in',labelsize=8)

    ax1.tick_params(axis="x",which='minor',length=5,direction='in',labelsize=8)
    ax1.tick_params(axis="x",which='major',length=10,direction='in',labelsize=8)


    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')


    im = ax1.scatter(X,Y,marker='o', c=z,s=5,cmap='Spectral_r')

    ax1.set_xticks(np.arange(axis_min,axis_max+0.1,0.1))
    ax1.set_yticks(np.arange(axis_min+0.1,axis_max+0.1,0.1))
    
    # if band == 4:
    #     ax1.set_ylabel("AHI Surface Reflectance Band4",fontsize=12)
    #     ax1.set_xlabel("SGLI Surface Reflectance PI02",fontsize=12)
    # elif band == 3:
    #     ax1.set_ylabel("AHI Surface Reflectance Band3",fontsize=12)
    #     ax1.set_xlabel("SGLI Surface Reflectance PI01",fontsize=12)
        
    ax1.plot(x,y,color='k',linewidth=1,linestyle='-.')
    ax1.plot(xx,yy,color='r',linewidth=1,linestyle='-') 


    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.35

    ax1.text(text_x,text_y,s = 'Land Cover : {}\ny = {} + {}x\nN = {}\nRMSE = {}\nr = {}'.format(LC,k,b,N,rmse,r),fontsize=12)

    cax = add_right_cax(ax1,pad=0.01,width=0.03)
    cb = fig.colorbar(im,cax=cax)
    cb.ax.set_xlabel('Count',rotation=360)
    ax1.set_xlim(axis_min,axis_max)
    ax1.set_ylim(axis_min,axis_max)