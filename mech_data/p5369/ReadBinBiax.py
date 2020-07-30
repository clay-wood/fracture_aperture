import numpy as np
import struct
import pandas as pd

def ReadBinBiax(filename, dataendianness):
    # filename='C:/Users/claywood93/Desktop/p4966/p4966_data_bin'
    # dataendianness='little'; 
    pandas=True; 

    try:
        f = open(filename,'rb')
    except:
        print("Error Opening %s "+filename)
    #     0

    col_headings = []
    col_recs     = []
    col_units    = []

    # Unpack information at the top of the file about the experiment
    name = struct.unpack('20c',f.read(20))
    name = ''.join(str(i) for i in name)
    name=name[::2]
    name=''.join(c for c in name[1:-1:2] if c not in '?:!/\;' ).replace(' ', '')
    print('\nName: ',name)

    # The rest of the header information is written in big endian format

    # # Number of records (int)
    num_recs = struct.unpack('>i',f.read(4))
    num_recs = int(num_recs[0])
    print("Number of records: %d" %num_recs)

    # # Number of columns (int)
    num_cols =  struct.unpack('>i',f.read(4))
    num_cols = int(num_cols[0])
    print("Number of columns: %d" %num_cols)

    # # Sweep (int) - No longer used
    swp =  struct.unpack('>i',f.read(4))[0]
    # print("Swp: ",swp)

    # # Date/time(int) - No longer used
    dtime =  struct.unpack('>i',f.read(4))[0]
    # print("dtime: ",dtime)

    # For each possible column (32 maximum columns) unpack its header
    # information and store it.  Only store column headers of columns
    # that contain data.  Use termination at first NUL.
    for i in range(32):

        # Channel name (13 characters)
        chname = struct.unpack('13c',f.read(13))
        chname = ''.join(str(i) for i in chname)
        chname = ''.join(c for c in chname[2:-1:4] if c not in '0\?:!/;xb' ).replace('', '').strip('\'')

        # Channel units (13 characters)
        chunits = struct.unpack('13c',f.read(13))
        chunits = ''.join(str(i) for i in chunits)
        chunits = ''.join(c for c in chunits[2:-1:4] if c not in '0\?:!/;xb' ).replace('', '').strip('\'')

    #     This field is now unused, so we just read past it (int)
        gain = struct.unpack('>i',f.read(4))

    #     This field is now unused, so we just read past it (50 characters)
        comment = struct.unpack('50c',f.read(50))

    #     Number of elements (int)
        nelem = struct.unpack('>i',f.read(4))
        nelem = int(nelem[0])

        if chname == 'no_val':
            continue # Skip Blank Channels
        else:
            col_headings.append(chname)
            col_recs.append(nelem)
            col_units.append(chunits)


    # Show column units and headings
    print("\n\n-------------------------------------------------")
    print("|%15s|%15s|%15s|" %('Name','Unit','Records'))
    print("-------------------------------------------------")
    for column in zip(col_headings,col_units,col_recs):
        print("|%15s|%15s|%15s|" %(column[0],column[1],column[2]))
    print("-------------------------------------------------")

    # Read the data into a numpy recarray
    dattype=[]
    for name in col_headings:
        dattype.append((name,'single'))
    dattype = np.dtype(dattype)

    data = np.zeros([num_recs,num_cols])

    for col in range(num_cols):
        for row in range(col_recs[col]):
            if dataendianness == 'little':
                data[row,col] = np.array(struct.unpack('<d',f.read(8)))[0]
            elif dataendianness == 'big':
                data[row,col] = np.array(struct.unpack('>d',f.read(8)))[0]
            else:
                print("Data endian setting invalid, please check and retry")
    #             return 0
    data_rec = np.rec.array(data)
    f.close()

    if pandas==True:
    #     If a pandas object is requested, make a data frame
    #     indexed on row number and return it
        dfo  = pd.DataFrame(data)
    #     Binary didn't give us a row number, so we just let
    #     pandas do that and name the index column
        dfo.index.name = 'row_num'
        return dfo

    else:
        # Otherwise return the default (Numpy Recarray)
        data_rec = np.rec.array(data,dtype=dtype)
        return data_rec
