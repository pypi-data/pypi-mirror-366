from datetime import datetime
import pandas as pd
import dearpygui.dearpygui as dpg2
import DPGComponents.DPGComponents as comps

dpg2.create_context()
dpg2.create_viewport()
dpg2.setup_dearpygui()

def _on_demo_close(sender, app_data, user_data):
    dpg2.delete_item('date_picker_1')
    dpg2.delete_item('text_box_1')
    dpg2.delete_item(sender)

with dpg2.window(label="Example Components Window", on_close=_on_demo_close, width=800, 
                 height=800, pos=(100,100) ) as w:
    
    with dpg2.tree_node(label="Date picker"):

        dpg2.add_component(comps.DatePickerComp, tag=f'date_picker_1')

        # Set default date to today
        dpg2.configure_item(f'date_picker_1', default_value = datetime.now().date())

    
    with dpg2.tree_node(label="Data Grid"):

        dpg2.add_text(default_value="Render a Pandas Data Frame to the GUI", show_label=False)
        # Add Data Grid component
        dpg2.add_component(comps.DataGridComp, tag=f'data_grid_1')
        
        data = {
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 28],
            'City': ['New York', 'London', 'Paris']
        }
        df = pd.DataFrame(data)
        
        # Set data grid value
        dpg2.set_value('data_grid_1', value = df)
        
        # get component config
        config = dpg2.get_item_configuration('data_grid_1')

# show dpg registry
dpg2.show_item_registry()

dpg2.show_viewport()
dpg2.start_dearpygui()
dpg2.destroy_context()