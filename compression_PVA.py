"""
Use: change the in_PATH and outPath then run.
Compress bw and color imageries using gdal translate, supports nested directory.
Python3 from qgis with gdal has been used.
"""


from osgeo import gdal
from pathlib import Path
import glob
import time
import sys
import logging

gdal.UseExceptions()
gdal.PushErrorHandler('CPLQuietErrorHandler')
logging.basicConfig(filename='c:/temp/gdal_error.log',
                    format='%(levelname)s:%(asctime)s %(message)s',
                    level=logging.INFO)

in_PATH = Path(r'S:\1_Photos_aeriennes\PVA_Catalogues')
out_PATH = r'S:\1_Photos_aeriennes\6_PVA_Catalogues_compress'

in_tif = []
out_tif = []



for filename in glob.glob(in_PATH / '**/*.tif', recursive=True):
# for filename in error_image:
    in_tif.append(filename)
    print(filename)
    filename = filename.replace(in_PATH, out_PATH)
    out_tif.append(filename)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)


start = time.time()

counter_color = 0
counter_bw = 0


for i, tif in enumerate(in_tif):
    print(f'Compressing picture: {tif}')
    try:
        ds = gdal.Open(tif)
        # if ds is None:
        #     print(f"IMPOSSIBLE D'OUVRIR L'IMAGE: {tif}")
        #     break
    except:
        print(f"Cannot open image error: {tif}")
        logging.error(gdal.GetLastErrorMsg())
        continue
    #########################################################################################

    bits_raster = None

    try:
        srcband = ds.GetRasterBand(1)
        RasterMinMax = srcband.ComputeRasterMinMax()
        if RasterMinMax[1] > 4096:
            bits_raster = '16bits'
        else:
            bits_raster = None
    except :
        print('No band found')
        logging.error(gdal.GetLastErrorMsg())

    #########################################################################################


    if ds.RasterCount == 3:
        counter_color += 1
        if bits_raster == '16bits':

            try:
                ds = gdal.Translate(out_tif[i], ds, format='GTiff', scaleParams=[[0, 4096]], outputType= gdal.GDT_Byte,
                                    creationOptions=['COMPRESS=JPEG', 'JPEG_QUALITY=90', 'BIGTIFF=IF_NEEDED', 'NBITS=8',
                                                     'PHOTOMETRIC=YCBCR'])
            except:
                print("Unexpected error color lzw:", sys.exc_info())
                logging.error(gdal.GetLastErrorMsg())


        else:
            try:
                ds = gdal.Translate(out_tif[i], ds, format='GTiff',
                                    creationOptions=['COMPRESS=JPEG', 'JPEG_QUALITY=90', 'PHOTOMETRIC=YCBCR',
                                                     'BIGTIFF=IF_NEEDED'])
            except:
                print("Unexpected error color:", sys.exc_info())
                logging.error(gdal.GetLastErrorMsg())

    elif ds.RasterCount == 1:
        counter_bw += 1
        if bits_raster == '16bits':
            try:
                ds = gdal.Translate(out_tif[i], ds, format='GTiff', scaleParams=[[]], outputType= gdal.GDT_Byte,
                                    creationOptions=['COMPRESS=JPEG', 'JPEG_QUALITY=80', 'BIGTIFF=IF_NEEDED', 'NBITS=8'
                                                     ])
            except:
                print("Unexpected error bw lzw:", sys.exc_info())
                logging.error(gdal.GetLastErrorMsg())
        else:
            try:
                ds = gdal.Translate(out_tif[i], ds, format='GTiff',
                                    creationOptions=['COMPRESS=JPEG', 'JPEG_QUALITY=80', 'BIGTIFF=IF_NEEDED'
                                                     ])
            except:
                print("Unexpected error bw:", sys.exc_info())
                logging.error(gdal.GetLastErrorMsg())
    else:
        print('Warning: Image not processed number of bands over 3: {} bands'.format(ds.RasterCount))
    ds = None
    band = None
end = time.time()


print(end - start)
print(f'Number of bw: {counter_bw}')
print(f'Number of color: {counter_color}')
print(f'Total number of images: {len(in_tif)}')


