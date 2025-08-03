// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.

function sendValue(value) {
  Streamlit.setComponentValue(value)
}

// Social network configurations
const SOCIAL_NETWORKS = {
  x: {
    name: 'X',
    color: '#000000',
    icon: '𝕏',
    getUrl: (text, url, image) => `https://x.com/intent/post?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`
  },
  linkedin: {
    name: 'LinkedIn',
    color: '#0077B5',
    icon: '💼',
    getUrl: (text, url, image) => `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`
  },
  reddit: {
    name: 'Reddit',
    color: '#FF4500',
    icon: '🔗',
    getUrl: (text, url, image) => `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`
  },
  facebook: {
    name: 'Facebook',
    color: '#1877F2',
    icon: '📘',
    getUrl: (text, url, image) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`
  },
  whatsapp: {
    name: 'WhatsApp',
    color: '#25D366',
    icon: '💬',
    getUrl: (text, url, image) => `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`
  },
  telegram: {
    name: 'Telegram',
    color: '#0088CC',
    icon: '✈️',
    getUrl: (text, url, image) => `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`
  },
  threads: {
    name: 'Threads',
    color: '#000000',
    icon: '🧵',
    getUrl: (text, url, image) => `https://www.threads.net/intent/post?text=${encodeURIComponent(text + ' ' + url)}`
  },
  email: {
    name: 'Email',
    color: '#666666',
    icon: '📧',
    getUrl: (text, url, image) => `mailto:?subject=${encodeURIComponent(text)}&body=${encodeURIComponent(text + '\n\n' + url)}`
  }
}

function createShareButton(network, text, url, image, customNetworks = {}) {
  // Check if it's a custom network first
  let config = customNetworks[network] || SOCIAL_NETWORKS[network]
  if (!config) return null

  const button = document.createElement('button')
  button.className = 'share-button'
  button.style.backgroundColor = config.color
  
  // Handle different icon types (emoji, character, URL, or path)
  let iconElement = ''
  if (config.icon) {
    if (config.icon.startsWith('http') || config.icon.startsWith('/') || config.icon.includes('.')) {
      // It's a URL or file path
      iconElement = `<img src="${config.icon}" alt="${config.name}" style="width: 16px; height: 16px; margin-right: 6px; vertical-align: middle;">`
    } else {
      // It's an emoji or character
      iconElement = `<span style="margin-right: 6px;">${config.icon}</span>`
    }
  }
  
  button.innerHTML = `${iconElement}${config.name}`
  
  button.onclick = () => {
    if (config.getUrl) {
      let shareUrl
      if (typeof config.getUrl === 'function') {
        shareUrl = config.getUrl(text, url, image)
      } else if (typeof config.getUrl === 'string') {
        // Handle string templates
        shareUrl = config.getUrl
          .replace('{text}', encodeURIComponent(text))
          .replace('{url}', encodeURIComponent(url))
          .replace('{image}', encodeURIComponent(image))
      }
      if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400')
      }
    }
    sendValue(network)
  }
  
  return button
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event) {
  const { 
    text = '', 
    url = window.location.href, 
    image = '', 
    networks = ['x', 'linkedin', 'reddit'],
    custom_networks = {}
  } = event.detail.args
  
  const root = document.getElementById('root')
  root.innerHTML = '' // Clear previous content
  
  const container = document.createElement('div')
  container.className = 'share-container'
  
  networks.forEach(network => {
    const button = createShareButton(network, text, url, image, custom_networks)
    if (button) {
      container.appendChild(button)
    }
  })
  
  root.appendChild(container)
  
  // Adjust frame height based on content
  const height = container.offsetHeight + 20 // Add some padding
  Streamlit.setFrameHeight(height)
}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady()
// Initial render
Streamlit.setFrameHeight(100)
