from pathlib import Path

import streamlit.components.v1 as components

# Tell streamlit that there is a component called streamlit_social_share,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
	"streamlit_social_share", path=str(frontend_dir)
)

# Global custom networks registry
_custom_networks = {}

def create_custom_network(
    network_id: str,
    name: str,
    color: str,
    icon: str,
    share_url: str
) -> str:
    """Create a custom network that can be used in streamlit_social_share.
    
    Parameters
    ----------
    network_id : str
        Unique identifier for the network (used in networks list)
    name : str
        Display name for the button
    color : str
        Background color (hex code like #FF6B6B)
    icon : str
        Emoji, character, or URL to an image
    share_url : str
        URL template with {text}, {url}, {image} placeholders
        
    Returns
    -------
    str
        The network_id that can be used in the networks parameter
        
    Example
    -------
    >>> my_network = create_custom_network(
    ...     "my_platform", 
    ...     "My Platform", 
    ...     "#FF6B6B", 
    ...     "🚀",
    ...     "https://myplatform.com/share?url={url}&text={text}"
    ... )
    >>> streamlit_social_share(networks=[my_network, "linkedin", "x"])
    """
    _custom_networks[network_id] = {
        "name": name,
        "color": color,
        "icon": icon,
        "getUrl": share_url
    }
    return network_id

# Create the python function that will be called
def streamlit_social_share(
    text: str = "",
    url: str | None = None,
    image: str | None = None,
    networks: list[str] | None = None,
    custom_networks: dict | None = None,
    key: str | None = None,
) -> str | None:
    """Display social sharing buttons in a Streamlit app.

    Parameters
    ----------
    text : str, optional
        Text to include in the shared message, by default an empty string.
    url : str | None, optional
        The URL to share. If ``None``, the current page URL is used.
    image : str | None, optional
        Image URL to attach to the share when supported.
    networks : list[str] | None, optional
        Social networks to display. If ``None``, all default networks are shown.
        Can include built-in network IDs and custom network IDs created with create_custom_network().
    custom_networks : dict | None, optional
        Custom networks configuration. Dictionary with network_id as key and 
        config dict as value. Config should contain: name, color, icon, getUrl.
        Example: {"custom": {"name": "My Network", "color": "#FF0000", 
                            "icon": "🔥", "getUrl": "https://example.com/share"}}
        Note: It's recommended to use create_custom_network() instead.
    key : str | None, optional
        An optional unique key to identify the component.

    Returns
    -------
    str | None
        The name of the network used for sharing or ``None`` if no share was
        performed.
    """
    # Merge global custom networks with local custom networks
    all_custom_networks = {}
    all_custom_networks.update(_custom_networks)
    if custom_networks:
        all_custom_networks.update(custom_networks)
    
    return _component_func(
        text=text,
        url=url,
        image=image,
        networks=networks,
        custom_networks=all_custom_networks,
        key=key,
    )
