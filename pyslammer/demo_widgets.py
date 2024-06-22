import ipywidgets as widgets

def setup_widgets():
    """
    Sets up the interactive widgets for the demo.

    Returns:
    gm_widget (ipywidgets.Dropdown): The dropdown widget for selecting the ground motion.
    ky_widget (ipywidgets.BoundedFloatText): The bounded float text widget for setting the input PGA.
    analysis_widget (ipywidgets.ToggleButtons): The toggle buttons widget for selecting the analysis type.
    start_widget (ipywidgets.Button): The button widget for starting the analysis.
    """
    # Setting the input PGA
    ky_widget = widgets.BoundedFloatText(
        value=0.35,
        min=0,
        max=5.0,
        step=0.01,
        description='k_y (g):',
        disabled=False
    )
    # Selecting the ground motion
    gm_widget = widgets.Dropdown(
        options=[('Northridge', 'Northridge_VSP-360.csv'), ('Loma Prieta (not implemented)', 102), ('Nisqually (not implemented)', 103)],
        value='Northridge_VSP-360.csv',
        description='Select ground motion:',
    )

    # Setting the input PGA
    analysis_widget = widgets.ToggleButtons(
        options=['Rigid', 'Decoupled', 'Coupled'],
        description='Analysis type:',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltips=[],
    #     icons=['check'] * 3
    )

    # Start analysis
    start_widget = widgets.Button(
        description='Run Analysis',
        disabled=False,
        button_style='warning', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Run Analysis',
        icon='brave' # (FontAwesome names without the `fa-` prefix)
    )

    return gm_widget, ky_widget, analysis_widget, start_widget