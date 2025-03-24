import base64
from io import BytesIO

def get_logo_base64():
    """
    This function returns a base64 encoded svg logo for the PDF Knowledge Assistant.
    The logo is a simple design with a book and a magnifying glass.
    """
    svg_content = '''
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <!-- Book -->
      <rect x="20" y="25" width="60" height="50" rx="2" ry="2" fill="#4f8bf9" />
      <rect x="22" y="27" width="56" height="46" rx="1" ry="1" fill="white" />
      
      <!-- Pages -->
      <rect x="30" y="33" width="40" height="3" fill="#e6e6e6" />
      <rect x="30" y="39" width="40" height="3" fill="#e6e6e6" />
      <rect x="30" y="45" width="40" height="3" fill="#e6e6e6" />
      <rect x="30" y="51" width="30" height="3" fill="#e6e6e6" />
      
      <!-- Magnifying Glass -->
      <circle cx="68" cy="60" r="15" fill="none" stroke="#ef4da0" stroke-width="4" />
      <line x1="78" y1="70" x2="88" y2="80" stroke="#ef4da0" stroke-width="4" stroke-linecap="round" />
    </svg>
    '''
    return base64.b64encode(svg_content.encode()).decode()

def get_logo_html():
    """Returns the HTML img tag with the base64 encoded logo"""
    return f'<img src="data:image/svg+xml;base64,{get_logo_base64()}" width="100">' 