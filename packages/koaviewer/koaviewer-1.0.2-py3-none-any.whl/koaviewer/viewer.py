import importlib.resources
from pathlib import Path
import base64

class koaViewer:

    def __init__(self):
        self.model = None

    def run(self, work, debug=False):

        import os.path
        import sys
        import math
        import socket
        import mviewer

        from dash import Dash, callback, callback_context, clientside_callback
        from dash import html, dcc, Input, Output, State, ALL, ctx, no_update

        from dash.exceptions import PreventUpdate

        import plotly.express as px
        import plotly.graph_objs as go
        import dash_bootstrap_components as dbc
        import dash_ag_grid as dag

        import pandas as pd
        import json
        import shutil

        import time
        import datetime

        from astropy.io import ascii

        from MontagePy.main import mExamine, mCoord, mSubimage, mShrink, mViewer, mCoverageCheck

        from PIL import Image
        from pathlib import Path


        # ---------------------------------------------------
        # 
        # NOTE:  Use of ZOOMBOX
        # 
        # The mapping of the PNG that is sent to the Javascript React component
        # aligns the PNG with the display window as follows.  'zoom' tracks the factor by
        # which the PNG should be sampled.  We define the image display Div to be bigger
        # or smaller that the actual PNG size by this factor and the browser samples 
        # appropriately.
        # 
        # 'width' and 'height' are the size of the display window, often smaller than 
        # the image display Div 'under' it (other parts of it accessed by panning).
        # 
        # 'xmin', 'ymin', 'dx' and 'dy' define the pixel box in the original FITS image
        # that will later be used by mSubimage() to provide a new image to be zoomed
        # and finally 'zoom' is used by mShrink() to make the new, zoomed-in, PNG.
        # 'dx' and 'dy' track the amount the box has been panned away from the upper
        # left corner (and 'dy' is reversed since FITS/Montage uses bottom-up where 
        # PNG uses top-down).
        # 
        # This is sent to React with every re-render (which happens frequently).  There
        # the parameters will get modified with every window resize and zoom / pan
        # operation.  These get passed back to the Python code via setProps().
        # 
        # Zooming is controlled by zoom in / out buttons in the React component and 
        # panning by scrollbars.
        # 
        # Example:
        #
        #    zoombox = {'zoom': 1, 'width': windowWidth, 'height': windowHeight, 
        #               'xmin': 0, 'ymin': 0, 'dx': windowWidth, 
        #               'dy': main_size[1]-windowHeight}
        # 
        # ---------------------------------------------------

        # Palette of colors to use for map overlays (and table labels)

        palette = ["#ffffff", "#fb6e6e", "#ff8000", "#ffff00", "#00ff00",
                   "#f9aeda", "#0bffbf", "#bdff39", "#0bdeff",
                   "#fc59a3", "#ffe30e", "#ffb000", "#e9f9e5",
                   "#ffb5c0", "#97d0ad", "#93b0e7", "#d5af26"]


        # ---------------------------------------------------
        # Find the 'assets' directory for the app

        app_data_dir = importlib.resources.files('koaviewer')

        assets_path  = app_data_dir.joinpath('data')


        # ---------------------------------------------------
        # LAYOUT INFO FROM COMMAND-LINE JSON FILE

        # Find and read the layout.json file.
        # This block is for command-line use.  We will
        # have to do it differently for web service use.

        workdir = os.path.expanduser(work)

        if not os.path.isdir(workdir):
            try:
                os.mkdir(workdir)
            except:
                pass

            try:
                os.mkdir(workdir + '/fits')
            except:
                pass

            try:
                os.mkdir(workdir + '/tbl')
            except:
                print('Error: "' + workdir + '" does not exist and we cannot create it.')
                sys.exit()


        # List workspace contents.  This will help the user 
        # update the layout or create a basic layout.json 
        # if none exists.

        directory = workdir + '/fits'

        try:
            images = sorted(os.listdir(directory))
        except:
            pass

        directory = workdir + '/tbl'

        try:
            tables = sorted(os.listdir(directory))
        except:
            pass


        # Check for a pre-existing layout.json file

        layout_file = workdir + '/layout.json'

        try:
            json_data = open(layout_file)

            layout_dict = json.load(json_data)
            json_data.close()
            
            overlays = layout_dict['Overlays']

            for overlay in overlays:
                if 'Show' not in overlay:
                    overlay['Show'] = True


        except FileNotFoundError:

            # If layout.json does not exist create a new  minimal one from file info.

            try:
                layout_dict = {}

                grayscale = []
                image     = {}

                image['File']         = 'fits/' + images[0]
                image['Color Table']  = 'Grayscale'
                image['Stretch Mode'] = 'Gaussian-log'
                image['Min']          = '-0.5'
                image['Min Units']    = 'sigma'
                image['Max']          = 'max'
                image['Max Units']    = 'sigma'
                image['Brightness']   = 0
                image['Contrast']     = 0

                grayscale.append(image)

                layout_dict['Grayscale'] = grayscale

                overlays = []
                index    = 0

                for table in tables:
                    overlay = {}

                    overlay['Show']              = True
                    overlay['Type']              = 'Catalog'
                    overlay['File']              = 'tbl/' + table
                    overlay['Color']             = palette[index]
                    overlay['Size of Ref Value'] = 3.0
                    overlay['Symbol']            = 'box'

                    overlays.append(overlay)

                    index = index + 1

                overlay = {}
                overlay['Show']  = True
                overlay['Type']  = 'Eq grid'
                overlay['Color'] = 'gray'

                overlays.append(overlay)
                layout_dict['Overlays'] = overlays

                print('\nlayout.json:\n')
                print(json.dumps(layout_dict, indent=2))

                print('\nMinimal layout.json.  You can add details using Image/Overlays pop-up controls.')

            except:
                print('Cannot create "' + layout_file + '".')
                sys.exit()



        # Check whether we are using a grayscale image or full color (three
        # images)

        mode = "Color"

        try:
            test = layout_dict['Grayscale']
            mode = 'Grayscale'
        except:
            pass


        # Create a "tmp" directory inside the workspace for temporary cutouts, etc.
        # Clear out the tmp directory if it was left over from a previous # session.

        tmpdir = workdir + '/tmp/'

        try:
            shutil.rmtree(tmpdir)
        except:
            pass

        try:
            os.mkdir(tmpdir)
        except:
            print('Error: Could not create "' + tmpdir + '".')
            sys.exit()



        # ---------------------------------------------------
        # SOME LOOKUP TABLES

        units   = {
                      'sigma':      's',
                      'percentile': '%',
                      'value':      ''
                  }

        stretch = {
                      'Linear':       'lin',
                      'Log':          'log',
                      'Loglog':       'loglog',
                      'Gaussian':     'gaussian',
                      'Gaussian-log': 'gaussian-log'
                  }

        ctable  = {
                      'Grayscale':         '0',
                      'Reverse grayscale': '1',
                      'Spectrum':          '4',
                      'Velocity':          '6'
                  }

        scaling = {
                      'flux':      '',
                      'log(flux)': 'log',
                      'magnitude': 'mag'
                  }


        # Create the initial PNG (and inset PNG)

        imgdict = {"image_type":"png"}
        
        if 'Brightness' in layout_dict:
            imgdict['brightness'] = layout_dict['Brightness']

        if 'Contrast' in layout_dict:
            imgdict['contrast'] = layout_dict['Contrast']

        image_label = 'Region'

        try:
            image_label = layout_dict['Image Label']
        except:
            pass

        if mode == 'Color':

            color = layout_dict['Color']

            for colr in color:

                colr_value = colr['Color']

                if colr['Min'] == 'min':
                    colr['Min Units'] = 'value'

                if colr['Max'] == 'max':
                    colr['Max Units'] = 'value'

                colr_data = {
                    "stretch_min":  colr['Min'] + units[colr['Min Units']],
                    "stretch_max":  colr['Max'] + units[colr['Max Units']],
                    "stretch_mode": stretch[colr['Stretch Mode']]
                }

                if colr_value == 'Blue':
                    colr_data['fits_file'] = workdir + '/' + colr['File']
                    imgdict['blue_file']  = colr_data

                if colr_value == 'Green':
                    colr_data['fits_file'] = workdir + '/' + colr['File']
                    imgdict['green_file'] = colr_data

                if colr_value == 'Red':
                    colr_data['fits_file'] = workdir + '/' + colr['File']
                    imgdict['red_file']   = colr_data

        else:

            grayscale = layout_dict['Grayscale']

            if grayscale[0]['Min'] == 'min':
                grayscale[0]['Min Units'] = 'value'

            if grayscale[0]['Max'] == 'max':
                grayscale[0]['Max Units'] = 'value'

            gray_file = {
                "fits_file":    workdir + '/' + grayscale[0]['File'],
                "stretch_min":  grayscale[0]['Min'] + units[grayscale[0]['Min Units']],
                "stretch_max":  grayscale[0]['Max'] + units[grayscale[0]['Max Units']],
                "stretch_mode": stretch[grayscale[0]['Stretch Mode']]
            }

            color_table = grayscale[0]['Color Table']
 
            try:
                color_table = ctable[color_table]
            except:
                pass

            color_table = str(color_table)

            gray_file['color_table'] = color_table

            imgdict['gray_file']  = gray_file


        overlays = layout_dict['Overlays']

        new_overlays = []

        catalogs = []
        colors   = []

        color_lookup = {}

        for ovly in overlays:

            if 'Type' not in ovly:
                continue

            if 'Show' in ovly and ovly['Show'] == False:
                continue


            if ovly['Type'] == 'Catalog':

                if 'File' not in ovly:
                    continue

                new_overlay = {}

                new_overlay['type'] = 'catalog'

                new_overlay['data_file'] = workdir + '/' + ovly['File']

                catalogs.append(new_overlay['data_file'])

                if 'Column' in ovly:
                    new_overlay['data_column'] = ovly['Column']

                if 'Ref Value' in ovly:
                    new_overlay['data_ref'] = ovly['Ref Value']

                if 'Scaling' in ovly:
                    new_overlay['data_type'] = ovly['Scaling']

                if 'Symbol' in ovly:
                   new_overlay['symbol'] = ovly['Symbol']
                else:
                   new_overlay['symbol'] = 'square'

                if 'Size of Ref Value' in ovly:
                   new_overlay['sym_size'] = ovly['Size of Ref Value']
                else:
                   new_overlay['sym_size'] = 5

                new_overlay['coord_sys'] = 'Equ J2000'

                if 'Color' in ovly:
                    new_overlay['color'] = ovly['Color']
                else:
                    new_overlay['color'] = 'ffff00'

                color = new_overlay['color']

                colors.append(color)

                catalog  = new_overlay['data_file']
                basename = Path(catalog).stem.upper() 

                color_lookup[basename] = color


            elif ovly['Type'] == 'Images':

                if 'File' not in ovly:
                    continue

                new_overlay = {
                                   'type':        'imginfo',
                                   'data_file':   workdir + '/' + ovly['File'],
                                   'coord_sys':   'Equ J2000',
                                   'color':       ovly['Color']
                              }


            elif ovly['Type'] == 'Eq grid':

                new_overlay = {
                                   'type':        'grid',
                                   'coord_sys':   'Equ J2000',
                                   'color':       ovly['Color']
                              }


            elif ovly['Type'] == 'Ec grid':

                new_overlay = {
                                   'type':        'grid',
                                   'coord_sys':   'Ecl J2000',
                                   'color':       ovly['Color']
                              }


            elif ovly['Type'] == 'Ga grid':

                new_overlay = {
                                   'type':        'grid',
                                   'coord_sys':   'ga',
                                   'color':       ovly['Color']
                              }

            new_overlays.append(new_overlay)
            
        imgdict['overlays'] = new_overlays


        # Convert the the dict to JSON as this is what mViewer will use to make the
        # PNG.

        main_image      = workdir + '/main.png'
        thumbnail_image = workdir + '/thumbnail.png'

        imgjson = json.dumps(imgdict)

        if debug == True:
            print('\nDEBUG> INIT imgjson:', imgjson, '\n')

        if debug == True:
            print('\nDEBUG> INIT mViewer (imgjson):', main_image)

        rtn = mViewer(imgjson, main_image, mode=1)

        if debug == True:
            print('\nDEBUG> main() mViewer rtn:', rtn)

        main_size = Image.open(main_image).size

        xsize = main_size[0]
        ysize = main_size[1]

        if xsize > ysize:
            ysize = 100. * ysize / xsize
            xsize = 100.

        else:
            xsize = 100. * xsize / ysize
            ysize = 100.

        try:
            size = xsize, ysize

            im = Image.open(main_image)
            im.thumbnail(size, Image.Resampling.LANCZOS)
            im.save(thumbnail_image, 'PNG')

            thumbnail_size = Image.open(thumbnail_image).size

        except IOError:
            print("Error: Cannot create thumbnail for '%s'" % main_image)
            sys.exit(0)

        cutout_file = workdir + '/tmp/cutout.png'


        # Make base64 versions of the images

        with open(main_image, 'rb') as image:
            encoded = base64.b64encode(image.read()).decode()
            main_data = f'data:image/png;base64, {encoded}'

        with open(thumbnail_image, 'rb') as image:
            encoded = base64.b64encode(image.read()).decode()
            thumbnail_data = f'data:image/png;base64, {encoded}'
        
            

        # ---------------------------------------------------
        # TABLE DATA

        table_tabs  = []
        table_files = []

        left = 10
        top  = 5

        index = 0

        for catalog in catalogs:

            basename = Path(catalog).stem.upper()

            tbl_data = ascii.read(catalog)

            tbl_df = tbl_data.to_pandas()

            tbl_df['Dist'] = ''

            table = dag.AgGrid(
                id={'type': 'tbldata', 'index': basename},
                rowData=tbl_df.to_dict('records'),
                columnDefs=[{'field': i} for i in tbl_df.columns],
                defaultColDef={'resizable': True, 'sortable': True, 'filter':
                               True, 'minWidth':115},
                columnSize='sizeToFit',
                dashGridOptions={'pagination':             True,
                                 'paginationAutoPageSize': True,
                                 'rowSelection':           'multiple'},
                className='ag-theme-balham-dark',
                style={'height': '1000px', 'width': '100%', 'border': '0px solid red'}
            )

            catalog_tab = dbc.Tab(label=basename,
                                  children=[table], 
                                  label_style={'color': '#' + color_lookup[basename]})

            table_tabs.append(catalog_tab)

            table_files.append([catalog, basename])

            index = index + 1


        catalog_tabs = dbc.Tabs(children=table_tabs, id='table_tabs') 


        # ---------------------------------------------------
        # START THE DASH APP

        app = Dash(__name__, assets_folder=assets_path, external_stylesheets=[dbc.themes.DARKLY])


        # ---------------------------------------------------
        # SET UP 'OVERLAYS' MODAL

        ovly_columnDefs=[
        {
            'field': 'Show',
            'cellRenderer': 'DBC_Switch',
            'cellEditorParams': {'color': 'success'},
            'editable': True
        },
        {
            "field": "Type",
            "cellEditor": "agTextCellEditor",
            'editable': True
        },
        {
            "field": "Color",
            "cellEditor": "agTextCellEditor",
            'editable': True
        },
        {
            "field": "File",
            "cellEditor": "agTextCellEditor",
            'editable': True
        },
        {
            "field": "Column",
            "cellEditor": "agTextCellEditor",
            'editable': True
        },
        {
            "field": "Ref Value",
            "cellEditor": "agTextCellEditor",
            'editable': True
        },
        {
            "field": "Size of Ref Value",
            "cellEditor": "agTextCellEditor",
            'editable': True
        },
        {
            'field': 'Scaling',
            'cellEditor': 'agSelectCellEditor',
            'cellEditorParams': {
                'values': [
                    'flux',
                    'log(flux)',
                    'magnitude',
                ]},
            'editable': True
        },
        {
            'field': 'Symbol',
            'cellEditor': 'agSelectCellEditor',
            'cellEditorParams': {
                'values': [
                    'circle',
                    'box',
                    'plus',
                    'compass',
                    'triangle',
                    'square',
                    'diamond',
                    'pentagon',
                    'hexagon',
                    'septagon',
                    'octagon',
                ]},
            'editable': True
        }]


        overlays_table = dag.AgGrid(
            id='overlays_table',
            rowData=layout_dict['Overlays'],
            columnDefs=ovly_columnDefs,

            defaultColDef={'resizable': True,
                           'sortable':  False,
                           'filter':    False,
                           'minWidth':  0},

            columnSize='sizeToFit',

            dashGridOptions={'pagination':                False,
                             'rowSelection':             'multiple',
                             'supressRowClickSelection':  True,
                             'rowDragManaged':            True},

            className='ag-theme-alpine'
        )

        ovly_response = html.Div([html.P(id='response')])

        ovly_addCatalog   = html.Button('Add Catalog',        id='ovly_addCatalog',   n_clicks=0, className='controlBtn')
        ovly_addImage     = html.Button('Add Image Metadata', id='ovly_addImage',     n_clicks=0, className='controlBtn')
        ovly_addEqu       = html.Button('Add Equ J200 Grid',  id='ovly_addEqu',       n_clicks=0, className='controlBtn')
        ovly_addGal       = html.Button('Add Galactic Grid',  id='ovly_addGal',       n_clicks=0, className='controlBtn')
        ovly_addEcl       = html.Button('Add Ecl J200 Grid',  id='ovly_addEcl',       n_clicks=0, className='controlBtn')

        ovly_modal = html.Div(
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle('Image Overlays',
                                                       style={'font-size': '20px', 'font-style': 'italic'})),

                        dbc.ModalBody(
                            dbc.Form([

                                html.Div([
                                    ovly_addCatalog, ovly_addImage, ovly_addEqu, ovly_addGal, ovly_addEcl
                                ]),

                                overlays_table
                            ])
                        ),

                        dbc.ModalFooter(
                            dbc.Button('Close', id='ovly_closeBtn', className='ml-auto')
                        )],

                        id='ovly_modal',
                        is_open=False,    # True, False
                        size='xl',        # 'sm', 'lg', 'xl'
                        backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
                        scrollable=True,  # False or True if modal has a lot of text
                        centered=True,    # True, False
                        fade=True         # True, False
                    )
                )


        # ---------------------------------------------------
        # SET UP GRAYSCALE IMAGE MODAL

        gray_columnDefs=[
            {'field': 'File', 'editable': True},

            {
                'field': 'Stretch Mode',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'Linear',
                        'Log',
                        'Loglog',
                        'Gaussian',
                        'Gaussian-log'
                    ]},
                'editable': True
            },

            {'field': 'Min', 'editable': True},

            {
                'field': 'Min Units',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'value',
                        'percentile',
                        'sigma'
                    ]},
                'editable': True
            },

            {'field': 'Max', 'editable': True},

            {
                'field': 'Max Units',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'value',
                        'percentile',
                        'sigma'
                    ]},
                'editable': True
            },

            {
                'field': 'Color Table',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'Grayscale',
                        'Reverse grayscale',
                        'Spectrum',
                        'Velocity'
                    ]},
                'editable': True
            }
        ]


        if mode == 'Grayscale':
            row_data   = layout_dict['Grayscale']
            gray_dict  = layout_dict['Grayscale']
            color_dict = []
        else:
            row_data   = layout_dict['Color']
            color_dict = layout_dict['Color']
            gray_dict  = []


        gray_imginfo = dag.AgGrid(
            id='gray_imginfo',
            rowData=row_data,
            columnDefs=gray_columnDefs,

            defaultColDef={'resizable': True,
                           'minWidth':  0},

            columnSize='sizeToFit',

            dashGridOptions={'pagination': False},

            className='ag-theme-alpine'
        )

        gray_modal = html.Div(
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle('Grayscale Image',
                                                       style={'font-size': '20px', 'font-style': 'italic'})),

                        dbc.ModalBody(
                            dbc.Form([

                                gray_imginfo

                            ])
                        ),

                        dbc.ModalFooter(
                            dbc.Button('Close', id='gray_closeBtn', className='ml-auto')
                        )],

                        id='gray_modal',
                        is_open=False,    # True, False
                        size='xl',        # 'sm', 'lg', 'xl'
                        backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
                        scrollable=True,  # False or True if modal has a lot of text
                        centered=True,    # True, False
                        fade=True         # True, False
                    )
                )


        # ---------------------------------------------------
        # SET UP COLOR IMAGE MODAL

        color_columnDefs=[
            {'field': 'Color', 'editable': False},
            {'field': 'File',  'editable': True},

            {
                'field': 'Stretch Mode',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'Linear',
                        'Log',
                        'Loglog',
                        'Gaussian',
                        'Gaussian-log'
                    ]},
                'editable': True
            },

            {'field': 'Min', 'editable': True},

            {
                'field': 'Min Units',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'value',
                        'percentile',
                        'sigma'
                    ]},
                'editable': True
            },

            {'field': 'Max', 'editable': True},

            {
                'field': 'Max Units',
                'cellEditor': 'agSelectCellEditor',
                'cellEditorParams': {
                    'values': [
                        'value',
                        'percentile',
                        'sigma'
                    ]},
                'editable': True
            }
        ]


        color_imginfo = dag.AgGrid(
            id='color_imginfo',
            rowData=row_data,
            columnDefs=color_columnDefs,

            defaultColDef={'resizable': True,
                           'sortable': False,
                           'minWidth':  0},

            columnSize='sizeToFit',

            dashGridOptions={'pagination': False},

            className='ag-theme-alpine'
        )

        color_modal = html.Div(
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle('Images for Color Display',
                                                       style={'font-size': '20px', 'font-style': 'italic'})),

                        dbc.ModalBody(
                            dbc.Form([
                                color_imginfo
                            ])
                        ),

                        dbc.ModalFooter(
                            dbc.Button('Close', id='color_closeBtn', className='ml-auto')
                        )],

                        id='color_modal',
                        is_open=False,    # True, False
                        size='xl',        # 'sm', 'lg', 'xl'
                        backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
                        scrollable=True,  # False or True if modal has a lot of text
                        centered=True,    # True, False
                        fade=True         # True, False
                    )
                )



        # ---------------------------------------------------
        # SET UP PICK MODAL


        pick_modal = html.Div(
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle('Pick Info',
                                                       style={'font-size': '20px', 'font-style': 'italic'})),

                        dbc.ModalBody(
                            html.Div([html.Pre('', id='pickinfo')], 
                                     style={'height': '100px', 'backgroundColor': 'white', 'font-size': '12px'})
                        ),

                        dbc.ModalFooter(
                            dbc.Button('Close', id='pick_closeBtn', className='ml-auto')
                        )],


                        id='pick_modal',
                        is_open=False,    # True, False
                        size='md',        # 'sm', 'lg', 'xl'
                        backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
                        scrollable=True,  # False or True if modal has a lot of text
                        centered=True,    # True, False
                        fade=True         # True, False
                    )
                )


        # ---------------------------------------------------

        # LAYOUT (BUTTONS, MVIEWER, MODALS)

        main_size = Image.open(main_image).size

        imgWidth  = main_size[0]
        imgHeight = main_size[1]

        cutout_dict = {'level'      : 1,
                       'img_width'  : imgWidth,
                       'img_height' : imgHeight,
                       'factor'     : 1.,
                       'xmin'       : 0,
                       'xmax'       : imgWidth,
                       'ymin'       : 0,
                       'ymax'       : imgHeight,
                       'label'      : ''}

        xsize = main_size[0]
        ysize = main_size[1]

        if xsize > ysize:
            ysize = 100. * ysize / xsize
            xsize = 100.

        else:
            xsize = 100. * xsize / ysize
            ysize = 100.

        try:
            thumbnail_image = workdir + '/thumbnail.png'

            size = xsize, ysize

            im = Image.open(main_image)
            im.thumbnail(size, Image.Resampling.LANCZOS)
            im.save(thumbnail_image, 'PNG')

            thumbnail_size = Image.open(thumbnail_image).size

        except IOError:
            print("Error: Cannot create thumbnail for '%s'" % main_image)
            sys.exit(0)

        windowWidth  = 800
        windowHeight = 800


        zoom_x = windowWidth / imgWidth
        zoom_y = windowHeight / imgHeight

        zoom = zoom_x
        if zoom_y < zoom:
            zoom = zoom_y

        zoombox = {'zoom': zoom, 'width': windowWidth, 'height': windowHeight, 
                   'xmin': 0, 'ymin': 0, 'dx': imgWidth, 'dy': imgHeight}

        if debug == True:
            print('\nDEBUG> Initial zoombox (passed into Mviewer():', zoombox)


        titleHeight  = 25
        appBtnHeight = 25
        infoHeight   = 20
         
        paneHeight = windowHeight + titleHeight + appBtnHeight + infoHeight
        paneWidth  = windowWidth;

        appbtn = html.Div([
            html.Button('Image',           className="cmdBtn", id='showImageStretch'),
            html.Button('Overlays',        className="cmdBtn", id='showOverlays'), 
            html.Button('Cutout',          className="cmdBtn", id='cutoutImg'),
            html.Button('Full Image',      className="cmdBtn", id='restoreImg'),
            html.Button('Clear Selection', className="cmdBtn", id='clearSelect')
        ],
            style={'display': 'flex', 'height': appBtnHeight, 'width': '100%'},
            id='appBtn')

        app.layout=html.Div(children=[

            color_modal,
            gray_modal,
            ovly_modal,
            pick_modal,

            dcc.Store(id='config',
                      data=[{'mode':       mode,  
                             'isCutout':   False,
                             'imgWidth':   imgWidth,
                             'imgHeight':  imgHeight,
                             'workdir':    workdir,
                             'first':      True}],
                      storage_type='memory'),

            dcc.Store(id='layout_store',    data=layout_dict,  storage_type='memory'),
            dcc.Store(id='zoombox',         data=zoombox,      storage_type='memory'),
            dcc.Store(id='color_lookup',    data=color_lookup, storage_type='memory'),
            dcc.Store(id='cutout_dict',     data=cutout_dict,  storage_type='memory'),

            dcc.Store(id='box',          data=[], storage_type='memory'),
            dcc.Store(id='pick',         data=[], storage_type='memory'),
            dcc.Store(id='imgcmd',       data=[], storage_type='memory'),

            dcc.Store(id='table_files', data=table_files, storage_type='memory'),
            
            html.Div([

                html.Div([image_label], 
                         className='title', id='title',
                         style={'height': str(titleHeight) + 'px'}),

                appbtn,

                mviewer.Mviewer(
                    id='viewer',
            
                    img         = main_data,
                    imgWidth    = main_size[0],
                    imgHeight   = main_size[1],
            
                    inset       = thumbnail_data,
                    insetWidth  = xsize,
                    insetHeight = ysize,

                    zoombox     = zoombox,

                    cutoutDesc  = ''
                ),

                html.Div( '', className='corner')

            ], className='pane', id='viewer_pane', 
                style={'height': str(paneHeight) + 'px', 'width': str(paneWidth) + 'px', 
                       'left': '75px', 'top': '75px', 'backgroundColor':
                       '#2c3539', 'zIndex': '2'}),

            html.Div([
        
                html.Div(['Catalogs'], className='title', id='table_title'),
                catalog_tabs,
                html.Div( '', className='corner', id='table_corner')
        
            ], className='pane',
                id='table_pane',
                style={'left': str(left) + 'px', 'top': str(top) + 'px',
                       'width': '1300px', 'height': '800px', 
                       'background': '#808080', 'zIndex': '1'}),

            html.Div([], id='tblmsg', style={'display': 'none'}),
        ])


        # ---------------------------------------------------
        # CLIENT_SIDE CALLBACK: WATCH IMAGE VIEWER PANE FOR RESIZES AND ADJUST CONTENTS.

        app.clientside_callback(
            """
            function viewer_resize_event(viewerpane_id) {

                var callback = function() {

                    var pane_style = document.getElementById('viewer_pane').style;

                    var pane_width  = parseInt(pane_style.width.slice(0,-2))
                    var pane_height = parseInt(pane_style.height.slice(0,-2))


                    var title_style = document.getElementById('title').style;

                    var title_height = parseInt(title_style.height.slice(0,-2))


                    var appBtn_style = document.getElementById('appBtn').style;

                    var appBtn_height = parseInt(appBtn_style.height.slice(0,-2))


                    var imgBtn_style = document.getElementById('imgBtn').style;

                    var imgBtn_height = parseInt(imgBtn_style.height.slice(0,-2))


                    var info_style = document.getElementById('info').style;

                    var info_height = parseInt(info_style.height.slice(0,-2))

                    var box_height = pane_height - title_height - appBtn_height - imgBtn_height - info_height;

                    var appBtn_width = pane_width;
                    var box_width    = pane_width;
                    var info_width   = pane_width;


                    var box_style = document.getElementById('mainBox').style;

                    appBtn_style.width = appBtn_width + 'px';
                    box_style.width    = box_width    + 'px';
                    info_style.width   = appBtn_width + 'px';

                    box_style.height   = box_height   + 'px';
                }

                new ResizeObserver(callback).observe(document.getElementById('viewer_pane'));

                pane_init();

                return width, height;
            }
            """,

            Output("viewer",      "width"),
            Output("viewer",      "height"),
            Input ("viewer_pane", "id")
        )


        # ---------------------------------------------------
        # CLIENT_SIDE CALLBACK: WATCH TABLE DISPLAY PANE FOR RESIZES AND ADJUST CONTENTS.

        app.clientside_callback(
            """
            function table_resize_event(table_pane_id, tables) {

                var callback = function()
                {
                    var paneHeight   = document.getElementById('table_pane').clientHeight;

                    var titleHeight  = document.getElementById('table_title').clientHeight;
                    var tabsHeight   = document.getElementById('table_tabs').clientHeight;
                    var cornerHeight = document.getElementById('table_corner').clientHeight;

                    tabsHeight = 18;

                    var dataHeight = paneHeight - titleHeight - tabsHeight - cornerHeight;

                    for (let i=0; i<tables.length; i++)
                    {
                        var tbl = document.getElementById('{"index":"' + tables[i][1] + '","type":"tbldata"}');
                        
                        tbl.clientHeight = dataHeight;
                        tbl.style.height = dataHeight + 'px';
                    }
                }

                new ResizeObserver(callback).observe(document.getElementById('table_pane'));

                pane_init();

                return "test worked";
            }
            """,

            Output("tblmsg",      "children"),
            Input ("table_pane",  "id"),
            State ("table_files", "data")
        )


        # ---------------------------------------------------
        # IMAGE_REDRAW CALLBACK

        @app.callback(
            Output('viewer',        'img'),
            Output('viewer',        'imgWidth'),
            Output('viewer',        'imgHeight'),
            Output('viewer',        'inset'),
            Output('viewer',        'insetWidth'),
            Output('viewer',        'insetHeight'),
            Output('viewer',        'cutoutDesc'),
            Output('viewer',        'zoombox'),
            Output('zoombox',       'data', allow_duplicate=True),
            Output('config',        'data', allow_duplicate=True),
            Output('cutout_dict',   'data'),
            Output('imgcmd',        'data'),
            Input('cutoutImg',      'n_clicks'),
            Input('imgcmd',         'data'),
            Input('restoreImg',     'n_clicks'),
            State('layout_store',   'data'),
            State('config',         'data'),
            State('zoombox',        'data'),
            State('box',            'data'),
            State('color_lookup',   'data'),
            State('cutout_dict',    'data'),
            State('overlays_table', 'virtualRowData'),
            prevent_initial_call=True)


        def image_redraw(ncutout, imgcmd, nreset, layout_dict, config, 
                         zoombox, box, color_lookup, cutout_dict, overlayRows):

            #  IMAGE_REDRAW:  This callback generates a new PNG (and inset overview PNG) and
            #  sends these to the viewer.  Several events can trigger this such as a
            #  request to cut a section out of the original image and work with it instead
            #  or changes to the JSON controling the image stretch and overlays.  Only the
            #  viewer properties and some related configuration parameters are output.

            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> image_redraw() Callback:')

            ctx = callback_context

            if debug == True:
                print('\nDEBUG> IM ctx.triggered_id:', ctx.triggered_id)
                print('DEBUG> IM ctx.triggered:   ', ctx.triggered, '\n')

            cmd = ctx.triggered_id

            if cmd == 'imgcmd':
                cmd = imgcmd

            if debug == True:
                print('DEBUG> cmd:         ', cmd)

            if debug == True:
                print('\nDEBUG> IM layout_dict:', layout_dict)

            if debug == True:
                print('\nDEBUG> IM zoombox (from props):', zoombox)

            if 'Grayscale' in layout_dict:
                grayscale = layout_dict['Grayscale']

            if 'Color' in layout_dict:
                color = layout_dict['Color']

            if overlayRows == None and 'Overlays' in layout_dict:
                overlayRows = layout_dict['Overlays']


            # If the trigger is the 'restoreImg' button (parameter nreset), we
            # override various things; pointing at the original image and
            # setting the zoom so as to fit it to the output display.  

            # And if the command is 'redraw' (parameter nredraw) it is even
            # more drastic.  Here we want to leave most things alone (the
            # 'final' FITS files and the state of things like 'zoombox' and
            # just create new PNGs based on the files left over from the
            # previous display with the only changes being whatever has changed
            # ins# the stretch and overlays.

            

            # Config info

            mode      = config[0]['mode']
            workdir   = config[0]['workdir']
            isCutout  = config[0]['isCutout']
            imgWidth  = config[0]['imgWidth']
            imgHeight = config[0]['imgHeight']

            dx_win    = zoombox['width']
            dy_win    = zoombox['height']

            tmpdir = workdir + '/tmp/'

            if cmd == 'restoreImg':
                isCutout = False

            if debug == True:
                print('DEBUG> IM mode:     ', mode)
                print('DEBUG> IM isCutout: ', isCutout)


            # List of overlays to hide

            hide_names = []

            if overlayRows != None:
                for ovly in overlayRows:

                    if 'Show' in ovly and ovly['Show'] == True:
                        continue

                    if 'File' in ovly:
                        basename = Path(ovly['File']).stem.upper()
                        hide_names.append(basename)


            # Decide what data to use

            current_files = {}

            blue_file  = ''
            green_file = ''
            red_file   = ''
            gray_file  = ''

            if mode == 'Color':

                for colr in color:
                    colr_value = colr['Color']

                    if colr_value == 'Blue':
                        blue_file = workdir + '/' + colr['File']

                    elif colr_value == 'Green':
                        green_file = workdir + '/' + colr['File']

                    elif colr_value == 'Red':
                        red_file = workdir + '/' + colr['File']
            else:

                gray_file = workdir + '/' + grayscale[0]['File']


            blue_tmp       = tmpdir + 'blue_tmp.fits'
            green_tmp      = tmpdir + 'green_tmp.fits'
            red_tmp        = tmpdir + 'red_tmp.fits'
            gray_tmp       = tmpdir + 'gray_tmp.fits'

            blue_cutout    = tmpdir + 'blue_cutout.fits'
            green_cutout   = tmpdir + 'green_cutout.fits'
            red_cutout     = tmpdir + 'red_cutout.fits'
            gray_cutout    = tmpdir + 'gray_cutout.fits'

            blue_shrunken  = tmpdir + 'blue_shrunken.fits'
            green_shrunken = tmpdir + 'green_shrunken.fits'
            red_shrunken   = tmpdir + 'red_shrunken.fits'
            gray_shrunken  = tmpdir + 'gray_shrunken.fits'


            # This is the first shortcut associated with cmd = 'redraw'. Here we want to
            # just point at the FITS files left over from the last interation.

            if cmd == 'redraw':

                if mode == 'Color':

                    if isCutout == True:

                        blue_file  = tmpdir + 'blue_shrunken.fits'
                        green_file = tmpdir + 'green_shrunken.fits'
                        red_file   = tmpdir + 'red_shrunken.fits'

                    else:
                        blue_shrunken  = blue_file
                        green_shrunken = green_file
                        red_shrunken   = red_file

                else:

                    if isCutout == True:
                        gray_file = tmpdir + 'gray_shrunken.fits'

                    else:
                        gray_shrunken = gray_file


            # If not 'redraw', we need to potentially cut out and shrink the 'previous'
            # FITS files.

            else:
                if cmd == 'cutoutImg':

                    if mode == 'Color':

                        if isCutout == True:

                            blue_file  = tmpdir + 'blue_shrunken.fits'
                            green_file = tmpdir + 'green_shrunken.fits'
                            red_file   = tmpdir + 'red_shrunken.fits'

                            if debug == True:
                                print('DEBUG> IM copy(', blue_file,  blue_tmp, ')')
                                print('DEBUG> IM copy(', green_file, green_tmp, ')')
                                print('DEBUG> IM copy(', red_file,   red_tmp, ')\n')

                            shutil.copy(blue_file,  blue_tmp)
                            shutil.copy(green_file, green_tmp)
                            shutil.copy(red_file,   red_tmp)
                        
                        else:
                            blue_tmp  = blue_file
                            green_tmp = green_file
                            red_tmp   = red_file

                    else:

                        if isCutout == True:
                            gray_file = tmpdir + 'gray_shrunken.fits'

                            if debug == True:
                                print('DEBUG> IM copy(', gray_file,  gray_tmp, ')')

                            shutil.copy(gray_file,  gray_tmp)

                        else:
                            gray_tmp = gray_file


                    # Find the original image window box outline

                    zoom = zoombox['zoom']

                    xmin = 0
                    ymin = 0
                    dx   = 0
                    dy   = 0

                    '''
                    # This block allows us to use a drawn box to set the
                    # subimage.  We are going to turn that off and perhaps 
                    # later turn it back on using a more specific control.

                    try:
                        xmin = box['xmin']
                        ymin = box['ymin']
                        dx   = box['dx']
                        dy   = box['dy']
                    except:
                        pass
                    '''

                    if dx == 0 or dy == 0:
                        xmin = zoombox['xmin']
                        ymin = zoombox['ymin']
                        dx   = zoombox['dx']
                        dy   = zoombox['dy']

                    if mode == 'Color':
                        if debug == True:
                            print('DEBUG> IM mSubimage:', blue_tmp,  blue_cutout,  xmin, ymin, dx, dy)

                        rtn = mSubimage(blue_tmp,  blue_cutout,  xmin, ymin, dx, dy, mode=1)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')

                        if debug == True:
                            print('DEBUG> IM mSubimage:', green_tmp,  green_cutout,  xmin, ymin, dx, dy)

                        rtn = mSubimage(green_tmp, green_cutout, xmin, ymin, dx, dy, mode=1)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')

                        if debug == True:
                            print('DEBUG> IM mSubimage:', red_tmp,  red_cutout,  xmin, ymin, dx, dy)

                        rtn = mSubimage(red_tmp,   red_cutout,   xmin, ymin, dx, dy, mode=1)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')

                    else:
                        if debug == True:
                            print('DEBUG> IM mSubimage:', gray_tmp,  gray_cutout,  xmin, ymin, dx, dy)

                        rtn = mSubimage(gray_tmp,  gray_cutout,  xmin, ymin, dx, dy, mode=1)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')


                    # Determine the scaling to fit this in the current display window

                    zoom_x = (dx + 5) / dx_win
                    zoom_y = (dy + 5) / dy_win

                    zoom = zoom_x
                    if zoom_y < zoom:
                        zoom = zoom_y


                    # Rescale FITS images

                    if mode == 'Color':

                        if debug == True:
                            print('DEBUG> IM mShrink:', blue_cutout,  blue_shrunken,  zoom)

                        rtn = mShrink(blue_cutout,  blue_shrunken,  zoom)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')

                        if debug == True:
                            print('DEBUG> IM mShrink:', green_cutout,  green_shrunken,  zoom)

                        rtn = mShrink(green_cutout, green_shrunken, zoom)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')

                        if debug == True:
                            print('DEBUG> IM mShrink:', red_cutout,  red_shrunken,  zoom)

                        rtn = mShrink(red_cutout,   red_shrunken,   zoom)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn, '\n')

                    else:
                        if debug == True:
                            print('DEBUG> IM mShrink:', gray_cutout,  gray_shrunken,  zoom)
                            
                        rtn = mShrink(gray_cutout,  gray_shrunken,  zoom)

                        if debug == True:
                            print('DEBUG> IM rtn:', rtn)

                    isCutout = True
                    config[0]['isCutout'] = isCutout

                    if debug == True:
                        print('DEBUG> IM isCutout -> True')


                    # Update the 'cutout' dict (including the cutout label string).

                    cutout_dict = current_cutout(cutout_dict, zoom, xmin, ymin, isCutout)


                # 'restoreImg' means going back to the original data

                else:
                    if mode == 'Color':

                        blue_shrunken  = blue_file
                        green_shrunken = green_file
                        red_shrunken   = red_file

                    else:

                        gray_shrunken = gray_file

                    isCutout = False
                    config[0]['isCutout'] = isCutout

                    if debug == True:
                        print('DEBUG> IM isCutout -> False')



            # Now, whether we are just redrawing or have created new FITS, we need to
            # generate the PNGs.  This means creating a dict based on the images we
            # have at this point plus the stretch and overlay information.

            current_files['Blue' ] = blue_shrunken
            current_files['Green'] = green_shrunken
            current_files['Red'  ] = red_shrunken
            current_files['Gray' ] = gray_shrunken

            imgdict = {"image_type":"png"}
            
            if 'Brightness' in layout_dict:
                imgdict['brightness'] = layout_dict['Brightness']

            if 'Contrast' in layout_dict:
                imgdict['contrast'] = layout_dict['Contrast']

            if mode == 'Color':

                for colr in color:

                    colr_value = colr['Color']

                    if colr['Min'] == 'min':
                        colr['Min Units'] = 'value'

                    if colr['Max'] == 'max':
                        colr['Max Units'] = 'value'

                    colr_data = {
                        "fits_file":    current_files[colr_value],
                        "stretch_min":  colr['Min'] + units[colr['Min Units']],
                        "stretch_max":  colr['Max'] + units[colr['Max Units']],
                        "stretch_mode": stretch[colr['Stretch Mode']]
                    }

                    if colr_value == 'Blue':
                        colr_data['fits_file'] = blue_shrunken
                        imgdict['blue_file']  = colr_data

                    if colr_value == 'Green':
                        colr_data['fits_file'] = green_shrunken
                        imgdict['green_file'] = colr_data

                    if colr_value == 'Red':
                        colr_data['fits_file'] = red_shrunken
                        imgdict['red_file']   = colr_data

            else:

                if grayscale[0]['Min'] == 'min':
                    grayscale[0]['Min Units'] = 'value'

                if grayscale[0]['Max'] == 'max':
                    grayscale[0]['Max Units'] = 'value'

                gray_file = {
                    "fits_file":    current_files['Gray'],
                    "stretch_min":  grayscale[0]['Min'] + units[grayscale[0]['Min Units']],
                    "stretch_max":  grayscale[0]['Max'] + units[grayscale[0]['Max Units']],
                    "stretch_mode": stretch[grayscale[0]['Stretch Mode']]
                }

                imgdict['gray_file']  = gray_file


            new_overlays = []


            if overlayRows != None and len(overlayRows) > 0:

                for ovly in overlayRows:

                    new_overlay = None

                    if ovly['Show'] == False:
                        continue

                    if ovly['Type'] == 'Catalog':

                        basename = Path(ovly['File']).stem.upper()

                        new_overlay = {
                                           'type':        'catalog',
                                           'data_file':   workdir + '/' + ovly['File'],
                                           'symbol':      ovly['Symbol'],
                                           'sym_size':    ovly['Size of Ref Value'],
                                           'coord_sys':   'Equ J2000',
                                           'color':       ovly['Color']
                                      }

                        if 'Column' in ovly:
                            new_overlay['data_column'] = ovly['Column']

                        if 'Ref Value' in ovly:
                            new_overlay['data_ref']    = ovly['Ref Value']

                        if 'Scaling' in ovly:
                            new_overlay['data_type']   = ovly['Scaling']


                    elif ovly['Type'] == 'Images':

                        basename = Path(ovly['File']).stem.upper()

                        new_overlay = {
                                           'type':        'imginfo',
                                           'data_file':   workdir + '/' + ovly['File'],
                                           'coord_sys':   'Equ J2000',
                                           'color':       ovly['Color']
                                      }


                    elif ovly['Type'] == 'Eq grid':

                        new_overlay = {
                                           'type':        'grid',
                                           'coord_sys':   'Equ J2000',
                                           'color':       ovly['Color']
                                      }


                    elif ovly['Type'] == 'Ec grid':

                        new_overlay = {
                                           'type':        'grid',
                                           'coord_sys':   'Ecl J2000',
                                           'color':       ovly['Color']
                                      }


                    elif ovly['Type'] == 'Ga grid':

                        new_overlay = {
                                           'type':        'grid',
                                           'coord_sys':   'ga',
                                           'color':       ovly['Color']
                                      }

                    if new_overlay != None:
                        new_overlays.append(new_overlay)
                

            # Special cases: table subset locations

            for tbl_file in table_files:

                basename = tbl_file[1]

                if basename in hide_names:
                    continue

                subsettbl = tmpdir + basename

                if os.path.exists(subsettbl):

                    new_overlay = {
                                       'type':        'catalog',
                                       'data_file':   subsettbl,
                                       'symbol':      'plus',
                                       'sym_size':    '10.0',
                                       'coord_sys':   'Equ J2000',
                                       'color':       color_lookup[basename]
                                  }

                    new_overlays.append(new_overlay)

            if len(new_overlays) > 0:
                imgdict['overlays']  = new_overlays


            # Convert the the dict to JSON as this is what mViewer will use to make the
            # PNG.

            imgjson = json.dumps(imgdict)

            if debug == True:
                print('\nDEBUG> IM imgjson:', imgjson, '\n')

                print('DEBUG> IM current_files:', current_files)

            cutout_image = tmpdir + 'cutout.png'

            if debug == True:
                print('\nDEBUG> IM mViewer (imgjson):', cutout_image)

            rtn = mViewer(imgjson, cutout_image, mode=1)

            if debug == True:
                print('\nDEBUG> IM mViewer rtn:', rtn)

            
            # For most of the use cases, we will have a new zoombox based on the 
            # processing done here.  However, for 'redraw' we want to leave the 
            # zoombox as it was; we are just updating the display Div with new
            # PNGs.

            if cmd != 'redraw':

                out_zoombox = {}

                out_zoombox['zoom'  ] = 1.
                out_zoombox['width' ] = rtn['nx']
                out_zoombox['height'] = rtn['ny']
                out_zoombox['xmin'  ] = 0.
                out_zoombox['ymin'  ] = 0.
                out_zoombox['dx'    ] = rtn['nx']
                out_zoombox['dy'    ] = rtn['ny']

                if debug == True:
                    print('\nDEBUG> IM cutout return zoombox:', out_zoombox)


            # Now make the thumbnail for this image

            cutout_size = Image.open(cutout_image).size

            config[0]['imgWidth']  = cutout_size[0]
            config[0]['imgHeight'] = cutout_size[1]

            xsize = cutout_size[0]
            ysize = cutout_size[1]

            if xsize > ysize:
                ysize = 100. * ysize / xsize
                xsize = 100.

            else:
                xsize = 100. * xsize / ysize
                ysize = 100.

            thumbnail_image = tmpdir + 'cutout_thumbnail.png'

            size = xsize, ysize

            im = Image.open(cutout_image)
            im.thumbnail(size, Image.Resampling.LANCZOS)
            im.save(thumbnail_image, 'PNG')

            presentDate = datetime.datetime.now()
            unix_timestamp = str(datetime.datetime.timestamp(presentDate)*1000)

            
            #  Make base64 versions of the images

            cutout_file = workdir + '/tmp/cutout.png'

            with open(cutout_file, 'rb') as image:
                encoded = base64.b64encode(image.read()).decode()
                cutout_data = f'data:image/png;base64, {encoded}'

            thumbnail_file = workdir + '/tmp/cutout_thumbnail.png'

            with open(thumbnail_file, 'rb') as image:
                encoded = base64.b64encode(image.read()).decode()
                thumbnail_data = f'data:image/png;base64, {encoded}'
            
            if debug == True:
                print('\nDEBUG> IM cutout_file:  ', cutout_file)
                print(  'DEBUG> IM cutout_size:  ', cutout_size, '\n')


            # The purpose of this callback is to configure the state of the
            # image display (i.e., what is shown in the mviewer React
            # component.  In the case of the 'redraw' command, we will have
            # regenerated the image and thumbnail PNGs, though their sizes and
            # the zoombox, cutout information, etc. will not have changes (and
            # so doesn't need to be updated.

            # The nominal return set is composed of
            # 
            #     cutout_url,            viewer.img  
            #     cutout_size[0],        viewer.imgWidth  
            #     cutout_size[1],        viewer.imgHeight  
            #     thumbnail_url,         viewer.inset  
            #     xsize,                 viewer.insetWidth  
            #     ysize,                 viewer.insetHeight  
            #     cutout_dict['label'],  viewer.cutoutDesc 
            #     out_zoombox,           viewer.zoombox  
            #     out_zoombox,           zoombox.data  
            #     config,                config.data  
            #     cutout_dict,           cutout_dict.data  
            #     ''                     imdcmd.data

            # The last parameter (the value of the imgcmd Store) is set in a
            # different callback and after being used in this callback is 
            # reset here (to '').

            cutoutDesc = cutout_dict['label']

            if cmd == 'redraw':

                return cutout_data,            \
                       no_update,             \
                       no_update,             \
                       thumbnail_data,         \
                       no_update,             \
                       no_update,             \
                       no_update,             \
                       no_update,             \
                       no_update,             \
                       no_update,             \
                       no_update,             \
                       ''                     
            else:

                return cutout_data,            \
                       cutout_size[0],        \
                       cutout_size[1],        \
                       thumbnail_data,         \
                       xsize,                 \
                       ysize,                 \
                       cutoutDesc,            \
                       out_zoombox,           \
                       out_zoombox,           \
                       config,                \
                       cutout_dict,           \
                       ''                     


        #  Keep track of cutout progression (and generate 'cutout' string).

        def current_cutout(cutout_dict, shrinki, xmini, ymini, isCutout):

            level = cutout_dict['level']

            img_width  = cutout_dict['img_width']
            img_height = cutout_dict['img_height']

            factori = 1./shrinki


            if level == 1:

                factor = factori

                xmin = xmini
                ymin = ymini

                xmin =         0. / factor + xmin
                xmax =  img_width / factor + xmin

                ymin =        0.  / factor + ymin
                ymax = img_height / factor + ymin

                dx = xmax - xmin
                dy = ymax - ymin


            else:

                factor = factori*cutout_dict['factor']

                xmin = cutout_dict['xmin'] + xmini/factor
                ymin = cutout_dict['ymin'] + ymini/factor

                dx = img_width/factor
                dy = img_height/factor

                xmax = xmin + dx
                ymax = ymin + dy


            if isCutout == False:
                cutoutDesc = ''
            else:
                cutoutDesc = f'Cutout: {dx:6.1f} x{dy:6.1f} @ ({xmin:6.1f},{ymin:6.1f})'


            #  cutoutDesc = f'Cutout: {dx:6.1f} x{dy:6.1f} @ ({xmin:6.1f},{ymin:6.1f})  max: {xmax:6.1f} {ymax:6.1f}'


            level = level + 1

            cutout_dict['level']  = level
            cutout_dict['factor'] = factor
            cutout_dict['xmin']   = xmin
            cutout_dict['xmax']   = xmax
            cutout_dict['ymin']   = ymin
            cutout_dict['xmax']   = xmax
            cutout_dict['label']  = cutoutDesc

            return cutout_dict

        # ---------------------------------------------------
        # PICK SET IN MVIEWER REACT COMPONENT

        @app.callback(
            Output('pick',        'data'),
            Output('imgcmd',      'data',          allow_duplicate=True),

            Output({'type': 'tbldata', 'index': ALL}, 'selectedRows',  allow_duplicate=True),
            Output({'type': 'tbldata', 'index': ALL}, 'rowData',       allow_duplicate=True),

            Input('viewer',       'pick'),
            State('config',       'data'),
            State('layout_store', 'data'),
            State('table_files',  'data'),

            State({'type': 'tbldata', 'index': ALL}, 'rowData'),

            prevent_initial_call=True)


        def image_pick_selection(pick, config, layout_dict, table_files, inRowData):
            
            #  IMAGE_PICK_SELECTION:  The only input to this callback is a location "pick"
            #  on the image display.  This function takes this pixel coordinate and
            #  converts it to RA,Dec.  It then searches the table data to determine which
            #  records are near the location (i.e. within five pixels distance).  This data
            #  is written to a selection table file and used by Montage to generate an
            #  updated PNG (again, through the outputting of command to the imgcmd Store).
            #  A list of the record IDs is also generated and sent to the table display
            #  tool to be highlight (which in turn gets sent to the scatter plot tool).


            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> image_pick_selection() Callback:')

            if 'Grayscale' in layout_dict:
                grayscale = layout_dict['Grayscale']

            if 'Color' in layout_dict:
                color = layout_dict['Color']

            x = pick['x']
            y = pick['y']


            # Config info

            mode      = config[0]['mode']
            workdir   = config[0]['workdir']
            isCutout  = config[0]['isCutout']

            blue_file  = ''
            green_file = ''
            red_file   = ''
            gray_file  = ''

            if mode == 'Color':

                for colr in color:
                    colr_value = colr['Color']

                    if colr_value == 'Blue':
                        blue_file = workdir + '/' + colr['File']

                    elif colr_value == 'Green':
                        green_file = workdir + '/' + colr['File']

                    elif colr_value == 'Red':
                        red_file = workdir + '/' + colr['File']
            else:

                gray_file = workdir + '/' + grayscale[0]['File']


            if isCutout == True:
                gray_file  = tmpdir + 'gray_shrunken.fits'
                blue_file  = tmpdir + 'blue_shrunken.fits'
                green_file = tmpdir + 'green_shrunken.fits'
                red_file   = tmpdir + 'red_shrunken.fits'


            # First, use mExamine to get the region statistics

            jstr = ''

            if mode == 'Grayscale':

                rtn_gray = mExamine(infile=gray_file,
                                    areaMode=1,
                                    ra=x,
                                    dec=y,
                                    radius=9,
                                    locinpix=True,
                                    radinpix=True)

                pixsize = abs(rtn_gray['cdelt1'])

                gray_max = rtn_gray['fluxmax']

                gray_max = round_to_sig_figs(gray_max,  3)

                try:
                    jstr = jstr + 'Gray:  ' + gray_max + ' at (' + \
                           str(rtn_gray['lonc']) + ', ' + str(rtn_gray['latc']) + ')'
                except:
                    pass

                rtn_gray = mCoord(imgfile=gray_file,
                                  ra=x, dec=y, locinpix=True)

                lonc = rtn_gray['ra']
                latc = rtn_gray['dec']

                try:
                    jstr = jstr + '\n\n\n\n\nFull Region Info\n\n'
                except:
                    pass

                fixed_rtn = {}
                for key, value in rtn_gray.items():
                    if isinstance(value, bytes):
                        fixed_rtn[key] = value.decode("utf-8")
                    else:
                        fixed_rtn[key] = value

                try:
                    jstr = jstr + 'Gray:\n' + json.dumps(fixed_rtn, indent=1)
                except:
                    pass


            else:

                rtn_blue = mExamine(infile=blue_file,
                                    areaMode=1,
                                    ra=x,
                                    dec=y,
                                    radius=9,
                                    locinpix=True,
                                    radinpix=True)

                blue_max = rtn_blue['fluxmax']

                pixsize = abs(rtn_blue['cdelt1'])

                blue_max = str(round_to_sig_figs(blue_max,  3))

                try:
                    jstr = jstr + 'Blue:  ' + blue_max + ' at (' + \
                           str(rtn_blue['lonc']) + ', ' + str(rtn_blue['latc']) + ')\n'
                except:
                    pass

                rtn_blue = mCoord(imgfile=blue_file,
                                  ra=x, dec=y, locinpix=True)

                lonc = rtn_blue['ra']
                latc = rtn_blue['dec']

            
                rtn_green = mExamine(infile=green_file,
                                     areaMode=1,
                                     ra=x,
                                     dec=y,
                                     radius=9,
                                     locinpix=True,
                                     radinpix=True)

                green_max = rtn_green['fluxmax']
            
                green_max = str(round_to_sig_figs(green_max,  3))

                try:
                    jstr = jstr + 'Green: ' + green_max + ' at (' + \
                           str(rtn_green['lonc']) + ', ' + str(rtn_green['latc']) + ')\n'
                except:
                    pass

            
                rtn_red = mExamine(infile=red_file,
                                   areaMode=1,
                                   ra=x,
                                   dec=y,
                                   radius=9,
                                   locinpix=True,
                                   radinpix=True)

                red_max = rtn_red['fluxmax']

                red_max = str(round_to_sig_figs(red_max,  3))

                try:
                    jstr = jstr + 'Red:   ' + red_max + ' at (' + \
                           str(rtn_red['lonc']) + ', ' + str(rtn_red['latc']) + ')\n'
            
                    jstr = jstr + '\n\n\n\n\nFull Region Info\n\n'
                except:
                    pass

                fixed_rtn = {}
                for key, value in rtn_blue.items():
                    if isinstance(value, bytes):
                        fixed_rtn[key] = value.decode("utf-8")
                    else:
                        fixed_rtn[key] = value

                try:
                    jstr = jstr + 'Blue:\n' + json.dumps(fixed_rtn, indent=1)
                except:
                    pass

                fixed_rtn = {}
                for key, value in rtn_green.items():
                    if isinstance(value, bytes):
                        fixed_rtn[key] = value.decode("utf-8")
                    else:
                        fixed_rtn[key] = value

                try:
                    jstr = jstr + '\n\nGreen:\n' + json.dumps(fixed_rtn, indent=1)
                except:
                    pass

                fixed_rtn = {}
                for key, value in rtn_red.items():
                    if isinstance(value, bytes):
                        fixed_rtn[key] = value.decode("utf-8")
                    else:
                        fixed_rtn[key] = value

                try:
                    jstr = jstr + '\n\nRed:\n' + json.dumps(fixed_rtn, indent=1)
                except:
                    pass


            # Finally created the subset tables for the 'pick' region

            print('\nPick coordinates (', lonc, latc, ')\n')

            x0 = math.cos(math.radians(lonc)) * math.cos(math.radians(latc))
            y0 = math.sin(math.radians(lonc)) * math.cos(math.radians(latc))
            z0 = math.sin(math.radians(latc))


            # The first iteration of this code made lists of the IDs in the
            # pick region and sent those as records to highlight. 

            itable     = 0
            idlists    = []

            ntot = 0

            for tbl_file in table_files:

                basename = tbl_file[1]

                outfile  = tmpdir + basename

                tbl_data = ascii.read(tbl_file[0])

                try:
                    os.unlink(outfile)
                except:
                    pass

                tbl_df = tbl_data.to_pandas()

                fpin  = open(tbl_file[0], "r")
                fpout = open(outfile,     "w+")
             
                in_header = False


                # Before header

                while True:
                    line = fpin.readline()

                    if line[0] == '|':
                        fpout.write(line)
                        in_header = True
                        break

                    fpout.write(line)


                # Rest of the header

                while True:
                    line = fpin.readline()

                    if line[0] == '|':
                        fpout.write(line)
                    else:
                        break


                # Check lines for distance

                nsrc = 0

                first = True

                ids = []

                scroll_to = {}

                updates = {}

                for index, rec in tbl_df.iterrows():

                    if 'ra' in rec:
                        ra  = rec['ra']
                        dec = rec['dec']

                    elif 'ra2000' in rec:
                        ra  = rec['ra2000']
                        dec = rec['dec2000']

                    if ra == None or dec == None:
                        continue
                    
                    x = math.cos(math.radians(ra)) * math.cos(math.radians(dec))
                    y = math.sin(math.radians(ra)) * math.cos(math.radians(dec))
                    z = math.sin(math.radians(dec))

                    dot = x*x0 + y*y0 + z*z0

                    dist = math.degrees(math.acos(dot))

                    if dist < 10.*pixsize/zoom:

                        print('Match: (', ra, ', ', dec, ')')

                        fpout.write(line)
                        nsrc = nsrc + 1

                        ids.append(str(index))

                        if first == True:
                            scroll_to['rowIndex'] = str(index)
                            first = False

                    line = fpin.readline()

                fpin.close()
                fpout.close()

                if len(ids) == 0:
                    idlist = no_update
                    os.unlink(outfile)
                else:
                    idlist = {'ids': ids}

                if debug == True:
                    print('DEBUG> PI Redraw ' + tbl_file[0] + ' with ', nsrc, ' selected sources.')

                if nsrc > 0:
                    print('Found ' + str(nsrc) + ' sources in ' + tbl_file[0] + '\n')

                idlists.append(idlist)

                ntot = ntot + nsrc

            if ntot > 0:
                print(ntot, 'matches total.\n')


            # This version of the code uses the set of rowData records
            # as the basis for updated tables, where a 'Dist' column has
            # been added (same calculation as above).

            outRowData = []

            for catalog in inRowData:

                outData = catalog


                # Calculate distance for each record in catalog

                nsrc = 0

                first = True

                for rec in outData:

                    if 'ra' in rec:
                        ra  = rec['ra']
                        dec = rec['dec']

                    elif 'ra2000' in rec:
                        ra  = rec['ra2000']
                        dec = rec['dec2000']

                    if ra == None or dec == None:
                        continue
                    
                    x = math.cos(math.radians(ra)) * math.cos(math.radians(dec))
                    y = math.sin(math.radians(ra)) * math.cos(math.radians(dec))
                    z = math.sin(math.radians(dec))

                    dot = x*x0 + y*y0 + z*z0

                    dist = math.degrees(math.acos(dot))

                    rec['Dist'] = dist


                outRowData.append(outData)

            return jstr, 'redraw', idlists, outRowData



        def round_to_sig_figs(num, sig_figs):
            if num == 0:
                return 0
            return str(float(f"{num:.{sig_figs}g}"))



        # ---------------------------------------------------
        # TABLE SELECTION CALLBACK

        @app.callback(
            Output('imgcmd',     'data',  allow_duplicate=True),
            Output('table_pane', 'style', allow_duplicate=True),
            Output('config',     'data', allow_duplicate=True),

            Input({'type': 'tbldata', 'index': ALL}, 'selectedRows'),
            Input({'type': 'tbldata', 'index': ALL}, 'virtualRowData'),
            Input({'type': 'tbldata', 'index': ALL}, 'rowData'),

            State('config',     'data'),
            State('table_pane', 'style'),

            prevent_initial_call=True)

        def table_selection(selectedRows, virtualRowData, rowData, config, table_style):

            #  TABLE_SELECTION:  The AG Grid table tool provides a couple of ways to
            #  "select" a subset of records (which it then highlights).  This callback
            #  reacts to that, generating an new figure to be sent to the scatterplot tool
            #  (original data plus an overlay of the selected records) and a table files
            #  of the selected records suitable for display by the image tools (by way of
            #  Montage mViewer).  Besides the figure going to scatter plot it also
            #  triggers regeneration of the PNG through an intermediate "imgcmd" Store. 

            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> table_selection() Callback:')
                print('DEBUG> selectedRows:',   selectedRows);
                print('DEBUG> config:      ',   config);
                print('DEBUG> table_style: ',   table_style);

            ctx = callback_context

            if debug == True:
                print('\nDEBUG> TS ctx.triggered_id:', ctx.triggered_id)

            selected_tbl = ctx.triggered_id['index'].upper()

            if debug == True:
                print('\nDEBUG> TS selected_tbl:', selected_tbl)


            # The first time bump the table size.
            # We save 'first' in the config Store, initialize it
            # to True and here reset it to False.

            first = config[0]['first']

            if first == True:

                orig_width = table_style['width']

                suffix = 'px'

                if orig_width.endswith(suffix):
                    width = orig_width[:-len(suffix)]

                width = str(int(width) + 1) + suffix

                table_style['width'] = width

                config[0]['first'] = False


            # See if there are any selected records in the first 

            length = len(ctx.triggered[0]['value'])

            if length == 0:
                if debug == True:
                    print('DEBUG> TS No data, so abort.\n')

                return no_update, table_style, config


            subsetfile = tmpdir + selected_tbl

            try:
                os.remove(subsetfile)
            except:
                pass

            if debug == True:
                print('\nDEBUG> TS subsetfile:', subsetfile)

            fp = open(subsetfile, "w+")

            fp.write('|     ra      |     dec     |\n')

            for rows in selectedRows:

                subset_df = pd.DataFrame(rows)

                for index, rec in subset_df.iterrows():

                    if 'ra' in rec:
                        ra  = rec['ra']
                        dec = rec['dec']
                    elif 'ra2000' in rec:
                        ra  = rec['ra2000']
                        dec = rec['dec2000']
                    else:
                        ra  = 0.
                        dec = 0.

                    fp.write(" {0:11.6f}  {1:12.6f} \n".format(ra, dec))

            fp.close()

            if debug == True:
                print('\nDEBUG> TS return imgcmd \'redraw\'')

            return 'redraw', table_style, config



        # ---------------------------------------------------
        # CLEAR SELECTION

        @app.callback(
            Output('imgcmd',     'data',         allow_duplicate=True),

            Output({'type': 'tbldata', 'index': ALL}, 'selectedRows',  allow_duplicate=True),

            Input('clearSelect', 'n_clicks'),
            State('table_files', 'data'),
            prevent_initial_call=True)


        def clear_selections(selection, table_files):

            #  CLEAR_SELECTION:  To clear the selections in all three displays, we simply
            #  remove the table files Montage uses to mark the records in the PNG and call
            #  for a "redraw"; then send the table viewer an empty "selectedRow" ID list.


            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> clear_selections() Callback:')

            idlists = []

            idlist = {'ids': []}

            for tbl_file in table_files:

                basename = tbl_file[1]

                subsetfile = tmpdir + basename

                try: 
                    os.remove(subsetfile)
                except:
                    pass 

                idlists.append(idlist)

            cmd = 'redraw'

            return cmd, idlists



        #  There are four modal pop-ups used by this application.  Each of these allow the
        #  user to modify some aspect of the image display:
        #  
        #    The overlay modal is used to control what display overlays to include in the
        #    image (astronomical catalog data, image metadata and coordinate grids.
        #  
        #    The "grayscale" modal controls what image is displayed, how it is stretched and
        #    what color table to use.
        #  
        #    The "color" modal is used for the same sort of thing but when the display is a
        #    three-color composite.
        #  
        #    Finally, the "pick" modal (currently hidden) is used to display region
        #    pixel statistics for points "picked" on the display.


        # ---------------------------------------------------
        # CALLBACKS FOR OVERLAY MODAL

        @app.callback(
            Output('overlays_table', 'rowTransaction', allow_duplicate=True),
            Input('ovly_addCatalog', 'n_clicks'),
            Input('ovly_addImage',   'n_clicks'),
            Input('ovly_addEqu',     'n_clicks'),
            Input('ovly_addGal',     'n_clicks'),
            Input('ovly_addEcl',     'n_clicks'),
            prevent_initial_call=True)

        def overlay_update(n_catalog, n_image, n_equ, n_gal, n_ecl):
            
            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> overlay_update() Callback:')

            ctx = callback_context

            if debug == True:
                print('\nDEBUG> OU ctx.triggered_id:', ctx.triggered_id)
                print('DEBUG> OU ctx.triggered:   ', ctx.triggered, '\n')

            try:
                if ctx.triggered_id == 'ovly_addCatalog':

                    row = {
                              'addIndex': 0,

                              'add':
                                  [{'Show':              True,
                                    'Type':              'Catalog',
                                    'Color':             'ffff00',
                                    'File':              '',
                                    'Column':            '',
                                    'Ref Value':          1,
                                    'Size of Ref Value':  1,
                                    'Scaling':           'mag',
                                    'Symbol':            'circle',
                                    'Scale of Ref Val':   1}]
                          }


                if ctx.triggered_id == 'ovly_addImage':

                    row = {
                              'addIndex': 0,

                              'add':
                                  [{'Show':              True,
                                    'Type':              'Image',
                                    'Color':             'ffff00',
                                    'File':              '',
                                    'Column':            '',
                                    'Ref Value':         float('NaN'),
                                    'Size of Ref Value': float('NaN'),
                                    'Scaling':           '',
                                    'Symbol':            '',
                                    'Scale of Ref Val':  ''}]
                          }


                if ctx.triggered_id == 'ovly_addEqu':

                    row = {
                              'addIndex': 0,

                              'add':
                                  [{'Show':              True,
                                    'Type':              'Eq grid',
                                    'Color':             'ffff00',
                                    'File':              '',
                                    'Column':            '',
                                    'Ref Value':         float('NaN'),
                                    'Size of Ref Value': float('NaN'),
                                    'Scaling':           '',
                                    'Symbol':            '',
                                    'Scale of Ref Val':  ''}]
                          }


                if ctx.triggered_id == 'ovly_addGal':

                    row = {
                              'addIndex': 0,

                              'add':
                                  [{'Show':              True,
                                    'Type':              'Ga grid',
                                    'Color':             'ffff00',
                                    'File':              '',
                                    'Column':            '',
                                    'Ref Value':         float('NaN'),
                                    'Size of Ref Value': float('NaN'),
                                    'Scaling':           '',
                                    'Symbol':            '',
                                    'Scale of Ref Val':  ''}]
                          }


                if ctx.triggered_id == 'ovly_addEcl':

                    row = {
                              'addIndex': 0,

                              'add':
                                  [{'Show':              True,
                                    'Type':              'Ec grid',
                                    'Color':             'ffff00',
                                    'File':              '',
                                    'Column':            '',
                                    'Ref Value':         float('NaN'),
                                    'Size of Ref Value': float('NaN'),
                                    'Scaling':           '',
                                    'Symbol':            '',
                                    'Scale of Ref Val':  ''}]
                          }


                return row

            except Exception as e:
                print(f'Error adding row.')
                return no_update


        # ---------------------------------------------------
        # BRING UP OVERLAY MODAL

        @app.callback(
            Output('ovly_modal',       'is_open'),
            Output('imgcmd',           'data', allow_duplicate=True),
            Input('showOverlays',      'n_clicks'),
            Input('ovly_closeBtn',     'n_clicks'),
            State('ovly_modal',        'is_open'),
            prevent_initial_call=True)

        def overlay_toggle_modal(n1, n2, is_open):
            
            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> overlay_toggle_modal() Callback:')

            ctx = callback_context

            if debug == True:
                print('\nDEBUG> OT ctx.triggered_id:', ctx.triggered_id)
                print('DEBUG> OT ctx.triggered:   ', ctx.triggered, '\n')

            if n1 or n2:
                return not is_open, 'redraw'
            return is_open, no_update



        # ---------------------------------------------------
        # CALLBACKS FOR IMAGE STRETCH MODALS

        @app.callback(
            Output('layout_store',    'data',         allow_duplicate=True),
            Output('gray_modal',      'is_open'),     # Set the gray modal visibility
            Output('color_modal',     'is_open'),     # Set the color mocal visibility
            Output('imgcmd',          'data',         allow_duplicate=True),

            Input('showImageStretch', 'n_clicks'),    # Image stretch button was pressed 
            Input('gray_closeBtn',    'n_clicks'),    # Grayscale close button was pressed
            Input('color_closeBtn',    'n_clicks'),   # Color close button was pressed
            State('gray_modal',       'is_open'),     # Current open state of gray modal
            State('color_modal',      'is_open'),     # Current open state of color modal
            State('gray_imginfo',     'rowData'),
            State('color_imginfo',    'rowData'),
            State('layout_store',     'data'),
            State('config',           'data'),
            prevent_initial_call=True)

        def image_toggle_modal(show_stretch,
                               gray_close, color_close,
                               gray_is_open, color_is_open, 
                               gray_updates, color_updates,
                               layout, config):
            
            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> image_toggle_modal() Callback:')

            ctx = callback_context

            mode = config[0]['mode']

            if debug == True:
                print('\nDEBUG> GT ctx.triggered_id:', ctx.triggered_id)
                print('DEBUG> GT ctx.triggered:   ', ctx.triggered, '\n')

            new_layout = layout

            if mode == 'Color':

                new_layout['Color'] = color_updates

                if show_stretch or color_close:
                    return new_layout, no_update, not color_is_open, 'redraw'
                
                return new_layout, no_update, color_is_open, no_update

            else:

                new_layout['Grayscale'] = gray_updates

                if show_stretch or gray_close:
                    return new_layout, not gray_is_open, no_update, 'redraw'
                
                return new_layout, gray_is_open, no_update, no_update


        # ---------------------------------------------------
        # CALLBACKS FOR PICK MODAL

        @app.callback(
            Output('pick_modal',   'is_open'),
            Output('pickinfo',     'children'),
            Input('pick_closeBtn', 'n_clicks'),
            Input('pick',          'data'),
            prevent_initial_call=True)

        def pick_toggle_modal(cancel, pickdata):

            #  PICK_MODAL_UPDATE:  The "image_pick_selection()" callback also generates
            #  image area statistics for near the picked location.  That data is stored in
            #  a "pick" Store and changes to that store are detected here and a modal
            #  window is normally popped up.  This routine both handles that display and
            #  can hide it based on a cancel button on the modal.  However, at the moment
            #  the modal kept hidden (we may want to change how it is made visible).

            
            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> pick_toggle_modal() Callback:')

            ctx = callback_context

            if debug == True:
                print('\nDEBUG> PT ctx.triggered_id:', ctx.triggered_id)
                print('DEBUG> PT ctx.triggered:   ', ctx.triggered, '\n')

            trigger = ctx.triggered_id

            if trigger == 'pick':
                # return True, pickdata
                return False, pickdata   # XXXXXXX Override showing pick info for now XXXXXXX

            else:
                return False, pickdata


        # ---------------------------------------------------
        # BOX SET IN MVIEWER REACT COMPONENT

        @app.callback(
            Output('box',   'data'),
            Input('viewer', 'box'),
            prevent_initial_call=True)

        def box_properties(box):

            #  When a box is drawn on an image, the box properties are saved to a "box"
            #  Store to be used if desired when cutting out a region into a subimage.

            
            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> box_properties() Callback:')
                print('DEBUG> BP From \'viewer\' setProps(box):', box)

            return(box)



        # ---------------------------------------------------
        # ZOOMBOX SET IN MVIEWER REACT COMPONENT

        @app.callback(
            Output('zoombox', 'data'),
            Input('viewer',   'zoombox'),
            prevent_initial_call=True)

        def zoom_properties(zoombox):

            #  Various actions (resizing the image display Div, zooming and panning)
            #  affect the display and we need to track these parameters in a "zoombox"
            #  Store which we use in various ways in the PNG generation.

            
            if debug == True:
                print('\n\nDEBUG> ==============================================================')
                print('DEBUG> zoom_properties() Callback:')
                print('DEBUG> ZP From \'viewer\' setProps(zoombox):', zoombox)
            return(zoombox)


        # ---------------------------------------------------
        # FIND A FREE PORT

        port = 8050

        with socket.socket() as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
            s.close()


        # ---------------------------------------------------
        # RUN THE APP

        app.run(jupyter_mode="external", port=port)
