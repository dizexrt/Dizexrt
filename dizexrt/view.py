from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle


__all__ = (
	'button',
	'ButtonGroup',
	'ButtonStyle'
)

'''
style (Union[ButtonStyle, int]) – Style of the button. Refer to ButtonStyle.
label (Optional[str]) – The label of the button.
emoji (Union[discord.Emoji, discord.PartialEmoji, dict]) – The emoji of the button.
custom_id (Optional[str]) – The custom_id of the button. Needed for non-link buttons.
url (Optional[str]) – The URL of the button. Needed for link buttons.
disabled (bool) – Whether the button is disabled or not. Defaults to False.
'''

button_style = {
	'red':4,
	'green':3,
	'blue':1,
	'gray':2,
	'link':5
}

def button(on:bool, style:str, label:str, id:str = None, url:str = None, emoji = None):
	style = button_style[style]
	disabled = False if on else True
	return create_button(style = style, label = label, emoji = emoji, custom_id = id, url = url, disabled = disabled)

def ButtonGroup(*buttons):
	return [create_actionrow(*buttons)]