from typing import List, Any, Callable, Union, Tuple
import importlib
import dearpygui.dearpygui as dpg
import dearpygui._dearpygui as internal_dpg
from abc import ABC, abstractmethod
from datetime import date
import os



'''
COM REGISTRY:
    COMP_ID(int,str) = {'comp_ref':CLASS_REF, 'source_id':ID}

SOURCE REGISTRY:
    SOURCE_ID(int,str) = {'value':Any, 'comps':[ID..]}

'''
# TODO Thread safe struct ?
COM_REG     = dict() 
SOURCE_REG  = dict()

def add_component(cls : any, tag : Union[int, str] = None, parent : Union[int, str] = None , source : Union[int, str] = None, *args, **kwargs):
    '''
		Create and register new components
    '''
    def create_instance(cls, *args, **kwargs):
        """
        Creates an instance of a class from its class.

        Args:
            cls (any): Class
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            An instance of the class, or None if an error occurs.
        """
        try:
            instance = cls(*args, **kwargs)
            return instance
        except (ImportError, AttributeError, TypeError) as e:
            print(f"Error creating instance of: {cls}")
            raise e


    #_parent = parent if parent else dpg.last_item()
    _parent = parent
    _item =  tag if tag else dpg.generate_uuid()
    _source = source if source else _item
    assert _item not in COM_REG , f'Item {_item} already exist'
    
    # Create component
    _component = create_instance(cls,  _item,  _parent)

    # Add to COM_REG
    COM_REG[_item] = {'comp_ref':_component, 'source_id':_source}

    # Add to SOURCE REF
    if _source not in SOURCE_REG.keys():
      SOURCE_REG[_source] = {'value':None, 'comps':[_item]}
    else:
      SOURCE_REG[_source]['comps'].append(_item)
      _component.set_value(SOURCE_REG[_source]['value'])
	
    return _item

def _is_component(item : Union[int, str]) -> bool:    
    '''
        Returns True if this is a valid component Id
    '''
    return item in COM_REG
    
def get_value(item : Union[int, str], **kwargs) -> Any:
	"""	 Returns an item's value.

	Args:
		item (Union[int, str]): 
	Returns:
		Any
	"""

	return SOURCE_REG[COM_REG[item]['source_id']]['value'] if _is_component(item) else internal_dpg.get_value(item,**kwargs)
    
def set_value(item : Union[int, str], value : Any, **kwargs) -> None:
	"""	 Set's an item's value.

	Args:
		item (Union[int, str]): 
		value (Any): 
	Returns:
		None
	"""
	if _is_component(item):
		SOURCE_REG[COM_REG[item]['source_id']]['value'] = value
		for id in SOURCE_REG[COM_REG[item]['source_id']]['comps']:
			COM_REG[id]['comp_ref'].set_value(value)
		return None
	else:
		return internal_dpg.set_value(item, value, **kwargs)

def delete_item(item : Union[int, str], *, children_only: bool =False, slot: int =-1, **kwargs) -> None:
	"""	 Deletes an item..

	Args:
		item (Union[int, str]): 
		children_only (bool, optional): 
		slot (int, optional): 
	Returns:
		None
	"""

	if _is_component(item):
		COM_REG[item]['comp_ref'].delete(children_only, **kwargs)
		if COM_REG[item]['source_id'] in SOURCE_REG:
			del SOURCE_REG[COM_REG[item]['source_id']]
		del COM_REG[item]
	else:
		internal_dpg.delete_item(item, children_only=children_only, slot=slot, **kwargs)

def get_item_configuration(item : Union[int, str], **kwargs) -> dict:
	"""	 Returns an item's configuration.

	Args:
		item (Union[int, str]): 
	Returns:
		dict
	"""
	if _is_component(item):
		return COM_REG[item]['comp_ref'].get_item_configuration(**kwargs)
	else:
		return internal_dpg.get_item_configuration(item, **kwargs)

def configure_item(item : Union[int, str], **kwargs) -> None:
	"""Configures an item after creation."""

	if _is_component(item):
		COM_REG[item]['comp_ref'].configure_item(**kwargs)
	else:
		internal_dpg.configure_item(item, **kwargs)


# Update global DPG module
# --------------------------
dpg.add_component = add_component
dpg.get_value = get_value
dpg.set_value = set_value
dpg.delete_item = delete_item
dpg.get_item_configuration = get_item_configuration
dpg.configure_item = configure_item
